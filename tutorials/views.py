# from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import UserCreationForm
# from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .models import Tutorial, Student, StudentTutorialStatus
from django.shortcuts import render, redirect



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            user.save()
            token = account_activation_token.make_token(user)

            current_site = get_current_site(request)
            mail_subject = 'Activate your Tutorialize account.'
            message = render_to_string('tutorials/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode('ascii'),
                'token': token,
            })

            to_email = form.cleaned_data.get('username')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
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
        return redirect('/admin')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')

    else:
        return HttpResponse('Activation link is invalid!')


def apply(request, tutorial_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(user=request.user)
    s = StudentTutorialStatus(tutorial=tutorial, student=student, status="P")
    s.save()

    return redirect('/admin/tutorials/tutorial/')

def withdraw(request, tutorial_id, student_id):
    tutorial = Tutorial.objects.get(pk=tutorial_id)
    student = Student.objects.get(pk=student_id)
    status = StudentTutorialStatus.objects.filter(student=student).get(tutorial=tutorial)
    status.delete()

    return redirect('/admin/tutorials/tutorial/')

