#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from os import path
import codecs
from Emulator import Emulator
import configparser
import json

cemuConfig  = batoceraFiles.CONF + '/cemu'

# Create the controller configuration file
# First controller will ALWAYS BE A Gamepad
# Additional controllers will either be a Pro Controller or Wiimote
def generateControllerConfig(system, playersControllers, rom):
    # Make controller directory if it doesn't exist
    if not path.isdir(cemuConfig + "/controllerProfiles"):
        os.mkdir(cemuConfig + "/controllerProfiles")

    # Purge old controller files
    for counter in range(0,8):
        configFileName = "{}/{}".format(cemuConfig + "/controllerProfiles/", "controller" + str(counter) +".txt")
        if os.path.isfile(configFileName):
            os.remove(configFileName)


    ## CONTROLLER: Create the config files
    #  We are exporting SDL_GAMECONTROLLERCONFIG in cemuGenerator, so we can assume all controllers are now working with xInput
    nplayer = 0
    for playercontroller, pad in sorted(playersControllers.items()):
        cemuSettings = configparser.ConfigParser(interpolation=None)
        cemuSettings.optionxform = str


        ## [GENERAL]
        if not cemuSettings.has_section("General"):
            cemuSettings.add_section("General")

        cemuSettings.set("General", "api", "XInput")
        cemuSettings.set("General", "controller", str(nplayer))

        # Controller combination type
        wiimote = 0
        if system.isOptSet('controller_combination') and system.config["controller_combination"] != '0':
            if system.config["controller_combination"] == '1':
                if (nplayer == 0):
                    cemuSettings.set("General", "emulate", "Wii U GamePad")
                    addIndex = 0
                else:
                    cemuSettings.set("General", "emulate", "Wiimote")
                    wiimote = 1
            elif system.config["controller_combination"] == '2':
                cemuSettings.set("General", "emulate", "Wii U Pro Controller")
                addIndex = 1
            else:
                cemuSettings.set("General", "emulate", "Wiimote")
                wiimote = 1
        else:
            if (nplayer == 0):
                cemuSettings.set("General", "emulate", "Wii U GamePad")
                addIndex = 0
            else:
                cemuSettings.set("General", "emulate", "Wii U Pro Controller")
                addIndex = 1


        ## [CONTROLLER]
        if not cemuSettings.has_section("Controller"):
            cemuSettings.add_section("Controller")

        # Rumble
        if system.isOptSet("rumble") and system.config["rumble"] == "0":
            cemuSettings.set("Controller", "rumble", "0")
        else:
            cemuSettings.set("Controller", "rumble", "0.5")

        cemuSettings.set("Controller", "leftRange", "1")
        cemuSettings.set("Controller", "rightRange", "1")
        cemuSettings.set("Controller", "leftDeadzone", ".2")
        cemuSettings.set("Controller", "rightDeadzone", ".2")
        cemuSettings.set("Controller", "buttonThreshold", ".5")

        # Wiimote (Assumes a sideways wiimote configuration)
        if wiimote == 1:
            cemuSettings.set("Controller", "1", "button_4")             # A
            cemuSettings.set("Controller", "2", "button_8")             # B
            cemuSettings.set("Controller", "3", "button_1")             # 1
            cemuSettings.set("Controller", "4", "button_2")             # 2
            cemuSettings.set("Controller", "5", "button_800000000")     # C
            cemuSettings.set("Controller", "6", "button_100000000")     # Z
            cemuSettings.set("Controller", "7", "button_40")            # +
            cemuSettings.set("Controller", "8", "button_80")            # -
            cemuSettings.set("Controller", "9", "button_10000000")      # Up (Binds to Left on Controller)
            cemuSettings.set("Controller", "10", "button_20000000")     # Down (Binds to Right on Controller)
            cemuSettings.set("Controller", "11", "button_8000000")      # Left (Binds to Down on Controller)
            cemuSettings.set("Controller", "12", "button_4000000")      # Right (Binds to Up on Controller
            cemuSettings.set("Controller", "13", "button_400000000")    # Nunchuk Up (RStick)
            cemuSettings.set("Controller", "14", "button_10000000000")  # Nunchuk Down (RStick)
            cemuSettings.set("Controller", "15", "button_8000000000")   # Nunchuk Left (RStick)
            cemuSettings.set("Controller", "16", "button_200000000")    # Nunchuk Right (RStick)
            cemuSettings.set("Controller", "17", "0")                   # Home
            cemuSettings.set("Controller", "nunchuck", "1")
            cemuSettings.set("Controller", "motionPlus", "0")
        # Wii U GamePad / Wii U Pro Controller
        else:
            cemuSettings.set("Controller", "1", "button_2")                         # A
            cemuSettings.set("Controller", "2", "button_1")                         # B
            cemuSettings.set("Controller", "3", "button_8")                         # X
            cemuSettings.set("Controller", "4", "button_4")                         # Y
            cemuSettings.set("Controller", "5", "button_10")                        # L
            cemuSettings.set("Controller", "6", "button_20")                        # R
            cemuSettings.set("Controller", "7", "button_100000000")                 # L2
            cemuSettings.set("Controller", "8", "button_800000000")                 # R2
            cemuSettings.set("Controller", "9", "button_40")                        # Start
            cemuSettings.set("Controller", "10", "button_80")                       # Select
            cemuSettings.set("Controller", str(11 + addIndex), "button_4000000")    # Up
            cemuSettings.set("Controller", str(12 + addIndex), "button_8000000")    # Down
            cemuSettings.set("Controller", str(13 + addIndex), "button_10000000")   # Left
            cemuSettings.set("Controller", str(14 + addIndex), "button_20000000")   # Right
            cemuSettings.set("Controller", str(15 + addIndex), "button_100")        # LStick Click
            cemuSettings.set("Controller", str(16 + addIndex), "button_200")        # RStick Click
            cemuSettings.set("Controller", str(17 + addIndex), "button_80000000")   # LStick Up
            cemuSettings.set("Controller", str(18 + addIndex), "button_2000000000") # LStick Down
            cemuSettings.set("Controller", str(19 + addIndex), "button_1000000000") # LStick Left
            cemuSettings.set("Controller", str(20 + addIndex), "button_40000000")   # LStick Right
            cemuSettings.set("Controller", str(21 + addIndex), "button_400000000")  # RStick Up
            cemuSettings.set("Controller", str(22 + addIndex), "button_10000000000")# RStick Down
            cemuSettings.set("Controller", str(23 + addIndex), "button_8000000000") # RStick Left
            cemuSettings.set("Controller", str(24 + addIndex), "button_200000000")  # RStick Right
            cemuSettings.set("Controller", str(25 + addIndex), "button_100")        # Blow Mic

        configFileName = "{}/{}".format(cemuConfig + "/controllerProfiles/", "controller" + str(nplayer) + ".txt")

        # Save Cemu controller profiles
        with open(configFileName, 'w') as configfile:
            cemuSettings.write(configfile)
        nplayer+=1
