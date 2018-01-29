from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import College, Student


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=30, help_text='Please enter your name.')
    email = forms.EmailField(max_length=254, help_text='Please enter your Minerva email address.')
    majors = forms.ModelMultipleChoiceField(College.objects.all(), to_field_name='code',
                                            help_text='Please select your majors.')

    class Meta:
        model = Student
        fields = ('name', 'email', 'majors', 'password1', 'password2')

    def clean_email(self):
        data = self.cleaned_data['email']
        if not data.lower().endswith('@minerva.kgi.edu'):
            raise forms.ValidationError('Please use your @minerva.kgi.edu email.')

        return data

    def clean_majors(self):
        data = self.cleaned_data['majors']
        if len(data) > 2:
            raise forms.ValidationError('Please select up to two majors only.')

        return data
