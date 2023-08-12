from django.utils import timezone
from events.models import Event
from factory.django import DjangoModelFactory
from factory import Faker
from factory import SubFactory
from tests.users.factories import UserFactory


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    organizer = SubFactory(UserFactory)
    title = Faker("text", max_nb_chars=60)
    description = Faker("text")
    picture = Faker("file_extension", category="image")
    is_published = Faker("boolean")
    started_at = Faker("date_time", tzinfo=timezone.get_current_timezone())
