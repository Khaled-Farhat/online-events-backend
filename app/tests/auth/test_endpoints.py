import pytest
from django.utils import timezone
from django.urls import reverse
from tests.users.conftest import get_user_representation
from django.contrib.auth import authenticate
from tests.users.factories import UserFactory


pytestmark = pytest.mark.django_db
__all__ = ["get_user_representation"]


class TestAuthEndpoints:
    def test_when_username_is_not_unique_then_register_should_fail(
        self, send_request
    ):
        UserFactory.create(username="username")
        user = UserFactory.build(username="username")

        url = reverse("user-register")
        payload = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": "password",
        }
        response = send_request(url, "post", payload)

        assert response.status_code == 400

    def test_login_logout(self, send_request, get_user_representation):
        user = UserFactory.create()

        url = reverse("knox-login")
        payload = {"username": user.username, "password": "password"}
        response = send_request(url, "post", payload)
        assert response.status_code == 200
        assert response.data["user"] == get_user_representation(
            user, include_avatar=True
        )
        token = response.data["token"]

        url = reverse("knox-logout")
        response = send_request(
            url, "post", HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert response.status_code == 204

    def test_register(self, send_request):
        user = UserFactory.build()

        url = reverse("user-register")
        payload = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "password": "password",
        }
        response = send_request(url, "post", payload)

        assert response.status_code == 201
        expected_response_data = payload.copy()
        expected_response_data.pop("password")
        assert response.data == expected_response_data

        authenticated_user = authenticate(
            username=user.username, password=payload["password"]
        )
        assert authenticated_user.username == user.username


class TestStreamAuthEndpoints:
    @pytest.mark.parametrize(
        "talk_kwargs, status_code",
        [
            ({"is_published": False}, 404),
            ({"status": "pending"}, 404),
            ({"status": "rejected"}, 404),
            (
                {
                    "start": timezone.now() + timezone.timedelta(hours=1),
                    "minutes_duration": 30,
                },
                403,
            ),
            (
                {
                    "start": timezone.now() - timezone.timedelta(hours=1),
                    "minutes_duration": 30,
                },
                403,
            ),
        ],
    )
    def test_when_a_condition_is_not_satisfied_then_publish_should_fail(
        self,
        talk_kwargs,
        status_code,
        send_request,
        talk_for_streaming,
        payload_for_streaming,
    ):
        talk = talk_for_streaming(**talk_kwargs)
        url = reverse("stream-publish")
        payload = payload_for_streaming(talk.id, talk.stream_key)
        response = send_request(url, "post", payload)
        assert response.status_code == status_code

    @pytest.mark.parametrize(
        "endpoint_name", ["stream-publish", "stream-play"]
    )
    def test_when_not_authenticated_then_publish_play_should_fail(
        self,
        endpoint_name,
        send_request,
        talk_for_streaming,
        payload_for_streaming,
    ):
        talk = talk_for_streaming()
        url = reverse(endpoint_name)
        payload = payload_for_streaming(talk.id)
        payload["param"] = ""
        response = send_request(url, "post", payload)
        assert response.status_code == 401

    def test_when_not_authorized_then_publish_should_fail(
        self, send_request, talk_for_streaming, payload_for_streaming
    ):
        talk = talk_for_streaming()
        other_talk = talk_for_streaming()
        url = reverse("stream-publish")
        payload = payload_for_streaming(talk.id, other_talk.stream_key)
        response = send_request(url, "post", payload)
        assert response.status_code == 403

    def test_when_not_registered_in_event_then_play_should_fail(
        self,
        send_request,
        talk_for_streaming,
        play_stream_key,
        payload_for_streaming,
    ):
        play_stream_key = play_stream_key()
        talk = talk_for_streaming()
        url = reverse("stream-play")
        payload = payload_for_streaming(talk.id, play_stream_key)
        response = send_request(url, "post", payload)
        assert response.status_code == 403

    def test_publish(
        self, send_request, talk_for_streaming, payload_for_streaming
    ):
        talk = talk_for_streaming()
        url = reverse("stream-publish")
        payload = payload_for_streaming(talk.id, talk.stream_key)
        response = send_request(url, "post", payload)
        assert response.status_code == 200
        assert response.data["code"] == 0

    def test_play(
        self,
        send_request,
        talk_for_streaming,
        play_stream_key,
        payload_for_streaming,
    ):
        talk = talk_for_streaming()
        user = UserFactory.create()
        talk.event.attendees.add(user.pk)
        play_stream_key = play_stream_key(for_user=user)
        url = reverse("stream-play")
        payload = payload_for_streaming(talk.id, play_stream_key)
        response = send_request(url, "post", payload)
        assert response.status_code == 200
        assert response.data["code"] == 0
