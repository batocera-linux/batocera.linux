from __future__ import annotations

import csv
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ..batoceraPaths import DEFAULTS_DIR
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from ..config import SystemConfig
    from ..types import Resolution, ScreenInfo

_logger = logging.getLogger(__name__)

_ROTATION_FILE: Final = Path("/var/run/rk-rotation")
_GLXINFO_BIN: Final = Path("/usr/bin/glxinfo")

# Set a specific video mode
def changeMode(videomode: str) -> None:
    if checkModeExists(videomode):
        cmd = ["batocera-resolution", "setMode", videomode]
        _logger.debug("setVideoMode(%s): %s", videomode, cmd)
        max_tries = 2  # maximum number of tries to set the mode
        for i in range(max_tries):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                _logger.debug(result.stdout.strip())
                return
            except subprocess.CalledProcessError as e:
                _logger.error("Error setting video mode: %s", e.stderr)
                if i == max_tries - 1:
                    raise BatoceraException("Error setting video mode") from e
                time.sleep(1)

def getCurrentMode() -> str:  # noqa: RET503
    proc = subprocess.Popen(["batocera-resolution currentMode"], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

    if TYPE_CHECKING:
        raise AssertionError("unreachable")

def getRefreshRate() -> str:  # noqa: RET503
    proc = subprocess.Popen(["batocera-resolution refreshRate"], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

    if TYPE_CHECKING:
        raise AssertionError("unreachable")

def getScreensInfos(config: SystemConfig) -> list[ScreenInfo]:
    outputs = getScreens()
    res: list[ScreenInfo] = []

    # output 1
    vo1 = getCurrentOutput()
    resolution1 = getCurrentResolution()
    res.append({"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0})

    # output2
    vo2 = None
    # find the configured one
    if (vo2_config := config.get("videooutput2")) and vo2_config in outputs and vo2_config != vo1:
        vo2 = vo2_config
    # find the first one
    for x in outputs:
        if x != vo1 and vo2 is None:
            vo2 = x
    if vo2 is not None:
        try:
            resolution2 = getCurrentResolution(vo2)
            res.append({"width": resolution2["width"], "height": resolution2["height"], "x": resolution1["width"], "y": 0})
        except Exception:
            pass # ignore bad information

    # output3
    vo3 = None
    # find the configured one
    if (vo3_config := config.get("videooutput3")) and vo3_config in outputs and vo3_config != vo1 and vo3_config != vo2:
        vo3 = vo3_config
    # find the first one
    for x in outputs:
        if x != vo1 and x != vo2 and vo3 is None:
            vo3 = x
    if vo3 is not None:
        try:
            resolution3 = getCurrentResolution(vo3)
            res.append({"width": resolution3["width"], "height": resolution3["height"], "x": resolution1["width"]+resolution2["width"], "y": 0})
        except Exception:
            pass # ignore bad information

    _logger.debug("Screens:")
    _logger.debug(res)
    return res

def getScreens() -> list[str]:
    proc = subprocess.Popen(["batocera-resolution listOutputs"], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()
    return out.decode().splitlines()

def minTomaxResolution() -> None:
    proc = subprocess.Popen(["batocera-resolution minTomaxResolution"], stdout=subprocess.PIPE, shell=True)
    proc.communicate()

def getCurrentResolution(name: str | None = None) -> Resolution:
    if name is None:
        proc = subprocess.Popen(["batocera-resolution currentResolution"], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen([f"batocera-resolution --screen {name} currentResolution"], stdout=subprocess.PIPE, shell=True)

    (out, _) = proc.communicate()
    vals = out.decode().split("x")
    return { "width": int(vals[0]), "height": int(vals[1]) }

def getCurrentOutput() -> str:
    proc = subprocess.Popen(["batocera-resolution currentOutput"], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()
    return out.decode().strip()

def supportSystemRotation() -> bool:
    proc = subprocess.Popen(["batocera-resolution supportSystemRotation"], stdout=subprocess.PIPE, shell=True)
    proc.communicate()
    return proc.returncode == 0

def isResolutionReversed():
    return _ROTATION_FILE.exists()

def checkModeExists(videomode: str) -> bool:
    # max resolution given
    if videomode[0:4] == "max-":
        matches = re.match(r"^max-[0-9]*x[0-9]*$", videomode)
        if matches is not None:
            return True

    # specific resolution given
    proc = subprocess.Popen(["batocera-resolution listModes"], stdout=subprocess.PIPE, shell=True)
    (out, _) = proc.communicate()
    for valmod in out.decode().splitlines():
        vals = valmod.split(":")
        if(videomode == vals[0]):
            return True

    _logger.error("invalid video mode %s", videomode)
    return False

def changeMouse(mode: bool) -> None:
    _logger.debug("changeMouseMode(%s)", mode)
    proc = subprocess.Popen([f"batocera-mouse {'show' if mode else 'hide'}"], stdout=subprocess.PIPE, shell=True)
    proc.communicate()

def getGLVersion() -> float:
    try:
        # optim for most sbc having not glxinfo
        if not _GLXINFO_BIN.exists():
            return 0

        glxVerCmd = 'glxinfo | grep "OpenGL version"'
        glVerOutput = subprocess.check_output(glxVerCmd, shell=True).decode(sys.stdout.encoding)
        glVerString = glVerOutput.split()
        glVerTemp = glVerString[3].split(".")
        if len(glVerTemp) > 2:
            del glVerTemp[2:]
        return float('.'.join(glVerTemp))
    except Exception:
        return 0

def getGLVendor() -> str:
    try:
        # optim for most sbc having not glxinfo
        if not _GLXINFO_BIN.exists():
            return "unknown"

        glxVendCmd = 'glxinfo | grep "OpenGL vendor string"'
        glVendOutput = subprocess.check_output(glxVendCmd, shell=True).decode(sys.stdout.encoding)
        glVendString = glVendOutput.split()
        return glVendString[3].casefold()
    except Exception:
        return "unknown"

def getAltDecoration(systemName: str, rom: str | Path, emulator: str) -> str:
    # Returns an ID for games that need rotated bezels/shaders or have special art
    # Vectrex will actually return an abbreviated game name for overlays, all others will return 0, 90, or 270 for rotation angle
    # 0 will be ignored.
    # Currently in use with bezels & libretro shaders
    if emulator not in [ 'mame', 'retroarch' ]:
        return "standalone"

    if systemName not in [ 'lynx', 'wswan', 'wswanc', 'mame', 'fbneo', 'naomi', 'atomiswave', 'nds', '3ds', 'vectrex' ]:
        return "0"

    # Look for external file, exit if not set up
    specialFile = DEFAULTS_DIR / 'data' / 'special' / f'{systemName}.csv'
    if not specialFile.exists():
        return "0"

    romCompare = Path(rom).stem.casefold()

    # Load the file, read it in
    # Each file will be a csv with each row being the standard (ie No-Intro) filename, angle of rotation (90 or 270)
    # Case indifferent, rom file name and filenames in list will be folded
    openFile = specialFile.open('r')
    with openFile:
        specialList = csv.reader(openFile, delimiter=';')
        for row in specialList:
            if row[0].casefold() == romCompare:
                return str(row[1])

    return "0"
