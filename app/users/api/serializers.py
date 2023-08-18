from rest_framework import serializers
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "headline",
            "bio",
            "password",
        ]
        extra_kwargs = {
            "email": {
                "required": True,
            },
            "first_name": {
                "required": True,
            },
            "last_name": {
                "required": True,
            },
            "password": {
                "required": False,
                "write_only": True,
            },
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
            validated_data.pop("password")
        return super().update(instance, validated_data)


class UpdateUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ["username", "email"]
