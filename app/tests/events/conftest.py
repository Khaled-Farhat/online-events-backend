import pytest
from rest_framework.serializers import DateTimeField
from .factories import EventFactory


@pytest.fixture
def published_event():
    return EventFactory.create(is_published=True)


@pytest.fixture
def unpublished_event():
    return EventFactory.create(is_published=False)


@pytest.fixture
def get_datetime_representation():
    def get_datetime_representation(datatime_field):
        return DateTimeField().to_representation(datatime_field)

    return get_datetime_representation


@pytest.fixture
def get_event_representation(get_datetime_representation):
    def get_event_representation(
        event, include_id=False, include_organizer=False, include_picture=False
    ):
        representation = {
            "title": event.title,
            "description": event.description,
            "is_published": event.is_published,
            "started_at": get_datetime_representation(event.started_at),
        }
        if include_id:
            representation["id"] = event.id
        if include_organizer:
            representation["organizer"] = event.organizer.username
        if include_picture:
            representation["picture"] = event.picture.url
        return representation

    return get_event_representation
