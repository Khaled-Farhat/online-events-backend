import pytest
from django.utils import timezone
from django.urls import reverse
from tests.users.factories import UserFactory
from tests.events.factories import EventFactory
from tests.talks.factories import TalkFactory
from tests.talks.conftest import get_talk_representation
from events.models import Event

pytestmark = pytest.mark.django_db
__all__ = ["get_talk_representation"]


class TestEventEndpoints:
    def test_when_not_authenticated_then_create_event_should_fail(
        self, send_request
    ):
        url = reverse("event-list")
        response = send_request(url, "post")
        assert response.status_code == 401

    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("event-detail", "put"),
            ("event-detail", "patch"),
            ("event-detail", "delete"),
            ("event-booking-list", "post"),
            ("event-booking-list", "delete"),
            ("event-list-talks", "post"),
        ],
    )
    def test_when_not_authenticated_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, published_event, send_request
    ):
        url = reverse(endpoint_name, kwargs={"pk": published_event.pk})
        response = send_request(url, method)
        assert response.status_code == 401

    def test_when_started_at_in_past_then_create_event_should_fail(
        self, send_request, get_event_representation
    ):
        event = EventFactory.build(
            organizer=UserFactory.create(),
            picture=None,
            started_at=timezone.now() - timezone.timedelta(minutes=1),
        )

        url = reverse("event-list")
        payload = get_event_representation(event)
        response = send_request(url, "post", payload, user=event.organizer)

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "endpoint_name",
        ["event-detail", "event-list-talks"],
    )
    def test_when_unpublished_then_retrieve_event_retrieve_talks_should_fail(
        self, endpoint_name, unpublished_event, send_request
    ):
        url = reverse(endpoint_name, kwargs={"pk": unpublished_event.pk})

        response = send_request(url, "get")
        assert response.status_code == 401

        user = UserFactory.create()
        response = send_request(url, "get", user=user)
        assert response.status_code == 403

    @pytest.mark.parametrize(
        "endpoint_name, method",
        [
            ("event-detail", "put"),
            ("event-detail", "patch"),
            ("event-detail", "delete"),
            ("event-list-talks", "post"),
        ],
    )
    def test_when_not_organizer_then_appropriate_endpoints_should_fail(
        self, endpoint_name, method, published_event, send_request
    ):
        user = UserFactory.create()
        url = reverse(endpoint_name, kwargs={"pk": published_event.pk})
        response = send_request(url, method, user=user)
        assert response.status_code == 403

    def test_when_not_organizer_then_filter_event_talks_should_fail(
        self, published_event, send_request
    ):
        url = reverse("event-list-talks", kwargs={"pk": published_event.pk})
        url = f"{url}?include_all=true"

        response = send_request(url, "get")
        assert response.status_code == 401

        user = UserFactory.create()
        response = send_request(url, "get", user=user)
        assert response.status_code == 403

    def test_when_organizer_then_create_booking_should_fail(
        self, published_event, send_request
    ):
        url = reverse("event-booking-list", kwargs={"pk": published_event.pk})
        response = send_request(url, "post", user=published_event.organizer)
        assert response.status_code == 403

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_when_not_published_then_publish_should_fail(
        self, method, unpublished_event, send_request
    ):
        url = reverse("event-detail", kwargs={"pk": unpublished_event.pk})
        payload = {"is_published", True}
        response = send_request(
            url, method, payload, unpublished_event.organizer
        )
        assert response.status_code == 400

    @pytest.mark.parametrize("method", ["put", "patch"])
    def test_organizer_cannot_update_started_at_to_time_in_past(
        self, method, send_request, get_event_representation
    ):
        event = EventFactory.create()
        data = get_event_representation(
            EventFactory.build(
                started_at=timezone.now() - timezone.timedelta(days=1)
            )
        )

        url = reverse("event-detail", kwargs={"pk": event.pk})
        payload = {"started_at": data["started_at"]}
        response = send_request(url, method, payload, event.organizer)
        assert response.status_code == 400

    def test_when_unpublished_then_create_booking_should_fail(
        self, send_request
    ):
        event = EventFactory.create(
            is_published=False,
            started_at=timezone.now() + timezone.timedelta(days=1),
        )
        user = UserFactory.create()

        url = reverse("event-booking-list", kwargs={"pk": event.pk})
        response = send_request(url, "post", user=user)
        assert response.status_code == 403

    @pytest.mark.parametrize("method", ["post", "delete"])
    def test_when_event_has_started_then_booking_endpoints_should_fail(
        self, method, send_request
    ):
        event = EventFactory.create(
            is_published=True,
            started_at=timezone.now() - timezone.timedelta(days=1),
        )
        user = UserFactory.create()

        url = reverse("event-booking-list", kwargs={"pk": event.pk})
        response = send_request(url, method, user=user)
        assert response.status_code == 400

    def test_when_speaker_is_not_verified_then_create_event_talk_should_fail(
        self, published_event, send_request, get_talk_representation
    ):
        talk = TalkFactory.build(
            speaker=UserFactory.create(is_verified=False),
            event=published_event,
            start=timezone.now() + timezone.timedelta(hours=1),
            end=timezone.now() + timezone.timedelta(hours=2),
            status="pending",
        )

        payload = get_talk_representation(talk, include_speaker=True)
        url = reverse("event-list-talks", kwargs={"pk": published_event.pk})
        response = send_request(
            url, "post", payload, user=published_event.organizer
        )
        assert response.status_code == 400

    def test_when_not_organizer_then_create_event_talk_should_fail(
        self, published_event, send_request
    ):
        url = reverse("event-list-talks", kwargs={"pk": published_event.pk})
        response = send_request(url, "post", user=UserFactory.create())
        assert response.status_code == 403

    def test_when_not_organizer_filter_event_talks_should_fail(
        self, unpublished_event, send_request
    ):
        url = reverse("event-list-talks", kwargs={"pk": unpublished_event.pk})
        url = f"{url}?include_all=true"
        response = send_request(url, "get", user=UserFactory.create())
        assert response.status_code == 403

    def test_list_events(self, send_request):
        EventFactory.create_batch(3, is_published=True)
        url = reverse("event-list")
        response = send_request(url, "get")
        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_filter_upcoming_events(
        self, send_request, get_event_representation
    ):
        datetimes = [
            timezone.now() - timezone.timedelta(days=1),
            timezone.now(),
            timezone.now() + timezone.timedelta(days=1),
        ]
        events = []
        for started_at in datetimes:
            events.append(
                EventFactory.create(is_published=True, started_at=started_at)
            )
        EventFactory.create_batch(3, is_published=False)

        url = reverse("event-list")
        url = f"{url}?only_upcoming=true"
        response = send_request(url, "get")

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0] == get_event_representation(
            events[2],
            include_id=True,
            include_organizer=True,
            include_picture=True,
        )

    def test_create_event(self, send_request, get_event_representation):
        event = EventFactory.build(
            organizer=UserFactory.create(),
            picture=None,
            started_at=timezone.now() + timezone.timedelta(days=1),
        )

        url = reverse("event-list")
        payload = get_event_representation(event)
        response = send_request(url, "post", payload, user=event.organizer)

        assert response.status_code == 201
        response.data.pop("id")
        expected_reponse_data = payload
        expected_reponse_data["organizer"] = event.organizer.username
        expected_reponse_data["picture"] = None
        assert response.data == expected_reponse_data

    def test_when_unpublished_then_organizer_can_retrieve_event(
        self, unpublished_event, send_request, get_event_representation
    ):
        url = reverse("event-detail", kwargs={"pk": unpublished_event.pk})
        response = send_request(url, "get", user=unpublished_event.organizer)
        assert response.status_code == 200
        assert response.data == get_event_representation(
            unpublished_event,
            include_id=True,
            include_organizer=True,
            include_picture=True,
        )

    def test_retrieve_published_event(
        self, published_event, send_request, get_event_representation
    ):
        url = reverse("event-detail", kwargs={"pk": published_event.pk})
        response = send_request(url, "get")
        assert response.status_code == 200
        assert response.data == get_event_representation(
            published_event,
            include_id=True,
            include_organizer=True,
            include_picture=True,
        )

    def test_update_event(self, send_request, get_event_representation):
        event = EventFactory.create(is_published=False)

        url = reverse("event-detail", kwargs={"pk": event.pk})
        payload = get_event_representation(
            EventFactory.build(
                is_published=True,
                started_at=timezone.now() + timezone.timedelta(days=1),
            )
        )
        response = send_request(url, "put", payload, user=event.organizer)

        assert response.status_code == 200
        excepted_response_data = payload
        excepted_response_data["id"] = event.id
        excepted_response_data["organizer"] = event.organizer.username
        excepted_response_data["picture"] = event.picture.url
        assert response.data == excepted_response_data

    @pytest.mark.parametrize(
        "field",
        [
            "title",
            "description",
            "is_published",
            "started_at",
        ],
    )
    def test_partial_update_event(
        self, field, send_request, get_event_representation
    ):
        event = EventFactory.create(is_published=False)
        data = get_event_representation(event)

        url = reverse("event-detail", kwargs={"pk": event.id})
        payload = {"field": data[field]}
        response = send_request(url, "patch", payload, user=event.organizer)

        expected_response = get_event_representation(
            event,
            include_id=True,
            include_organizer=True,
            include_picture=True,
        )
        expected_response[field] = data[field]
        assert response.status_code == 200
        assert response.data == expected_response

    def test_destory_event(self, send_request):
        event = EventFactory.create()
        url = reverse("event-detail", kwargs={"pk": event.pk})

        response = send_request(url, "delete", user=event.organizer)
        assert response.status_code == 204

        response = send_request(url, "get", user=event.organizer)
        assert response.status_code == 404

    def test_event_create_and_destroy_booking(self, send_request):
        user = UserFactory.create()
        event = EventFactory.create(
            is_published=True,
            started_at=timezone.now() + timezone.timedelta(days=1),
        )
        url = reverse("event-booking-list", kwargs={"pk": event.pk})

        # test create event booking
        response = send_request(url, "post", user=user)
        assert response.status_code == 204
        assert event.attendees.filter(pk=user.pk).exists()

        # test cannot book event twice
        response = send_request(url, "post", user=user)
        assert response.status_code == 409

        # test destroy event booking
        response = send_request(url, "delete", user=user)
        assert response.status_code == 204
        assert not event.attendees.filter(pk=user.pk).exists()

        # test cannot destroy event booking twice
        response = send_request(url, "delete", user=user)
        assert response.status_code == 409

    def test_list_published_event_talks(self, published_event, send_request):
        TalkFactory.create_batch(3, event=published_event, status="approved")
        TalkFactory.create_batch(2, event=published_event, status="rejected")
        TalkFactory.create_batch(1, event=published_event, status="pending")

        url = reverse("event-list-talks", kwargs={"pk": published_event.pk})
        response = send_request(url, "get")

        assert response.status_code == 200
        assert len(response.data) == 3

    def test_filter_event_talks(self, published_event, send_request):
        TalkFactory.create_batch(3, event=published_event, status="approved")
        TalkFactory.create_batch(2, event=published_event, status="rejected")
        TalkFactory.create_batch(1, event=published_event, status="pending")

        base_url = reverse(
            "event-list-talks", kwargs={"pk": published_event.pk}
        )

        url = f"{base_url}?include_all=true"
        response = send_request(url, "get", user=published_event.organizer)
        assert response.status_code == 200
        assert len(response.data) == 6

        url = f"{base_url}?include_all=false"
        response = send_request(url, "get", user=published_event.organizer)
        assert response.status_code == 200
        assert len(response.data) == 3

    def test_create_event_talk(
        self, unpublished_event, send_request, get_talk_representation
    ):
        talk = TalkFactory.build(
            speaker=UserFactory.create(),
            event=unpublished_event,
            start=timezone.now() + timezone.timedelta(hours=1),
            end=timezone.now() + timezone.timedelta(hours=2),
            status="pending",
        )

        url = reverse("event-list-talks", kwargs={"pk": unpublished_event.pk})
        payload = get_talk_representation(talk, include_speaker=True)
        response = send_request(
            url, "post", payload, user=unpublished_event.organizer
        )

        assert response.status_code == 201
        expected_response_data = get_talk_representation(
            talk, include_event=True, include_status=True
        )
        response.data.pop("id")
        assert response.data == expected_response_data
        assert len(Event.objects.all()) == 1
