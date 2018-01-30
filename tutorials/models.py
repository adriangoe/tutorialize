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
    class Meta:
        verbose_name = 'Tutorial'
        verbose_name_plural = 'Browse All Tutorials'

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    colleges = models.ManyToManyField(College)

    def __str__(self):
        return '{t} ({c})'.format(t=self.title, c=', '.join([str (c) for c in self.colleges.all()]))

    def n_members(self):
        return StudentTutorialStatus.objects.filter(tutorial=self).filter(status__in=["A", "O"]).count()


class TutorialLink(models.Model):
    class Meta:
        verbose_name = 'Inspiration/Resource Link'
        verbose_name_plural = 'Inspiration/Resource Link'
    tutorial = models.ForeignKey(Tutorial, on_delete=models.PROTECT)
    url = models.URLField()


class StudentTutorialStatus(models.Model):
    class Meta:
        unique_together = (("tutorial", "student"),)
        verbose_name = 'Tutorial Enrollment'
        verbose_name_plural = 'Manage Enrollments in your Tutorials'

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
        return "({}) {} {}".format(self.status, self.tutorial, self.student.email)

