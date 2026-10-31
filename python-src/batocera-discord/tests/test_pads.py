from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import pytest

pytest.importorskip('evdev')

import evdev
from evdev import ecodes

from batocera_discord import pads
from batocera_discord.controls import Action, Family, detect_family
from batocera_discord.pads import KEYMAPS, Pads


@dataclass
class FakeEvent:
    type: int
    code: int
    value: int


def _pad(family: Family = Family.XBOX) -> Any:
    return pads._Pad(cast('Any', object()), family)


def test_detect_family() -> None:
    assert detect_family('Xbox Wireless Controller', 0x045E) is Family.XBOX
    assert detect_family('DualSense Wireless Controller', 0x054C) is Family.PLAYSTATION
    assert detect_family('Wireless Controller', 0x054C) is Family.PLAYSTATION
    assert detect_family('Pro Controller', 0x057E) is Family.NINTENDO
    assert detect_family('8BitDo Ultimate', 0x2DC8) is Family.XBOX


def test_nintendo_confirms_with_the_right_button() -> None:
    assert KEYMAPS[Family.XBOX][ecodes.BTN_SOUTH] is Action.CONFIRM
    assert KEYMAPS[Family.NINTENDO][ecodes.BTN_EAST] is Action.CONFIRM
    assert KEYMAPS[Family.NINTENDO][ecodes.BTN_SOUTH] is Action.BACK


def _press(reader: Pads, pad: Any, code: int, /) -> None:
    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, code, 1)))
    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, code, 0)))


def test_guide_or_hotkey_key_closes_the_panel() -> None:
    closes: list[bool] = []
    reader = Pads(lambda: closes.append(True), close_keys=frozenset({ecodes.BTN_MODE, ecodes.KEY_RECORD}))
    pad = _pad()

    _press(reader, pad, ecodes.BTN_MODE)
    _press(reader, pad, ecodes.KEY_RECORD)

    assert closes == [True, True]
    assert reader.actions.empty()


def test_buttons_become_actions() -> None:
    reader = Pads(lambda: None)
    pad = _pad(Family.PLAYSTATION)

    _press(reader, pad, ecodes.BTN_SOUTH)

    assert reader.actions.get_nowait() is Action.CONFIRM
    assert reader.last_family is Family.PLAYSTATION


def test_nothing_is_read_while_the_panel_is_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_devices() -> list[str]:
        return []

    monkeypatch.setattr(evdev, 'list_devices', no_devices)
    reader = Pads(lambda: None)

    assert not reader.active
    assert reader._thread is None
    reader.set_active(True)
    thread = reader._thread
    assert thread is not None
    reader.set_active(False)
    thread.join(5)

    assert not thread.is_alive()
    assert reader._thread is None
