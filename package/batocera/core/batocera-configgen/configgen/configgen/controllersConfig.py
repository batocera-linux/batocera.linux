from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict

import evdev
import pyudev

from .batoceraPaths import ES_GAMES_METADATA

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .types import DeviceInfoDict, DeviceInfoMapping, GunDict, GunMapping

eslog = logging.getLogger(__name__)

def gunsNeedCrosses(guns: GunMapping) -> bool:
    # no gun, enable the cross for joysticks, mouses...
    if len(guns) == 0:
        return True

    for gun in guns:
        if guns[gun]["need_cross"]:
            return True
    return False

# returns None is no border is wanted
def gunsBordersSizeName(guns: GunMapping, config: Mapping[str, object]) -> str | None:
    bordersSize = "medium"
    if "controllers.guns.borderssize" in config and config["controllers.guns.borderssize"]:
        bordersSize = config["controllers.guns.borderssize"]

    # overriden by specific options
    bordersmode = "normal"
    if "controllers.guns.bordersmode" in config and config["controllers.guns.bordersmode"] and config["controllers.guns.bordersmode"] != "auto":
        bordersmode = config["controllers.guns.bordersmode"]
    if "bordersmode" in config and config["bordersmode"] and config["bordersmode"] != "auto":
        bordersmode = config["bordersmode"]

    # others are gameonly and normal
    if bordersmode == "hidden":
        return None
    if bordersmode == "force":
        return bordersSize

    for gun in guns:
        if guns[gun]["need_borders"]:
            return bordersSize
    return None

# returns None to follow the bezel overlay size by default
def gunsBorderRatioType(guns: GunMapping, config: dict[str, str]) -> str | None:
    if "controllers.guns.bordersratio" in config:
        return config["controllers.guns.bordersratio"] # "4:3"
    return None

def getMouseButtons(device: evdev.InputDevice) -> list[str]:
    caps = device.capabilities()
    caps_keys = caps[evdev.ecodes.EV_KEY]
    caps_filter = [evdev.ecodes.BTN_LEFT, evdev.ecodes.BTN_RIGHT, evdev.ecodes.BTN_MIDDLE, evdev.ecodes.BTN_1, evdev.ecodes.BTN_2, evdev.ecodes.BTN_3, evdev.ecodes.BTN_4, evdev.ecodes.BTN_5, evdev.ecodes.BTN_6, evdev.ecodes.BTN_7, evdev.ecodes.BTN_8]
    caps_intersection = list(set(caps_keys) & set(caps_filter))
    buttons: list[str] = []
    if evdev.ecodes.BTN_LEFT in caps_intersection:
        buttons.append("left")
    if evdev.ecodes.BTN_RIGHT in caps_intersection:
        buttons.append("right")
    if evdev.ecodes.BTN_MIDDLE in caps_intersection:
        buttons.append("middle")
    if evdev.ecodes.BTN_1 in caps_intersection:
        buttons.append("1")
    if evdev.ecodes.BTN_2 in caps_intersection:
        buttons.append("2")
    if evdev.ecodes.BTN_3 in caps_intersection:
        buttons.append("3")
    if evdev.ecodes.BTN_4 in caps_intersection:
        buttons.append("4")
    if evdev.ecodes.BTN_5 in caps_intersection:
        buttons.append("5")
    if evdev.ecodes.BTN_6 in caps_intersection:
        buttons.append("6")
    if evdev.ecodes.BTN_7 in caps_intersection:
        buttons.append("7")
    if evdev.ecodes.BTN_8 in caps_intersection:
        buttons.append("8")
    return buttons

def mouseButtonToCode(button: str) -> int | None:
    if button == "left":
        return evdev.ecodes.BTN_LEFT
    if button == "right":
        return evdev.ecodes.BTN_RIGHT
    if button == "middle":
        return evdev.ecodes.BTN_MIDDLE
    if button == "1":
        return evdev.ecodes.BTN_1
    if button == "2":
        return evdev.ecodes.BTN_2
    if button == "3":
        return evdev.ecodes.BTN_3
    if button == "4":
        return evdev.ecodes.BTN_4
    if button == "5":
        return evdev.ecodes.BTN_5
    if button == "6":
        return evdev.ecodes.BTN_6
    if button == "7":
        return evdev.ecodes.BTN_7
    if button == "8":
        return evdev.ecodes.BTN_8
    return None

def getGuns() -> GunDict:
    import re

    import pyudev

    guns: GunDict = {}
    context = pyudev.Context()

    # guns are mouses, just filter on them
    mouses = context.list_devices(subsystem='input')

    # keep only mouses with /dev/iput/eventxx
    mouses_clean = {}
    for mouse in mouses:
        matches = re.match(r"^/dev/input/event([0-9]*)$", str(mouse.device_node))
        if matches != None:
            if ("ID_INPUT_MOUSE" in mouse.properties and mouse.properties["ID_INPUT_MOUSE"]) == '1':
                mouses_clean[int(matches.group(1))] = mouse
    mouses = mouses_clean

    nmouse = 0
    ngun   = 0
    for eventid in sorted(mouses):
        eslog.info("found mouse {} at {} with id_mouse={}".format(nmouse, mouses[eventid].device_node, nmouse))
        if "ID_INPUT_GUN" not in mouses[eventid].properties or mouses[eventid].properties["ID_INPUT_GUN"] != "1":
            nmouse = nmouse + 1
            continue

        device = evdev.InputDevice(mouses[eventid].device_node)
        buttons = getMouseButtons(device)

        # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE (TOUCHPAD are listed after mouses)
        need_cross   = "ID_INPUT_GUN_NEED_CROSS"   in mouses[eventid].properties and mouses[eventid].properties["ID_INPUT_GUN_NEED_CROSS"]   == '1'
        need_borders = "ID_INPUT_GUN_NEED_BORDERS" in mouses[eventid].properties and mouses[eventid].properties["ID_INPUT_GUN_NEED_BORDERS"] == '1'
        guns[ngun] = {"node": mouses[eventid].device_node, "id_mouse": nmouse, "need_cross": need_cross, "need_borders": need_borders, "name": device.name, "buttons": buttons}
        eslog.info("found gun {} at {} with id_mouse={} ({})".format(ngun, mouses[eventid].device_node, nmouse, guns[ngun]["name"]))
        nmouse = nmouse + 1
        ngun = ngun + 1

    if len(guns) == 0:
        eslog.info("no gun found")

    return guns

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
            inblock = True
    return ret

def getGamesMetaData(system: str, rom: str | Path) -> dict[str, str]:
    # load the database
    tree = ET.parse(ES_GAMES_METADATA)
    root = tree.getroot()
    game = shortNameFromPath(rom)
    res: dict[str, str] = {}
    eslog.info("looking for game metadata ({}, {})".format(system, game))

    targetSystem = system
    # hardcoded list of system for arcade
    # this list can be found in es_system.yml
    # at this stage we don't know if arcade will be kept as one system only in metadata, so i hardcode this list for now
    if system in ['naomi', 'naomi2', 'atomiswave', 'fbneo', 'mame', 'neogeo', 'triforce', 'hypseus-singe', 'model2', 'model3', 'hikaru', 'gaelco', 'cave3rd', 'namco2x6']:
        targetSystem = 'arcade'

    for nodesystem in root.findall(".//system"):
        for sysname in nodesystem.get("name").split(','):
            if sysname == targetSystem:
                # search the game named default
                for nodegame in nodesystem.findall(".//game"):
                    if nodegame.get("name") == "default":
                        for child in nodegame:
                            for attribute in child.attrib:
                                key = "{}_{}".format(child.tag, attribute)
                                res[key] = child.get(attribute)
                                eslog.info("found game metadata {}={} (system level)".format(key, res[key]))
                        break
                for nodegame in nodesystem.findall(".//game"):
                    if nodegame.get("name") != "default" and nodegame.get("name") in game:
                        for child in nodegame:
                            for attribute in child.attrib:
                                key = "{}_{}".format(child.tag, attribute)
                                res[key] = child.get(attribute)
                                eslog.info("found game metadata {}={}".format(key, res[key]))
                        return res
    return res

def dev2int(dev: str) -> int | None:
    matches = re.match(r"^/dev/input/event([0-9]*)$", dev)
    if matches is None:
        return None
    return int(matches.group(1))


class _Device(TypedDict):
    node: str
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
                devices[eventId] = { "node": ev.device_node, "group": group, "isJoystick": isJoystick, "isWheel": isWheel, "isMouse": isMouse }
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
        res[d["node"]] = { "eventId": device, "isJoystick": d["isJoystick"], "isWheel": d["isWheel"], "isMouse": d["isMouse"], "associatedDevices": dgroup, "joystick_index": njoystick, "mouse_index": nmouse }
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
