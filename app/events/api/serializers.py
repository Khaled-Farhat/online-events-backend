from rest_framework import serializers
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
        ]

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
