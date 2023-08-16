from django.utils import timezone
from talks.models import Talk
from factory.django import DjangoModelFactory
import factory
from factory import fuzzy
from tests.events.factories import EventFactory
from tests.users.factories import UserFactory


class TalkFactory(DjangoModelFactory):
    class Meta:
        model = Talk

    event = factory.SubFactory(EventFactory)
    speaker = factory.SubFactory(UserFactory)
    title = factory.Faker("text", max_nb_chars=60)
    start = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    end = factory.LazyAttribute(
        lambda obj: obj.start + timezone.timedelta(hours=1)
    )
    status = fuzzy.FuzzyChoice(Talk.STATUSES, getter=lambda c: c[0])
