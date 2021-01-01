#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from os import path
import codecs
from Emulator import Emulator
from utils.logger import eslog
import ConfigParser
import json

# Create the controller configuration file
#first controller will ALWAYS BE A Gamepad
#additional controllers will either be a Pro Controller or Wiimote
def generateControllerConfig(system, playersControllers, rom):
    #make controller directory if it doesn't exist
    if not path.isdir(batoceraFiles.CONF + "/cemu/controllerProfiles"):
        os.mkdir(batoceraFiles.CONF + "/cemu/controllerProfiles")

    if not path.isdir(batoceraFiles.CONF + "/evmapy"):
        os.mkdir(batoceraFiles.CONF + "/evmapy")

    #purge old controller files
    for counter in range(0,8):
        configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller" + str(counter) +".txt")
        if os.path.isfile(configFileName):
            os.remove(configFileName)

    #Create the evmapy configFile

    configFileName = "{}/{}".format(batoceraFiles.CONF + "/evmapy/","wiiu.keys")
    if os.path.isfile(configFileName):
        os.remove(configFileName)



    data =  {}
    data['actions_player1'] = []
    data['actions_player1'].append({
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": [ "KEY_LEFTALT", "KEY_F4" ]
        })

    with open(batoceraFiles.CONF + "/evmapy/wiiu.keys", 'w') as outfile:
        json.dump(data, outfile)


    #We are exporting SDL_GAMECONTROLLERCONFIG in cemuGenerator, so we can assume all controllers are now working with xInput
    nplayer = 0

    for playercontroller, pad in sorted(playersControllers.items()):
        cemuSettings = ConfigParser.ConfigParser()
        cemuSettings.optionxform = str

        #Add Default Sections
        if not cemuSettings.has_section("General"):
            cemuSettings.add_section("General")
        if not cemuSettings.has_section("Controller"):
            cemuSettings.add_section("Controller")

        cemuSettings.set("General", "api", "XInput")
        cemuSettings.set("General", "controller", nplayer)

        if (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True):
            cemuSettings.set("General", "emulate", "Wiimote")
        elif (nplayer == 0):
            cemuSettings.set("General", "emulate", "Wii U GamePad")
            addIndex = 0
        else:
            cemuSettings.set("General", "emulate", "Wii U Pro Controller")
            addIndex = 1


        cemuSettings.set("Controller", "rumble", "0")
        cemuSettings.set("Controller", "leftRange", "1")
        cemuSettings.set("Controller", "rightRange", "1")
        cemuSettings.set("Controller", "leftDeadzone", ".2")
        cemuSettings.set("Controller", "rightDeadzone", ".2")
        cemuSettings.set("Controller", "buttonThreshold", ".5")

        if (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True):
            #Assumes a sideways wiimote configuration
            cemuSettings.set("Controller", "1", "button_4")    # A
            cemuSettings.set("Controller", "2", "button_8")    # B
            cemuSettings.set("Controller", "3", "button_1")    # 1
            cemuSettings.set("Controller", "4", "button_2")    # 2
            cemuSettings.set("Controller", "5", "button_800000000")    # C
            cemuSettings.set("Controller", "6", "button_100000000")    # Z
            cemuSettings.set("Controller", "7", "button_40")    # +
            cemuSettings.set("Controller", "8", "button_80")    # -
            cemuSettings.set("Controller", "9", "button_10000000")    # Up (Binds to Left on Controller)
            cemuSettings.set("Controller", "10", "button_20000000")   # Down (Binds to Right on Controller)
            cemuSettings.set("Controller", "11", "button_8000000")   # Left (Binds to Down on Controller)
            cemuSettings.set("Controller", "12", "button_4000000")   # Right (Binds to Up on Controller
            cemuSettings.set("Controller", "13", "button_400000000")   # Nunchuk Up (RStick)
            cemuSettings.set("Controller", "14", "button_10000000000")   # Nunchuk Down (RStick)
            cemuSettings.set("Controller", "15", "button_8000000000")   # Nunchuk Left (RStick)
            cemuSettings.set("Controller", "16", "button_200000000")   # Nunchuk Right (RStick)
            cemuSettings.set("Controller", "17", "0")   # Home
            cemuSettings.set("Controller", "nunchuck", "1")
            cemuSettings.set("Controller", "motionPlus", "0")
        else:
            cemuSettings.set("Controller", "1", "button_2")    # A
            cemuSettings.set("Controller", "2", "button_1")    # B
            cemuSettings.set("Controller", "3", "button_8")    # X
            cemuSettings.set("Controller", "4", "button_4")    # Y
            cemuSettings.set("Controller", "5", "button_10")    # L
            cemuSettings.set("Controller", "6", "button_20")    # R
            cemuSettings.set("Controller", "7", "button_100000000")    # L2
            cemuSettings.set("Controller", "8", "button_800000000")    # R2
            cemuSettings.set("Controller", "9", "button_40")    # Start
            cemuSettings.set("Controller", "10", "button_80")   # Select
            cemuSettings.set("Controller", 11 + addIndex, "button_4000000")   # Up
            cemuSettings.set("Controller", 12 + addIndex, "button_8000000")   # Down
            cemuSettings.set("Controller", 13 + addIndex, "button_10000000")   # Left
            cemuSettings.set("Controller", 14 + addIndex, "button_20000000")   # Right
            cemuSettings.set("Controller", 15 + addIndex, "button_100")   # LStick Click
            cemuSettings.set("Controller", 16 + addIndex, "button_200")   # RStick Click
            cemuSettings.set("Controller", 17 + addIndex, "button_80000000")   # LStick Up
            cemuSettings.set("Controller", 18 + addIndex, "button_2000000000")   # LStick Down
            cemuSettings.set("Controller", 19 + addIndex, "button_1000000000")   # LStick Left
            cemuSettings.set("Controller", 20 + addIndex, "button_40000000")   # LStick Right
            cemuSettings.set("Controller", 21 + addIndex, "button_400000000")   # RStick Up
            cemuSettings.set("Controller", 22 + addIndex, "button_10000000000")   # RStick Down
            cemuSettings.set("Controller", 23 + addIndex, "button_8000000000")   # RStick Left
            cemuSettings.set("Controller", 24 + addIndex, "button_200000000")   # RStick Right


        configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller" + str(nplayer) + ".txt")
                # save dolphin.ini
        with open(configFileName, 'w') as configfile:
            cemuSettings.write(configfile)
        nplayer+=1

