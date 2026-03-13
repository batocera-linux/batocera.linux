from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Final, NotRequired, TypedDict, cast

import pyudev

if TYPE_CHECKING:
    from .types import DeviceInfoDict, DeviceInfoMapping

_logger: Final = logging.getLogger(__name__)

def dev2int(dev: str) -> int | None:
    matches = re.match(r"^/dev/input/event([0-9]*)$", dev)
    if matches is None:
        return None
    return int(matches.group(1))


class _Device(TypedDict):
    node: str
    sysfs_path: str
    group: str | None
    isJoystick: bool
    isWheel: bool
    isMouse: bool
    wheel_rotation: NotRequired[int]

def getDevicesInformation() -> DeviceInfoDict:
    groups: dict[str | None, list[str]] = {}
    devices: dict[int, _Device] = {}
    context   = pyudev.Context()
    events    = context.list_devices(subsystem='input')
    mouses: list[int]    = []
    joysticks: list[int] = []
    for ev in events:
        eventId = dev2int(str(ev.device_node))
        if eventId is not None:
            isJoystick = ("ID_INPUT_JOYSTICK" in ev.properties and ev.properties["ID_INPUT_JOYSTICK"] == "1")
            isWheel    = ("ID_INPUT_WHEEL"    in ev.properties and ev.properties["ID_INPUT_WHEEL"] == "1")
            isMouse    = ("ID_INPUT_MOUSE"    in ev.properties and ev.properties["ID_INPUT_MOUSE"] == "1") or ("ID_INPUT_TOUCHPAD" in ev.properties and ev.properties["ID_INPUT_TOUCHPAD"] == "1")
            group = None
            if "ID_PATH" in ev.properties:
                group = ev.properties["ID_PATH"]
            if isJoystick or isMouse:
                if isJoystick:
                    joysticks.append(eventId)
                if isMouse:
                    mouses.append(eventId)
                devices[eventId] = {
                    "node": cast('str', ev.device_node),
                    "sysfs_path": str((Path(ev.sys_path) / "device" / "device").resolve()),
                    "group": group,
                    "isJoystick": isJoystick,
                    "isWheel": isWheel,
                    "isMouse": isMouse
                }
                if "ID_PATH" in ev.properties:
                    if isWheel and "WHEEL_ROTATION_ANGLE" in ev.properties:
                        devices[eventId]["wheel_rotation"] = int(ev.properties["WHEEL_ROTATION_ANGLE"])
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(cast('str', ev.device_node))
    mouses.sort()
    joysticks.sort()
    res: DeviceInfoDict = {}
    for device in devices:
        d = devices[device]
        dgroup = None
        if d["group"] is not None:
            dgroup = groups[d["group"]].copy()
            dgroup.remove(d["node"])
        nmouse    = None
        njoystick = None
        if d["isJoystick"]:
            njoystick = joysticks.index(device)
        nmouse = None
        if d["isMouse"]:
            nmouse = mouses.index(device)
        res[d["node"]] = { "eventId": device, "sysfs_path": d["sysfs_path"], "isJoystick": d["isJoystick"], "isWheel": d["isWheel"], "isMouse": d["isMouse"], "associatedDevices": dgroup, "joystick_index": njoystick, "mouse_index": nmouse }
        if "wheel_rotation" in d:
            res[d["node"]]["wheel_rotation"] = d["wheel_rotation"]
    return res

def getAssociatedMouse(devicesInformation: DeviceInfoMapping, dev: str) -> str | None:
    device = devicesInformation.get(dev)
    if device is None or device["associatedDevices"] is None:
        return None
    for candidate in device["associatedDevices"]:
        if devicesInformation[candidate]["isMouse"]:
            return candidate
    return None
