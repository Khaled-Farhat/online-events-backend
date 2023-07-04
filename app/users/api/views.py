from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from events.models import Event
from events.api.serializers import EventSerializer
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
    list_organized_events=extend_schema(
        responses={
            200: EventSerializer(many=True),
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                default=None,
                description="Filter talk status (pending/approved/rejected)",
            )
        ],
    )
    @action(detail=True, methods=["get"], url_path="talks")
    def list_talks(self, request, username):
        user = self.get_object()
        queryset = Talk.objects.filter(speaker=user)
        status_param = request.query_params.get("status", None)
        if status_param is not None:
            queryset = queryset.filter(status=status_param)
        serializer = TalkSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="organized-events")
    def list_organized_events(self, request, username):
        # to do: support filtering event status
        user = self.get_object()
        queryset = Event.objects.filter(organizer=user).all()
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="booked-events")
    def list_booked_events(self, request, username):
        user = self.get_object()
        queryset = user.booked_events.all()
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)
