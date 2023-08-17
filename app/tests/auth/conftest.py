import pytest
from django.utils import timezone
from users.models import PlayStreamKey
from tests.events.factories import EventFactory
from tests.talks.factories import TalkFactory
from tests.users.factories import UserFactory


@pytest.fixture
def talk_for_streaming():
    def talk_for_streaming(
        is_published=True,
        status="approved",
        start=timezone.now() - timezone.timedelta(minutes=30),
        minutes_duration=60,
    ):
        return TalkFactory.create(
            event=EventFactory.create(
                is_published=is_published,
                started_at=timezone.now() - timezone.timedelta(days=1),
            ),
            status=status,
            start=start,
            end=start + timezone.timedelta(minutes=minutes_duration),
        )

    return talk_for_streaming


@pytest.fixture
def payload_for_streaming():
    def payload_for_streaming(talk_id, talk_stream_key=""):
        return {
            "stream_url": f"/live/{talk_id}",
            "param": f"?token={talk_stream_key}",
        }

    return payload_for_streaming


@pytest.fixture
def play_stream_key():
    def play_stream_key(for_user=None):
        user = UserFactory.create() if for_user is None else for_user
        _, token = PlayStreamKey.objects.create(user)
        return token

    return play_stream_key
