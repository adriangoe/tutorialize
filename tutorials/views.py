# from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm
# from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.contrib.auth.models import User
from .models import Tutorial, Student, StudentTutorialStatus
from django.shortcuts import render, redirect
from .email_utils import send_email, email_tutorial_owners
import csv


def signup(request):
    if request.user.is_authenticated:
        return redirect('/_/')

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            token = account_activation_token.make_token(user)

            to_email = form.cleaned_data.get('username')
            name = form.cleaned_data.get('name')
            mail_subject = 'Activate your Tutorialize account.'
            context = {
                'name': name,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('ascii'),
                'token': token,
            }
            send_email(to_email, mail_subject, 'tutorials/activation_email.html', context)

            return HttpResponse('Please confirm your email address to complete the registration')

    else:
        form = SignUpForm()

    return render(request, 'tutorials/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    print(user, token, type(token), len(token))
    print(account_activation_token.check_token(user, token))
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/_/')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')

    else:
        return HttpResponse('Activation link is invalid!')


def apply(request, tutorial_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(user=request.user)
    status = StudentTutorialStatus(tutorial=tutorial, student=student, status="P", priority=1)
    status.save()

    mail_subject = 'Tutorialize: tutorial join request'
    template = 'tutorials/tutorial_request_email.html'
    email_tutorial_owners(request, student, tutorial, status, mail_subject, template)

    return redirect('/_/tutorials/mytutorial/')


def withdraw(request, tutorial_id, student_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(pk=student_id)
    status = StudentTutorialStatus.objects.filter(student=student).get(tutorial=tutorial)
    status.delete()

    mail_subject = 'Tutorialize: tutorial withdrawal'
    template = 'tutorials/tutorial_withdrawal_email.html'
    email_tutorial_owners(request, student, tutorial, status, mail_subject, template)

    return redirect('/_/tutorials/tutorial/')


def cancel(request, tutorial_id, student_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(pk=student_id)
    status = StudentTutorialStatus.objects.filter(student=student).get(tutorial=tutorial)
    status.delete()

    return redirect('/_/tutorials/tutorial/')


def set_prio(request, status_id):
    status = StudentTutorialStatus.objects.get(pk=status_id)
    prio = request.POST['prio']
    print(prio, "HI ADRIAN")

    status.priority = int(prio)
    status.save()

    return redirect('/_/tutorials/mytutorial/')


def export(request):
    user = request.user
    student = Student.objects.get(user=user)
    statuses = StudentTutorialStatus.objects.filter(student=student).filter(status__in=['O', 'A']).order_by('priority', 'id')
    statuses_per_tutorial = [StudentTutorialStatus.objects.
                                 filter(tutorial=status.tutorial).
                                 exclude(status="R").
                                 exclude(status="P").
                                 order_by('student__name')
                             for status in statuses]

    send_email(user.username, 'Tutorialize Proposals Export', 'tutorials/export_email.html', {
        'student': student, 'statuses': statuses, 'statuses_per_tutorial': statuses_per_tutorial
    }, html=True)

    return render(request, 'tutorials/export_email_alert_and_redirect.html', {})

def export_csv(request):
    if not request.user.is_superuser:
        return redirect('/')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tutorialize.csv"'

    statuses = StudentTutorialStatus.objects.filter(status__in=['O', 'A']).order_by('tutorial', 'priority', 'id')
    writer = csv.writer(response)
    writer.writerow(['Tutorial Name', 'Description', 'Requirements', 'Colleges', 'Student Name', 'Student Majors', 'Student Priority'])
    for status in statuses:
        writer.writerow([status.tutorial.title, status.tutorial.description, status.tutorial.prerequisites, ' '.join([str(c.code) for c in status.tutorial.colleges.all()]), status.student.name, ' '.join([str(c.code) for c in status.student.majors.all()]), status.priority])

    # TODO finish writing export.
    return response
