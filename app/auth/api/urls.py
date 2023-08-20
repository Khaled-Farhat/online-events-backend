from django.urls import path, include
from rest_framework import routers

from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    StreamAuthViewSet,
    EmailVerficiationViewSet,
)


streamsRouter = routers.SimpleRouter()
streamsRouter.register(r"", StreamAuthViewSet, basename="stream")

verificationRouter = routers.SimpleRouter()
verificationRouter.register(
    r"", EmailVerficiationViewSet, basename="verification"
)

urlpatterns = [
    path("login", LoginView.as_view(), name="knox-login"),
    path("logout", LogoutView.as_view(), name="knox-logout"),
    path("register", RegisterView.as_view(), name="user-register"),
    path(r"streams/", include(streamsRouter.urls)),
    path(r"verification/", include(verificationRouter.urls)),
]
