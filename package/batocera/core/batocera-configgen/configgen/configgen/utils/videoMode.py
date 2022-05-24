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
        cmd = "batocera-resolution setMode \"{}\"".format(videomode)
        if cmd is not None:
            eslog.debug("setVideoMode({}): {} ".format(videomode, cmd))
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

def isResolutionReversed():
    return os.path.exists("/var/run/rk-rotation")

def checkModeExists(videomode):
    proc = subprocess.Popen(["batocera-resolution listModes"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for valmod in out.decode().splitlines():
        vals = valmod.split(":")
        if(videomode == vals[0]):
            return True
    eslog.error("invalid video mode {}".format(videomode))
    return False

def changeMouse(mode):
    eslog.debug("changeMouseMode({})".format(mode))
    if mode:
        cmd = "unclutter-remote -s"
    else:
        cmd = "unclutter-remote -h"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def getGLVersion():
    try:
        glxVerCmd = 'glxinfo | grep "OpenGL version"'
        glVerOutput = subprocess.check_output(glxVerCmd, shell=True).decode(sys.stdout.encoding)
        glVerString = glVerOutput.split()
        glVersion = float(glVerString[3])
        return glVersion
    except:
        return 0

def getGLVendor():
    try:
        glxVendCmd = 'glxinfo | grep "OpenGL vendor string"'
        glVendOutput = subprocess.check_output(glxVendCmd, shell=True).decode(sys.stdout.encoding)
        glVendString = glVendOutput.split()
        glVendor = glVendString[3].casefold()
        return glVendor
    except:
        return "unknown"

def getGameSpecial(systemName, rom, retroarch):
    # Returns an ID for games that need rotated bezels/shaders or have special art
    # Vectrex will actually return an abbreviated game name for overlays, all others will return 0, 90, or 270 for rotation angle
    # 0 will be ignored.
    # Currently in use with bezels & libretro shaders
    if not retroarch:
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
