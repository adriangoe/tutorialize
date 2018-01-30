from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import Tutorial, Student, StudentTutorialStatus
from django.core.validators import validate_email, ValidationError
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)


def email_current_user(request, subject, template, context):
    to_email = request.user.username

    try:
        validate_email(to_email)

    except ValidationError:
        print('Username {u} is not an email, not sending email'.format(u=to_email))
        return

    send_email(to_email, subject, template, context)


def send_email(to_emails, subject, template, context):
    if isinstance(to_emails, str):
        to_emails = [to_emails]

    message = render_to_string(template, context)
    email = EmailMessage(subject, message, to=to_emails)
    email.send()


def email_tutorial_owners(request, student, tutorial, status, mail_subject, template):
    owner_statuses = StudentTutorialStatus.objects.filter(tutorial=tutorial, status="O")
    if owner_statuses is None or len(owner_statuses) == 0:
        logger.error('Found a tutorial without owners: {t}'.format(t=tutorial))
        return

    context = {
        'student': student,
        'tutorial': tutorial,
        'status': status,
        'domain': get_current_site(request).domain,
    }

    for owner in owner_statuses:
        context['owner'] = owner
        send_email(owner.student.email, mail_subject, template, context)
