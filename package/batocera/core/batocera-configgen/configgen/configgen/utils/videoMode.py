#!/usr/bin/env python
import os
import sys
import batoceraFiles
import re
import time
import subprocess
import json
import csv
from .logger import get_logger

eslog = get_logger(__name__)

# Set a specific video mode
def changeMode(videomode):
    if checkModeExists(videomode):
        cmd = ["batocera-resolution", "setMode", videomode]
        eslog.debug(f"setVideoMode({videomode}): {cmd}")
        max_tries = 2  # maximum number of tries to set the mode
        for i in range(max_tries):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                eslog.debug(result.stdout.strip())
                return
            except subprocess.CalledProcessError as e:
                eslog.error(f"Error setting video mode: {e.stderr}")
                if i == max_tries - 1:
                    raise
                time.sleep(1)

def getCurrentMode():
    proc = subprocess.Popen(["batocera-resolution currentMode"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

def getRefreshRate():
    proc = subprocess.Popen(["batocera-resolution refreshRate"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

def getScreensInfos(config):
    outputs = getScreens()
    res = []

    # output 1
    vo1 = getCurrentOutput()
    resolution1 = getCurrentResolution()
    res.append({"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0})

    # output2
    vo2 = None
    # find the configured one
    if "videooutput2" in config and config["videooutput2"] in outputs and config["videooutput2"] != vo1:
        vo2 = config["videooutput2"]
    # find the first one
    for x in outputs:
        if x != vo1 and vo2 is None:
            vo2 = x
    if vo2 is not None:
        resolution2 = getCurrentResolution(vo2)
        res.append({"width": resolution2["width"], "height": resolution2["height"], "x": resolution1["width"], "y": 0})

    # output3
    vo3 = None
    # find the configured one
    if "videooutput3" in config and config["videooutput3"] in outputs and config["videooutput3"] != vo1 and config["videooutput2"] != vo2:
        vo3 = config["videooutput3"]
    # find the first one
    for x in outputs:
        if x != vo1 and x != vo2 and vo3 is None:
            vo3 = x
    if vo3 is not None:
        resolution3 = getCurrentResolution(vo3)
        res.append({"width": resolution3["width"], "height": resolution3["height"], "x": resolution1["width"]+resolution2["width"], "y": 0})

    eslog.debug("Screens:")
    eslog.debug(res)
    return res

def getScreens():    
    proc = subprocess.Popen(["batocera-resolution listOutputs"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode().splitlines()

def minTomaxResolution():
    proc = subprocess.Popen(["batocera-resolution minTomaxResolution"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def getCurrentResolution(name = None):
    if name is None:
        proc = subprocess.Popen(["batocera-resolution currentResolution"], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(["batocera-resolution --screen {} currentResolution".format(name)], stdout=subprocess.PIPE, shell=True)

    (out, err) = proc.communicate()
    vals = out.decode().split("x")
    return { "width": int(vals[0]), "height": int(vals[1]) }

def getCurrentOutput():
    proc = subprocess.Popen(["batocera-resolution currentOutput"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode().strip()

def supportSystemRotation():
    proc = subprocess.Popen(["batocera-resolution supportSystemRotation"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return proc.returncode == 0

def isResolutionReversed():
    return os.path.exists("/var/run/rk-rotation")

def checkModeExists(videomode):
    # max resolution given
    if videomode[0:4] == "max-":
        matches = re.match(r"^max-[0-9]*x[0-9]*$", videomode)
        if matches != None:
            return True

    # specific resolution given
    proc = subprocess.Popen(["batocera-resolution listModes"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for valmod in out.decode().splitlines():
        vals = valmod.split(":")
        if(videomode == vals[0]):
            return True

    eslog.error(f"invalid video mode {videomode}")
    return False

def changeMouse(mode):
    eslog.debug(f"changeMouseMode({mode})")
    if mode:
        cmd = "batocera-mouse show"
    else:
        cmd = "batocera-mouse hide"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def getGLVersion():
    try:
        # optim for most sbc having not glxinfo
        if os.path.exists("/usr/bin/glxinfo") == False:
            return 0

        glxVerCmd = 'glxinfo | grep "OpenGL version"'
        glVerOutput = subprocess.check_output(glxVerCmd, shell=True).decode(sys.stdout.encoding)
        glVerString = glVerOutput.split()
        glVerTemp = glVerString[3].split(".")
        if len(glVerTemp) > 2:
            del glVerTemp[2:]
        glVersion = float('.'.join(glVerTemp))
        return glVersion
    except:
        return 0

def getGLVendor():
    try:
        # optim for most sbc having not glxinfo
        if os.path.exists("/usr/bin/glxinfo") == False:
            return "unknown"

        glxVendCmd = 'glxinfo | grep "OpenGL vendor string"'
        glVendOutput = subprocess.check_output(glxVendCmd, shell=True).decode(sys.stdout.encoding)
        glVendString = glVendOutput.split()
        glVendor = glVendString[3].casefold()
        return glVendor
    except:
        return "unknown"

def getAltDecoration(systemName, rom, emulator):
    # Returns an ID for games that need rotated bezels/shaders or have special art
    # Vectrex will actually return an abbreviated game name for overlays, all others will return 0, 90, or 270 for rotation angle
    # 0 will be ignored.
    # Currently in use with bezels & libretro shaders
    if not emulator in [ 'mame', 'retroarch' ]:
        return "standalone"

    if not systemName in [ 'lynx', 'wswan', 'wswanc', 'mame', 'fbneo', 'naomi', 'atomiswave', 'nds', '3ds', 'vectrex' ]:
        return "0"

    # Look for external file, exit if not set up
    specialFile = '/usr/share/batocera/configgen/data/special/' + systemName + '.csv'
    if not os.path.exists(specialFile):
        return "0"

    romBasename = os.path.basename(rom)
    romName = os.path.splitext(romBasename)[0]
    romCompare = romName.casefold()

    # Load the file, read it in
    # Each file will be a csv with each row being the standard (ie No-Intro) filename, angle of rotation (90 or 270)
    # Case indifferent, rom file name and filenames in list will be folded
    openFile = open(specialFile, 'r')
    with openFile:
        specialList = csv.reader(openFile, delimiter=';')
        for row in specialList:
            if row[0].casefold() == romCompare:
                return str(row[1])

    return "0"
