#!/usr/bin/env python

import os
import configparser
import Command
from generators.Generator import Generator
import batoceraFiles
import shutil
from utils.logger import get_logger
import controllersConfig
from utils.batoceraServices import batoceraServices

eslog = get_logger(__name__)

vpinballConfigPath = batoceraFiles.CONF + "/vpinball"
vpinballConfigFileSource = vpinballConfigPath + "/VPinballX.ini"
vpinballConfigFile = vpinballConfigPath + "/VPinballX-configgen.ini"
vpinballPinmameIniPath = batoceraFiles.CONF + "/vpinball/pinmame/ini"

class VPinballGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # create vpinball config directory and default config file if they don't exist
        if not os.path.exists(vpinballConfigPath):
            os.makedirs(vpinballConfigPath)
        if not os.path.exists(vpinballPinmameIniPath):
            os.makedirs(vpinballPinmameIniPath)            
        if not os.path.exists(vpinballConfigFileSource):
            shutil.copy("/usr/bin/vpinball/assets/Default_VPinballX.ini", vpinballConfigFileSource)
        # all the modifications will be applied to the VPinballX-configgen.ini which is a copy of the VPinballX.ini
        # this way VPinballX.ini is never touched, so advanced users (who edit VPinballX.ini) will never loose their settings
        shutil.copy(vpinballConfigFileSource, vpinballConfigFile)            

        ## [ VPinballX.ini ] ##
        try:
            vpinballSettings = configparser.ConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.optionxform = str
            vpinballSettings.read(vpinballConfigFile)
        except configparser.DuplicateOptionError as e:
            eslog.debug(f"Error reading VPinballX.ini: {e}")
            eslog.debug(f"*** Using default VPinballX.ini file ***")
            shutil.copy("/usr/bin/vpinball/assets/Default VPinballX.ini", vpinballConfigFile)
            vpinballSettings = configparser.ConfigParser(interpolation=None, allow_no_value=True)
            vpinballSettings.optionxform = str
            vpinballSettings.read(vpinballConfigFile)
        # Sections
        if not vpinballSettings.has_section("Standalone"):
            vpinballSettings.add_section("Standalone")
        if not vpinballSettings.has_section("Player"):
            vpinballSettings.add_section("Player")
            
        # By default, this configgen is on (switchon)
        # vpinball will use VPinballX-configgen.ini which is a temporary edited copy of VPinballX.ini
        # If an Advanced User turns the configgen off, vpinball will directly use VPinballX.ini
        if not system.isOptSet("vpinball_enableconfiggen"):
            #Tables are organised by folders containing the vpx file, and sub-folders with the roms, altcolor, altsound,...
            # We keep a switch to allow users with the old unique pinmame to be able to continue using vpinball (switchon)
            if system.isOptSet("vpinball_folders"):
                vpinballSettings.set("Standalone", "PinMAMEPath", "")
            else:
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
                # regarding performance settings

            #Altcolor (switchon)
            if system.isOptSet("vpinball_altcolor"):
                vpinballSettings.set("Standalone", "AltColor", "0")
            else:
                vpinballSettings.set("Standalone", "AltColor","1")

            # Extra_windows (pinmamedmd, flexdmd, b2s,b2sdmd)
            # VideogetCurrentResolution to convert from percentage to pixel value
            # necessary trick because people can plug their 1080p laptop on a 4k TV
            # (and because VPinballX.ini uses absolute pixel coordinates)
            def ConvertToPixel(total_size,percentage):
                pixel_value = str(int(int(total_size)*float(percentage)*1e-2))
                return pixel_value
            # Calculates the relative height, depending on the screen ratio
            # (normaly 16/9), the element ratio (4/3 for the b2s) and the relative width
            def RelativeHeightCalculate(Rscreen,Relement,RelativeWidth):
                return int(Rscreen*RelativeWidth/Relement)
            # Reasonable constants / default values
            Rscreen=16/9
            small,medium,large=20,25,30
            x,y,width=0,0,medium 

            # PinMame
            WindowName="PinMAMEWindow"
            Rwindow = 4/1   #Usual Ratio for this window
            # Auto default behaviour is to read values from VPinballX.ini file
            # so we don't do anything in the configgen
            if system.isOptSet("vpinball_pinmame"):                                
                if system.config["vpinball_pinmame"]=="pinmame_disabled":
                    vpinballSettings.set("Standalone", WindowName,"0")                    
                else: 
                    vpinballSettings.set("Standalone", WindowName,"1")                    
                    if system.config["vpinball_pinmame"]=="pinmame_topright_small":
                        width=small
                        x=100-width
                    if system.config["vpinball_pinmame"]=="pinmame_topright_medium":
                        width=medium
                        x=100-width
                    if system.config["vpinball_pinmame"]=="pinmame_topright_large":
                        width=large
                        x=100-width
                    if system.config["vpinball_pinmame"]=="pinmame_topleft_small":
                        width=small
                        x=0
                    if system.config["vpinball_pinmame"]=="pinmame_topleft_medium":
                        width=medium
                        x=0
                    if system.config["vpinball_pinmame"]=="pinmame_topleft_large":
                        width=large
                        x=0
                    # apply settings
                    height=RelativeHeightCalculate(Rscreen,Rwindow,width)
                    vpinballSettings.set("Standalone",WindowName+"X",ConvertToPixel(gameResolution["width"],x))
                    vpinballSettings.set("Standalone",WindowName+"Y",ConvertToPixel(gameResolution["height"],y))
                    vpinballSettings.set("Standalone",WindowName+"Width",ConvertToPixel(gameResolution["width"],width))
                    vpinballSettings.set("Standalone",WindowName+"Height",ConvertToPixel(gameResolution["height"],height))

            # FlexDMD
            WindowName="FlexDMDWindow"
            Rwindow=4/1   #Usual Ratio for this window
            # Auto default behaviour is to read values from VPinballX.ini file
            # so we don't do anything in the configgen            
            if system.isOptSet("vpinball_flexdmd"):                            
                if system.config["vpinball_flexdmd"]=="flexdmd_disabled":
                    vpinballSettings.set("Standalone", WindowName,"0")                    
                else: 
                    vpinballSettings.set("Standalone", WindowName,"1")                    
                    if system.config["vpinball_flexdmd"]=="flexdmd_topright_small":
                        width=small
                        x=100-width
                    if system.config["vpinball_flexdmd"]=="flexdmd_topright_medium":
                        width=medium
                        x=100-width
                    if system.config["vpinball_flexdmd"]=="flexdmd_topright_large":
                        width=large
                        x=100-width
                    if system.config["vpinball_flexdmd"]=="flexdmd_topleft_small":
                        width=small
                        x=0
                    if system.config["vpinball_flexdmd"]=="flexdmd_topleft_medium":
                        width=medium
                        x=0
                    if system.config["vpinball_flexdmd"]=="flexdmd_topleft_large":
                        width=large
                        x=0
                    # apply settings
                    height=RelativeHeightCalculate(Rscreen,Rwindow,width)
                    vpinballSettings.set("Standalone",WindowName+"X",ConvertToPixel(gameResolution["width"],x))
                    vpinballSettings.set("Standalone",WindowName+"Y",ConvertToPixel(gameResolution["height"],y))
                    vpinballSettings.set("Standalone",WindowName+"Width",ConvertToPixel(gameResolution["width"],width))
                    vpinballSettings.set("Standalone",WindowName+"Height",ConvertToPixel(gameResolution["height"],height))
            
            # B2S and B2SDMD
            WindowName="B2SBackglass"
            Rwindow = 4/3   #Usual Ratio for this window
            # Auto default behaviour is to read values from VPinballX.ini file
            # so we don't do anything in the configgen
            if system.isOptSet("vpinball_b2s"):                                
                if system.config["vpinball_b2s"]=="b2s_disabled":                                           
                    vpinballSettings.set("Standalone", "B2SWindows","0")
                    vpinballSettings.set("Standalone", "B2SHideB2SDMD","1")               
                else:                                
                    vpinballSettings.set("Standalone", "B2SHideGrill","1")        
                    vpinballSettings.set("Standalone", "B2SWindows","1")
                    vpinballSettings.set("Standalone", "B2SHideB2SDMD","0")               
                    if system.config["vpinball_b2s"]=="b2s_topright_small":
                        width=small
                        x=100-width
                    if system.config["vpinball_b2s"]=="b2s_topright_medium":
                        width=medium
                        x=100-width
                    if system.config["vpinball_b2s"]=="b2s_topright_large":
                        width=large
                        x=100-width
                    if system.config["vpinball_b2s"]=="b2s_topleft_small":
                        width=small
                        x=0
                    if system.config["vpinball_b2s"]=="b2s_topleft_medium":
                        width=medium
                        x=0
                    if system.config["vpinball_b2s"]=="b2s_topleft_large":
                        width=large
                        x=0
                    # apply settings
                    height=RelativeHeightCalculate(Rscreen,Rwindow,width)
                    vpinballSettings.set("Standalone",WindowName+"X",ConvertToPixel(gameResolution["width"],x))
                    vpinballSettings.set("Standalone",WindowName+"Y",ConvertToPixel(gameResolution["height"],y))
                    vpinballSettings.set("Standalone",WindowName+"Width",ConvertToPixel(gameResolution["width"],width))
                    vpinballSettings.set("Standalone",WindowName+"Height",ConvertToPixel(gameResolution["height"],height))
                    # B2SDMD
                    WindowName="B2SDMD"
                    y=height
                    Rwindow = 3   #Usual Ratio for this window
                    height=RelativeHeightCalculate(Rscreen,Rwindow,width)
                    vpinballSettings.set("Standalone",WindowName+"X",ConvertToPixel(gameResolution["width"],x))
                    vpinballSettings.set("Standalone",WindowName+"Y",ConvertToPixel(gameResolution["height"],y))
                    vpinballSettings.set("Standalone",WindowName+"Width",ConvertToPixel(gameResolution["width"],width))
                    vpinballSettings.set("Standalone",WindowName+"Height",ConvertToPixel(gameResolution["height"],height))
            # B2S DMD: not displayed if B2S is hidden
            if system.isOptSet("vpinball_b2sdmd"): #switchon
                vpinballSettings.set("Standalone", "B2SHideB2SDMD","1")               
            else:
                vpinballSettings.set("Standalone", "B2SHideB2SDMD","0")               
                
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
                vpinballSettings.set("Standalone", "AltSound", "0")
            else:
                vpinballSettings.set("Standalone", "AltSound","1")

            # DMDServer
            if batoceraServices.isServiceEnabled("dmd_real"):
                vpinballSettings.set("Standalone", "DMDServer","1")
            else:
                vpinballSettings.set("Standalone", "DMDServer","0")

            # Save VPinballX.ini
            with open(vpinballConfigFile, 'w') as configfile:
                vpinballSettings.write(configfile)

            # set the config path to be sure
            commandArray = [
                "/usr/bin/vpinball/VPinballX_GL",
                "-PrefPath", vpinballConfigPath,
                "-Ini", vpinballConfigFile,
                "-Play", rom
            ]
        else:
            # we don't use the configgen
            commandArray = [
                "/usr/bin/vpinball/VPinballX_GL",
                "-PrefPath", vpinballConfigPath,
                "-Play", rom
            ]
            
        return Command.Command(array=commandArray, env={"SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)})

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
