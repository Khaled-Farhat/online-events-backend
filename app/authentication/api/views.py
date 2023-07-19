from django.contrib.auth import login
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import (
    generics,
    serializers,
    permissions,
    views,
    status,
    response,
)
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    inline_serializer,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from knox.views import LoginView as KnoxLoginView, LogoutView as KnoxLogoutView
from users.api.serializers import UserSerializer
from talks.models import Talk
from .serializers import RegisterSerializer, LoginSerializer


@extend_schema_view(
    post=extend_schema(responses={200: RegisterSerializer, 400: None})
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


@extend_schema_view(
    post=extend_schema(
        request=LoginSerializer,
        responses={
            200: inline_serializer(
                "login_response_serializer",
                fields={
                    "expiry": serializers.DateTimeField(),
                    "token": serializers.CharField(),
                    "user": UserSerializer(),
                },
            ),
            400: None,
        },
    )
)
class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def get_user_serializer_class(self):
        return UserSerializer

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return super(LoginView, self).post(request, format=None)


@extend_schema_view(post=extend_schema(responses={204: None, 401: None}))
class LogoutView(KnoxLogoutView):
    pass


class RTMPAllowedRedirect(HttpResponseRedirect):
    allowed_schemes = ["rtmp"]


@extend_schema_view(
    post=extend_schema(
        description="Endpoint called by the nginx server for authorizing"
        " the streamer.",
        request=inline_serializer(
            name="push-stream-serializer",
            fields={
                "name": serializers.IntegerField(
                    help_text="Name of the stream"
                    "(secret stream key for the talk)"
                )
            },
        ),
        responses={302: None, 403: None, 404: None},
    ),
    get=extend_schema(
        description="Endpoint called by the nginx server for authorizing"
        " the consumer.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Stream name (talk id)",
            )
        ],
        responses={204: None, 403: None, 404: None},
    ),
)
class StreamView(views.APIView):
    def post(self, request, format=None):
        try:
            stream_key = request.data["name"]
            talk = get_object_or_404(Talk, stream_key=stream_key)
        except KeyError:
            raise Http404

        if not (talk.has_started()) or talk.has_finished():
            return response.Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        return RTMPAllowedRedirect(
            redirect_to=f"{settings.STREAM_APPLICATION_BASE_URL}/{talk.id}"
        )

    def get(self, request, format=None):
        try:
            talk_id = request.query_params.get("talk_id", None)
            talk = get_object_or_404(Talk, id=talk_id)
        except KeyError:
            raise Http404

        if (
            not (talk.event.attendees.filter(pk=request.user.pk).exists())
            or not (talk.has_started())
            or talk.has_finished()
        ):
            return response.Response(status=status.HTTP_403_FORBIDDEN)

        return response.Response(status=status.HTTP_204_NO_CONTENT)
