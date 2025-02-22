from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict

import pyudev

from .batoceraPaths import ES_GAMES_METADATA

if TYPE_CHECKING:
    from .types import DeviceInfoDict, DeviceInfoMapping

_logger = logging.getLogger(__name__)


def shortNameFromPath(path: str | Path) -> str:
    redname = Path(path).stem.lower()
    inpar   = False
    inblock = False
    ret = ""
    for c in redname:
        if not inpar and not inblock and ( (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') ):
            ret += c
        elif c == '(':
            inpar = True
        elif c == ')':
            inpar = False
        elif c == '[':
            inblock = True
        elif c == ']':
            inblock = False
    return ret

def getGamesMetaData(system: str, rom: str | Path) -> dict[str, str]:
    # load the database
    tree = ET.parse(ES_GAMES_METADATA)
    root = tree.getroot()
    game = shortNameFromPath(rom)
    res: dict[str, str] = {}
    _logger.info("looking for game metadata (%s, %s)", system, game)

    targetSystem = system
    # hardcoded list of system for arcade
    # this list can be found in es_system.yml
    # at this stage we don't know if arcade will be kept as one system only in metadata, so i hardcode this list for now
    if system in ['lindbergh', 'naomi', 'naomi2', 'atomiswave', 'fbneo', 'mame', 'neogeo', 'triforce', 'hypseus-singe', 'model2', 'model3', 'hikaru', 'gaelco', 'cave3rd', 'namco2x6']:
        targetSystem = 'arcade'

    for nodesystem in root.findall(".//system"):
        for sysname in nodesystem.get("name").split(','):
            if sysname == targetSystem:
                # search the game named default
                for nodegame in nodesystem.findall(".//game"):
                    if nodegame.get("name") == "default":
                        for child in nodegame:
                            for attribute in child.attrib:
                                key = f"{child.tag}_{attribute}"
                                res[key] = child.get(attribute)
                                _logger.info("found game metadata %s=%s (system level)", key, res[key])
                        break
                for nodegame in nodesystem.findall(".//game"):
                    if nodegame.get("name") != "default" and nodegame.get("name") in game:
                        for child in nodegame:
                            for attribute in child.attrib:
                                key = f"{child.tag}_{attribute}"
                                res[key] = child.get(attribute)
                                _logger.info("found game metadata %s=%s", key, res[key])
                        return res
    return res

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
    mouses    = []
    joysticks = []
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
                    "node": ev.device_node,
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
                    groups[group].append(ev.device_node)
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
