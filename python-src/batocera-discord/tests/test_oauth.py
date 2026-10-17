from __future__ import annotations

import base64
import email.message
import hashlib
import io
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import pytest

from batocera_discord.oauth import PKCE, REDIRECT_URI, OAuthError, TokenClient
from batocera_discord.storage import AppConfig, Tokens


class FakeOpener:
    def __init__(self, answer: dict[str, Any] | None = None, error: tuple[int, dict[str, Any]] | None = None) -> None:
        self.answer = answer or {'access_token': 'access', 'refresh_token': 'refresh', 'expires_in': 3600}
        self.error = error
        self.requests: list[tuple[str, dict[str, str]]] = []

    def __call__(self, request: urllib.request.Request, /, *, timeout: float) -> io.BytesIO:
        body = request.data
        assert isinstance(body, bytes)
        self.requests.append((request.full_url, dict(urllib.parse.parse_qsl(body.decode()))))
        if self.error is not None:
            status, payload = self.error
            raise urllib.error.HTTPError(
                request.full_url, status, 'error', email.message.Message(), io.BytesIO(json.dumps(payload).encode())
            )
        return io.BytesIO(json.dumps(self.answer).encode())


def test_pkce_challenge_is_s256() -> None:
    pkce = PKCE.generate()
    expected = base64.urlsafe_b64encode(hashlib.sha256(pkce.verifier.encode()).digest()).rstrip(b'=').decode()

    assert pkce.challenge == expected
    assert 43 <= len(pkce.verifier) <= 128


def test_public_client_exchange_sends_no_secret() -> None:
    opener = FakeOpener()
    pkce = PKCE.generate()

    tokens = TokenClient(opener).exchange_code(AppConfig('123456789012345678'), 'the-code', pkce)

    url, form = opener.requests[0]
    assert url.endswith('/oauth2/token')
    assert form['code_verifier'] == pkce.verifier
    assert form['redirect_uri'] == REDIRECT_URI
    assert 'client_secret' not in form
    assert tokens.access_token == 'access'


def test_secret_is_sent_when_configured() -> None:
    opener = FakeOpener()

    TokenClient(opener).refresh(AppConfig('123456789012345678', 'shh'), Tokens('a', 'old-refresh', 0))

    _url, form = opener.requests[0]
    assert form['client_secret'] == 'shh'
    assert form['grant_type'] == 'refresh_token'
    assert form['refresh_token'] == 'old-refresh'


def test_invalid_client_means_a_secret_is_needed() -> None:
    opener = FakeOpener(error=(401, {'error': 'invalid_client', 'error_description': 'Unknown client'}))

    with pytest.raises(OAuthError) as raised:
        TokenClient(opener).exchange_code(AppConfig('123456789012345678'), 'code', PKCE.generate())

    assert raised.value.needs_secret


def test_revoke_ignores_errors() -> None:
    opener = FakeOpener(error=(400, {'error': 'invalid_request'}))

    TokenClient(opener).revoke(AppConfig('123456789012345678'), Tokens('a', 'r', 0))

    assert [form['token'] for _url, form in opener.requests] == ['r', 'a']
