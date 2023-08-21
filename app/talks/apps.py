from django.apps import AppConfig


class TalksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "talks"

    def ready(self):
        from . import signals  # noqa: F401
