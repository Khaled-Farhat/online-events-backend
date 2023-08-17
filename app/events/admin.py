from django.contrib import admin
from .models import Event
from talks.models import Talk


class TalkInline(admin.StackedInline):
    model = Talk


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "organizer", "is_published", "started_at"]
    inlines = [TalkInline]
