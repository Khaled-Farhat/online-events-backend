from django.db.models.signals import post_save
from django.dispatch import receiver
from .mails import send_talk_invitation_mail, send_talk_status_mail
from .models import Talk


@receiver(post_save, sender=Talk)
def post_save_talk_send_talk_invitation_mail(
    sender, instance, created, **kwargs
):
    if created is True:
        send_talk_invitation_mail(instance)


@receiver(post_save, sender=Talk)
def post_save_talk_send_talk_status_mail(sender, instance, created, **kwargs):
    if created is False:
        send_talk_status_mail(instance)
