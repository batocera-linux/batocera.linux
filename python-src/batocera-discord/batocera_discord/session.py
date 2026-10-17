"""Background thread that keeps a Discord RPC session alive and mirrors it into the shared State."""

from __future__ import annotations

import logging
import queue
import threading
import time
from typing import TYPE_CHECKING, Any, Final, Protocol, cast

from . import discord_app, ipc, paths
from .errors import LOOKUP_ERRORS
from .oauth import PKCE, SCOPES, OAuthError, TokenClient
from .state import Call, Phase, State
from .storage import AppConfig, Tokens, read_json, write_json

if TYPE_CHECKING:
    from collections.abc import Callable

_logger: Final = logging.getLogger(__name__)

VOICE_EVENTS: Final = (
    'VOICE_STATE_CREATE',
    'VOICE_STATE_UPDATE',
    'VOICE_STATE_DELETE',
    'SPEAKING_START',
    'SPEAKING_STOP',
)
VOICE_CHANNEL_TYPES: Final = (2, 13)  # voice, stage
MAX_RECENTS: Final = 12
LAUNCH_RETRY: Final = 45.0
AUTO_INSTALL_RETRY: Final = 300.0  # seconds: the network may not be up yet when the service starts
INSTALL_ERROR_HOLD: Final = 10.0  # seconds the panel shows a failed install before offering it again


class SessionHooks(Protocol):
    def authorize_started(self) -> None: ...
    def authorize_finished(self) -> None: ...
    def image_wanted(self, key: str, url: str, /) -> None: ...


def avatar_url(user: dict[str, Any], /) -> str:
    if user.get('avatar'):
        return f'https://cdn.discordapp.com/avatars/{user["id"]}/{user["avatar"]}.png?size=128'
    try:
        index = (int(user['id']) >> 22) % 6
    except LOOKUP_ERRORS:
        index = 0
    return f'https://cdn.discordapp.com/embed/avatars/{index}.png'


def avatar_key(user: dict[str, Any], /) -> str:
    return f'u{user.get("id", "")}{user.get("avatar") or ""}'


class Session:
    def __init__(
        self,
        state: State,
        hooks: SessionHooks,
        /,
        *,
        tokens: TokenClient | None = None,
        auto_install: bool = False,
    ) -> None:
        self.state = state
        self.hooks = hooks
        self.tokens = tokens or TokenClient()
        self.auto_install = auto_install
        self.rpc = ipc.DiscordIPC(self._on_event)
        self._jobs: queue.Queue[Callable[[], object]] = queue.Queue()
        self._reconfigured = threading.Event()
        self._last_launch = 0.0
        self._discord_installed = False
        self._installing = threading.Lock()
        self._install_thread: threading.Thread | None = None
        self._last_auto_install: float | None = None
        self._install_error_until = 0.0
        self.recents: list[dict[str, str]] = [
            cast('dict[str, str]', item)
            for item in read_json(paths.RECENTS_FILE).get('items', [])
            if isinstance(item, dict)
        ]

    # -- public API (any thread) --
    def run_later(self, job: Callable[[], object], /) -> None:
        self._jobs.put(job)

    def reconfigure(self) -> None:
        """The application settings changed (setup page): reconnect with them."""
        self._reconfigured.set()

    def start(self) -> None:
        threading.Thread(target=self._loop, name='discord-session', daemon=True).start()

    def install(self) -> None:
        """Install Discord from Flathub in the background; the progress goes to the state."""
        if not self._installing.acquire(blocking=False):
            return
        with self.state.lock:
            self.state.install_progress = 0
        self.state.set_phase(Phase.INSTALLING)
        self._install_thread = threading.Thread(target=self._install, name='discord-install', daemon=True)
        self._install_thread.start()

    def _install(self) -> None:
        def progress(percent: int) -> None:
            with self.state.lock:
                self.state.install_progress = percent
                self.state.bump()

        try:
            ok = discord_app.install(progress)
        except Exception:
            _logger.exception('Discord install failed')
            ok = False
        # publish the result before releasing the lock, so the connection loop never sees an in-between state
        if ok:
            self._discord_installed = True
            self.state.set_phase(Phase.STARTING)
        else:
            self._install_error_until = time.monotonic() + INSTALL_ERROR_HOLD
            self.state.set_phase(Phase.ERROR, 'flatpak install failed')
        self._installing.release()
        self._reconfigured.set()  # wake the connection loop

    def _auto_install(self) -> None:
        """Install Discord as soon as the service runs, so it is ready by the time the panel is opened."""
        if not self.auto_install or self._discord_installed or self._installing.locked():
            return
        now = time.monotonic()
        if self._last_auto_install is not None and now - self._last_auto_install < AUTO_INSTALL_RETRY:
            return
        self._last_auto_install = now
        if not discord_app.flatpak_available():
            return
        if discord_app.installed():
            self._discord_installed = True
            return
        _logger.info('Discord is not installed: installing it in the background')
        self.install()

    # -- connection loop --
    def _loop(self) -> None:
        while True:
            try:
                self._connect_and_serve()
            except Exception as exc:
                _logger.exception('Discord session error')
                self.state.set_phase(Phase.ERROR, str(exc)[:160])
                self._reconfigured.wait(5)
            self.rpc.close()
            with self.state.lock:
                self.state.user, self.state.call = None, None
                self.state.bump()

    def _connect_and_serve(self) -> None:
        self._reconfigured.clear()
        self._auto_install()
        if self._installing.locked() or time.monotonic() < self._install_error_until:
            # the install progress, then its error, have priority over the setup and launch screens
            self._reconfigured.wait(1)
            return
        config = AppConfig.load()
        if not config.configured:
            self.state.set_phase(Phase.NO_CONFIG)
            self._reconfigured.wait(3)
            return
        if (sock := ipc.find_socket()) is None:
            self._ensure_discord_running()
            return
        self.state.set_phase(Phase.CONNECTING)
        self.rpc.connect(config.client_id, sock)
        user = self._authenticate(config)
        with self.state.lock:
            self.state.user = user
            self.state.needs_secret = False
            self.state.bump()
        self.hooks.image_wanted(avatar_key(user), avatar_url(user))
        self.rpc.subscribe('VOICE_CHANNEL_SELECT')
        self.rpc.subscribe('VOICE_SETTINGS_UPDATE')
        self._apply_voice_settings(self.rpc.call('GET_VOICE_SETTINGS'))
        self._load_guilds()
        self._enter_call(self.rpc.call('GET_SELECTED_VOICE_CHANNEL') or None)
        self.state.set_phase(Phase.READY)
        _logger.info('connected to Discord as %s', user.get('username'))
        while self.rpc.connected and not self._reconfigured.is_set():
            try:
                job = self._jobs.get(timeout=1)
            except queue.Empty:
                continue
            try:
                job()
            except ipc.RPCError as exc:
                _logger.warning('action failed: %s', exc)

    def _ensure_discord_running(self) -> None:
        if not self._discord_installed and not discord_app.installed():
            self.state.set_phase(Phase.NO_DISCORD)
            self._reconfigured.wait(5)
            return
        self._discord_installed = True
        self.state.set_phase(Phase.LAUNCHING)
        if time.monotonic() - self._last_launch > LAUNCH_RETRY:
            self._last_launch = time.monotonic()
            discord_app.launch()
        self._reconfigured.wait(3)

    def _authenticate(self, config: AppConfig, /) -> dict[str, Any]:
        tokens = Tokens.load()
        if tokens.access_token and tokens.expired and tokens.refresh_token:
            try:
                tokens = self.tokens.refresh(config, tokens)
                tokens.save()
            except OAuthError as exc:
                _logger.info('token refresh failed (%s), asking for a new authorization', exc)
                tokens = Tokens()
        if tokens.access_token and not tokens.expired:
            try:
                return self._user(self.rpc.call('AUTHENTICATE', {'access_token': tokens.access_token}))
            except ipc.RPCError as exc:
                _logger.info('stored token rejected: %s', exc)
        return self._authorize(config)

    def _authorize(self, config: AppConfig, /) -> dict[str, Any]:
        pkce = PKCE.generate()
        self.state.set_phase(Phase.AUTHORIZE)
        self.hooks.authorize_started()
        try:
            answer = self.rpc.call(
                'AUTHORIZE',
                {
                    'client_id': config.client_id,
                    'scopes': list(SCOPES),
                    'response_type': 'code',
                    'code_challenge': pkce.challenge,
                    'code_challenge_method': 'S256',
                },
                timeout=300,
            )
        finally:
            self.hooks.authorize_finished()
        try:
            tokens = self.tokens.exchange_code(config, str(answer.get('code', '')), pkce)
        except OAuthError as exc:
            if exc.needs_secret:
                with self.state.lock:
                    self.state.needs_secret = True
                    self.state.bump()
            raise
        tokens.save()
        return self._user(self.rpc.call('AUTHENTICATE', {'access_token': tokens.access_token}))

    @staticmethod
    def _user(answer: dict[str, Any], /) -> dict[str, Any]:
        user = answer.get('user')
        if not isinstance(user, dict):
            raise ipc.RPCError('AUTHENTICATE: no user in answer')
        return cast('dict[str, Any]', user)

    # -- data --
    def _apply_voice_settings(self, settings: dict[str, Any], /) -> None:
        with self.state.lock:
            self.state.mute, self.state.deaf = bool(settings.get('mute')), bool(settings.get('deaf'))
            self.state.bump()

    def _load_guilds(self) -> None:
        guilds = cast('list[dict[str, Any]]', self.rpc.call('GET_GUILDS').get('guilds', []))
        with self.state.lock:
            self.state.guilds = guilds
            self.state.bump()
        for guild in guilds:
            if guild.get('icon_url'):
                self.hooks.image_wanted(f'g{guild["id"]}', str(guild['icon_url']))

    def load_channels(self, guild_id: str, /) -> None:
        channels = [
            channel
            for channel in cast(
                'list[dict[str, Any]]', self.rpc.call('GET_CHANNELS', {'guild_id': guild_id}).get('channels', [])
            )
            if channel.get('type') in VOICE_CHANNEL_TYPES
        ]
        with self.state.lock:
            self.state.channels[guild_id] = channels
            self.state.bump()
        for channel in channels:
            try:
                full = self.rpc.call('GET_CHANNEL', {'channel_id': channel['id']})
            except ipc.RPCError:
                continue
            voice_states = cast('list[dict[str, Any]]', full.get('voice_states', []))
            with self.state.lock:
                channel['voice_states'] = voice_states
                self.state.bump()
            for voice_state in voice_states:
                if isinstance(user := voice_state.get('user'), dict):
                    self._want_avatar(cast('dict[str, Any]', user))

    def _want_avatar(self, user: dict[str, Any], /) -> None:
        if user.get('id'):
            self.hooks.image_wanted(avatar_key(user), avatar_url(user))

    def _enter_call(self, channel: dict[str, Any] | None, /) -> None:
        with self.state.lock:
            previous = self.state.call
        if previous is not None and (channel is None or channel.get('id') != previous.id):
            for evt in VOICE_EVENTS:
                self.rpc.unsubscribe(evt, {'channel_id': previous.id})
        if not channel or not channel.get('id'):
            with self.state.lock:
                self.state.call, self.state.members, self.state.speaking = None, {}, set()
                self.state.bump()
            return
        if 'voice_states' not in channel:
            channel = self.rpc.call('GET_CHANNEL', {'channel_id': channel['id']})
        voice_states = cast('list[dict[str, Any]]', channel.get('voice_states', []))
        with self.state.lock:
            since = previous.since if previous is not None and previous.id == channel['id'] else time.time()
            call = Call(
                channel['id'], str(channel.get('name') or ''), channel.get('type'), channel.get('guild_id'), since
            )
            self.state.call = call
            self.state.members = {vs['user']['id']: vs for vs in voice_states if isinstance(vs.get('user'), dict)}
            self.state.speaking = set()
            self.state.bump()
        for voice_state in voice_states:
            self._want_avatar(voice_state.get('user') or {})
        for evt in VOICE_EVENTS:
            self.rpc.subscribe(evt, {'channel_id': channel['id']})
        if call.private:
            self._remember(channel, voice_states)

    def _remember(self, channel: dict[str, Any], voice_states: list[dict[str, Any]], /) -> None:
        me = (self.state.user or {}).get('id')
        names = [
            str(vs['user'].get('global_name') or vs['user'].get('username'))
            for vs in voice_states
            if isinstance(vs.get('user'), dict) and vs['user'].get('id') != me
        ]
        label = str(channel.get('name') or ', '.join(names) or 'Discord')
        self.recents = [{'name': label, 'channel_id': channel['id']}] + [
            r for r in self.recents if r.get('channel_id') != channel['id']
        ]
        del self.recents[MAX_RECENTS:]
        write_json(paths.RECENTS_FILE, {'items': self.recents})

    # -- events (IPC reader thread) --
    def _on_event(self, evt: str, data: dict[str, Any], /) -> None:
        state = self.state
        if evt == 'VOICE_CHANNEL_SELECT':
            channel_id = data.get('channel_id')
            self.run_later(lambda: self._enter_call({'id': channel_id} if channel_id else None))
        elif evt == 'VOICE_SETTINGS_UPDATE':
            self._apply_voice_settings(data)
        elif evt in ('VOICE_STATE_CREATE', 'VOICE_STATE_UPDATE'):
            if isinstance(user := data.get('user'), dict):
                user = cast('dict[str, Any]', user)
                with state.lock:
                    state.members[str(user['id'])] = data
                    state.bump()
                self._want_avatar(user)
        elif evt == 'VOICE_STATE_DELETE':
            with state.lock:
                user = cast('dict[str, Any]', data.get('user') or {})
                state.members.pop(str(user.get('id')), None)
                state.bump()
        elif evt in ('SPEAKING_START', 'SPEAKING_STOP'):
            with state.lock:
                user_id = str(data.get('user_id'))
                if evt == 'SPEAKING_START':
                    state.speaking.add(user_id)
                else:
                    state.speaking.discard(user_id)
                state.bump()

    # -- actions (queued from the overlay, executed on the session thread) --
    def join(self, channel_id: str, /) -> None:
        self.run_later(
            lambda: self.rpc.call('SELECT_VOICE_CHANNEL', {'channel_id': channel_id, 'force': True}, timeout=15)
        )

    def leave(self) -> None:
        self.run_later(lambda: self.rpc.call('SELECT_VOICE_CHANNEL', {'channel_id': None}))

    def toggle_mute(self) -> None:
        self.run_later(lambda: self.rpc.call('SET_VOICE_SETTINGS', {'mute': not self.state.mute}))

    def toggle_deaf(self) -> None:
        self.run_later(lambda: self.rpc.call('SET_VOICE_SETTINGS', {'deaf': not self.state.deaf}))

    def set_user_volume(self, user_id: str, volume: int, /) -> None:
        self.run_later(
            lambda: self.rpc.call('SET_USER_VOICE_SETTINGS', {'user_id': user_id, 'volume': max(0, min(200, volume))})
        )

    def set_user_mute(self, user_id: str, mute: bool, /) -> None:
        self.run_later(lambda: self.rpc.call('SET_USER_VOICE_SETTINGS', {'user_id': user_id, 'mute': mute}))

    def logout(self) -> None:
        """Revoke and forget the tokens; the next connection asks for a fresh authorization."""
        config, tokens = AppConfig.load(), Tokens.load()
        self.tokens.revoke(config, tokens)
        Tokens.clear()
        self.reconfigure()
