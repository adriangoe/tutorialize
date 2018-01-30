from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import College, Student


class SignUpForm(UserCreationForm):
    username = forms.EmailField(max_length=254, help_text='Please enter your Minerva email address.',
                                widget=forms.EmailInput(attrs={'class':'form-control',
                                                               'placeholder':'yourname@minerva.kgi.edu'}))
    name = forms.CharField(max_length=30, help_text='Please enter your name.',
                           widget=forms.TextInput(attrs={'class': 'form-control',
                                                         'placeholder': 'Your Name'})
                           )
    majors = forms.ModelMultipleChoiceField(College.objects.all(), to_field_name='code',
                                            help_text='Please select your majors.')

    class Meta:
        model = User
        fields = ('username', 'name', 'majors', 'password1', 'password2')

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

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit)
        user.is_active = False
        user.is_staff = True
        user.save()

        student_group = Group.objects.get(name='Students')
        student_group.user_set.add(user)
        student_group.save()

        student = Student(name=self.cleaned_data['name'],
                          email=self.cleaned_data['username'],
                          user=user)
        student.save(commit)
        student.majors.set(self.cleaned_data['majors'])
        student.save()
        return user

