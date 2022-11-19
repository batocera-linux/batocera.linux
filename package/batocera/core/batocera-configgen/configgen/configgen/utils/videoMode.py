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
        cmd = f"batocera-resolution setMode \"{videomode}\""
        if cmd is not None:
            eslog.debug(f"setVideoMode({videomode}): {cmd} ")
            os.system(cmd)

def getCurrentMode():
    proc = subprocess.Popen(["batocera-resolution currentMode"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

def minTomaxResolution():
    proc = subprocess.Popen(["batocera-resolution minTomaxResolution"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def getCurrentResolution():
    proc = subprocess.Popen(["batocera-resolution currentResolution"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    vals = out.decode().split("x")
    return { "width": int(vals[0]), "height": int(vals[1]) }

def getDisplayMode():
    proc = subprocess.Popen(["batocera-resolution getDisplayMode"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode().strip()

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
        cmd = "unclutter-remote -s"
    else:
        cmd = "unclutter-remote -h"
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

def setupRatpoisonFrames(orientation, splitSize, subFrames):
    ratpoisonCommands = []

    # Switch away from ES
    ratpoisonCommands += [ 'switchtodesktop1' ]
    # Start slicing the screen into frames
    # Large window on left, vertical stack on right
    if orientation == "vert":
        ratpoisonCommands += [ f'hsplit {splitSize}' ]
        if subFrames > 1:
            ratpoisonCommands += [ 'next' ]
            for frame in range(subFrames, 1, -1):
                ratpoisonCommands += [ f'vsplit 1/{str(f)}', 'next' ]
    # Large window on top, horizontal row on the bottom
    elif orientation == "horiz":
        ratpoisonCommands += [ f'vsplit {splitSize}' ]
        if subFrames > 1:
            ratpoisonCommands += [ 'next' ]
            for frame in range(subFrames, 1, -1):
                ratpoisonCommands += [ f'hsplit 1/{str(f)}', 'next' ]
    # Classic split screen - 2P = P1 top, P2 bottom, 3/4P = P1/P2 top, P3/P4 bottom
    # 3P will be centered on the bottom if only 3 players
    elif orientation == "even":
        if subFrames == 1:
            ratpoisonCommands += [ 'vsplit 1/2' ]
        elif subFrames > 1:
            ratpoisonCommands += [ 'vsplit 1/2', 'hsplit 1/2', 'number 2 3' ]
            if subframes == 3:
                ratpoisonCommands += [ 'fselect 3', 'hsplit 1/2' ]

    # Reselect the first frame and set hooks for events
    ratpoisonCommands += [ 'fselect 1', 'addhook newwindow next', 'addhook deletewindow "execa ratpoison-reset"' ]

    # Run the commands (split into another function so it can be called from elsewhere if needed)
    runRatpoisonCommands(ratpoisonCommands)

def runRatpoisonCommands(commandList):
    for command in commandList:
        subprocess.call(f'LC_ALL=C ratpoison -c "{command}"', shell=True)