from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from users.models import User
from ..models import Event


class EventOrganizerSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class EventSerializer(ModelSerializer):
    organizer = EventOrganizerSerializer(read_only=True)

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
