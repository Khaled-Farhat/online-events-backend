import pytest


@pytest.fixture
def get_user_representation():
    def get_user_representation(user, include_avatar=False):
        representation = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "headline": user.headline,
            "bio": user.bio,
        }
        if include_avatar:
            representation["avatar"] = user.avatar.url
        return representation

    return get_user_representation
