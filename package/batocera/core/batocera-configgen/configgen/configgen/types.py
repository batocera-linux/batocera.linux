from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import NotRequired, TypedDict


class Resolution(TypedDict):
    width: int
    height: int


class BezelInfo(TypedDict):
    width: int
    height: int
    top: int
    left: int
    bottom: int
    right: int
    opacity: NotRequired[float]
    messagex: NotRequired[float]
    messagey: NotRequired[float]


class ScreenInfo(TypedDict):
    width: int
    height: int
    x: int
    y: int


class DeviceInfo(TypedDict):
    eventId: int
    sysfs_path: str
    isJoystick: bool
    isWheel: bool
    isMouse: bool
    associatedDevices: list[str] | None
    joystick_index: int | None
    mouse_index: int | None
    wheel_rotation: NotRequired[int]


type DeviceInfoMapping = Mapping[str, DeviceInfo]
type DeviceInfoDict = dict[str, DeviceInfo]


class HotkeysContext(TypedDict):
    name: str
    keys: dict[str, Sequence[str]]  # Sequence[str] covers both str and list[str]
