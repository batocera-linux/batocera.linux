#!/usr/bin/env python

import controllersConfig
import evdev
import subprocess
import os
import signal
import re
import math

from utils.logger import get_logger
eslog = get_logger(__name__)

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

def reconfigureControllers(playersControllers, system, rom, metadata, deviceList):
    eslog.info("wheels reconfiguration");
    wheelsmetadata = None

    eslog.info("before wheel reconfiguration :")
    for playercontroller, pad in sorted(playersControllers.items()):
        eslog.info("  {}. index:{} dev:{} name:{}".format(playercontroller, str(pad.index), pad.dev,pad.realName))

    # reconfigure wheel buttons
    # no need to sort, but i like keeping the same loop (sorted by players)
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if pad.dev in deviceList:
            if deviceList[pad.dev]["isWheel"]:
                eslog.info("Wheel reconfiguration for pad {}".format(pad.realName))
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
                                    eslog.info("wheel: erase the key {}".format(wheelkey))

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
                                    eslog.info("wheel: fill key {} with {}".format(wantedkey, wheelkey))
                                else:
                                    eslog.info("wheel: unable to replace {} with {}".format(wantedkey, wheelkey))
        nplayer += 1

    # reconfigure wheel min/max/deadzone
    procs = []
    recomputeSdlIds = False
    newPads = []
    for playercontroller, pad in sorted(playersControllers.items()):
        if pad.dev in deviceList and deviceList[pad.dev]["isWheel"] and "wheel_rotation" in deviceList[pad.dev]:
            ra = int(deviceList[pad.dev]["wheel_rotation"])
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
                (newdev, p) = reconfigureAngleRotation(pad.dev, int(pad.inputs["joystick1left"].id), ra, wanted_ra, wanted_deadzone, wanted_midzone)
                if newdev is not None:
                    eslog.info("replacing device {} by device {} for player {}".format(pad.dev, newdev, playercontroller))
                    deviceList[newdev] = dict(deviceList[pad.dev])
                    deviceList[newdev]["eventId"] = controllersConfig.dev2int(newdev)
                    pad.physdev = pad.dev # save the physical device for ffb
                    pad.dev = newdev # needs to recompute sdl ids
                    recomputeSdlIds = True
                    newPads.append(newdev)
                    procs.append(p)

    # recompute sdl ids
    if recomputeSdlIds:
        # build the new joystick list
        joysticks = {}
        for node in deviceList:
            if deviceList[node]["isJoystick"]:
                joysticks[deviceList[node]["eventId"]] = { "node": node }
        # add the new devices
        for p in newPads:
            matches = re.match(r"^/dev/input/event([0-9]*)$", str(p))
            if matches != None:
                joysticks[int(matches.group(1))] = { "node": p }
        # find new sdl numeration
        joysticksByDev = {}
        currentId = 0
        for e, x in sorted(joysticks.items()):
            joysticksByDev[joysticks[e]["node"]] = currentId
            currentId += 1
        # renumeration
        for playercontroller, pad in sorted(playersControllers.items()):
            if pad.dev in joysticksByDev:
                playersControllers[playercontroller].index = joysticksByDev[pad.dev]
                deviceList[pad.dev]["joystick_index"] = joysticksByDev[pad.dev]
        # fill physid
        for playercontroller, pad in sorted(playersControllers.items()):
            if hasattr(pad, 'physdev') and pad.physdev in deviceList and "joystick_index" in deviceList[pad.physdev]:
                pad.physid = deviceList[pad.physdev]["joystick_index"] # save the physical device for ffb

    # reorder players to priorize wheel pads
    playersControllersNew = {}
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if (pad.dev in deviceList and deviceList[pad.dev]["isWheel"]) or pad.dev in newPads:
            pad.player = str(nplayer)
            playersControllersNew[str(nplayer)] = pad
            nplayer += 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if not ((pad.dev in deviceList and deviceList[pad.dev]["isWheel"]) or pad.dev in newPads):
            pad.player = str(nplayer)
            playersControllersNew[str(nplayer)] = pad
            nplayer += 1

    eslog.info("after wheel reconfiguration :")
    for playercontroller, pad in sorted(playersControllersNew.items()):
        eslog.info("  {}. index:{} dev:{} name:{}".format(playercontroller, str(pad.index), pad.dev,pad.realName))

    return (procs, playersControllersNew, deviceList)

def getWheelsFromDevicesInfos(deviceInfos):
    res = {}
    for x in deviceInfos:
        if deviceInfos[x]["isWheel"]:
            res[x] = deviceInfos[x]
    return res

def reconfigureAngleRotation(dev, wheelAxis, rotationAngle, wantedRotationAngle, wantedDeadzone, wantedMidzone):
    devInfos = evdev.InputDevice(dev)
    caps = devInfos.capabilities()

    absmin = None
    absmax = None
    for v, absinfo in caps[evdev.ecodes.EV_ABS]:
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

def resetControllers(wheelProcesses):
    for p in wheelProcesses:
        eslog.info("killing wheel process {}".format(p.pid))
        os.kill(p.pid, signal.SIGTERM)
        out, err = p.communicate()
