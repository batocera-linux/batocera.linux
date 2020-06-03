#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import dolphinControllers
import dolphinSYSCONF
import shutil
import os.path
from os import environ
import ConfigParser

class DolphinGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(os.path.dirname(batoceraFiles.dolphinIni)):
            os.makedirs(os.path.dirname(batoceraFiles.dolphinIni))

        dolphinControllers.generateControllerConfig(system, playersControllers, rom)

        # dolphin.ini
        dolphinSettings = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        dolphinSettings.optionxform = str
        if os.path.exists(batoceraFiles.dolphinIni):
            dolphinSettings.read(batoceraFiles.dolphinIni)

        # sections
        if not dolphinSettings.has_section("General"):
            dolphinSettings.add_section("General")
        if not dolphinSettings.has_section("Core"):
            dolphinSettings.add_section("Core")
        if not dolphinSettings.has_section("Interface"):
            dolphinSettings.add_section("Interface")
        if not dolphinSettings.has_section("Analytics"):
            dolphinSettings.add_section("Analytics")

        # draw or not FPS
        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
            dolphinSettings.set("General", "ShowLag", "True")
            dolphinSettings.set("General", "ShowFrameCount", "True")
        else:
            dolphinSettings.set("General", "ShowLag", "False")
            dolphinSettings.set("General", "ShowFrameCount", "False")

        # don't ask about statistics
        dolphinSettings.set("Analytics", "PermissionAsked", "True")

        # don't confirm at stop
        dolphinSettings.set("Interface", "ConfirmStop", "False")

        # language (for gamecube at least)
        dolphinSettings.set("Core", "SelectedLanguage", getGameCubeLangFromEnvironment())
        dolphinSettings.set("Core", "GameCubeLanguage", getGameCubeLangFromEnvironment())

        # wiimote scanning
        dolphinSettings.set("Core", "WiimoteContinuousScanning", "True")

        # gamecube pads forced as standard pad
        dolphinSettings.set("Core", "SIDevice0", "6")
        dolphinSettings.set("Core", "SIDevice1", "6")
        dolphinSettings.set("Core", "SIDevice2", "6")
        dolphinSettings.set("Core", "SIDevice3", "6")

        # save dolphin.ini
        with open(batoceraFiles.dolphinIni, 'w') as configfile:
            dolphinSettings.write(configfile)

        # gfx.ini
        dolphinGFXSettings = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        dolphinGFXSettings.optionxform = str
        dolphinGFXSettings.read(batoceraFiles.dolphinGfxIni)

        if not dolphinGFXSettings.has_section("Settings"):
            dolphinGFXSettings.add_section("Settings")
        dolphinGFXSettings.set("Settings", "AspectRatio", getGfxRatioFromConfig(system.config, gameResolution))

        # show fps
        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
            dolphinGFXSettings.set("Settings", "ShowFPS", "True")
        else:
            dolphinGFXSettings.set("Settings", "ShowFPS", "False")

        # for to search for custom textures
        if (system.isOptSet('hires_textures') and (system.config['hires_textures'] == '1')):
            dolphinGFXSettings.set("Settings", "HiresTextures", "True")
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", "True")
        else:
            dolphinGFXSettings.set("Settings", "HiresTextures", "False")
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", "False")
            
        # widescreen hack
        if (system.isOptSet('widescreen_hack') and (system.config['widescreen_hack'] == '1')):
            dolphinGFXSettings.set("Settings", "wideScreenHack", "True")
        else:
            dolphinGFXSettings.remove_option("Settings", "wideScreenHack")

        # various performance hacks
        if (system.isOptSet('perf_hacks') and (system.config['perf_hacks'] == '1')):
            if not dolphinGFXSettings.has_section("Hacks"):
                dolphinGFXSettings.add_section("Hacks")
            if not dolphinGFXSettings.has_section("Enhancements"):
                dolphinGFXSettings.add_section("Enhancements")        
            dolphinGFXSettings.set("Hacks", "BBoxEnable", "False")
            dolphinGFXSettings.set("Hacks", "DeferEFBCopies", "True")
            dolphinGFXSettings.set("Hacks", "EFBEmulateFormatChanges", "False")
            dolphinGFXSettings.set("Hacks", "EFBScaledCopy", "True")
            dolphinGFXSettings.set("Hacks", "EFBToTextureEnable", "True")
            dolphinGFXSettings.set("Hacks", "SkipDuplicateXFBs", "True")
            dolphinGFXSettings.set("Hacks", "XFBToTextureEnable", "True")
            dolphinGFXSettings.set("Enhancements", "ForceFiltering", "True")
            dolphinGFXSettings.set("Enhancements", "ArbitraryMipmapDetection", "True")
            dolphinGFXSettings.set("Enhancements", "DisableCopyFilter", "True")
            dolphinGFXSettings.set("Enhancements", "ForceTrueColor", "True")            
        else:
            if dolphinGFXSettings.has_section("Hacks"):
                dolphinGFXSettings.remove_option("Hacks", "BBoxEnable")
                dolphinGFXSettings.remove_option("Hacks", "DeferEFBCopies")
                dolphinGFXSettings.remove_option("Hacks", "EFBEmulateFormatChanges")
                dolphinGFXSettings.remove_option("Hacks", "EFBScaledCopy")
                dolphinGFXSettings.remove_option("Hacks", "EFBToTextureEnable")
                dolphinGFXSettings.remove_option("Hacks", "SkipDuplicateXFBs")
                dolphinGFXSettings.remove_option("Hacks", "XFBToTextureEnable")
            if dolphinGFXSettings.has_section("Enhancements"):
                dolphinGFXSettings.remove_option("Enhancements", "ForceFiltering")
                dolphinGFXSettings.remove_option("Enhancements", "ArbitraryMipmapDetection")
                dolphinGFXSettings.remove_option("Enhancements", "DisableCopyFilter")
                dolphinGFXSettings.remove_option("Enhancements", "ForceTrueColor")  
  
        # internal resolution settings
        if system.isOptSet('internalresolution'):
            dolphinGFXSettings.set("Settings", "InternalResolution", system.config["internalresolution"])
        else:
            dolphinGFXSettings.set("Settings", "InternalResolution", "0")

        # save gfx.ini
        with open(batoceraFiles.dolphinGfxIni, 'w') as configfile:
            dolphinGFXSettings.write(configfile)

        # update SYSCONF
        try:
            dolphinSYSCONF.update(system.config, batoceraFiles.dolphinSYSCONF, gameResolution)
        except Exception:
            pass # don't fail in case of SYSCONF update

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-platform", "xcb", "-e", rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.SAVES})

def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9  ; 0: auto
    if "ratio" in config:
        if config["ratio"] == "4/3":
            return 2
        if config["ratio"] == "16/9":
            return 1
    return 0

# seem to be only for the gamecube. However, while this is not in a gamecube section
# it may be used for something else, so set it anyway

def getGameCubeLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": 0, "de_DE": 1, "fr_FR": 2, "es_ES": 3, "it_IT": 4, "nl_NL": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
