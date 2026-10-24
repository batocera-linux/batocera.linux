"""Controller vocabulary shared by the input reader and the overlay (no evdev needed)."""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class Family(StrEnum):
    XBOX = 'xbox'
    PLAYSTATION = 'playstation'
    NINTENDO = 'nintendo'


class Action(StrEnum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    CONFIRM = 'confirm'
    BACK = 'back'
    MUTE = 'mute'
    DEAFEN = 'deafen'
    PREV_TAB = 'prev_tab'
    NEXT_TAB = 'next_tab'
    START = 'start'
    SCROLL_UP = 'scroll_up'
    SCROLL_DOWN = 'scroll_down'


_SONY_VENDOR: Final = 0x054C
_NINTENDO_VENDOR: Final = 0x057E


def detect_family(name: str, vendor: int, /) -> Family:
    lowered = name.lower()
    if vendor == _SONY_VENDOR or any(
        word in lowered for word in ('dualsense', 'dualshock', 'playstation', 'ps4', 'ps5', 'sony')
    ):
        return Family.PLAYSTATION
    if vendor == _NINTENDO_VENDOR or any(
        word in lowered for word in ('pro controller', 'joy-con', 'nintendo', 'switch')
    ):
        return Family.NINTENDO
    return Family.XBOX
