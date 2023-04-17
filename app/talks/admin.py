from django.contrib import admin
from .models import Talk


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ["title", "event", "speaker", "start", "end", "status"]
