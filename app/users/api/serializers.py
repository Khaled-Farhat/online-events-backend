from rest_framework.serializers import ModelSerializer
from ..models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
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
