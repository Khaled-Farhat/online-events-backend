from celery import Celery

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY_CONF")
app.autodiscover_tasks()
