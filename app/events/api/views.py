from rest_framework import (
    pagination,
    viewsets,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Event
from .permissions import EventPermission
from .serializers import EventSerializer


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

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        event = self.get_object()
        event.is_published = True
        event.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
