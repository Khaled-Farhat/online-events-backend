from django.urls import path, include
from rest_framework import routers

from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    StreamAuthViewSet,
)


router = routers.SimpleRouter()
router.register(r"", StreamAuthViewSet, basename="stream")

urlpatterns = [
    path("login", LoginView.as_view(), name="knox-login"),
    path("logout", LogoutView.as_view(), name="knox-logout"),
    path("register", RegisterView.as_view(), name="user-register"),
    path(r"streams/", include(router.urls)),
]
