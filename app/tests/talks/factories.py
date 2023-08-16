from django.utils import timezone
from talks.models import Talk
from factory.django import DjangoModelFactory
import factory
from factory import fuzzy

# from factory import Faker, fuzzy, SelfAttribute, LazyAttribute
# from factory import SubFactory
from tests.events.factories import EventFactory
from tests.users.factories import UserFactory


class TalkFactory(DjangoModelFactory):
    class Meta:
        model = Talk

    event = factory.SubFactory(EventFactory)
    speaker = factory.SubFactory(UserFactory)
    title = factory.Faker("text", max_nb_chars=60)
    start = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    # end = factory.Faker("date_time", tzinfo=timezone.get_current_timezone())
    end = factory.Faker(
        "date_time_between_dates",
        tzinfo=timezone.get_current_timezone(),
        datetime_start=factory.SelfAttribute("..start"),
    )
    # end_date=lambda self: self.start + timezone.timedelta(minutes=30),
    # )
    # end = LazyAttribute(lambda obj: obj.start + timezone.timedelta(hours=1))
    # end = LazyAttribute(lambda x: fuzzy.FuzzyDateTime("x.start").fuzz())
    # end = fuzzy.FuzzyDateTime(start_dt=SelfAttribute("start"))
    status = fuzzy.FuzzyChoice(Talk.STATUSES, getter=lambda c: c[0])

    # @factory.post_generation
    # def schedule(self, create, extracted, **kwargs):
    #     if not create:
    #         return

    #     if self.start > self.end:
    #         self.start, self.end = self.end, self.start
