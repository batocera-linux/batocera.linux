#!/usr/bin/env python

import os
import configparser
import Command
from generators.Generator import Generator
import batoceraFiles

vpinballConfigPath = batoceraFiles.CONF + "/vpinball"
vpinballConfigFile = vpinballConfigPath + "/VPinballX.ini"

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        # create vpinball config directory
        if not os.path.exists(vpinballConfigPath):
            os.makedirs(vpinballConfigPath)

        #VideogetCurrentResolution to convert from percentage to pixel value
        #necessary because people can plug their 1080p laptop on a 4k TV
        def convertToPixel(total_size,percentage):
            pixel_value = str(int(int(total_size)*float(percentage)*1e-2))
            return pixel_value

        ## [ VPinballX.ini ] ##
        vpinballSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        vpinballSettings.optionxform = str
        if os.path.exists(vpinballConfigFile):
            vpinballSettings.read(vpinballConfigFile)
        #Tables are organised by folders containing the vpx file, and sub-folders with the roms, altcolor, altsound,...
        vpinballSettings.set("Standalone", "PinMAMEPath", "./")
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
                vpinballSettings.set("Player", "FXAA", "")
                vpinballSettings.set("Player", "Sharpen", "")
                vpinballSettings.set("Player", "DisableAO", "")
                vpinballSettings.set("Player", "DynamicAO", "")
                vpinballSettings.set("Player", "SSRefl", "")
                vpinballSettings.set("Player", "PFReflection", "")
                vpinballSettings.set("Player", "ForceAnisotropicFiltering", "")
                vpinballSettings.set("Player", "AlphaRampAccuracy", "")     
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
                vpinballSettings.set("Player", "DisableAO", "1")
                vpinballSettings.set("Player", "DynamicAO", "0")
                vpinballSettings.set("Player", "SSRefl", "0")
                vpinballSettings.set("Player", "PFReflection", "3")
                vpinballSettings.set("Player", "ForceAnisotropicFiltering", "0")
                vpinballSettings.set("Player", "AlphaRampAccuracy", "5")
            # if nothing is specified, we're in manual settings, ie we don't change any value in the config file

        #Altcolor (switchon)
        if system.isOptSet("vpinball_altcolor"):
            vpinballSettings.set("Standalone", "AltColor", "0")
        else:
            vpinballSettings.set("Standalone", "AltColor","1")
        #PinMAMEWindow (switch)
        if system.isOptSet("vpinball_pinmamewindow"):
            vpinballSettings.set("Standalone", "PinMAMEWindow","1")
        else:
            vpinballSettings.set("Standalone", "PinMAMEWindow","0")
        if system.isOptSet("vpinball_pinmamewindowx"):
            vpinballSettings.set("Standalone", "PinMAMEWindowX",convertToPixel(gameResolution["width"],system.config["vpinball_pinmamewindowx"]))
        else:
            vpinballSettings.set("Standalone", "PinMAMEWindowX","")
        if system.isOptSet("vpinball_pinmamewindowy"):
            vpinballSettings.set("Standalone", "PinMAMEWindowY",convertToPixel(gameResolution["height"],system.config["vpinball_pinmamewindowy"]))
        else:
            vpinballSettings.set("Standalone", "PinMAMEWindowY","")           
        if system.isOptSet("vpinball_pinmamewindowwidth"):
            vpinballSettings.set("Standalone", "PinMAMEWindowWidth",convertToPixel(gameResolution["width"],system.config["vpinball_pinmamewindowwidth"]))
        else:
            vpinballSettings.set("Standalone", "PinMAMEWindowWidth","")
        if system.isOptSet("vpinball_pinmamewindowheight"):
            vpinballSettings.set("Standalone", "PinMAMEWindowHeight",convertToPixel(gameResolution["height"],system.config["vpinball_pinmamewindowheight"]))
        else:
            vpinballSettings.set("Standalone", "PinMAMEWindowHeight","")           

        #FlexDMDWindow (switch)
        if system.isOptSet("vpinball_flexdmdwindow"):
            vpinballSettings.set("Standalone", "FlexDMDWindow","1")
        else:
            vpinballSettings.set("Standalone", "FlexDMDWindow","0")
        if system.isOptSet("vpinball_flexdmdwindowx"):
            vpinballSettings.set("Standalone", "FlexDMDWindowX",convertToPixel(gameResolution["width"],system.config["vpinball_flexdmdwindowx"]))
        else:
            vpinballSettings.set("Standalone", "FlexDMDWindowX","")
        if system.isOptSet("vpinball_flexdmdwindowy"):
            vpinballSettings.set("Standalone", "FlexDMDWindowY",convertToPixel(gameResolution["height"],system.config["vpinball_flexdmdwindowy"]))
        else:
            vpinballSettings.set("Standalone", "FlexDMDWindowY","")           
        if system.isOptSet("vpinball_flexdmdwindowwidth"):
            vpinballSettings.set("Standalone", "FlexDMDWindowWidth",convertToPixel(gameResolution["width"],system.config["vpinball_flexdmdwindowwidth"]))
        else:
            vpinballSettings.set("Standalone", "FlexDMDWindowWidth","")
        if system.isOptSet("vpinball_flexdmdwindowheight"):
            vpinballSettings.set("Standalone", "FlexDMDWindowHeight",convertToPixel(gameResolution["height"],system.config["vpinball_flexdmdwindowheight"]))
        else:
            vpinballSettings.set("Standalone", "FlexDMDWindowHeight","")           
            
        #B2SWindows (switchon)
        if system.isOptSet("vpinball_b2swindows"):
            vpinballSettings.set("Standalone", "B2SWindows","0")
        else:
            vpinballSettings.set("Standalone", "B2SWindows","1")
        if system.isOptSet("vpinball_b2sbackglassx"):
            vpinballSettings.set("Standalone", "B2SBackglassX",convertToPixel(gameResolution["width"],system.config["vpinball_b2sbackglassx"]))
        else:
            vpinballSettings.set("Standalone", "B2SBackglassX","")
        if system.isOptSet("vpinball_b2sbackglassy"):
            vpinballSettings.set("Standalone", "B2SBackglassY",convertToPixel(gameResolution["height"],system.config["vpinball_b2sbackglassy"]))
        else:
            vpinballSettings.set("Standalone", "B2SBackglassY","")           
        if system.isOptSet("vpinball_b2sbackglasswidth"):
            vpinballSettings.set("Standalone", "B2SBackglassWidth",convertToPixel(gameResolution["width"],system.config["vpinball_b2sbackglasswidth"]))
        else:
            vpinballSettings.set("Standalone", "B2SBackglassWidth","")
        if system.isOptSet("vpinball_b2sbackglassheight"):
            vpinballSettings.set("Standalone", "B2SBackglassHeight",convertToPixel(gameResolution["height"],system.config["vpinball_b2sbackglassheight"]))
        else:
            vpinballSettings.set("Standalone", "B2SBackglassHeight","")           

        #B2S Hide B2SDMD (switchon)
        if system.isOptSet("vpinball_b2swindows"):
            vpinballSettings.set("Standalone", "B2SHideB2SDMD","0")
        else:
            vpinballSettings.set("Standalone", "B2SHideB2SDMD","1")
        if system.isOptSet("vpinball_b2sdmdx"):
            vpinballSettings.set("Standalone", "B2SDMDX",convertToPixel(gameResolution["width"],system.config["vpinball_b2sdmdx"]))
        else:
            vpinballSettings.set("Standalone", "B2SDMDX","")
        if system.isOptSet("vpinball_b2sdmdy"):
            vpinballSettings.set("Standalone", "B2SDMDY",convertToPixel(gameResolution["height"],system.config["vpinball_b2sdmdy"]))
        else:
            vpinballSettings.set("Standalone", "B2SDMDY","")           
        if system.isOptSet("vpinball_b2sdmdwidth"):
            vpinballSettings.set("Standalone", "B2SDMDWidth",convertToPixel(gameResolution["width"],system.config["vpinball_b2sdmdwidth"]))
        else:
            vpinballSettings.set("Standalone", "B2SDMDWidth","")
        if system.isOptSet("vpinball_b2sdmdheight"):
            vpinballSettings.set("Standalone", "B2SDMDHeight",convertToPixel(gameResolution["height"],system.config["vpinball_b2sdmdheight"]))
        else:
            vpinballSettings.set("Standalone", "B2SDMDHeight","")           

        #Sound balance
        if system.isOptSet("vpinball_musicvolume"):
            vpinballSettings.set("Player", "MusicVolume", system.config["vpinball_musicvolume"])
        else:
            vpinballSettings.set("Player", "MusicVolume", "")
        if system.isOptSet("vpinball_soundvolume"):
            vpinballSettings.set("Player", "SoundVolume", system.config["vpinball_soundvolume"])
        else:
            vpinballSettings.set("Player", "SoundVolume", "")
        #Altsound
        if system.isOptSet("vpinball_altsound"):
            vpinballSettings.set("Standalone", "AltSound", system.config["vpinball_altsound"])
        else:
            vpinballSettings.set("Standalone", "AltSound","1")
                

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
        return 16/9
