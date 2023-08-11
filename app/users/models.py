from django.contrib.auth.models import AbstractUser
from django.db import models
from knox.models import AuthToken


class User(AbstractUser):
    avatar = models.ImageField(blank=True, upload_to="users/avatars")
    headline = models.CharField(blank=True, max_length=60)
    bio = models.TextField(blank=True, max_length=255)


class ChatKey(AuthToken):
    pass


class PlayStreamKey(AuthToken):
    pass
