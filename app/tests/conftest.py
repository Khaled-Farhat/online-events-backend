import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    def api_client(user):
        client = APIClient()
        if user is not None:
            client.force_authenticate(user=user)
        return client

    return api_client


@pytest.fixture
def send_request(api_client):
    def send_request(url, method, data=None, user=None):
        client = api_client(user)
        request = getattr(client, method)
        response = request(url, data, format="json")
        return response

    return send_request
