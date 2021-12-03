#!/usr/bin/env python
import os
import sys
import batoceraFiles
import re
import time
import subprocess
import json
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

def getCurrentAspectRatio():
    proc = subprocess.Popen(["batocera-resolution currentAspectRatio"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    val = out.decode().strip("\n")
    return val

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
