from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from talks.models import Talk
from talks.api.serializers import TalkSerializer
from ..models import User
from .serializers import UserSerializer
from .permissions import UserPermission


@extend_schema_view(
    retrieve=extend_schema(responses={200: UserSerializer, 404: None}),
    update=extend_schema(
        responses={200: UserSerializer, 401: None, 403: None, 404: None}
    ),
    partial_update=extend_schema(
        responses={200: UserSerializer, 401: None, 403: None, 404: None}
    ),
    list_talks=extend_schema(
        responses={
            200: TalkSerializer(many=True),
            401: None,
            403: None,
            404: None,
        }
    ),
)
class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
    lookup_field = "username"

    @action(detail=True, methods=["get"], url_path="talks")
    def list_talks(self, request, username):
        # to do: support filtering talk status
        user = self.get_object()
        queryset = Talk.objects.filter(speaker=user).all()
        serializer = TalkSerializer(queryset, many=True)
        return Response(serializer.data)
