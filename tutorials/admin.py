from django.contrib import admin

# Register your models here.
from .models import College, Student, Tutorial, TutorialLink, StudentTutorialStatus

[admin.site.register(model) for model in (College, Student, Tutorial, TutorialLink, StudentTutorialStatus)]
