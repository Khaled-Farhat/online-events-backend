from django.contrib.auth import login
from rest_framework import (
    generics,
    serializers,
    permissions,
)
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    inline_serializer,
)
from knox.views import LoginView as KnoxLoginView, LogoutView as KnoxLogoutView
from users.api.serializers import UserSerializer
from ..serializers.auth import RegisterSerializer, LoginSerializer
from auth.mails import send_verification_email
from users.models import VerificationKey


@extend_schema_view(
    post=extend_schema(responses={200: RegisterSerializer, 400: None})
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        _, verification_key = VerificationKey.objects.create(user)
        send_verification_email(user.username, user.email, verification_key)


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
            403: None,
        },
    )
)
class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def get_context(self):
        context = super().get_context()
        context.pop("request")  # To return a relative avatar URI
        return context

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
