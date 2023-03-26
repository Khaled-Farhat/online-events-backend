from django.urls import path
from knox.views import LogoutView
from .views import LoginView, RegisterView

urlpatterns = [
    path("login", LoginView.as_view(), name="knox-login"),
    path("logout", LogoutView.as_view(), name="knox-logout"),
    path("register", RegisterView.as_view(), name="user-register"),
]
