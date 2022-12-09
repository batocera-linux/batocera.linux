#!/usr/bin/env python

import sys
import os
import io
import batoceraFiles
import settings
from Emulator import Emulator
import configparser

ppssppConf   = batoceraFiles.CONF + '/ppsspp/PSP/SYSTEM'
ppssppConfig = ppssppConf + '/ppsspp.ini'


def writePPSSPPConfig(system):
    iniConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    iniConfig.optionxform = str
    if os.path.exists(ppssppConfig):
        try:
            with io.open(ppssppConfig, 'r', encoding='utf_8_sig') as fp:
                iniConfig.readfp(fp)
        except:
            pass

    createPPSSPPConfig(iniConfig, system)
    # Save the ini file
    if not os.path.exists(os.path.dirname(ppssppConfig)):
        os.makedirs(os.path.dirname(ppssppConfig))
    with open(ppssppConfig, 'w') as configfile:
        iniConfig.write(configfile)

def createPPSSPPConfig(iniConfig, system):

    ## [GRAPHICS]
    if not iniConfig.has_section("Graphics"):
        iniConfig.add_section("Graphics")

    # Graphics Backend
    if system.isOptSet('gfxbackend'):
        iniConfig.set("Graphics", "GraphicsBackend", system.config["gfxbackend"])
    else:
        iniConfig.set("Graphics", "GraphicsBackend", "0 (OPENGL)")

    # Display FPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
        iniConfig.set("Graphics", "ShowFPSCounter", "3") # 1 for Speed%, 2 for FPS, 3 for both
    else:
        iniConfig.set("Graphics", "ShowFPSCounter", "0")

    # Frameskip
    iniConfig.set("Graphics", "FrameSkipType", "0") # Use number and not percent
    if system.isOptSet("frameskip") and not system.config["frameskip"] == "automatic":
        iniConfig.set("Graphics", "FrameSkip", str(system.config["frameskip"]))
    elif system.isOptSet('rendering_mode') and system.getOptBoolean('rendering_mode') == False:
        iniConfig.set("Graphics", "FrameSkip", "0")
    else:
        iniConfig.set("Graphics", "FrameSkip", "2")

    # Buffered rendering
    if system.isOptSet('rendering_mode') and system.getOptBoolean('rendering_mode') == False:
        iniConfig.set("Graphics", "RenderingMode", "0")
        # Have to force autoframeskip off here otherwise PPSSPP sets rendering mode back to 1.
        iniConfig.set("Graphics", "AutoFrameSkip", "False")
    else:
        iniConfig.set("Graphics", "RenderingMode", "1")
        # Both internal resolution and auto frameskip are dependent on buffered rendering being on, only check these if the user is actually using buffered rendering.
        # Internal Resolution
        if system.isOptSet('internal_resolution'):
            iniConfig.set("Graphics", "InternalResolution", str(system.config["internal_resolution"]))
        else:
            iniConfig.set("Graphics", "InternalResolution", "1")
        # Auto frameskip
        if system.isOptSet("autoframeskip") and system.getOptBoolean("autoframeskip") == False:
            iniConfig.set("Graphics", "AutoFrameSkip", "False")
        else:
            iniConfig.set("Graphics", "AutoFrameSkip", "True")

    # VSync Interval
    if system.isOptSet('vsyncinterval') and system.getOptBoolean('vsyncinterval') == False:
        iniConfig.set("Graphics", "VSyncInterval", "False")
    else:
        iniConfig.set("Graphics", "VSyncInterval", "True")

    # Texture Scaling Level
    if system.isOptSet('texture_scaling_level'):
        iniConfig.set("Graphics", "TexScalingLevel", system.config["texture_scaling_level"])
    else:
        iniConfig.set("Graphics", "TexScalingLevel", "1")
    # Texture Scaling Type
    if system.isOptSet('texture_scaling_type'):
        iniConfig.set("Graphics", "TexScalingType", system.config["texture_scaling_type"])
    else:
        iniConfig.set("Graphics", "TexScalingType", "0")
    # Texture Deposterize
    if system.isOptSet('texture_deposterize'):
        iniConfig.set("Graphics", "TexDeposterize", system.config["texture_deposterize"])
    else:
        iniConfig.set("Graphics", "TexDeposterize", "True")

    # Anisotropic Filtering
    if system.isOptSet('anisotropic_filtering'):
        iniConfig.set("Graphics", "AnisotropyLevel", system.config["anisotropic_filtering"])
    else:
        iniConfig.set("Graphics", "AnisotropyLevel", "3")


   ## [SYSTEM PARAM]
    if not iniConfig.has_section("SystemParam"):
        iniConfig.add_section("SystemParam")

    # Forcing Nickname to Batocera or User name
    if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True and system.isOptSet('retroachievements.username') and system.config.get('retroachievements.username', "") != "":
        iniConfig.set("SystemParam", "NickName", system.config.get('retroachievements.username', ""))
    else:
        iniConfig.set("SystemParam", "NickName", "Batocera")
    # Disable Encrypt Save (permit to exchange save with different machines)
    iniConfig.set("SystemParam", "EncryptSave", "False")   


    ## [GENERAL]
    if not iniConfig.has_section("General"):
        iniConfig.add_section("General")

    # Rewinding
    if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        iniConfig.set("General", "RewindFlipFrequency", "300") # 300 = every 5 seconds
    else:
        iniConfig.set("General", "RewindFlipFrequency",  "0")
    # Cheats
    if system.isOptSet('enable_cheats'):
        iniConfig.set("General", "EnableCheats", system.config["enable_cheats"])
    else:
        iniConfig.set("General", "EnableCheats", "False")
    # Don't check for a new version
    iniConfig.set("General", "CheckForNewVersion", "False")

    ## [UPGRADE] - don't upgrade
    if not iniConfig.has_section("Upgrade"):
        iniConfig.add_section("Upgrade")
    iniConfig.set("Upgrade", "UpgradeMessage", "")
    iniConfig.set("Upgrade", "UpgradeVersion", "")
    iniConfig.set("Upgrade", "DismissedVersion", "")

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
