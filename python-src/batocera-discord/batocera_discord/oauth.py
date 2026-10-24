"""OAuth2 token handling for the user's own Discord application.

The preferred flow uses PKCE with a "Public Client" application, so no client secret is ever needed
on the console. A client secret is only sent when the user chose to provide one (non-public app).
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import secrets
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, Protocol, cast

from .errors import IO_ERRORS
from .storage import Tokens

if TYPE_CHECKING:
    from .storage import AppConfig

_logger: Final = logging.getLogger(__name__)

API: Final = 'https://discord.com/api/v10'
REDIRECT_URI: Final = 'http://127.0.0.1'
SCOPES: Final = ('rpc', 'identify', 'rpc.voice.read', 'rpc.voice.write')
USER_AGENT: Final = 'batocera-discord (https://batocera.org, 1.0)'


class OAuthError(Exception):
    def __init__(self, message: str, /, *, needs_secret: bool = False) -> None:
        super().__init__(message)
        self.needs_secret = needs_secret


class Opener(Protocol):
    def __call__(self, request: urllib.request.Request, /, *, timeout: float) -> Any: ...


def _default_opener(request: urllib.request.Request, /, *, timeout: float) -> Any:
    return urllib.request.urlopen(request, timeout=timeout)


@dataclass(frozen=True, slots=True)
class PKCE:
    verifier: str
    challenge: str

    @classmethod
    def generate(cls) -> PKCE:
        verifier = secrets.token_urlsafe(64)[:96]
        digest = hashlib.sha256(verifier.encode('ascii')).digest()
        return cls(verifier, base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii'))


class TokenClient:
    def __init__(self, opener: Opener = _default_opener, /) -> None:
        self._opener = opener

    def _post(self, endpoint: str, form: dict[str, str], /) -> dict[str, Any]:
        request = urllib.request.Request(
            f'{API}{endpoint}',
            data=urllib.parse.urlencode(form).encode(),
            headers={'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': USER_AGENT},
            method='POST',
        )
        try:
            with self._opener(request, timeout=15) as response:
                data = json.load(response)
        except urllib.error.HTTPError as exc:
            detail = _error_detail(exc)
            # Discord answers invalid_client when the app is not a Public Client and no secret was sent
            raise OAuthError(detail, needs_secret='invalid_client' in detail) from exc
        except IO_ERRORS as exc:
            raise OAuthError(f'network error: {exc}') from exc
        if not isinstance(data, dict):
            raise OAuthError('unexpected answer from Discord')
        return cast('dict[str, Any]', data)

    @staticmethod
    def _client_fields(config: AppConfig, /) -> dict[str, str]:
        fields = {'client_id': config.client_id}
        if config.client_secret:
            fields['client_secret'] = config.client_secret
        return fields

    def exchange_code(self, config: AppConfig, code: str, pkce: PKCE, /) -> Tokens:
        form = {
            **self._client_fields(config),
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'code_verifier': pkce.verifier,
        }
        return Tokens.from_response(self._post('/oauth2/token', form))

    def refresh(self, config: AppConfig, tokens: Tokens, /) -> Tokens:
        form = {**self._client_fields(config), 'grant_type': 'refresh_token', 'refresh_token': tokens.refresh_token}
        return Tokens.from_response(self._post('/oauth2/token', form))

    def revoke(self, config: AppConfig, tokens: Tokens, /) -> None:
        for token in (tokens.refresh_token, tokens.access_token):
            if token:
                try:
                    self._post('/oauth2/token/revoke', {**self._client_fields(config), 'token': token})
                except OAuthError as exc:
                    _logger.info('token revocation failed: %s', exc)


def _error_detail(exc: urllib.error.HTTPError, /) -> str:
    try:
        body = json.loads(exc.read() or b'{}')
    except IO_ERRORS:
        body = {}
    if isinstance(body, dict):
        info = cast('dict[str, object]', body)
        return f'{info.get("error", exc.code)}: {info.get("error_description", exc.reason)}'
    return f'{exc.code}: {exc.reason}'
