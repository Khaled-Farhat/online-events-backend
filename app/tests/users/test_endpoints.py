import pytest
from django.urls import reverse
from tests.users.factories import UserFactory
from django.contrib.auth import authenticate
from tests.events.factories import EventFactory
from tests.talks.factories import TalkFactory


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

    def test_update_user(self, send_request, get_user_representation):
        user = UserFactory.create()
        data = UserFactory.build()

        url = reverse("user-detail", kwargs={"username": user.username})
        payload = get_user_representation(data)
        payload["password"] = "newpassword"
        response = send_request(url, "put", payload, user)

        expected_response_data = payload
        expected_response_data.pop("password")
        expected_response_data["avatar"] = user.avatar.url

        assert response.status_code == 200
        assert response.data == expected_response_data
        assert (
            authenticate(username=data.username, password="newpassword")
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
    def test_partial_update_user(
        self, field, send_request, get_user_representation
    ):
        user = UserFactory.create()
        data = UserFactory.build()

        url = reverse("user-detail", kwargs={"username": user.username})
        data = get_user_representation(data)
        data["password"] = "newpassword"
        response = send_request(url, "patch", {field: data.get(field)}, user)

        expected_response_data = get_user_representation(
            user, include_avatar=True
        )
        if field != "password":
            expected_response_data[field] = data[field]

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

    def test_list_user_booked_events(self, send_request):
        events = EventFactory.create_batch(3)
        user = UserFactory.create()
        for event in events:
            event.attendees.add(user.pk)

        url = reverse(
            "user-list-booked-events", kwargs={"username": user.username}
        )
        response = send_request(url, "get", user=user)

        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_list_user_organized_events(self, send_request):
        user = UserFactory.create()
        EventFactory.create_batch(3, organizer=user)

        url = reverse(
            "user-list-organized-events", kwargs={"username": user.username}
        )
        response = send_request(url, "get", user=user)

        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_list_user_talks(self, send_request):
        user = UserFactory.create()
        TalkFactory.create_batch(3, speaker=user)

        url = reverse("user-list-talks", kwargs={"username": user.username})
        response = send_request(url, "get", user=user)

        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_filter_user_talks(self, send_request):
        user = UserFactory.create()
        data = [
            {"status": "pending", "count": 3},
            {"status": "approved", "count": 2},
            {"status": "rejected", "count": 1},
        ]
        for element in data:
            TalkFactory.create_batch(
                element["count"], speaker=user, status=element["status"]
            )

        base_url = reverse(
            "user-list-talks", kwargs={"username": user.username}
        )

        for element in data:
            url = f"{base_url}?status={element['status']}"
            response = send_request(url, "get", user=user)
            assert response.status_code == 200
            assert len(response.data["results"]) == element["count"]
