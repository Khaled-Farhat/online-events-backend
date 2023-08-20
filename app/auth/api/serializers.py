from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import serializers, exceptions
from core.utils import ModelPluggableTokenAuthentication
from events.models import Event
from talks.models import Talk
from users.models import User, PlayStreamKey, VerificationKey
from users.api.serializers import UserSerializer


class RegisterSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["username", "email", "first_name", "last_name", "password"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if user := authenticate(
            username=data["username"],
            password=data["password"],
        ):
            if not user.is_verified:
                message = "Please verify your account."
                raise exceptions.PermissionDenied(message)
            data["user"] = user
            return data
        else:
            message = "Unable to log in with provided credentials."
            raise serializers.ValidationError(message, code="authorization")


# Validate that stream_url has the form /live/talk_id and
# corresponds to an active approved talk,
# and that param corresponds to a valid query string.
class StreamSerializer(serializers.Serializer):
    stream_url = serializers.CharField()
    param = serializers.CharField(allow_blank=True)

    def validate_stream_url(self, stream_url):
        segments = stream_url.split("/")
        if len(segments) != 3 or segments[1] != "live":
            message = "Invalid stream_url"
            raise serializers.ValidationError(message)
        stream = -1
        try:
            stream = int(segments[2])
        except Exception:
            message = "Invalid stream_url"
            raise serializers.ValidationError(message)

        self.talk = get_object_or_404(
            Talk, Q(status="approved", event__is_published=True), pk=stream
        )
        if self.talk.has_finished() or not self.talk.has_started():
            raise exceptions.PermissionDenied()
        return stream_url

    def validate_param(self, param):
        message = "Invalid query string"
        if len(param) == 0:
            self.query_params = ""
            self.validate_token()
            return param
        if param[0] == "?":
            param = param[1:]
        try:
            self.query_params = dict(
                segment.split("=") for segment in param.split("&")
            )
        except Exception:
            raise serializers.ValidationError(message)
        self.validate_token()
        return param

    def validate_token(self):
        if "token" not in self.query_params:
            raise exceptions.AuthenticationFailed()
        self.token = self.query_params.get("token")


class PublishStreamSerializer(StreamSerializer):
    def validate(self, attrs):
        self.validate_token()
        if self.talk.stream_key != self.token:
            raise exceptions.PermissionDenied()
        return attrs


class PlayStreamSerializer(StreamSerializer):
    def validate(self, attrs):
        self.validate_token()
        knox_auth = ModelPluggableTokenAuthentication()
        knox_auth.model = PlayStreamKey
        user, _ = knox_auth.authenticate_credentials(
            self.token.encode("utf-8")
        )
        if not Event.objects.filter(
            (Q(attendees=user) | Q(organizer=user)) & Q(talk__id=self.talk.id)
        ).exists():
            raise exceptions.PermissionDenied()
        return attrs


# A serializer that allows any traffic (for testing purposes)
class DummyStreamSerializer(StreamSerializer):
    def validate_stream_url(self, stream):
        return stream

    def validate_param(self, param):
        return param

    def validate_token(self):
        return True


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
