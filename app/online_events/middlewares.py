import binascii
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from channels.db import database_sync_to_async
from knox.auth import TokenAuthentication
from knox.crypto import hash_token
from knox.settings import CONSTANTS, knox_settings
from knox.auth import compare_digest
from users.models import ChatKey


class ModelPluggableTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, token):
        msg = _("Invalid token.")
        token = token.decode("utf-8")
        for auth_token in self.model.objects.filter(
            token_key=token[: CONSTANTS.TOKEN_KEY_LENGTH]
        ):
            if self._cleanup_token(auth_token):
                continue

            try:
                digest = hash_token(token)
            except (TypeError, binascii.Error):
                raise exceptions.AuthenticationFailed(msg)
            if compare_digest(digest, auth_token.digest):
                if knox_settings.AUTO_REFRESH and auth_token.expiry:
                    self.renew_token(auth_token)
                return self.validate_user(auth_token)
        raise exceptions.AuthenticationFailed(msg)


@database_sync_to_async
def get_user(token):
    if token is None:
        return AnonymousUser()
    else:
        knox_auth = ModelPluggableTokenAuthentication()
        knox_auth.model = ChatKey
        user, _ = knox_auth.authenticate_credentials(token)
        return user


class TokenAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_params = dict(
            (x.split("=") for x in scope["query_string"].decode().split("&"))
        )
        token = query_params.get("token", "").encode("utf-8")
        scope["user"] = await get_user(token)
        return await self.app(scope, receive, send)
