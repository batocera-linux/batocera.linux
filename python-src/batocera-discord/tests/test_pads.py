from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import pytest

pytest.importorskip('evdev')

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


def test_lone_guide_press_toggles() -> None:
    toggles: list[bool] = []
    reader = Pads(lambda: toggles.append(True))
    pad = _pad()

    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, ecodes.BTN_MODE, 1)))
    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, ecodes.BTN_MODE, 0)))

    assert toggles == [True]


def test_hotkey_combo_does_not_toggle() -> None:
    toggles: list[bool] = []
    reader = Pads(lambda: toggles.append(True))
    pad = _pad()

    for code, value in ((ecodes.BTN_MODE, 1), (ecodes.BTN_START, 1), (ecodes.BTN_START, 0), (ecodes.BTN_MODE, 0)):
        reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, code, value)))

    assert toggles == []


def test_guide_button_can_be_disabled() -> None:
    toggles: list[bool] = []
    reader = Pads(lambda: toggles.append(True), guide_enabled=False)
    pad = _pad()

    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, ecodes.BTN_MODE, 1)))
    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, ecodes.BTN_MODE, 0)))

    assert toggles == []


def test_buttons_only_act_while_grabbed() -> None:
    reader = Pads(lambda: None)
    pad = _pad(Family.PLAYSTATION)

    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, ecodes.BTN_SOUTH, 1)))
    assert reader.actions.empty()
    assert reader.last_family is Family.PLAYSTATION

    reader._grabbed = True
    reader.handle(pad, cast('Any', FakeEvent(ecodes.EV_KEY, ecodes.BTN_SOUTH, 1)))
    assert reader.actions.get_nowait() is Action.CONFIRM
