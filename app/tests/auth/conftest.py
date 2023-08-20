import pytest
from django.urls import reverse
from django.utils import timezone
from users.models import PlayStreamKey, VerificationKey
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


@pytest.fixture
def email_verification_key():
    def email_verification_key(user):
        _, token = VerificationKey.objects.create(user)
        return token

    return email_verification_key


@pytest.fixture
def send_register_request(send_request):
    def send_register_request(user):
        url = reverse("user-register")
        payload = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": "password",
        }
        return send_request(url, "post", payload)

    return send_register_request


@pytest.fixture
def send_verify_email_request(send_request):
    def send_verify_email_request(verificatoin_key):
        url = reverse("verification-verify-email")
        payload = {"verification_key": verificatoin_key}
        return send_request(url, "post", payload)

    return send_verify_email_request
