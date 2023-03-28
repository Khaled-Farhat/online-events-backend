from rest_framework.serializers import ModelSerializer
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
        read_only_fields = ["is_published"]

    def create(self, validated_data):
        user = self.context.get("user")
        return Event.objects.create(organizer=user, **validated_data)
