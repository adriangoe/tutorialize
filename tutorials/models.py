from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class College(models.Model):
    name = models.CharField(max_length=30, unique=True)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return str(self.name)


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    majors = models.ManyToManyField(College)
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.name)


class Tutorial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    colleges = models.ManyToManyField(College)

    # def __str__(self):
    #     return '{t} ({c})'.format(t=self.title, c=', '.join([str (c) for c in self.colleges.all()]))


class TutorialLink(models.Model):
    tutorial = models.ForeignKey(Tutorial, on_delete=models.PROTECT)
    url = models.URLField()


class StudentTutorialStatus(models.Model):
    class Meta:
        unique_together = (("tutorial", "student"),)
        verbose_name_plural = 'Student-tutorial statuses'

    tutorial = models.ForeignKey(Tutorial, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    STATUS_OPTIONS = (
        ('O', 'Owner'),
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    status = models.CharField(max_length=1, choices=STATUS_OPTIONS)

    def __str__(self):
        return "({})".format(self.status) + str(self.tutorial) + str(self.student)

