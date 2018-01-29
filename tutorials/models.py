from django.db import models


class College(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=2)


class Tutorial(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    colleges = models.ManyToManyField(College)


class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    colleges = models.ManyToManyField(College)


class StudentTutorialStatus(models.Model):
    class Meta:
        unique_together = (("tutorial", "student"),)

    tutorial = models.OneToOneField(Tutorial, on_delete=models.PROTECT)
    student = models.OneToOneField(Student, on_delete=models.PROTECT)
    STATUS_OPTIONS = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    status = models.CharField(max_length=1, choices=STATUS_OPTIONS)

