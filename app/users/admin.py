from django.contrib import admin
from .models import User, ChatKey, PlayStreamKey

# Register your models here.
admin.site.register(User)
admin.site.register(ChatKey)
admin.site.register(PlayStreamKey)
