from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from .models import Tutorial, College, Student, StudentTutorialStatus

[admin.site.register(model) for model in (College, Student, StudentTutorialStatus)]

class TutorialAdmin(admin.ModelAdmin):

    list_per_page = 5
    list_display = ['title', 'description', 'college', 'open_spots', 'action_buttons']
    search_fields = ['title']
    fields = ['title', 'description', 'colleges']
    list_filter = ['colleges']
    # filter_horizontal = ['colleges']

    def college(self, obj):
        return str(', '.join([str (c) for c in obj.colleges.all()]))

    def open_spots(self, obj):
        return 4 - StudentTutorialStatus.objects.filter(tutorial=obj).filter(status="A").count()

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="/apply/{}">Apply</a>',
            obj.pk
        )
    action_buttons.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and request.user.has_perm('tutorials.read_item'):
            return [f.name for f in self.model._meta.fields]
        return super(TutorialAdmin, self).get_readonly_fields(
            request, obj=obj
        )

    def save_model(self, request, obj, form, change):
        super(TutorialAdmin, self).save_model(request, obj, form, change)

        if not StudentTutorialStatus.objects.filter(tutorial=obj):
            student = request.user
            print(student)
            s = StudentTutorialStatus(tutorial=obj, student=Student.objects.first(), status="O")
            s.save()

admin.site.register(Tutorial, TutorialAdmin)
