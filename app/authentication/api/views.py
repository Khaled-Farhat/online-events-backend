from django.contrib.auth import login
from rest_framework import generics
from rest_framework.permissions import AllowAny
from knox.views import LoginView as KnoxLoginView
from users.api.serializers import UserSerializer
from .serializers import LoginSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


class LoginView(KnoxLoginView):
    permission_classes = (AllowAny,)

    def get_user_serializer_class(self):
        return UserSerializer

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)
