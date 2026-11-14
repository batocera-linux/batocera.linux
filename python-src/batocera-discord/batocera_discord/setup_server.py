"""On-demand web page used from a phone (QR code on the TV) to enter the Discord application settings.

* Runs only while setup is shown, and stops after ``IDLE_TIMEOUT`` without requests.
* Every URL carries a random token from the QR code; anything else gets a 404.
* POST bodies must be JSON (no cross-site form posts), are size limited and validated.
* The client secret is write-only: it is never sent back to the browser.
"""

from __future__ import annotations

import json
import logging
import secrets
import socket
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources
from typing import TYPE_CHECKING, Any, ClassVar, Final, cast

from .storage import AppConfig, Favorite, Tokens, is_snowflake

if TYPE_CHECKING:
    from collections.abc import Callable

    from .state import State

_logger: Final = logging.getLogger(__name__)

DEFAULT_PORT: Final = 8099
IDLE_TIMEOUT: Final = 15 * 60
MAX_BODY: Final = 16 * 1024
MAX_FAVORITES: Final = 30
_SECURITY_HEADERS: Final = {
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
    'X-Frame-Options': 'DENY',
    'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:",
}


def lan_address() -> str:
    """Address of the interface used to reach the network (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(('192.0.2.1', 9))  # TEST-NET-1, never routed
            return str(probe.getsockname()[0])
        except OSError:
            return '127.0.0.1'


def parse_config(body: dict[str, Any], current: AppConfig, /) -> AppConfig | None:
    """Validated settings from the page, or None if the client id is invalid."""
    client_id = body.get('client_id')
    if not is_snowflake(client_id):
        return None
    secret = body.get('client_secret')
    if body.get('clear_secret'):
        client_secret = ''
    elif isinstance(secret, str) and secret.strip():
        client_secret = secret.strip()[:128]
    else:
        client_secret = current.client_secret if current.client_id == client_id else ''
    favorites: list[Favorite] = []
    raw_favorites = body.get('favorites')
    for item in cast('list[object]', raw_favorites)[:MAX_FAVORITES] if isinstance(raw_favorites, list) else []:
        if isinstance(item, dict):
            fav = cast('dict[str, object]', item)
            if is_snowflake(channel_id := fav.get('channel_id')):
                favorites.append(Favorite(str(fav.get('name') or 'Discord').strip()[:40] or 'Discord', str(channel_id)))
    return AppConfig(client_id=str(client_id), client_secret=client_secret, favorites=favorites)


class SetupServer:
    def __init__(
        self, state: State, on_saved: Callable[[], None], on_logout: Callable[[], None], /, *, port: int = DEFAULT_PORT
    ) -> None:
        self.state = state
        self.on_saved = on_saved
        self.on_logout = on_logout
        self.port = port
        self.token = ''
        self.last_activity = 0.0
        self._httpd: ThreadingHTTPServer | None = None
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        return self._httpd is not None

    def url(self) -> str | None:
        """Start the server if needed and return the URL to put in the QR code."""
        with self._lock:
            if self._httpd is None and not self._start():
                return None
            self.last_activity = time.monotonic()
            assert self._httpd is not None
            return f'http://{lan_address()}:{self._httpd.server_address[1]}/s/{self.token}'

    def _start(self) -> bool:
        self.token = secrets.token_urlsafe(18)
        handler = type('Handler', (_Handler,), {'server_ref': self})
        for port in (self.port, 0):
            try:
                self._httpd = ThreadingHTTPServer(('0.0.0.0', port), handler)
                break
            except OSError as exc:
                _logger.warning('setup server cannot listen on %s: %s', port, exc)
        if self._httpd is None:
            return False
        self._httpd.daemon_threads = True
        threading.Thread(target=self._httpd.serve_forever, name='discord-setup', daemon=True).start()
        threading.Thread(target=self._watchdog, name='discord-setup-watchdog', daemon=True).start()
        _logger.info('setup page listening on port %s', self._httpd.server_address[1])
        return True

    def stop(self) -> None:
        with self._lock:
            httpd, self._httpd = self._httpd, None
            self.token = ''
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()
            _logger.info('setup page stopped')

    def _watchdog(self) -> None:
        while self._httpd is not None:
            time.sleep(5)
            if time.monotonic() - self.last_activity > IDLE_TIMEOUT:
                self.stop()

    # -- API used by the handler --
    def status(self) -> dict[str, Any]:
        config = AppConfig.load()
        return {
            **self.state.snapshot(),
            'client_id': config.client_id,
            'has_secret': bool(config.client_secret),
            'favorites': [{'name': f.name, 'channel_id': f.channel_id} for f in config.favorites],
        }

    def save(self, body: dict[str, Any], /) -> bool:
        current = AppConfig.load()
        config = parse_config(body, current)
        if config is None:
            return False
        if config.client_id != current.client_id or config.client_secret != current.client_secret:
            Tokens.clear()  # tokens belong to the previous application
        config.save()
        self.on_saved()
        return True


class _Handler(BaseHTTPRequestHandler):
    server_ref: ClassVar[SetupServer]
    server_version = 'batocera-discord'
    sys_version = ''

    def log_message(self, format: str, *args: object) -> None:
        _logger.debug('setup page: %s', format % args)

    def _route(self) -> str | None:
        """Path after ``/s/<token>``, or None when the token is wrong."""
        owner = self.server_ref
        prefix = f'/s/{owner.token}'
        path = self.path.split('?', 1)[0]
        if not owner.token or not (path == prefix or path.startswith(prefix + '/')):
            return None
        owner.last_activity = time.monotonic()
        return path[len(prefix) :] or '/'

    def _send(self, status: HTTPStatus, body: bytes, content_type: str, /) -> None:
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        for name, value in _SECURITY_HEADERS.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data: object, status: HTTPStatus = HTTPStatus.OK, /) -> None:
        self._send(status, json.dumps(data).encode(), 'application/json')

    def _not_found(self) -> None:
        self._send(HTTPStatus.NOT_FOUND, b'Not found', 'text/plain')

    def do_GET(self) -> None:
        route = self._route()
        if route == '/':
            page = resources.files(__package__ or 'batocera_discord').joinpath('web', 'setup.html').read_bytes()
            self._send(HTTPStatus.OK, page, 'text/html; charset=utf-8')
        elif route == '/api/status':
            self._json(self.server_ref.status())
        else:
            self._not_found()

    def do_POST(self) -> None:
        route = self._route()
        if route not in ('/api/config', '/api/logout'):
            self._not_found()
            return
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            self._json({'ok': False, 'error': 'json expected'}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
            return
        length = int(self.headers.get('Content-Length') or 0)
        if length > MAX_BODY:
            self._json({'ok': False, 'error': 'too large'}, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        try:
            body = json.loads(self.rfile.read(length) or b'{}')
        except ValueError:
            body = None
        if not isinstance(body, dict):
            self._json({'ok': False, 'error': 'invalid json'}, HTTPStatus.BAD_REQUEST)
            return
        if route == '/api/logout':
            self.server_ref.on_logout()
            self._json({'ok': True})
        elif self.server_ref.save(cast('dict[str, Any]', body)):
            self._json({'ok': True})
        else:
            self._json({'ok': False, 'error': 'invalid client id'}, HTTPStatus.BAD_REQUEST)
