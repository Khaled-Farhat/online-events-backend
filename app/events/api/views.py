from rest_framework import (
    pagination,
    viewsets,
)
from drf_spectacular.utils import extend_schema_view, extend_schema
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
