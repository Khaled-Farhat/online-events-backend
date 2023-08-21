import pytest
from django.urls import reverse
from django.utils import timezone
from tests.events.factories import EventFactory
from tests.talks.factories import TalkFactory
from tests.users.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestTalkEndpoints:
    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("talk-detail", "put"),
            ("talk-detail", "patch"),
            ("talk-detail", "delete"),
            ("talk-retrieve-stream-key", "get"),
        ],
    )
    def test_when_not_authenticated_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, send_request
    ):
        talk = TalkFactory.create()
        url = reverse(endpoint_name, kwargs={"pk": talk.pk})
        response = send_request(url, method)
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("talk-detail", "put"),
            ("talk-detail", "patch"),
            ("talk-detail", "delete"),
            ("talk-retrieve-stream-key", "get"),
        ],
    )
    def test_when_not_speaker_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, send_request
    ):
        talk = TalkFactory.create(
            start=timezone.now() + timezone.timedelta(days=1)
        )
        url = reverse(endpoint_name, kwargs={"pk": talk.pk})
        response = send_request(url, method, user=UserFactory.create())
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("talk-detail", "put"),
            ("talk-detail", "patch"),
            ("talk-detail", "delete"),
        ],
    )
    def test_when_talk_has_started_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, send_request
    ):
        talk = TalkFactory.create(
            start=timezone.now() - timezone.timedelta(minutes=1)
        )
        url = reverse(endpoint_name, kwargs={"pk": talk.pk})
        response = send_request(url, method, user=UserFactory.create())
        assert response.status_code == 403

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_when_talk_is_rejected_then_approve_talk_should_fail(
        self, method, send_request
    ):
        talk = TalkFactory.create(
            start=timezone.now() + timezone.timedelta(days=1),
            status="rejected",
        )

        url = reverse("talk-detail", kwargs={"pk": talk.pk})
        payload = {"status": "approved"}
        response = send_request(url, method, payload, user=talk.speaker)
        assert response.status_code == 400

    def test_when_event_is_unpublished_then_retrieve_stream_key_should_fail(
        self, send_request
    ):
        talk = TalkFactory.create(
            event=EventFactory.create(is_published=False)
        )
        url = reverse("talk-retrieve-stream-key", kwargs={"pk": talk.pk})
        response = send_request(url, "get", user=talk.speaker)
        assert response.status_code == 403

    @pytest.mark.parametrize("method", ["put", "patch"])
    @pytest.mark.parametrize("new_status", ["approved", "rejected"])
    def test_when_update_talk_status(self, method, new_status, send_request):
        talk = TalkFactory.create(
            start=timezone.now() + timezone.timedelta(days=1),
            status="pending",
        )

        url = reverse("talk-detail", kwargs={"pk": talk.pk})
        payload = {"status": new_status}
        response = send_request(url, method, payload, user=talk.speaker)
        assert response.status_code == 200

    def test_retrieve_stream_key(self, send_request):
        talk = TalkFactory.create(event=EventFactory.create(is_published=True))
        url = reverse("talk-retrieve-stream-key", kwargs={"pk": talk.pk})
        response = send_request(url, "get", user=talk.speaker)
        assert response.status_code == 200
        assert type(response.data["stream_key"]) is str
