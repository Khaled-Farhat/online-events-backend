from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task


@shared_task
def send_mail_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        html_message=message,
    )
