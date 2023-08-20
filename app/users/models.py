from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from knox.models import AuthToken


class VerfifiedUserManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_verified=True)


class ExtraUserManagers(models.Model):
    verified_objects = VerfifiedUserManager()

    class Meta:
        abstract = True


class User(AbstractUser, ExtraUserManagers):
    avatar = models.ImageField(blank=True, upload_to="users/avatars")
    headline = models.CharField(blank=True, max_length=60)
    bio = models.TextField(blank=True, max_length=255)
    is_verified = models.BooleanField(default=False)


class ChatKey(AuthToken):
    pass


class PlayStreamKey(AuthToken):
    pass


class VerificationKey(AuthToken):
    pass
