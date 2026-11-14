"""State shared between the Discord session thread, the overlay and the setup web server."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Phase(StrEnum):
    STARTING = 'starting'
    NO_CONFIG = 'no_config'
    NO_DISCORD = 'no_discord'
    INSTALLING = 'installing'
    LAUNCHING = 'launching'
    CONNECTING = 'connecting'
    AUTHORIZE = 'authorize'
    READY = 'ready'
    ERROR = 'error'


@dataclass(slots=True)
class AudioDevices:
    mic: str | None = None  # readable name of the capture device Discord will use, None if there is none
    output: str = ''  # readable name of the default output
    headset_without_mic: str | None = None  # bluetooth headset connected in high quality (A2DP) mode: no mic


@dataclass(slots=True)
class Call:
    id: str
    name: str
    type: int | None
    guild_id: str | None
    since: float = field(default_factory=time.time)

    @property
    def private(self) -> bool:
        return self.type in (1, 3)  # DM or group DM


@dataclass(slots=True)
class State:
    lock: threading.RLock = field(default_factory=threading.RLock, repr=False)
    changed: threading.Condition = field(init=False, repr=False)
    version: int = 0

    phase: Phase = Phase.STARTING
    error: str = ''
    needs_secret: bool = False
    install_progress: int = 0
    user: dict[str, Any] | None = None
    guilds: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    channels: dict[str, list[dict[str, Any]]] = field(default_factory=dict[str, list[dict[str, Any]]])
    call: Call | None = None
    members: dict[str, dict[str, Any]] = field(default_factory=dict[str, dict[str, Any]])
    speaking: set[str] = field(default_factory=set[str])
    mute: bool = False
    deaf: bool = False
    audio: AudioDevices = field(default_factory=AudioDevices)

    def __post_init__(self) -> None:
        self.changed = threading.Condition(self.lock)

    def bump(self) -> None:
        """Call with the lock held after any change, to wake up the overlay and the setup page."""
        with self.lock:
            self.version += 1
            self.changed.notify_all()

    def set_phase(self, phase: Phase, /, error: str = '') -> None:
        with self.lock:
            if self.phase != phase or self.error != error:
                self.phase, self.error = phase, error
                self.bump()

    def snapshot(self) -> dict[str, Any]:
        """Public status, safe to expose to the setup page (no secret, no token)."""
        with self.lock:
            return {
                'phase': self.phase.value,
                'error': self.error,
                'needs_secret': self.needs_secret,
                'install_progress': self.install_progress,
                'user': None
                if self.user is None
                else {
                    'name': self.user.get('global_name') or self.user.get('username'),
                    'username': self.user.get('username'),
                },
                'in_call': self.call.name if self.call else None,
            }
