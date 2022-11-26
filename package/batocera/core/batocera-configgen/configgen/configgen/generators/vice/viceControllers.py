#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from Emulator import Emulator
import configparser
from utils.logger import get_logger

eslog = get_logger(__name__)

viceJoystick = {
            "up":               "0 1 # 1 1 1",
            "down":             "0 1 # 1 1 2",
            "left":             "0 1 # 1 1 4",
            "right":            "0 1 # 1 1 8",
            "select":           "0 1 # 5 Virtual keyboard",
            "start":            "0 1 # 4",      # Main menu
            "hotkey":           "0 1 # 5 Quit emulator",
            "a":                "0 1 # 2 7 4",  # Space
            "b":                "0 1 # 1 1 16", # Fire button
            "x":                "0 1 # 2 4 7",  # N
            "y":                "0 1 # 2 3 1",  # Y
            "pagedown":         "0 1 # 2 0 1",  # Enter
            "pageup":           "0 1 # 2 7 7", # Run/stop
        }

# Create the controller configuration file
def generateControllerConfig(viceConfigFile, playersControllers):
    # vjm file
    viceFile = viceConfigFile + "/sdl-joymap.vjm"
                
    if not os.path.exists(os.path.dirname(viceFile)):
        os.makedirs(os.path.dirname(viceFile))

    listVice = [];
    nplayer = 1
    listVice = [];
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer == 1:    
            listVice.append("!CLEAR")
            # joystick 1 right
            listVice.append("0 0 0 1 1 8")
            # joystick 1 left
            listVice.append("0 0 1 1 1 4")
            # joystick 1 down
            listVice.append("0 0 2 1 1 2")
            # joystick 1 up
            listVice.append("0 0 3 1 1 1")

            # hat 1 right
            listVice.append("0 2 0 1 1 1")
            # hat 1 left
            listVice.append("0 2 1 1 1 2")
            # hat 1 down
            listVice.append("0 2 2 1 1 4")
            # hat 1 up
            listVice.append("0 2 3 1 1 8")
        
        # more logic for controllers with fewer configured buttons
        for x in pad.inputs:
            input = pad.inputs[x]
            for indexName, indexValue in viceJoystick.items():
                if indexName == input.name:
                    eslog.debug(f"*** indexName = {indexName}, input.name = {input.name} ***")
                    listVice.append(indexValue.replace('#', pad.inputs[indexName].id, 1))
        nplayer += 1

    f = open(viceFile, 'w')
    for i in range(len(listVice)):
        f.write(str(listVice[i]) + "\n")
    f.write
    f.close()
