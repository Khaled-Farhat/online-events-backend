from django.urls import path, include
from rest_framework import routers
from .views import EventViewSet

router = routers.SimpleRouter()
router.register(r"", EventViewSet, basename="event")

urlpatterns = [
    path(r"", include(router.urls)),
]
