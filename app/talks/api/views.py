from rest_framework import viewsets
from rest_framework import mixins
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
)
from ..models import Talk
from .permissions import TalkPermission
from .serializers import UpdateTalkSerializer


@extend_schema_view(
    update=extend_schema(
        responses={200: UpdateTalkSerializer, 401: None, 403: None, 404: None},
    ),
    partial_update=extend_schema(
        responses={200: UpdateTalkSerializer, 401: None, 403: None, 404: None}
    ),
    destroy=extend_schema(
        responses={204: None, 401: None, 403: None, 404: None}
    ),
)
class TalkViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Talk.objects.all()
    permission_classes = [TalkPermission]
    serializer_class = UpdateTalkSerializer
