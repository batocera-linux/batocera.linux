#!/usr/bin/env python

import controllersConfig
from utils.logger import get_logger
eslog = get_logger(__name__)

wheelMapping = {
    "wheel":      "joystick1left",
    "accelerate": "r2",
    "brake":      "l2"
}

# partial mapping between real pads buttons and batocera pads
emulatorMapping = {
    "dreamcast": {
        "lt": "l2",
        "rt": "r2"
    },
    "gamecube": {
        "lt": "l2",
        "rt": "r2",
        "a":  "a",
        "b":  "b",
        "x":  "x",
        "y":  "y"
    },
    "ps2": {
        "cross":    "b",
        "square":   "y",
        "round":    "a",
        "triangle": "x"
    }
}

def reconfigureControllers(playersControllers, system, rom, deviceList):
    eslog.info("wheels reconfiguration");
    wheelsmetadata = None

    # no need to sort, but i like keeping the same loop (sorted by players)
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if pad.dev in deviceList:
            if deviceList[pad.dev]["isWheel"]:
                eslog.info("Wheel reconfiguration for pad {}".format(pad.realName))
                originalInputs = pad.inputs.copy()

                # read metadata if not already done
                if wheelsmetadata is None:
                    wheelsmetadata = controllersConfig.getGameWheelsMetaData(system.name, rom)

                # erase target keys
                for md in wheelsmetadata:
                    if md in wheelMapping:
                        if system.name in emulatorMapping and wheelsmetadata[md] in emulatorMapping[system.name]:
                            wheelkey  = wheelMapping[md]
                            if wheelkey in playersControllers[playercontroller].inputs:
                                del playersControllers[playercontroller].inputs[wheelkey]
                                eslog.info("wheel: erase the key {}".format(wheelkey))

                # fill with the wanted keys
                for md in wheelsmetadata:
                    if md in wheelMapping:
                        if system.name in emulatorMapping and wheelsmetadata[md] in emulatorMapping[system.name]:
                            wheelkey  = wheelMapping[md]
                            wantedkey = emulatorMapping[system.name][wheelsmetadata[md]]

                            if wheelkey in originalInputs:
                                playersControllers[playercontroller].inputs[wantedkey] = originalInputs[wheelkey]
                                playersControllers[playercontroller].inputs[wantedkey].name = wantedkey
                                eslog.info("wheel: fill key {} with {}".format(wantedkey, wheelkey))
                            else:
                                eslog.info("wheel: unable to replace {} with {}".format(wantedkey, wheelkey))
        nplayer += 1
    return playersControllers

def getWheelsFromDevicesInfos(deviceInfos):
    res = {}
    for x in deviceInfos:
        if deviceInfos[x]["isWheel"]:
            res[x] = deviceInfos[x]
    return res
