#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from Emulator import Emulator
import configparser

daphneKeyboard = {
                    "KEY_UP":           "1073741906 0",
                    "KEY_DOWN":         "1073741905 0",
                    "KEY_LEFT":         "1073741904 0",
                    "KEY_RIGHT":        "1073741903 0",
                    "KEY_COIN1":        "53 54",
                    "KEY_COIN2":        "54 53",
                    "KEY_START1":       "49 0",
                    "KEY_START2":       "50 0",
                    "KEY_BUTTON1":      "1073742048 0",
                    "KEY_BUTTON2":      "1073742050 0",
                    "KEY_BUTTON3":      "32 0",
                    "KEY_SKILL1":       "1073742049 0",
                    "KEY_SKILL2":       "122 0",
                    "KEY_SKILL3":       "120 0",
                    "KEY_SERVICE":      "57 0",
                    "KEY_TEST":         "1073741883 0",
                    "KEY_RESET":        "48 0",
                    "KEY_SCREENSHOT":   "1073741893 0",
                    "KEY_QUIT":         "27 0",
                    "KEY_PAUSE":        "112 0",
                    "KEY_CONSOLE":      "92 0",
                    "KEY_TILT":         "116 0"
                }

daphneJoystick = {
                    "KEY_UP":           "up",
                    "KEY_DOWN":         "down",
                    "KEY_LEFT":         "left",
                    "KEY_RIGHT":        "right",
                    "KEY_BUTTON1":      "a",
                    "KEY_BUTTON2":      "b",
                    "KEY_BUTTON3":      "x",
                    "KEY_START1":       "start",
                    "KEY_START2":       "",
                    "KEY_COIN1":        "select",
                    "KEY_COIN2":        "",
                    "KEY_SKILL1":       "",
                    "KEY_SKILL2":       "",
                    "KEY_SKILL3":       "",
                    "KEY_SERVICE":      "",
                    "KEY_TEST":         "",
                    "KEY_RESET":        "",
                    "KEY_SCREENSHOT":   "l2",
                    "KEY_QUIT":         "hotkey",
                    "KEY_PAUSE":        "r2",
                    "KEY_CONSOLE":      "",
                    "KEY_TILT":         ""
                }

# Create the controller configuration file
def generateControllerConfig(daphneConfigFile, playersControllers):
    # ini file
    daphneConfig = configparser.RawConfigParser()
    if os.path.exists(daphneConfigFile):
        daphneConfig.read(daphneConfigFile)

    # layout section
    if not daphneConfig.has_section("KEYBOARD"):
        daphneConfig.add_section("KEYBOARD")

    for indexController in playersControllers:
        controller = playersControllers[indexController]
       
        for indexName, indexValue in daphneKeyboard.items():
            buttonValue = str(0)
            if(daphneJoystick[indexName] != ""):
                buttonName = daphneJoystick[indexName]
                if buttonName in controller.inputs:
                    inputInst = controller.inputs[buttonName]
                    if inputInst.type == 'button':
                        buttonValue = str(int(inputInst.id) + 1)

            daphneConfig.set("KEYBOARD", indexName, indexValue +" "+ buttonValue)

    # update the configuration file
    with open(daphneConfigFile, 'w') as configfile:
        daphneConfig.write(configfile)
