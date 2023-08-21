from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from core.utils import ModelPluggableTokenAuthentication
from users.models import User, VerificationKey


class EmailVerificationMixin:
    def validate_verification_permitted(self, user):
        if user.is_verified:
            message = "Account is already verified."
            raise serializers.ValidationError(message)
        if User.objects.filter(email=user.email, is_verified=True).exists():
            message = "Email was used to verify another account."
            raise exceptions.PermissionDenied(message)


class VerficationKeySerializer(EmailVerificationMixin, serializers.Serializer):
    verification_key = serializers.CharField()

    def validate_verification_key(self, verification_key):
        knox_auth = ModelPluggableTokenAuthentication()
        knox_auth.model = VerificationKey
        self.user, _ = knox_auth.authenticate_credentials(
            verification_key.encode("utf-8")
        )
        self.validate_verification_permitted(self.user)
        return verification_key


class ResendVerficationKeySerializer(
    EmailVerificationMixin, serializers.Serializer
):
    username = serializers.CharField()

    def validate_username(self, username):
        self.user = get_object_or_404(User, username=username)
        self.validate_verification_permitted(self.user)
        return username
