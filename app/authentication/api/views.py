from django.contrib.auth import login
from rest_framework import generics, serializers, permissions
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    inline_serializer,
)
from knox.views import LoginView as KnoxLoginView, LogoutView as KnoxLogoutView
from users.api.serializers import UserSerializer
from .serializers import RegisterSerializer, LoginSerializer


@extend_schema_view(
    post=extend_schema(responses={200: RegisterSerializer, 400: None})
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


@extend_schema_view(
    post=extend_schema(
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                "login_response_serializer",
                fields={
                    "expiry": serializers.DateTimeField(),
                    "token": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            400: None,
        },
    )
)
class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def get_user_serializer_class(self):
        return UserSerializer

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)


@extend_schema_view(post=extend_schema(responses={204: None, 401: None}))
class LogoutView(KnoxLogoutView):
    pass
