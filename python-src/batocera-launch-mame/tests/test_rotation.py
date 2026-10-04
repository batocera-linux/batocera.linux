from __future__ import annotations

import subprocess
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

from batocera_launch_mame.rotation import MameRotationPlugin

from batocera_launch.plugins import HookContext, load_plugins

if TYPE_CHECKING:
    from collections.abc import Callable

    import pytest


def _context(emulator: str, /) -> HookContext:
    return HookContext(cast('Any', SimpleNamespace(emulator=emulator)))


def _resolution(outputs: dict[str, str], calls: list[list[str]], /) -> Callable[..., SimpleNamespace]:
    def run(command: list[str], /, **kwargs: object) -> SimpleNamespace:
        calls.append(command)
        return SimpleNamespace(stdout=outputs.get(command[1], ''))

    return run


def test_other_emulators_are_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(subprocess, 'run', _resolution({}, calls))

    MameRotationPlugin().stop(_context('snes9x'))

    assert calls == []


def test_reapplies_the_xorg_rotation(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(subprocess, 'run', _resolution({'getDisplayMode': 'xorg\n', 'getRotation': '1\n'}, calls))

    MameRotationPlugin().stop(_context('mame'))

    assert calls[-1] == ['batocera-resolution', 'setRotation', '1']


def test_leaves_wayland_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(subprocess, 'run', _resolution({'getDisplayMode': 'wayland\n'}, calls))

    MameRotationPlugin().stop(_context('mame'))

    assert calls == [['batocera-resolution', 'getDisplayMode']]


def test_is_registered() -> None:
    assert 'MameRotationPlugin' in {type(plugin).__name__ for plugin in load_plugins()}
