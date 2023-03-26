from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if user := authenticate(
            username=data["username"],
            password=data["password"],
        ):
            data["user"] = user
            return data
        else:
            message = "Unable to log in with provided credentials."
            raise serializers.ValidationError(message, code="authorization")
