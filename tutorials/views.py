from django.shortcuts import render, redirect

# Create your views here.

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Tutorial, Student, StudentTutorialStatus

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'tutorials/signup.html', {'form': form})

def apply(request, tutorial_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = request.user
    student = Student.objects.first()
    s = StudentTutorialStatus(tutorial=tutorial, student=student, status="P")
    s.save()

    return redirect('/admin/tutorials/tutorial/')

def approve(request, tutorial_id, student_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(pk=student_id)
    status = StudentTutorialStatus.objects.filter(student=student).get(tutorial=tutorial)
    status.status = "A"
    status.save()

    return redirect('/admin/tutorials/tutorial/')


def reject(request, tutorial_id, student_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(pk=student_id)
    status = StudentTutorialStatus.objects.filter(student=student).get(tutorial=tutorial)
    status.status = "R"
    status.save()

    return redirect('/admin/tutorials/tutorial/')

