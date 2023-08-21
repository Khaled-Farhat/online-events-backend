from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from ..serializers.verification import (
    VerficationKeySerializer,
    ResendVerficationKeySerializer,
)
from auth.mails import send_verification_email
from users.models import VerificationKey


@extend_schema_view(
    verify_email=extend_schema(
        responses={204: None, 400: None, 401: None, 403: None, 404: None},
    ),
    resend_verification_email=extend_schema(
        responses={204: None, 400: None, 401: None, 403: None, 404: None},
    ),
)
class EmailVerficiationViewSet(GenericViewSet):
    def get_serializer_class(self):
        if self.action == "verify_email":
            return VerficationKeySerializer
        elif self.action == "resend_verification_email":
            return ResendVerficationKeySerializer

    @action(detail=False, methods=["post"], url_path="verify-email")
    def verify_email(self, request):
        serializer = self.run_serializer(request)
        serializer.user.is_verified = True
        serializer.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["post"],
        url_path="resend-verification-email",
        url_name="resend-email",
    )
    def resend_verification_email(self, request):
        serializer = self.run_serializer(request)
        _, verification_key = VerificationKey.objects.create(serializer.user)
        send_verification_email(
            serializer.user.username, serializer.user.email, verification_key
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def run_serializer(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer
