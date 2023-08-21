from django.utils import timezone
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
from .serializers import ListRetrieveEventSerializer, EventSerializer


@extend_schema_view(
    create=extend_schema(
        responses={201: EventSerializer, 400: None, 401: None}
    ),
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
    list=extend_schema(
        description="Retrieve the published events, "
        "ordered by decreasing order of started_at.",
        parameters=[
            OpenApiParameter(
                name="only_upcoming",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                default=False,
                description="Include only the upcoming events. "
                "The events will be ordered in "
                "increasing order of started_at.",
            )
        ],
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [EventPermission]

    def get_queryset(self):
        if self.action == "list":
            queryset = Event.objects.is_published()

            only_upcoming = self.request.query_params.get(
                "only_upcoming", "false"
            )
            if only_upcoming == "true":
                queryset = queryset.filter(
                    started_at__gte=timezone.now()
                ).order_by("started_at")

            return queryset
        else:
            return Event.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        if self.action in ["retrieve", "list"]:
            return ListRetrieveEventSerializer
        else:
            return EventSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.pop("request")  # To return a relative picture URI
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
        description="The event should be in the future and "
        "the user should not be the organizer.",
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
        url_name="booking-list",
        pagination_class=None,
    )
    def create_booking(self, request, pk):
        event = self.get_object()
        user = request.user

        if event.has_started():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Event has started."},
            )
        if event.attendees.filter(pk=request.user.pk).exists():
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"detail": "You have already booked this event."},
            )

        event.attendees.add(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        description="The event should be in the future and "
        "the user should have booked the event before",
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
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Event has started."},
            )
        if not event.attendees.filter(pk=request.user.pk).exists():
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"detail": "You have not booked this event before."},
            )

        event.attendees.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
