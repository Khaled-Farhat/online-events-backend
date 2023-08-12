from users.models import User
from factory.django import DjangoModelFactory
from factory import Faker
from factory import PostGenerationMethodCall


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("user_name")
    headline = Faker("text", max_nb_chars=60)
    email = Faker("email")
    bio = Faker("paragraph")
    avatar = Faker("file_extension", category="image")
    password = PostGenerationMethodCall("set_password", "password")
