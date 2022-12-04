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

def setupRatpoisonFrames(orientation, splitSize, subCount, reverseScreens):
    ratpoisonCommands = []
    mainRes = {}
    subRes = []
    splitFrames = []

    screenRes = getCurrentResolution()
    if orientation == 'vert':
        mainRes['width'] = screenRes['width'] * splitSize
        mainRes['height'] = screenRes['height']
        currentFrame = 1
        for app in range(0, subCount):
            subRes.append({})
            subRes[app]['width'] = screenRes['width'] - mainRes['width']
            subRes[app]['height'] = int(screenRes['height'] / subCount)
            subRes[app]['x'] = mainRes['width']
            subRes[app]['y'] = subRes[app]['height'] * (currentFrame - 1)
            subRes[app]['frame'] = currentFrame
            currentFrame = currentFrame + 1
    elif orientation == 'horiz':
        mainRes['width'] = screenRes['width']
        mainRes['height'] = screenRes['height'] * splitSize
        currentFrame = 1
        for app in range(0, subCount):
            subRes.append({})
            subRes[app]['width'] = int(screenRes['width'] / subCount)
            subRes[app]['height'] = screenRes['height'] - mainRes['height']
            subRes[app]['x'] = subRes[app]['width'] * (currentFrame - 1)
            subRes[app]['y'] = mainRes['height']
            subRes[app]['frame'] = currentFrame
            currentFrame = currentFrame + 1
    elif orientation == 'even':
        if subCount == 2:
            mainRes['width'] = screenRes['width']
            mainRes['height'] = int(screenRes['height'] / 2)
            subRes[0]['width'] = screenRes['width']
            subRes[0]['height'] = int(screenRes['height'] / 2)
            subRes[0]['x'] = 0
            subRes[0]['y'] = subRes[subApp[0]]['height']
            subRes[0]['frame'] = 1
        elif subCount == 2:
            mainRes['width'] = int(screenRes['width'] / 2)
            mainRes['height'] = int(screenRes['height'] / 2)
            subRes[0]['width'] = int(screenRes['width'] / 2)
            subRes[0]['height'] = int(screenRes['height'] / 2)
            subRes[0]['x'] = int(screenRes['width'] / 2)
            subRes[0]['y'] = 0
            subRes[0]['frame'] = 1
            subRes[1]['width'] = screenRes['width']
            subRes[1]['height'] = int(screenRes['height'] / 2)
            subRes[1]['x'] = 0
            subRes[1]['y'] = subRes[subApp[1]]['height']
            subRes[1]['frame'] = 2
        elif subCount == 3:
            mainRes['width'] = int(screenRes['width'] / 2)
            mainRes['height'] = int(screenRes['height'] / 2)
            subRes[0]['width'] = int(screenRes['width'] / 2)
            subRes[0]['height'] = int(screenRes['height'] / 2)
            subRes[0]['x'] = int(screenRes['width'] / 2)
            subRes[0]['y'] = 0
            subRes[0]['frame'] = 1
            subRes[1]['width'] = int(screenRes['width'] / 2)
            subRes[1]['height'] = int(screenRes['height'] / 2)
            subRes[1]['x'] = 0
            subRes[1]['y'] = subRes[subApp[0]]['height']
            subRes[1]['frame'] = 2
            subRes[2]['width'] = int(screenRes['width'] / 2)
            subRes[2]['height'] = int(screenRes['height'] / 2)
            subRes[2]['x'] = subRes[subApp[2]]['width']
            subRes[2]['y'] = subRes[subApp[2]]['height']
            subRes[2]['frame'] = 3
    elif orientation == 'offscreen':
        mainRes['width'] = screenRes['width']
        mainRes['height'] = screenRes['height']
        currentFrame = 1
        for app in range(0, subCount):
            subRes.append({})
            subRes[app]['width'] = screenRes['width']
            subRes[app]['height'] = screenRes['height']
            subRes[app]['x'] = 0
            subRes[app]['y'] = screenRes['height'] + 1
            subRes[app]['frame'] = currentFrame
            currentFrame = currentFrame + 1

    if reverseScreens:
        mainFrame = 1
    else:
        mainFrame = 0
    splitFrames.append({})
    splitFrames[0] = f"(frame :number {mainFrame} :x 0 :y 0 :width {mainRes['width']} :height {mainRes['height']} :screenw {screenRes['width']} :screenh {screenRes['height']} :window 0 :last-access 0 :dedicated 1)"
    currentFrame = 1
    for subFrame in subRes:
        splitFrames.append({})
        if reverseScreens and subFrame['frame'] == 1:
            useFrame = 0
        else:
            useFrame = subFrame['frame']
        splitFrames[currentFrame] = f"(frame :number {useFrame} :x {subFrame['x']} :y {subFrame['y']} :width {subFrame['width']} :height {subFrame['height']} :screenw {screenRes['width']} :screenh {screenRes['height']} :window 0 :last-access {subFrame['frame']} :dedicated 1)"
        currentFrame = currentFrame + 1
    # Dummy frame
    splitFrames.append({})
    splitFrames[currentFrame] = f"(frame :number {currentFrame} :x {screenRes['width'] + 1} :y {screenRes['height'] + 1} :width 1 :height 1 :screenw {screenRes['width']} :screenh {screenRes['height']} :window 0 :last-access {currentFrame} :dedicated 0)"
    newFrameset = ",".join(splitFrames)

    ratpoisonCommands += [ f'setenv frameset {getFrameset()}', 'unmanage emulationstation', \
        'addhook deletewindow exec batocera-ratpoison reset', 'set winname title', 'unmanage Select e-Reader Cards' ]
    if reverseScreens:
        ratpoisonCommands += [ 'addhook newwindow focusprev' ]
    else:
        ratpoisonCommands += [ 'addhook newwindow focus' ]
    ratpoisonCommands += [ f'frestore {newFrameset}', 'fselect 0' ]

    runRatpoisonCommands(ratpoisonCommands)

def runRatpoisonCommands(commandList):
    for command in commandList:
        eslog.debug(f'Running: ratpoison -c "{command}"')
        subprocess.call(f'LC_ALL=C ratpoison -c "{command}"', shell=True)

def getFrameset():
    try:
        tempVar = subprocess.check_output('LC_ALL=C ratpoison -c fdump', shell=True).decode(sys.stdout.encoding)
    except:
        eslog.debug('Reading current frame dump failed, generating generic one.')
        screenRes = getCurrentResolution()
        tempVar = f"(frame :number 0 :x 0 :y 0 :width {screenRes['width']} :height {screenRes['height']} :screenw {screenRes['width']} :screenh {screenRes['height']} :window {getAppID()} :last-access 0 :dedicated 0)"
        if not "number 0" in tempVar:
            eslog.debug('Frame dump appears wrong, generating generic one.')
            screenRes = getCurrentResolution()
            tempVar = f"(frame :number 0 :x 0 :y 0 :width {screenRes['width']} :height {screenRes['height']} :screenw {screenRes['width']} :screenh {screenRes['height']} :window {getAppID()} :last-access 0 :dedicated 0)"
    return tempVar.strip()

def getAppID():
    try:
        tempVar = subprocess.check_output('LC_ALL=C ratpoison -c "windows %i"', shell=True).decode(sys.stdout.encoding)
    except:
        eslog.debug('Reading application ID failed.')
        tempVar = "0"
    return tempVar