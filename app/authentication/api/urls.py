from django.urls import path
from .views import LoginView, RegisterView, LogoutView, StreamView


urlpatterns = [
    path("login", LoginView.as_view(), name="knox-login"),
    path("logout", LogoutView.as_view(), name="knox-logout"),
    path("register", RegisterView.as_view(), name="user-register"),
    path("stream", StreamView.as_view(), name="stream-auth"),
]
