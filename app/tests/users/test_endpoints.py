import pytest
from django.urls import reverse
from tests.users.factories import UserFactory
from django.contrib.auth import authenticate


pytestmark = pytest.mark.django_db


class TestUserEndpoints:
    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("user-detail", "put"),
            ("user-detail", "patch"),
            ("user-list-booked-events", "get"),
            ("user-retrieve-chat-key", "get"),
            ("user-list-organized-events", "get"),
            ("user-retrieve-play-stream-key", "get"),
            ("user-list-talks", "get"),
        ],
    )
    def test_when_not_authenticated_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, send_request
    ):
        owner = UserFactory.create()
        url = reverse(endpoint_name, kwargs={"username": owner.username})
        response = send_request(url, method)
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("user-detail", "put"),
            ("user-detail", "patch"),
            ("user-list-booked-events", "get"),
            ("user-retrieve-chat-key", "get"),
            ("user-list-organized-events", "get"),
            ("user-retrieve-play-stream-key", "get"),
            ("user-list-talks", "get"),
        ],
    )
    def test_when_not_owner_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, send_request
    ):
        owner = UserFactory.create()
        url = reverse(endpoint_name, kwargs={"username": owner.username})
        response = send_request(url, method, user=UserFactory.create())
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("user-detail", "get"),
            ("user-detail", "put"),
            ("user-detail", "patch"),
            ("user-list-booked-events", "get"),
            ("user-retrieve-chat-key", "get"),
            ("user-list-organized-events", "get"),
            ("user-retrieve-play-stream-key", "get"),
            ("user-list-talks", "get"),
        ],
    )
    def test_when_not_found_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, send_request
    ):
        url = reverse(endpoint_name, kwargs={"username": "username"})
        response = send_request(url, method, user=UserFactory.create())
        assert response.status_code == 404

    def test_retrieve_user(self, send_request):
        user = UserFactory.create()
        url = reverse("user-detail", kwargs={"username": user.username})
        response = send_request(url, "get", user=UserFactory.create())
        assert response.status_code == 200
        expected_response_data = dict(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "avatar": user.avatar.url,
                "headline": user.headline,
                "bio": user.bio,
            }
        )
        assert response.data == expected_response_data

    def test_update_user(self, send_request):
        user = UserFactory.create()
        url = reverse("user-detail", kwargs={"username": user.username})
        payload = dict(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "headline": user.headline,
                "bio": user.bio,
                "password": "newpassword",
            }
        )
        response = send_request(url, "put", payload, user)
        expected_response_data = payload
        expected_response_data.pop("password")
        expected_response_data["avatar"] = user.avatar.url
        assert response.status_code == 200
        assert response.data == expected_response_data
        assert (
            authenticate(username=user.username, password="newpassword")
            == user
        )

    @pytest.mark.parametrize(
        "field",
        [
            "username",
            "email",
            "first_name",
            "last_name",
            "headline",
            "bio",
            "password",
        ],
    )
    def test_partial_update_user(self, field, send_request):
        user = UserFactory.create()
        url = reverse("user-detail", kwargs={"username": user.username})
        data = dict(
            {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "headline": user.headline,
                "bio": user.bio,
                "password": "newpassword",
            }
        )
        response = send_request(url, "patch", {field: data.get(field)}, user)
        expected_response_data = data
        expected_response_data.pop("password")
        expected_response_data["avatar"] = user.avatar.url
        assert response.status_code == 200
        assert response.data == expected_response_data
        if field == "password":
            assert (
                authenticate(username=user.username, password="newpassword")
                == user
            )

    @pytest.mark.parametrize(
        "endpoint_name, key_name",
        [
            ("user-retrieve-chat-key", "chat_key"),
            ("user-retrieve-play-stream-key", "play_stream_key"),
        ],
    )
    def test_retrieve_keys(self, endpoint_name, key_name, send_request):
        user = UserFactory.create()
        url = reverse(endpoint_name, kwargs={"username": user.username})
        response = send_request(url, "get", user=user)
        assert response.status_code == 200
        assert type(response.data[key_name]) is str
