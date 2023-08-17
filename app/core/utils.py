import binascii
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from knox.auth import TokenAuthentication
from knox.crypto import hash_token
from knox.settings import CONSTANTS, knox_settings
from knox.auth import compare_digest


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
