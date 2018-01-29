from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save


class College(models.Model):
    name = models.CharField(max_length=30, unique=True)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return str(self.name)

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class StudentManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class Student(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    majors = models.ManyToManyField(College)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)

    objects = StudentManager()

    def __str__(self):
        return str(self.name)

    def has_perm(self, perm, obj=None):
        # TODO: implement
        return True

    def has_module_perms(self, app_label):
        # TODO: implement
        return True

    USERNAME_FIELD = 'email'
    # EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


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
        return "({})".format(self.status), str(self.tutorial), str(self.student)

