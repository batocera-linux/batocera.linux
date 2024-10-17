from __future__ import annotations

import logging
import math
import os
import re
import signal
import subprocess
from typing import TYPE_CHECKING, cast

import evdev

from .. import controllersConfig

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from ..controller import ControllerDict, ControllerMapping
    from ..Emulator import Emulator
    from ..types import DeviceInfoDict, DeviceInfoMapping

eslog = logging.getLogger(__name__)

wheelMapping = {
    "wheel":      "joystick1left",
    "accelerate": "r2",
    "brake":      "l2",
    "downshift":  "pageup",
    "upshift":    "pagedown"
}

# partial mapping between real pads buttons and batocera pads
emulatorMapping = {
    "dreamcast": {
        "lt":   "l2",
        "rt":   "r2",
        "up":   "pageup",
        "down": "pagedown"
    },
    "gamecube": {
        "lt": "l2",
        "rt": "r2",
        "a":  "a",
        "b":  "b",
        "x":  "x",
        "y":  "y"
    },
    "saturn": {
        "l":      "l2",
        "r":      "r2",
        "a":      "b",
        "b":      "a",
        "c":      "pagedown",
        "x":      "y",
        "y":      "x",
        "z":      "pageup",
        "start":  "start"
    },
    "n64": {
        "l":     "pageup",
        "r":     "pagedown",
        "a":     "b",
        "b":     "y",
        "start": "start"
    },
    "wii": {
        "lt": "l2",
        "rt": "r2",
        "a":  "a",
        "b":  "b",
        "x":  "x",
        "y":  "y"
    },
    "wiiu": {
        "a":      "a",
        "b":      "b",
        "x":      "x",
        "y":      "y",
        "start":  "start",
        "select": "select"
    },
    "psx": {
        "cross":    "b",
        "square":   "y",
        "round":    "a",
        "triangle": "x",
        "start":    "start",
        "select":    "select"
    },
    "ps2": {
        "cross":    "b",
        "square":   "y",
        "round":    "a",
        "triangle": "x"
    },
    "xbox": {
        "lt": "l2",
        "rt": "r2",
        "a":  "b",
        "b":  "a",
        "x":  "y",
        "y":  "x"
    },
}

def reconfigureControllers(playersControllers: ControllerMapping, system: Emulator, rom: str | Path, metadata: dict[str, str], deviceList: DeviceInfoDict) -> tuple[list[subprocess.Popen[bytes]], ControllerDict, DeviceInfoDict]:
    eslog.info("wheels reconfiguration")
    wheelsmetadata = None

    eslog.info("before wheel reconfiguration :")
    for playercontroller, pad in sorted(playersControllers.items()):
        eslog.info(f"  {playercontroller}. index:{pad.index!s} dev:{pad.device_path} name:{pad.real_name}")

    # reconfigure wheel buttons
    # no need to sort, but i like keeping the same loop (sorted by players)
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if pad.device_path in deviceList:
            if deviceList[pad.device_path]["isWheel"]:
                eslog.info(f"Wheel reconfiguration for pad {pad.real_name}")
                originalInputs = pad.inputs.copy()

                # erase target keys
                for md in metadata:
                    if md[:6] == "wheel_":
                        shortmd = md[6:]
                        if shortmd in wheelMapping:
                            if system.name in emulatorMapping and metadata[md] in emulatorMapping[system.name]:
                                wheelkey  = wheelMapping[shortmd]
                                if wheelkey in playersControllers[playercontroller].inputs:
                                    del playersControllers[playercontroller].inputs[wheelkey]
                                    eslog.info(f"wheel: erase the key {wheelkey}")

                # fill with the wanted keys
                for md in metadata:
                    if md[:6] == "wheel_":
                        shortmd = md[6:]
                        if shortmd in wheelMapping:
                            if system.name in emulatorMapping and metadata[md] in emulatorMapping[system.name]:
                                wheelkey  = wheelMapping[shortmd]
                                wantedkey = emulatorMapping[system.name][metadata[md]]

                                if wheelkey in originalInputs:
                                    playersControllers[playercontroller].inputs[wantedkey] = originalInputs[wheelkey]
                                    playersControllers[playercontroller].inputs[wantedkey].name = wantedkey
                                    eslog.info(f"wheel: fill key {wantedkey} with {wheelkey}")
                                else:
                                    eslog.info(f"wheel: unable to replace {wantedkey} with {wheelkey}")
        nplayer += 1

    # reconfigure wheel min/max/deadzone
    procs: list[subprocess.Popen[bytes]] = []
    recomputeSdlIds = False
    newPads: list[str] = []
    for playercontroller, pad in sorted(playersControllers.items()):
        if (device := deviceList.get(pad.device_path)) is not None and device["isWheel"] and "wheel_rotation" in device:
            ra = int(device["wheel_rotation"])
            wanted_ra = ra
            wanted_deadzone = 0
            wanted_midzone  = 0

            # initialize values with games metadata
            if "wheel_rotation" in metadata:
                wanted_ra = int(metadata["wheel_rotation"])
            if "wheel_deadzone" in metadata:
                wanted_deadzone = int(metadata["wheel_deadzone"])
            if "wheel_midzone" in metadata:
                wanted_midzone = int(metadata["wheel_midzone"])

            # override with user configs
            if "wheel_rotation" in system.config:
                wanted_ra = int(system.config["wheel_rotation"])
            if "wheel_deadzone" in system.config:
                wanted_deadzone = int(system.config["wheel_deadzone"])
            if "wheel_midzone" in system.config:
                wanted_midzone = int(system.config["wheel_midzone"])

            eslog.info("wheel rotation angle is " + str(ra) + " ; wanted wheel rotation angle is " + str(wanted_ra) + " ; wanted deadzone is " + str(wanted_deadzone) + " ; wanted midzone is " + str(wanted_midzone))
            # no need new device in some cases
            if wanted_ra < ra or wanted_deadzone > 0:
                (newdev, p) = reconfigureAngleRotation(pad.device_path, int(pad.inputs["joystick1left"].id), ra, wanted_ra, wanted_deadzone, wanted_midzone)
                if newdev is not None:
                    eslog.info(f"replacing device {pad.device_path} by device {newdev} for player {playercontroller}")
                    deviceList[newdev] = device.copy()
                    deviceList[newdev]["eventId"] = controllersConfig.dev2int(newdev)
                    pad.physical_device_path = pad.device_path # save the physical device for ffb
                    pad.device_path = newdev # needs to recompute sdl ids
                    recomputeSdlIds = True
                    newPads.append(newdev)
                    procs.append(p)

    # recompute sdl ids
    if recomputeSdlIds:
        # build the new joystick list
        joysticks: dict[int, dict[str, str]] = {}
        for node in deviceList:
            if deviceList[node]["isJoystick"]:
                joysticks[deviceList[node]["eventId"]] = { "node": node }
        # add the new devices
        for p in newPads:
            matches = re.match(r"^/dev/input/event([0-9]*)$", str(p))
            if matches != None:
                joysticks[int(matches.group(1))] = { "node": p }
        # find new sdl numeration
        joysticksByDev: dict[str, int] = {}
        for currentId, (_, x) in enumerate(sorted(joysticks.items())):
            joysticksByDev[x["node"]] = currentId
        # renumeration
        for playercontroller, pad in sorted(playersControllers.items()):
            joystick_index = joysticksByDev.get(pad.device_path)
            if joystick_index is not None:
                playersControllers[playercontroller].index = joystick_index
                deviceList[pad.device_path]["joystick_index"] = joystick_index
        # fill physical_index
        for _, pad in sorted(playersControllers.items()):
            if pad.physical_device_path is not None and pad.physical_device_path in deviceList and "joystick_index" in deviceList[pad.physical_device_path]:
                pad.physical_index = deviceList[pad.physical_device_path]["joystick_index"] # save the physical device for ffb

    # reorder players to priorize wheel pads
    playersControllersNew: ControllerDict = {}
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        if (pad.device_path in deviceList and deviceList[pad.device_path]["isWheel"]) or pad.device_path in newPads:
            playersControllersNew[nplayer] = pad.replace(player_number=nplayer)
            nplayer += 1
    for _, pad in sorted(playersControllers.items()):
        if not ((pad.device_path in deviceList and deviceList[pad.device_path]["isWheel"]) or pad.device_path in newPads):
            playersControllersNew[nplayer] = pad.replace(player_number=nplayer)
            nplayer += 1

    eslog.info("after wheel reconfiguration :")
    for playercontroller, pad in sorted(playersControllersNew.items()):
        eslog.info(f"  {playercontroller}. index:{pad.index!s} dev:{pad.device_path} name:{pad.real_name}")

    return (procs, playersControllersNew, deviceList)

def getWheelsFromDevicesInfos(deviceInfos: DeviceInfoMapping) -> DeviceInfoDict:
    return { key: deviceInfo for key, deviceInfo in deviceInfos.items() if deviceInfo['isWheel']}

def reconfigureAngleRotation(dev: str, wheelAxis: int, rotationAngle: int, wantedRotationAngle: int, wantedDeadzone: int, wantedMidzone: int) -> tuple[str, subprocess.Popen[bytes]] | tuple[None, None]:
    devInfos = evdev.InputDevice(dev)
    caps = devInfos.capabilities()

    absmin = None
    absmax = None
    for v, absinfo in cast(list[tuple[int, evdev.AbsInfo]], caps[evdev.ecodes.EV_ABS]):
        if v == wheelAxis:
            absmin = absinfo.min
            absmax = absinfo.max

    if absmin is None or absmax is None:
        eslog.warning("unable to get min/max of " + dev)
        return (None, None)

    totalRange = absmax - absmin
    newmin = absmin
    newmax = absmax
    if wantedRotationAngle < rotationAngle:
        newRange = math.floor(totalRange * wantedRotationAngle / rotationAngle)
        newmin = absmin + math.ceil((totalRange - newRange) / 2)
        newmax = absmax - math.floor((totalRange - newRange) / 2)

    newdz = 0
    if wantedDeadzone > 0 and wantedDeadzone > wantedMidzone:
        newdz = math.floor(totalRange * wantedDeadzone / rotationAngle)
        newmin -= newdz // 2
        newmax += newdz // 2

    newmz = 0
    if wantedMidzone > 0:
        newmz = math.floor(totalRange * wantedMidzone / rotationAngle)
        newmin += newmz // 2
        newmax -= newmz // 2

    pipeout, pipein = os.pipe()
    cmd = ["batocera-wheel-calibrator", "-d", dev, "-a", str(wheelAxis), "-m", str(newmin), "-M", str(newmax), "-z", str(newdz), "-c", str(newmz)]
    eslog.info(cmd)
    proc = subprocess.Popen(cmd, stdout=pipein, stderr=subprocess.PIPE)
    try:
        fd = os.fdopen(pipeout)
        newdev = fd.readline().rstrip('\n')
        fd.close()
    except:
        os.kill(proc.pid, signal.SIGTERM)
        out, err = proc.communicate()
        raise

    return (newdev, proc)

def resetControllers(wheelProcesses: Iterable[subprocess.Popen[bytes]]) -> None:
    for p in wheelProcesses:
        eslog.info(f"killing wheel process {p.pid}")
        os.kill(p.pid, signal.SIGTERM)
        out, err = p.communicate()
