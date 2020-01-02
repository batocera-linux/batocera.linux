#!/usr/bin/env python

import sys
import os
import io
import batoceraFiles
import settings
from Emulator import Emulator
import ConfigParser

def writePPSSPPConfig(system):
    iniConfig = ConfigParser.ConfigParser()
    # To prevent ConfigParser from converting to lower case
    iniConfig.optionxform = str
    if os.path.exists(batoceraFiles.ppssppConfig):
        try:
            with io.open(batoceraFiles.ppssppConfig, 'r', encoding='utf_8_sig') as fp:
                iniConfig.readfp(fp)
        except:
            pass

    createPPSSPPConfig(iniConfig, system)
    # save the ini file
    if not os.path.exists(os.path.dirname(batoceraFiles.ppssppConfig)):
        os.makedirs(os.path.dirname(batoceraFiles.ppssppConfig))
    with open(batoceraFiles.ppssppConfig, 'w') as configfile:
        iniConfig.write(configfile)

def createPPSSPPConfig(iniConfig, system):
    if not iniConfig.has_section("Graphics"):
        iniConfig.add_section("Graphics")
    if not iniConfig.has_section("General"):
        iniConfig.add_section("General")

    # Display FPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
        iniConfig.set("Graphics", "ShowFPSCounter", "3") # 1 for Speed%, 2 for FPS, 3 for both
    else:
        iniConfig.set("Graphics", "ShowFPSCounter", "0")

    # Performances
    if system.isOptSet('frameskip') and system.getOptBoolean('frameskip') == True:
        iniConfig.set("Graphics", "FrameSkip",  "1")
    else:
        iniConfig.set("Graphics", "FrameSkip", "0")

    if system.isOptSet('frameskiptype'):
        iniConfig.set("Graphics", "FrameSkipType", system.config["frameskiptype"])
    else:
        iniConfig.set("Graphics", "FrameSkipType",  "0")

    if system.isOptSet('internalresolution'):
        iniConfig.set("Graphics", "InternalResolution", system.config["internalresolution"])
    else:
        iniConfig.set("Graphics", "InternalResolution", "1")

    # rewinding
    if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        iniConfig.set("General", "RewindFlipFrequency", "300") # 300 = every 5 seconds
    else:
        iniConfig.set("General", "RewindFlipFrequency",  "0")
