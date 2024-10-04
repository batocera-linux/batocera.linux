from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import NotRequired, TypeAlias, TypedDict


class Resolution(TypedDict):
    width: int
    height: int


class ScreenInfo(TypedDict):
    width: int
    height: int
    x: int
    y: int


class Gun(TypedDict):
    node: str | None
    id_mouse: int
    need_cross: bool
    need_borders: bool
    name: str
    buttons: list[str]


GunMapping: TypeAlias = Mapping[int, Gun]
GunDict: TypeAlias = dict[int, Gun]


class DeviceInfo(TypedDict):
    eventId: int
    isJoystick: bool
    isWheel: bool
    isMouse: bool
    associatedDevices: list[str] | None
    joystick_index: int | None
    mouse_index: int | None
    wheel_rotation: NotRequired[int]


DeviceInfoMapping: TypeAlias = Mapping[str, DeviceInfo]
DeviceInfoDict: TypeAlias = dict[str, DeviceInfo]


class HotkeysContext(TypedDict):
    name: str
    keys: dict[str, Sequence[str]]  # Sequence[str] covers both str and list[str]
