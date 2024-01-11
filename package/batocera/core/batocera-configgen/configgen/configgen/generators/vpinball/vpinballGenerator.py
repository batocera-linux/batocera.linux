#!/usr/bin/env python

import os
import configparser
import Command
from generators.Generator import Generator
import batoceraFiles

vpinballConfigPath = batoceraFiles.CONF + "/vpinball"
vpinballMusicPath = vpinballConfigPath + "/music"
vpinballConfigFile = vpinballConfigPath + "/VPinballX.ini"
vpinballAltcolorPath = vpinballConfigPath + "/pinmame/altcolor"
vpinballAltsoundPath = vpinballConfigPath + "/pinmame/altsound"

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        # create vpinball config directory
        if not os.path.exists(vpinballConfigPath):
            os.makedirs(vpinballConfigPath)
        # create vpinball music directory
        if not os.path.exists(vpinballMusicPath):
            os.makedirs(vpinballMusicPath)
        # create pinmame extra directories
        if not os.path.exists(vpinballAltcolorPath):
            os.makedirs(vpinballAltcolorPath)
        if not os.path.exists(vpinballAltsoundPath):
            os.makedirs(vpinballAltsoundPath)

        ## [ VPinballX.ini ] ##
        vpinballSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        vpinballSettings.optionxform = str
        if os.path.exists(vpinballConfigFile):
            vpinballSettings.read(vpinballConfigFile)
        #Ball trail
        if system.isOptSet("vpinball_balltrail"):
            vpinballSettings.set("Player", "BallTrail", "1")
            vpinballSettings.set("Player", "BallTrailStrength", system.config["vpinball_balltrail"])
        else:
            vpinballSettings.set("Player", "BallTrail", "0")
            vpinballSettings.set("Player", "BallTrailStrength", "0")
                #Visual Nugde Strength
        if system.isOptSet("vpinball_nudgestrength"):
            vpinballSettings.set("Player", "NudgeStrength", system.config["vpinball_nudgestrength"])
        else:
            vpinballSettings.set("Player", "NudgeStrength", "")
            #Sound balance
        if system.isOptSet("vpinball_musicvolume"):
            vpinballSettings.set("Player", "MusicVolume", system.config["vpinball_musicvolume"])
        else:
            vpinballSettings.set("Player", "MusicVolume", "")
        if system.isOptSet("vpinball_soundvolume"):
            vpinballSettings.set("Player", "SoundVolume", system.config["vpinball_soundvolume"])
        else:
            vpinballSettings.set("Player", "SoundVolume", "")
        # Performance settings
        if system.isOptSet("vpinball_maxframerate"):
            vpinballSettings.set("Player", "MaxFramerate", system.config["vpinball_maxframerate"])
        else:
            vpinballSettings.set("Player", "MaxFramerate", "")
        if system.isOptSet("vpinball_vsync"):
            vpinballSettings.set("Player", "SyncMode", system.config["vpinball_vsync"])
        else:
            vpinballSettings.set("Player", "SyncMode", "2")
        if system.isOptSet("vpinball_presets"):
            if system.config["vpinball_presets"]=="defaults":
                vpinballSettings.set("Player", "FXAA", "2")
                vpinballSettings.set("Player", "Sharpen", "0")
                vpinballSettings.set("Player", "DisableAO", "0")
                vpinballSettings.set("Player", "DynamicAO", "0")
                vpinballSettings.set("Player", "SSRefl", "0")
                vpinballSettings.set("Player", "PFReflection", "5")
                vpinballSettings.set("Player", "ForceAnisotropicFiltering", "1")
                vpinballSettings.set("Player", "AlphaRampAccuracy", "10")
            if system.config["vpinball_presets"]=="highend":
                vpinballSettings.set("Player", "FXAA", "3")
                vpinballSettings.set("Player", "Sharpen", "2")
                vpinballSettings.set("Player", "DisableAO", "0")
                vpinballSettings.set("Player", "DynamicAO", "1")
                vpinballSettings.set("Player", "SSRefl", "1")
                vpinballSettings.set("Player", "PFReflection", "5")
                vpinballSettings.set("Player", "ForceAnisotropicFiltering", "1")
                vpinballSettings.set("Player", "AlphaRampAccuracy", "10")
            if system.config["vpinball_presets"]=="lowend":
                vpinballSettings.set("Player", "FXAA", "0")
                vpinballSettings.set("Player", "Sharpen", "0")
                vpinballSettings.set("Player", "DisableAO", "0")
                vpinballSettings.set("Player", "DynamicAO", "0")
                vpinballSettings.set("Player", "SSRefl", "0")
                vpinballSettings.set("Player", "PFReflection", "3")
                vpinballSettings.set("Player", "ForceAnisotropicFiltering", "0")
                vpinballSettings.set("Player", "AlphaRampAccuracy", "5")
        else:
                vpinballSettings.set("Player", "FXAA", "")
                vpinballSettings.set("Player", "Sharpen", "")
                vpinballSettings.set("Player", "DisableAO", "")
                vpinballSettings.set("Player", "DynamicAO", "")
                vpinballSettings.set("Player", "SSRefl", "")
                vpinballSettings.set("Player", "PFReflection", "")
                vpinballSettings.set("Player", "ForceAnisotropicFiltering", "")
                vpinballSettings.set("Player", "AlphaRampAccuracy", "")
        #Ratio
        ratio=16/9 #default value
        if system.isOptSet("vpinball_ratio"):
            if system.config["vpinball_ratio"]=="43":
                ratio=4/3
        if system.isOptSet("vpinball_resolution"):
            height = int(system.config["vpinball_resolution"])
            width = int(height * ratio)
            vpinballSettings.set("Player", "Height", str(height))
            vpinballSettings.set("Player", "Width", str(width))
        else:
            vpinballSettings.set("Player", "Height", "")
            vpinballSettings.set("Player", "Width", "")

        # Save VPinballX.ini
        with open(vpinballConfigFile, 'w') as configfile:
            vpinballSettings.write(configfile)

        # set the config path to be sure
        commandArray = [
            "/usr/bin/vpinball/VPinballX_GL",
            "-PrefPath", vpinballConfigPath,
            "-Play", rom
        ]

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        if ("vpinball_ratio" in config and config["vpinball_ratio"] == "43"):
            return 4/3
        return 16/9

