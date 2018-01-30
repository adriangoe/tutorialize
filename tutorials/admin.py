from django.contrib import admin
from django.utils.html import format_html
from .models import College, Student, Tutorial, TutorialLink, StudentTutorialStatus
from django.shortcuts import redirect
from .email_utils import send_email
from django.contrib.sites.shortcuts import get_current_site
from url_filter.filtersets import ModelFilterSet


# Register your models here.
from .models import Tutorial, College, Student, StudentTutorialStatus, TutorialLink

[admin.site.register(model) for model in (College, Student)]


def remove_from_fieldsets(fieldsets, fields):
    for fieldset in fieldsets:
        for field in fields:
            if field in fieldset[1]['fields']:
                new_fields = []
                for new_field in fieldset[1]['fields']:
                    if not new_field in fields:
                        new_fields.append(new_field)

                fieldset[1]['fields'] = tuple(new_fields)
                break

class TutorialLinkInline(admin.TabularInline):
    model = TutorialLink
    extra = 1
    readonly_fields = ('id',)

    def get_readonly_fields(self, request, obj=None):
        user = Student.objects.get(user=request.user)
        status = StudentTutorialStatus.objects.filter(tutorial=obj).filter(student=user).first()
        if not obj or (status and status.status == "O") or request.user.is_superuser:
            return super(TutorialLinkInline, self).get_readonly_fields(
                request, obj=obj
            )
        return ['url']


class TutorialFilterSet(ModelFilterSet):
    class Meta(object):
        model = Tutorial


class TutorialAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = ['title', 'description', 'college', 'open_spots', 'action_buttons']
    search_fields = ['title']
    list_filter = ['colleges']
    inlines = [
        TutorialLinkInline,
    ]
    ordering = ('-title', )
    change_form_template = 'admin/no_history.html'

    def college(self, obj):
        return str(', '.join([str(c.code) for c in obj.colleges.all()]))

    def open_spots(self, obj):
        n = obj.n_members()
        color = 'orange'
        if n in [3,4]:
            color = 'green'
        elif n == 5:
            color = 'blue'
        return format_html('<b style="color:{};">{}</b>'.format(color, 5 - n))

    def action_buttons(self, obj):
        user = Student.objects.get(user=self.request.user)
        status = StudentTutorialStatus.objects.filter(tutorial=obj).filter(student=user).first()
        quota = 5 * user.majors.all().count()

        if status and status.status == "P":
            return format_html(
                '<a class="button" href="/cancel/{}/{}">Cancel Request</a>',
                obj.pk, user.pk
            )
        elif status and status.status == "A":
            return format_html(
                '<a class="button" href="/withdraw/{}/{}">Withdraw</a>',
                obj.pk, user.pk
            )
        elif status and status.status == "R":
            return format_html("Rejected :(")
        elif status and status.status == "O":
            return format_html(
                '<a class="button" href="/_/tutorials/studenttutorialstatus/?tutorial__id__exact={}">Manage {} Applicants</a>',
                obj.pk, StudentTutorialStatus.objects.filter(tutorial=obj).filter(status="P").count()
            )
        elif obj.n_members() > 5:
            return format_html(
                'Tutorial full'
            )
        elif StudentTutorialStatus.objects.filter(student=user).filter(status__in=["O","A"]).count() >= quota:
            return format_html(
                'You are over your quota of {}'.format(quota)
            )
        return format_html(
            '<a class="button" href="/apply/{}">Apply</a>',
            obj.pk
        )
    action_buttons.allow_tags = True

    def members(self, obj):
        students = StudentTutorialStatus.objects.filter(tutorial=obj).exclude(status="R").exclude(status="P")
        return ", ".join([str(s.student) + " (" + s.status + ")" for s in students])

    def get_fieldsets(self, request, obj=None):
        user = Student.objects.get(user=request.user)
        status = StudentTutorialStatus.objects.filter(tutorial=obj).filter(student=user).first()

        fieldsets = super(TutorialAdmin, self).get_fieldsets(request, obj)

        if not request.user.is_superuser and (not status or status.status not in ["O", "A"]):
            remove_from_fieldsets(fieldsets, ('member',))
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        user = Student.objects.get(user=request.user)
        status = StudentTutorialStatus.objects.filter(tutorial=obj).filter(student=user).first()
        if not obj or (status and status.status == "O") or request.user.is_superuser:
            return super(TutorialAdmin, self).get_readonly_fields(
                request, obj=obj
            ) + ('open_spots', 'members')
        elif status and status.status == "A":
            return ['title', 'description', 'colleges', 'open_spots', 'members', 'action_buttons']
        return ['title', 'description', 'colleges', 'open_spots', 'action_buttons']

    def save_model(self, request, obj, form, change):
        super(TutorialAdmin, self).save_model(request, obj, form, change)

        if not StudentTutorialStatus.objects.filter(tutorial=obj):
            s = StudentTutorialStatus(tutorial=obj, student=Student.objects.get(user=request.user), status="O")
            s.save()

        if not change:
            email_set = set()
            for college in form.cleaned_data['colleges']:
                email_set.update([student.email for student in college.student_set.all()])

            mail_subject = 'Tutorialize: new tutorial added'
            template = 'tutorials/new_tutorial_email.html'
            send_email(list(email_set), mail_subject, template,
                       {'tutorial': obj, 'domain': get_current_site(request).domain})

    def get_queryset(self, request):
        qs = super(TutorialAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.exclude(studenttutorialstatus__student=Student.objects.get(user=request.user))

    def changelist_view(self, request, extra_context=None):
        # Initial filter by first major
        self.request = request
        if request.user.is_superuser:
            return super(TutorialAdmin,self).changelist_view(request)
        referrer = request.META.get('HTTP_REFERER', '')
        get_param = "colleges__id__in={}".format(",".join([str(m.id) for m in Student.objects.get(user=request.user).majors.all()])) # set default filter on colleges here
        print(get_param, request.path)
        if len(request.GET) == 0 and '?' not in referrer:
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(TutorialAdmin,self).changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        #Disable delete
        actions = super(TutorialAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(Tutorial, TutorialAdmin)


class StudentTutorialStatusAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = ['tutorial', 'student', 'status']
    search_fields = ['tutorial']
    readonly_fields = ['tutorial', 'student']
    ordering = ('-tutorial','-status')

    def get_queryset(self, request):
        qs = super(StudentTutorialStatusAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs.filter()
        else:
            tutorials = StudentTutorialStatus.objects.filter(student=Student.objects.get(user=request.user)).filter(status="O").values_list('tutorial')
            print(tutorials)

            return qs.filter(tutorial__in=tutorials).exclude(student=Student.objects.get(user=request.user))

    def save_model(self, request, obj, form, change):
        super(StudentTutorialStatusAdmin, self).save_model(request, obj, form, change)

        student = obj.student
        tutorial = obj.tutorial
        members = StudentTutorialStatus.objects.filter(tutorial=tutorial).exclude(status="R").exclude(status="P")
        if obj.status == 'A':
            mail_subject = 'Tutorialize: tutorial request approved'
            template = 'tutorials/tutorial_approved_email.html'
            send_email(student.email, mail_subject, template,
                       {'student': student, 'tutorial': tutorial,
                        'members': members, 'domain': get_current_site(request).domain})

        elif obj.status == 'R':
            mail_subject = 'Tutorialize: tutorial request rejected'
            template = 'tutorials/tutorial_rejected_email.html'
            send_email(student.email, mail_subject, template,
                       {'student': student, 'tutorial': tutorial,
                        'domain': get_current_site(request).domain})

    def get_actions(self, request):
        #Disable delete
        actions = super(StudentTutorialStatusAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(StudentTutorialStatus, StudentTutorialStatusAdmin)

class MyTutorial(Tutorial):
    class Meta:
        proxy = True
        verbose_name = 'Tutorial/Request'
        verbose_name_plural = 'My Tutorials and Requests'

class MyTutorialAdmin(TutorialAdmin):

    def get_queryset(self, request):
        qs = super(TutorialAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(studenttutorialstatus__student=Student.objects.get(user=request.user))

    def changelist_view(self, request, extra_context=None):
        # Initial filter by first major
        self.request = request
        return super(TutorialAdmin,self).changelist_view(request, extra_context=extra_context)

admin.site.register(MyTutorial, MyTutorialAdmin)

