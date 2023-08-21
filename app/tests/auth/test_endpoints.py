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
        self, send_register_request
    ):
        UserFactory.create(username="username")
        user = UserFactory.build(username="username")
        response = send_register_request(user)
        assert response.status_code == 400

    def test_when_existing_verified_email_then_register_should_fail(
        self, send_register_request
    ):
        existing = UserFactory.create()
        user = UserFactory.build(email=existing.email)
        response = send_register_request(user)
        assert response.status_code == 400

    def test_when_existing_unverified_email_then_register_should_success(
        self, send_register_request
    ):
        existing = UserFactory.create(is_verified=False)
        user = UserFactory.build(email=existing.email)
        response = send_register_request(user)
        assert response.status_code == 201

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

    def test_register(self, mocker, send_request):
        from auth.api.views import auth

        spy = mocker.spy(auth, "send_verification_email")
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

        spy.assert_called_once()
        assert spy.call_args[0][0] == user.username
        assert spy.call_args[0][1] == user.email
        assert isinstance(spy.call_args[0][2], str) is True


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


class TestVerificationEndpoints:
    def test_when_user_is_not_verified_then_login_should_fail(
        self, send_request
    ):
        user = UserFactory.create(is_verified=False)
        url = reverse("knox-login")
        payload = {"username": user.username, "password": "password"}
        response = send_request(url, "post", payload)
        assert response.status_code == 403

    def test_email_cannot_be_used_to_verify_two_accounts(
        self, send_verify_email_request, email_verification_key
    ):
        users = [
            UserFactory.create(is_verified=False, email="name@example.com")
            for _ in range(2)
        ]
        verification_keys = [email_verification_key(user) for user in users]

        expected_status_codes = [204, 403]
        for i, key in enumerate(verification_keys):
            response = send_verify_email_request(key)
            assert response.status_code == expected_status_codes[i]

    def test_when_verified_then_verify_email_should_fail(
        self, send_verify_email_request, email_verification_key
    ):
        user = UserFactory.create()
        verificatoin_key = email_verification_key(user)
        response = send_verify_email_request(verificatoin_key)
        assert response.status_code == 400

    def test_when_verified_then_resend_verification_email_should_fail(
        self, send_request
    ):
        user = UserFactory.create()
        url = reverse("verification-resend-email")
        response = send_request(url, "post", {"username": user.username})
        assert response.status_code == 400

    def test_when_duplicate_email_then_resend_verification_email_should_fail(
        self, send_request
    ):
        existing = UserFactory.create()
        user = UserFactory.create(is_verified=False, email=existing.email)
        url = reverse("verification-resend-email")
        response = send_request(url, "post", {"username": user.username})
        assert response.status_code == 403

    def test_when_non_existing_username_then_resend_email_should_fail(
        self, send_request
    ):
        url = reverse("verification-resend-email")
        response = send_request(url, "post", {"username": "username"})
        assert response.status_code == 404

    def test_verify_email(
        self, send_verify_email_request, email_verification_key
    ):
        user = UserFactory.create(is_verified=False)
        verificatoin_key = email_verification_key(user)
        response = send_verify_email_request(verificatoin_key)
        user.refresh_from_db()
        assert response.status_code == 204
        assert user.is_verified is True

    def test_user_request_resend_verification_email(
        self, mocker, send_request
    ):
        from auth.api.views import verification

        spy = mocker.spy(verification, "send_verification_email")
        user = UserFactory.create(is_verified=False)
        url = reverse("verification-resend-email")
        response = send_request(url, "post", {"username": user.username})
        assert response.status_code == 204

        spy.assert_called_once()
        assert spy.call_args[0][0] == user.username
        assert spy.call_args[0][1] == user.email
        assert isinstance(spy.call_args[0][2], str) is True
