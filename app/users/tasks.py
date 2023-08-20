from celery import shared_task
from .models import ChatKey, PlayStreamKey
from knox.models import AuthToken
from django.utils import timezone


@shared_task(name="users__clean_expired_tokens")
def clean_expired_tokens():
    models = [AuthToken, ChatKey, PlayStreamKey]
    for model in models:
        model.objects.filter(expiry__lt=timezone.now()).delete()
