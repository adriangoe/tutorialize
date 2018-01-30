from django.contrib import admin
from django.utils.html import format_html
from .models import College, Student, Tutorial, TutorialLink, StudentTutorialStatus
from django.shortcuts import redirect
from .email_utils import send_email
from django.contrib.sites.shortcuts import get_current_site

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


class TutorialAdmin(admin.ModelAdmin):

    list_per_page = 50
    list_display = ['title', 'description', 'college', 'open_spots', 'action_buttons']
    search_fields = ['title']
    list_filter = ['colleges']
    inlines = [
        TutorialLinkInline,
    ]

    def college(self, obj):
        return str(', '.join([str (c) for c in obj.colleges.all()]))

    def open_spots(self, obj):
        return 5 - StudentTutorialStatus.objects.filter(tutorial=obj).filter(status__in=["A", "O"]).count()

    def action_buttons(self, obj):
        user = Student.objects.get(user=self.request.user)
        status = StudentTutorialStatus.objects.filter(tutorial=obj).filter(student=user).first()

        if status and status.status == "P":
            return format_html("PENDING")
        elif status and status.status == "A":
            return format_html(
                '<a class="button" href="/withdraw/{}">Withdraw</a>',
                obj.pk
            )
        elif status and status.status == "R":
            return format_html("Rejected :(")
        elif status and status.status == "O":
            return format_html(
                '<a class="button" href="/admin/tutorials/studenttutorialstatus/?tutorial__id__exact={}">Manage</a>',
                obj.pk
            )
        return format_html(
            '<a class="button" href="/apply/{}">Apply</a>',
            obj.pk
        )
    action_buttons.allow_tags = True

    def members(self, obj):
        students = StudentTutorialStatus.objects.filter(tutorial=obj).exclude(status="R").exclude(status="P")
        return "".join([str(s.student) + "(" + s.status + ")" for s in students])

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
            student = request.user
            s = StudentTutorialStatus(tutorial=obj, student=Student.objects.get(user=request.user), status="O")
            s.save()

        email_set = set()
        for college in obj.colleges:
            email_set.update([student.email for student in college.student_set])

        mail_subject = 'Tutorialize: new tutorial added'
        template = 'tutorials/new_tutorial_email.html'
        send_email(email_set, mail_subject, template,
                   {'tutorial': obj, 'domain': get_current_site(request).domain})

    def changelist_view(self, request, extra_context=None):
        self.request = request
        referrer = request.META.get('HTTP_REFERER', '')
        get_param = "colleges__in=['AH','CS']" # set default filter on colleges here
        if len(request.GET) == 0 and '?' not in referrer:
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(TutorialAdmin,self).changelist_view(request, extra_context=extra_context)


admin.site.register(Tutorial, TutorialAdmin)


class StudentTutorialStatusAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = ['tutorial', 'student', 'status']
    search_fields = ['tutorial']
    list_filter = ['tutorial']
    readonly_fields = ['tutorial', 'student']

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


admin.site.register(StudentTutorialStatus, StudentTutorialStatusAdmin)
