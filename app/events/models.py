from django.db import models
from users.models import User


class EventQuerySet(models.QuerySet):
    def is_published(self):
        return self.filter(is_published=True)


class Event(models.Model):
    organizer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="organized_events"
    )
    attendees = models.ManyToManyField(User, related_name="booked_events")
    title = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    picture = models.ImageField(blank=True, upload_to="events/pictures")
    is_published = models.BooleanField(default=False)
    objects = EventQuerySet.as_manager()

    def __str__(self):
        return self.title

    def has_finished(self):
        # To do
        return False
    
    def has_started(self):
        # To do
        return False
