#!/usr/bin/env python

from __future__ import annotations

import logging
from os import environ
from struct import pack, unpack
from typing import TYPE_CHECKING, Any

from configgen.utils.logger import setup_logging

from .dolphinPaths import DOLPHIN_SAVES

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import Resolution


eslog = logging.getLogger(__name__)

def readBEInt16(f):
    bytes = f.read(2)
    unpacked = unpack(">H", bytes)
    return unpacked[0]

def readBEInt32(f):
    bytes = f.read(4)
    unpacked = unpack(">L", bytes)
    return unpacked[0]

def readBEInt64(f):
    bytes = f.read(8)
    unpacked = unpack(">Q", bytes)
    return unpacked[0]

def readBytes(f, x):
    return f.read(x)

def readString(f, x):
    bytes = f.read(x)
    decodedbytes = bytes.decode('utf-8')
    return str(decodedbytes)

def readInt8(f):
    bytes = f.read(1)
    unpacked = unpack("b", bytes)
    return unpacked[0]

def writeInt8(f, x):
    bytes = pack("b", x)
    f.write(bytes)

def readWriteEntry(f, setval):
    itemHeader     = readInt8(f)
    itemType       = (itemHeader & 0xe0) >> 5
    itemNameLength = (itemHeader & 0x1f) + 1
    itemName       = readString(f, itemNameLength)

    if itemName in setval:
        if itemType == 3: # byte
            itemValue = setval[itemName]
            writeInt8(f, itemValue)
        else:
            raise Exception(f"not writable type {itemType}")
    else:
        if itemType == 1: # big array
            dataSize = readBEInt16(f) + 1
            readBytes(f, dataSize)
            itemValue = "[Big Array]"
        elif itemType == 2: # small array
            dataSize = readInt8(f) + 1
            readBytes(f, dataSize)
            itemValue = "[Small Array]"
        elif itemType == 3: # byte
            itemValue = readInt8(f)
        elif itemType == 4: # short
            itemValue = readBEInt16(f)
        elif itemType == 5: # long
            itemValue = readBEInt32(f)
        elif itemType == 6: # long long
            itemValue = readBEInt64(f)
        elif itemType == 7: # bool
            itemValue = readInt8(f)
        else:
            raise Exception(f"unknown type {itemType}")

    if not setval or itemName in setval:
        eslog.debug(f'{itemName:12s} = {itemValue}')

def readWriteFile(filepath: Path, setval):
    # open in read read/write depending of the action
    if not setval:
        f = filepath.open("rb")
    else:
        f = filepath.open("r+b")

    try:
        version    = readString(f, 4) # read SCv0
        numEntries = readBEInt16(f)   # num entries
        offsetSize = (numEntries+1)*2 # offsets
        readBytes(f, offsetSize)

        for i in range(0, numEntries): # entries
            readWriteEntry(f, setval)
    finally:
        f.close()

def getWiiLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "jp_JP": 0, "en_US": 1, "de_DE": 2,
                           "fr_FR": 3, "es_ES": 4, "it_IT": 5,
                           "nl_NL": 6, "zh_CN": 7, "zh_TW": 8, "ko_KR": 9 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]

def getRatioFromConfig(config, gameResolution):
    # Sets the setting available to the Wii's internal NAND. Only has two values:
    # 0: 4:3 ; 1: 16:9
    if "tv_mode" in config:
        if config["tv_mode"] == "1":
            return 1
        else:
            return 0
    else:
        return 0

def getSensorBarPosition(config):
    # Sets the setting available to the Wii's internal NAND. Only has two values:
    # 0: BOTTOM ; 1: TOP
    if "sensorbar_position" in config:
        if config["sensorbar_position"] == "1":
            return 1
        else:
            return 0
    else:
        return 0

def update(config: dict[str, Any], filepath: Path, gameResolution: Resolution) -> None:
    arg_setval = {
        "IPL.LNG": getWiiLangFromEnvironment(),
        "IPL.AR": getRatioFromConfig(config, gameResolution),
        "BT.BAR": getSensorBarPosition(config)
    }
    readWriteFile(filepath, arg_setval)

if __name__ == '__main__':
    with setup_logging():
        readWriteFile(DOLPHIN_SAVES / "Wii" / "shared2" / "sys" / "SYSCONF", {})
