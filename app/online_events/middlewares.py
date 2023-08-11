from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from users.models import ChatKey
from .utils import ModelPluggableTokenAuthentication


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
