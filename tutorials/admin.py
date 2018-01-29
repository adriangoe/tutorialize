from django.contrib import admin

# Register your models here.
from .models import Tutorial, College, Student, StudentTutorialStatus

[admin.site.register(model) for model in (Tutorial, College, Student, StudentTutorialStatus)]
