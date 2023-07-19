from django.utils import timezone
from django.db import models
from events.models import Event
from users.models import User
from django.utils.crypto import get_random_string
from functools import partial


class TalkQuerySet(models.QuerySet):
    def only_approved(self):
        return self.filter(status="approved")


class Talk(models.Model):
    STATUSES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    speaker = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(
        choices=STATUSES, max_length=8, default="pending"
    )
    stream_key = models.CharField(
        max_length=20,
        unique=True,
        default=partial(get_random_string, 20),
    )

    objects = TalkQuerySet.as_manager()

    def has_started(self):
        return self.start <= timezone.now()

    def has_finished(self):
        return self.end < timezone.now()
