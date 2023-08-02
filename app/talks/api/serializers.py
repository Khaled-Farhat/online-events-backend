from django.utils import timezone
from rest_framework import serializers, exceptions
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from users.models import User
from ..models import Talk


class TalkSerializer(serializers.ModelSerializer):
    speaker = serializers.SlugRelatedField(
        queryset=User.objects.all(), write_only=True, slug_field="username"
    )

    class Meta:
        model = Talk
        fields = ["id", "event", "speaker", "title", "start", "end", "status"]
        read_only_fields = ["id", "event", "status"]

    def validate_start(self, start):
        if start < timezone.now():
            raise exceptions.ValidationError(
                "Start time must be in the future."
            )
        return start

    def validate_end(self, end):
        if end < timezone.now():
            raise exceptions.ValidationError("End time must be in the future.")
        return end

    def validate(self, attrs):
        if attrs["start"] > attrs["end"]:
            raise exceptions.ValidationError(
                "start field must not exceed the end field."
            )
        if attrs["start"] < self.context.get("event").started_at:
            raise exceptions.ValidationError(
                "start field must be at least the started_at field of the "
                "event."
            )
        if Talk.objects.filter(
            status__in=["pending", "approved"],
            event=self.context.get("event"),
            start__lt=attrs["end"],
            end__gt=attrs["start"],
        ):
            raise exceptions.ValidationError("Talk collides with other talks.")
        return attrs

    def create(self, validated_data):
        return Talk.objects.create(
            event=self.context.get("event"), **validated_data
        )


class TalkSpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "avatar",
            "headline",
            "bio",
        ]


class TalkWithSpeakerDetailSerializer(TalkSerializer):
    speaker = TalkSpeakerSerializer()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "approve_talk",
            summary="Approve talk",
            value={"status": "approved"},
            request_only=True,
        ),
        OpenApiExample(
            "reject_talk",
            summary="Reject talk",
            value={"status": "rejected"},
            request_only=True,
        ),
    ],
)
class UpdateTalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Talk
        fields = ["status"]

    def validate_status(self, status):
        if self.instance is not None and (
            (self.instance.status != "pending" and status == "pending")
            or (self.instance.status == "rejected" and status == "approved")
        ):
            message = (
                f"Changing status from {self.instance.status} to"
                f" {status} is not allowed."
            )
            raise exceptions.ValidationError(message)
        return status
