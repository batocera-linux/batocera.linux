#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from Emulator import Emulator
import ConfigParser

viceJoystick = [
                    "!CLEAR",

                    "# analog left",
                    "# right",
                    "0 0 0 1 1 8",
                    "# left",
                    "0 0 1 1 1 4",
                    "# down",
                    "0 0 2 1 1 2",
                    "# up",
                    "0 0 3 1 1 1",

                    "# analog right",
                    "# right",
                    "0 0 6 1 1 8",
                    "# left",
                    "0 0 7 1 1 4",
                    "# down",
                    "0 0 8 2 0 7",
                    "# up",
                    "0 0 9 2 0 7",

                    "# DPad"
                    "# up",
                    "0 1 13 1 1 1",
                    "# down",
                    "0 1 14 1 1 2",
                    "# left",
                    "0 1 15 1 1 4",
                    "# right",
                    "0 1 16 1 1 8",

                    "# select",
                    "0 1 8 5 Virtual keyboard",
                    "# start",
                    "0 1 9 4",
                    "# hotkey",
                    "0 1 10 5 Quit emulator",

                    "# L1 -> fire",
                    "0 1 4 1 1 16 ",
                    "# R1 -> return",
                    "0 1 5 2 0 1",

                    "# L2 -> fire",
                    "0 1 6 1 1 16",
                    "# R2 -> fire",
                    "0 1 7 1 1 16",

                    "# L3 -> N",
                    "0 1 11 2 4 7",
                    "# R3 -> Y",
                    "0 1 12 2 3 1"
                ]

# Create the controller configuration file
def generateControllerConfig(viceConfigFile, system):
    # vjm file
    viceFile = viceConfigFile + "/sdl-joymap.vjm"
                
    if not os.path.exists(os.path.dirname(viceFile)):
        os.makedirs(os.path.dirname(viceFile))

    f = open(viceFile, 'w')
    for i in range(len(viceJoystick)):
        f.write(str(viceJoystick[i]) + "\n")
    f.write
    f.close()
