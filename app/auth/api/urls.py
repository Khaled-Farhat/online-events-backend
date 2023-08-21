from django.urls import path, include
from rest_framework import routers

from .views import auth, streaming, verification


streamsRouter = routers.SimpleRouter()
streamsRouter.register(r"", streaming.StreamAuthViewSet, basename="stream")

verificationRouter = routers.SimpleRouter()
verificationRouter.register(
    r"", verification.EmailVerficiationViewSet, basename="verification"
)

urlpatterns = [
    path("login", auth.LoginView.as_view(), name="knox-login"),
    path("logout", auth.LogoutView.as_view(), name="knox-logout"),
    path("register", auth.RegisterView.as_view(), name="user-register"),
    path(r"streams/", include(streamsRouter.urls)),
    path(r"verification/", include(verificationRouter.urls)),
]
