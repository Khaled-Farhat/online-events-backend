from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    inline_serializer,
)
from ..serializers.streaming import (
    StreamSerializer,
    PublishStreamSerializer,
    PlayStreamSerializer,
)


docs_stream_serializer = inline_serializer(
    name="stream-publish-serializer",
    fields={
        "code": serializers.IntegerField(),
        "msg": serializers.CharField(),
    },
)


@extend_schema_view(
    publish=extend_schema(
        description="Returns 200 with code 0 if the user is allowed to"
        " publish the stream."
        " The talk should be approved and ongoing, the event should"
        " be published, and the token should be a talk stream-key"
        " obtained by the talk speaker."
        " SRS service uses this endpoint to authenticate and"
        " authorize the user.",
        responses={
            200: docs_stream_serializer,
            401: docs_stream_serializer,
            403: docs_stream_serializer,
            404: docs_stream_serializer,
        },
    ),
    play=extend_schema(
        description="Returns 200 with code 0 if the user is allowed to"
        " play the stream."
        " The talk should be approved and ongoing, and the event should"
        " be published, and the token should be a play-stream-token"
        " for a user that has booked the event or for the organizer."
        " SRS service uses this endpoint to authenticate and"
        " authorize the user.",
        responses={
            200: docs_stream_serializer,
            401: docs_stream_serializer,
            403: docs_stream_serializer,
            404: docs_stream_serializer,
        },
    ),
)
class StreamAuthViewSet(GenericViewSet):
    serializer_class = StreamSerializer

    def get_serializer_class(self):
        if self.action == "publish":
            return PublishStreamSerializer
        elif self.action == "play":
            return PlayStreamSerializer
        return self.serializer_class

    @action(detail=False, methods=["post"], url_path="publish")
    def publish(self, request):
        return self.run_serializer(request)

    @action(detail=False, methods=["post"], url_path="play")
    def play(self, request):
        return self.run_serializer(request)

    def run_serializer(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(status=200, data={"code": 0, "msg": "OK"})
        except APIException as e:
            return Response(
                status=e.status_code, data={"code": 0, "msg": e.detail}
            )
