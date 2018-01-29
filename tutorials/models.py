from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class College(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=2)

    def __str__(self):
        return str(self.name)


class Student(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    colleges = models.ManyToManyField(College)

    def __str__(self):
        return str(self.name)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'colleges']


class Tutorial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    colleges = models.ManyToManyField(College)

    def __str__(self):
        return '{t} ({c})'.format(t=self.title, c=', '.join([str (c) for c in self.colleges.all()]))


class TutorialLink(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.PROTECT)
    url = models.URLField()


class StudentTutorialStatus(models.Model):
    class Meta:
        unique_together = (("tutorial", "student"),)
        verbose_name_plural = 'Student-tutorial statuses'

    tutorial = models.OneToOneField(Tutorial, on_delete=models.PROTECT)
    student = models.OneToOneField(Student, on_delete=models.PROTECT)
    STATUS_OPTIONS = (
        ('O', 'Owner'),
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    status = models.CharField(max_length=1, choices=STATUS_OPTIONS)

