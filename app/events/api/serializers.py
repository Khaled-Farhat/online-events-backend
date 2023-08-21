from django.utils import timezone
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from ..models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "title",
            "description",
            "picture",
            "is_published",
            "started_at",
        ]

    def validate_started_at(self, started_at):
        if started_at < timezone.now():
            raise exceptions.ValidationError(
                "started_at field must be in the future."
            )
        return started_at

    def validate_is_published(self, value):
        if (
            self.instance
            and self.instance.is_published is True
            and value is False
        ):
            raise ValidationError(
                "Unpublishing a published event is not allowed."
            )
        return value

    def create(self, validated_data):
        user = self.context.get("user")
        return Event.objects.create(organizer=user, **validated_data)


class ListRetrieveEventSerializer(EventSerializer):
    is_booked = serializers.SerializerMethodField()

    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ["is_booked"]

    def get_is_booked(self, event) -> bool:
        return event.attendees.filter(
            pk=self.context.get("user", None).pk
        ).exists()
