#!/usr/bin/env python

import sys
import os
import io
import batoceraFiles
import settings
from Emulator import Emulator
import configparser

def writePPSSPPConfig(system):
    iniConfig = configparser.ConfigParser(interpolation=None)
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

    # Frameskip
    iniConfig.set("Graphics", "FrameSkipType", "0") # Use number and not pourcent
    iniConfig.set("Graphics", "AutoFrameSkip", "False")
    if system.isOptSet("frameskip") and system.config["frameskip"] != 0:
        if system.config["frameskip"] == "automatic":
            iniConfig.set("Graphics", "AutoFrameSkip", "True")
            iniConfig.set("Graphics", "FrameSkip",     "1")
        else:
            iniConfig.set("Graphics", "FrameSkip", str(system.config["frameskip"]))
    else:
        iniConfig.set("Graphics", "FrameSkip",     "0")

    # Internal Resolution
    if system.isOptSet('internalresolution'):
        iniConfig.set("Graphics", "InternalResolution", str(system.config["internalresolution"]))
    else:
        iniConfig.set("Graphics", "InternalResolution", "1")

    # Rewinding
    if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        iniConfig.set("General", "RewindFlipFrequency", "300") # 300 = every 5 seconds
    else:
        iniConfig.set("General", "RewindFlipFrequency",  "0")

    # Custom : allow the user to configure directly PPSSPP via batocera.conf via lines like : ppsspp.section.option=value
    for user_config in system.config:
        if user_config[:7] == "ppsspp.":
            section_option = user_config[7:]
            section_option_splitter = section_option.find(".")
            custom_section = section_option[:section_option_splitter]
            custom_option = section_option[section_option_splitter+1:]
            if not iniConfig.has_section(custom_section):
                iniConfig.add_section(custom_section)
            iniConfig.set(custom_section, custom_option, str(system.config[user_config]))
