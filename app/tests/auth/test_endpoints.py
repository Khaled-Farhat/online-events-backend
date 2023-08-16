import pytest
from django.urls import reverse
from tests.users.conftest import get_user_representation
from django.contrib.auth import authenticate
from tests.users.factories import UserFactory


pytestmark = pytest.mark.django_db
__all__ = ["get_user_representation"]


class TestAuthEndpoints:
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
