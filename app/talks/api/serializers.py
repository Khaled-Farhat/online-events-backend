from django.utils import timezone
from rest_framework import serializers, exceptions
from users.models import User
from ..models import Talk


class TalkSerializer(serializers.ModelSerializer):
    speaker__username = serializers.SlugRelatedField(
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
                "Start time must not exceed end time."
            )
        if Talk.objects.filter(
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
