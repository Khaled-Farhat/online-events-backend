from django.utils import timezone
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    inline_serializer,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from events.models import Event
from events.api.serializers import EventSerializer
from talks.models import Talk
from talks.api.serializers import TalkWithEventDetailSerializer
from ..models import User, ChatKey
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
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                default=None,
                description="Filter talk status (pending/approved/rejected)",
            )
        ],
        responses={
            200: TalkWithEventDetailSerializer(many=True),
            401: None,
            403: None,
            404: None,
        },
    ),
    list_organized_events=extend_schema(
        responses={
            200: EventSerializer(many=True),
            401: None,
            403: None,
            404: None,
        }
    ),
    list_booked_events=extend_schema(
        responses={
            200: EventSerializer(many=True),
            401: None,
            403: None,
            404: None,
        }
    ),
    retrieve_chat_key=extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                "chat-key-serializer",
                fields={
                    "chat_key": serializers.CharField(),
                    "expiry": serializers.DateTimeField(),
                },
            ),
            401: None,
            403: None,
            404: None,
        },
        description="Retrieve a chat-key to be used in chats."
        "The key is intended to be temporal, so it will have a short expiry.",
    ),
)
class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]
    pagination_class = LimitOffsetPagination
    lookup_field = "username"

    @action(detail=True, methods=["get"], url_path="talks")
    def list_talks(self, request, username):
        user = self.get_object()

        queryset = Talk.objects.filter(speaker=user).select_related(
            "event", "event__organizer"
        )
        status_param = request.query_params.get("status", None)
        if status_param is not None:
            queryset = queryset.filter(status=status_param)

        page = self.paginate_queryset(queryset)
        serializer = TalkWithEventDetailSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="organized-events")
    def list_organized_events(self, request, username):
        # to do: support filtering event status
        user = self.get_object()
        queryset = Event.objects.filter(organizer=user).all()
        page = self.paginate_queryset(queryset)
        serializer = EventSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="booked-events")
    def list_booked_events(self, request, username):
        user = self.get_object()
        queryset = user.booked_events.all()
        page = self.paginate_queryset(queryset)
        serializer = EventSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=["get"], url_path="chat-key")
    def retrieve_chat_key(self, request, username):
        user = self.get_object()
        expiry = timezone.timedelta(minutes=10)
        instance, token = ChatKey.objects.create(user, expiry)
        return Response(
            status=status.HTTP_200_OK,
            data={"chat_key": token, "expiry": instance.expiry},
        )
