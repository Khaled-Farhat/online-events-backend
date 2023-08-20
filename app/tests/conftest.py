import pytest
from rest_framework.test import APIClient
from rest_framework.serializers import DateTimeField


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
    def send_request(url, method, data=None, user=None, **kwargs):
        client = api_client(user)
        request = getattr(client, method)
        response = request(url, data, format="json", **kwargs)
        return response

    return send_request


@pytest.fixture
def get_datetime_representation():
    def get_datetime_representation(datatime_field):
        return DateTimeField().to_representation(datatime_field)

    return get_datetime_representation


@pytest.fixture(autouse=True)
def disable_celery(mocker):
    delay_patch = mocker.patch("celery.app.task.Task.delay", return_value=1)
    apply_async_patch = mocker.patch(
        "celery.app.task.Task.apply_async", return_value=1
    )

    yield

    mocker.stop(delay_patch)
    mocker.stop(apply_async_patch)
