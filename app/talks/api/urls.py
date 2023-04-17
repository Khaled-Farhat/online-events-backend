from django.urls import path, include
from rest_framework import routers
from .views import TalkViewSet

router = routers.SimpleRouter()
router.register(r"", TalkViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
]
