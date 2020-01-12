#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from Emulator import Emulator
import ConfigParser

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

# Create the controller configuration file
def generateControllerConfig(daphneConfigFile, playersControllers):
    # ini file
    daphneConfig = ConfigParser.RawConfigParser()
    if os.path.exists(daphneConfigFile):
        daphneConfig.read(daphneConfigFile)

    # layout section
    if not daphneConfig.has_section("KEYBOARD"):
        daphneConfig.add_section("KEYBOARD")








    # update the configuration file
    if not os.path.exists(os.path.dirname(daphneConfigFile)):
        os.makedirs(os.path.dirname(daphneConfigFile))
    with open(daphneConfigFile, 'w') as configfile:
        daphneConfig.write(configfile)