from __future__ import annotations

from typing import Any

from batocera_discord import paths
from batocera_discord.session import Session, avatar_key, avatar_url
from batocera_discord.state import State
from batocera_discord.storage import read_json


class Hooks:
    def __init__(self) -> None:
        self.images: list[str] = []

    def authorize_started(self) -> None: ...
    def authorize_finished(self) -> None: ...

    def image_wanted(self, key: str, url: str, /) -> None:
        self.images.append(key)


class FakeRPC:
    def __init__(self, channels: dict[str, dict[str, Any]]) -> None:
        self.channels = channels
        self.subscribed: set[tuple[str, str]] = set()

    def call(self, cmd: str, args: dict[str, Any] | None = None, /, **_kw: object) -> dict[str, Any]:
        assert cmd == 'GET_CHANNEL'
        assert args is not None
        return self.channels[args['channel_id']]

    def subscribe(self, evt: str, args: dict[str, Any] | None = None, /) -> None:
        self.subscribed.add((evt, (args or {}).get('channel_id', '')))

    def unsubscribe(self, evt: str, args: dict[str, Any] | None = None, /) -> None:
        self.subscribed.discard((evt, (args or {}).get('channel_id', '')))


ME = {'id': '1', 'username': 'me'}
GLENN = {'id': '2', 'username': 'glenn', 'global_name': 'Glenn', 'avatar': 'abc'}


def _session(channels: dict[str, dict[str, Any]]) -> tuple[Session, State, FakeRPC, Hooks]:
    state = State()
    state.user = ME
    hooks = Hooks()
    session = Session(state, hooks)
    rpc = FakeRPC(channels)
    session.rpc = rpc  # pyright: ignore[reportAttributeAccessIssue]
    return session, state, rpc, hooks


def test_avatar_url() -> None:
    assert avatar_url(GLENN) == 'https://cdn.discordapp.com/avatars/2/abc.png?size=128'
    assert avatar_url({'id': '175928847299117063'}).startswith('https://cdn.discordapp.com/embed/avatars/')
    assert avatar_key(GLENN) == 'u2abc'


def test_private_call_is_remembered_and_left() -> None:
    dm_id = '300000000000000001'
    dm: dict[str, Any] = {'id': dm_id, 'type': 1, 'name': '', 'voice_states': [{'user': ME}, {'user': GLENN}]}
    session, state, rpc, hooks = _session({dm_id: dm})

    session._enter_call({'id': dm_id})

    assert state.call is not None
    assert state.call.private
    assert set(state.members) == {'1', '2'}
    assert ('SPEAKING_START', dm_id) in rpc.subscribed
    assert 'u2abc' in hooks.images
    assert session.recents == [{'name': 'Glenn', 'channel_id': dm_id}]
    assert read_json(paths.RECENTS_FILE)['items'] == session.recents

    session._enter_call(None)
    assert state.call is None
    assert not rpc.subscribed


def test_voice_events_update_state() -> None:
    session, state, _rpc, _hooks = _session({})

    session._on_event('VOICE_STATE_CREATE', {'user': GLENN, 'volume': 100})
    session._on_event('SPEAKING_START', {'user_id': '2'})
    session._on_event('VOICE_SETTINGS_UPDATE', {'mute': True, 'deaf': False})
    assert '2' in state.members
    assert state.speaking == {'2'}
    assert state.mute
    assert not state.deaf

    session._on_event('SPEAKING_STOP', {'user_id': '2'})
    session._on_event('VOICE_STATE_DELETE', {'user': GLENN})
    assert not state.speaking
    assert not state.members
