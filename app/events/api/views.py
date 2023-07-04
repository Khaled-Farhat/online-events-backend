from rest_framework import pagination, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from talks.models import Talk
from talks.api.serializers import (
    TalkWithSpeakerDetailSerializer,
    TalkSerializer,
)
from ..models import Event
from .permissions import EventPermission
from .serializers import EventSerializer


@extend_schema_view(
    create=extend_schema(responses={201: EventSerializer, 401: None}),
    retrieve=extend_schema(
        responses={200: EventSerializer, 401: None, 403: None}
    ),
    update=extend_schema(
        responses={200: EventSerializer, 401: None, 403: None}
    ),
    partial_update=extend_schema(
        responses={200: EventSerializer, 401: None, 403: None}
    ),
    destroy=extend_schema(responses={204: None, 401: None, 403: None}),
)
class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [EventPermission]

    def get_queryset(self):
        if self.action == "list":
            return Event.objects.is_published()
        else:
            return Event.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="include_all",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                default=False,
                description="Include pending and rejected talks.",
            )
        ],
        responses={
            200: TalkWithSpeakerDetailSerializer(many=True),
            401: None,
            403: None,
            404: None,
        },
    )
    @action(
        detail=True, methods=["get"], url_path="talks", pagination_class=None
    )
    def list_talks(self, request, pk):
        # to do: add query params include_all (available only for organizer)
        event = self.get_object()
        queryset = Talk.objects.filter(event=event).only_approved()
        include_all = request.query_params.get("include_all", "false")
        if include_all == "true":
            queryset = Talk.objects.filter(event=event).all()
        serializer = TalkWithSpeakerDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=TalkSerializer,
        responses={
            201: TalkSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
        },
    )
    @list_talks.mapping.post
    def create_talk(self, request, pk):
        event = self.get_object()
        serializer = TalkSerializer(
            data=request.data, context={"event": event}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        description="Idempotent endpoint to book an event. The event should be"
        " in the future and the user should not be the organizer.",
        request=None,
        responses={
            204: None,
            400: None,
            401: None,
            403: None,
            404: None,
            409: None,
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="bookings",
        pagination_class=None,
    )
    def create_booking(self, request, pk):
        event = self.get_object()
        user = request.user

        if event.has_started():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if event.attendees.filter(pk=request.user.pk).exists():
            return Response(status=status.HTTP_409_CONFLICT)

        event.attendees.add(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="Idempotent endpoint to cancel event booking."
        " The event should be in the future and the user should have "
        "booked the event before",
        request=None,
        responses={
            204: None,
            401: None,
            403: None,
            404: None,
            409: None,
        },
    )
    @create_booking.mapping.delete
    def destroy_booking(self, request, pk):
        event = self.get_object()
        user = request.user

        if event.has_started():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not event.attendees.filter(pk=request.user.pk).exists():
            return Response(status=status.HTTP_409_CONFLICT)

        event.attendees.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
