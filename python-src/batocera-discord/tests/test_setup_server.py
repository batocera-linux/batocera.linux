from __future__ import annotations

import http.client
import json
import stat
from typing import TYPE_CHECKING, Any

import pytest

from batocera_discord import paths
from batocera_discord.setup_server import SetupServer, parse_config
from batocera_discord.state import Phase, State
from batocera_discord.storage import AppConfig, Tokens

if TYPE_CHECKING:
    from collections.abc import Iterator

CLIENT_ID = '123456789012345678'


@pytest.fixture
def events() -> list[str]:
    return []


@pytest.fixture
def server(events: list[str]) -> Iterator[SetupServer]:
    state = State()
    state.set_phase(Phase.NO_CONFIG)
    setup = SetupServer(state, lambda: events.append('saved'), lambda: events.append('logout'), port=0)
    url = setup.url()
    assert url is not None
    yield setup
    setup.stop()


def _request(
    setup: SetupServer, method: str, path: str, body: object = None, content_type: str = 'application/json'
) -> tuple[int, Any]:
    assert setup.running
    assert setup._httpd is not None
    port = setup._httpd.server_address[1]
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    headers = {'Content-Type': content_type} if body is not None else {}
    conn.request(method, path, json.dumps(body) if body is not None else None, headers)
    response = conn.getresponse()
    raw = response.read()
    conn.close()
    try:
        return response.status, json.loads(raw)
    except ValueError:
        return response.status, raw


def test_wrong_token_is_not_found(server: SetupServer) -> None:
    assert _request(server, 'GET', '/s/wrong')[0] == 404
    assert _request(server, 'GET', '/')[0] == 404
    assert _request(server, 'POST', '/s/wrong/api/config', {'client_id': CLIENT_ID})[0] == 404


def test_page_and_status(server: SetupServer) -> None:
    status, page = _request(server, 'GET', f'/s/{server.token}')
    assert status == 200
    assert b'discord.com/developers/applications' in page

    status, data = _request(server, 'GET', f'/s/{server.token}/api/status')
    assert status == 200
    assert data['phase'] == 'no_config'
    assert data['client_id'] == ''


def test_save_config_and_secret_stays_private(server: SetupServer, events: list[str]) -> None:
    body = {
        'client_id': CLIENT_ID,
        'client_secret': 'top-secret',
        'favorites': [{'name': 'Glenn', 'channel_id': '223456789012345678'}],
    }

    assert _request(server, 'POST', f'/s/{server.token}/api/config', body) == (200, {'ok': True})
    assert events == ['saved']
    assert stat.S_IMODE(paths.CONFIG_FILE.stat().st_mode) == 0o600
    assert AppConfig.load().client_secret == 'top-secret'

    _status, data = _request(server, 'GET', f'/s/{server.token}/api/status')
    assert data['has_secret'] is True
    assert 'top-secret' not in json.dumps(data)
    assert data['favorites'] == [{'name': 'Glenn', 'channel_id': '223456789012345678'}]


def test_post_requires_json(server: SetupServer) -> None:
    status, _data = _request(
        server, 'POST', f'/s/{server.token}/api/config', {'client_id': CLIENT_ID}, 'application/x-www-form-urlencoded'
    )
    assert status == 415
    assert not paths.CONFIG_FILE.exists()


def test_invalid_client_id_is_rejected(server: SetupServer) -> None:
    assert _request(server, 'POST', f'/s/{server.token}/api/config', {'client_id': 'abc'})[0] == 400


def test_logout(server: SetupServer, events: list[str]) -> None:
    assert _request(server, 'POST', f'/s/{server.token}/api/logout', {}) == (200, {'ok': True})
    assert events == ['logout']


def test_parse_config_keeps_secret_for_same_application() -> None:
    current = AppConfig(CLIENT_ID, 'kept')

    same = parse_config({'client_id': CLIENT_ID, 'client_secret': ''}, current)
    other = parse_config({'client_id': '923456789012345678'}, current)
    cleared = parse_config({'client_id': CLIENT_ID, 'clear_secret': True}, current)

    assert same is not None
    assert same.client_secret == 'kept'
    assert other is not None
    assert other.client_secret == ''
    assert cleared is not None
    assert cleared.client_secret == ''


def test_changing_application_forgets_tokens(server: SetupServer) -> None:
    Tokens('a', 'r', 0).save()

    assert server.save({'client_id': CLIENT_ID})
    assert Tokens.load() == Tokens()
