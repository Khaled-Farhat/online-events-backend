from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
    retrieve_stream_key=extend_schema(
        request=None, responses={200: None, 401: None, 403: None, 404: None}
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

    @action(detail=True, methods=["get"], url_path="key")
    def retrieve_stream_key(self, request, pk):
        talk = self.get_object()
        return Response(
            status=status.HTTP_200_OK, data={"stream_key": talk.stream_key}
        )
