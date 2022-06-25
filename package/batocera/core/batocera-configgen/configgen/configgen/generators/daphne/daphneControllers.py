#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from Emulator import Emulator
import configparser

daphneKeyboard = {
                    "KEY_UP":           "SDLK_UP 0",
                    "KEY_DOWN":         "SDLK_DOWN 0",
                    "KEY_LEFT":         "SDLK_LEFT 0",
                    "KEY_RIGHT":        "SDLK_RIGHT 0",
                    "KEY_COIN1":        "SDLK_5 0",
                    "KEY_COIN2":        "SDLK_6 0",
                    "KEY_START1":       "SDLK_1 0",
                    "KEY_START2":       "SDLK_2 0",
                    "KEY_BUTTON1":      "SDLK_LCTRL 0",
                    "KEY_BUTTON2":      "SDLK_LALT 0",
                    "KEY_BUTTON3":      "SDLK_SPACE 0",
                    "KEY_SKILL1":       "SDLK_LSHIFT 0",
                    "KEY_SKILL2":       "SDLK_z 0",
                    "KEY_SKILL3":       "SDLK_x 0",
                    "KEY_SERVICE":      "SDLK_9 0",
                    "KEY_TEST":         "SDLK_F2 0",
                    "KEY_RESET":        "SDLK_0 0",
                    "KEY_SCREENSHOT":   "SDLK_F12 0",
                    "KEY_QUIT":         "SDLK_ESCAPE 0",
                    "KEY_PAUSE":        "SDLK_p 0",
                    "KEY_CONSOLE":      "SDLK_BACKSLASH 0",
                    "KEY_TILT":         "SDLK_t 0"
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
