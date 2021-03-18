#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
from os import environ
import configparser
from . import dolphinControllers
from . import dolphinSYSCONF

class DolphinGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(os.path.dirname(batoceraFiles.dolphinIni)):
            os.makedirs(os.path.dirname(batoceraFiles.dolphinIni))

        # Dir required for saves
        if not os.path.exists(batoceraFiles.dolphinData + "/StateSaves"):
            os.makedirs(batoceraFiles.dolphinData + "/StateSaves")

        dolphinControllers.generateControllerConfig(system, playersControllers, rom)

        ## dolphin.ini ##

        dolphinSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinSettings.optionxform = str
        if os.path.exists(batoceraFiles.dolphinIni):
            dolphinSettings.read(batoceraFiles.dolphinIni)

        # Sections
        if not dolphinSettings.has_section("General"):
            dolphinSettings.add_section("General")
        if not dolphinSettings.has_section("Core"):
            dolphinSettings.add_section("Core")
        if not dolphinSettings.has_section("Interface"):
            dolphinSettings.add_section("Interface")
        if not dolphinSettings.has_section("Analytics"):
            dolphinSettings.add_section("Analytics")

        # Draw or not FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinSettings.set("General", "ShowLag",        '"True"')
            dolphinSettings.set("General", "ShowFrameCount", '"True"')
        else:
            dolphinSettings.set("General", "ShowLag",        '"False"')
            dolphinSettings.set("General", "ShowFrameCount", '"False"')

        # Don't ask about statistics
        dolphinSettings.set("Analytics", "PermissionAsked", '"True"')

        # PanicHandlers displaymessages
        dolphinSettings.set("Interface", "UsePanicHandlers",        '"False"')
        dolphinSettings.set("Interface", "OnScreenDisplayMessages", '"True"')

        # Don't confirm at stop
        dolphinSettings.set("Interface", "ConfirmStop", '"False"')

        # Enable Cheats
        if system.isOptSet("enable_cheats") and system.getOptBoolean("enable_cheats"):
            dolphinSettings.set("Core", "EnableCheats", '"True"')
        else:
            dolphinSettings.set("Core", "EnableCheats", '"False"')

        # Speed up disc transfert rate
        if system.isOptSet("enable_fastdisc") and system.getOptBoolean("enable_fastdisc"):
            dolphinSettings.set("Core", "FastDiscSpeed", '"True"')
        else:
            dolphinSettings.set("Core", "FastDiscSpeed", '"False"')

        # Dual Core
        if system.isOptSet("dual_core") and not system.getOptBoolean("dual_core"):
            dolphinSettings.set("Core", "CPUThread", '"False"')
        else:
            dolphinSettings.set("Core", "CPUThread", '"True"')

        # Gpu Sync
        if system.isOptSet("gpu_sync") and system.getOptBoolean("gpu_sync"):
            dolphinSettings.set("Core", "SyncGPU", '"True"')
        else:
            dolphinSettings.set("Core", "SyncGPU", '"False"')

        # Language (for gamecube at least)
        dolphinSettings.set("Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment()))
        dolphinSettings.set("Core", "GameCubeLanguage", str(getGameCubeLangFromEnvironment()))

        # Enable MMU
        if system.isOptSet("enable_mmu") and system.getOptBoolean("enable_mmu"):
            dolphinSettings.set("Core", "MMU", '"True"')
        else:
            dolphinSettings.set("Core", "MMU", '"False"')

        # Backend - Default OpenGL
        if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == 'Vulkan':
            dolphinSettings.set("Core", "GFXBackend", '"Vulkan"')
        else:
            dolphinSettings.set("Core", "GFXBackend", '"OGL"')

        # Wiimote scanning
        dolphinSettings.set("Core", "WiimoteContinuousScanning", '"True"')

        # Gamecube pads forced as standard pad
        dolphinSettings.set("Core", "SIDevice0", '"6"')
        dolphinSettings.set("Core", "SIDevice1", '"6"')
        dolphinSettings.set("Core", "SIDevice2", '"6"')
        dolphinSettings.set("Core", "SIDevice3", '"6"')

        # Save dolphin.ini
        with open(batoceraFiles.dolphinIni, 'w') as configfile:
            dolphinSettings.write(configfile)

        ## gfx.ini ##

        dolphinGFXSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinGFXSettings.optionxform = str
        dolphinGFXSettings.read(batoceraFiles.dolphinGfxIni)

        # Add Default Sections
        if not dolphinGFXSettings.has_section("Settings"):
            dolphinGFXSettings.add_section("Settings")
        if not dolphinGFXSettings.has_section("Hacks"):
            dolphinGFXSettings.add_section("Hacks")
        if not dolphinGFXSettings.has_section("Enhancements"):
            dolphinGFXSettings.add_section("Enhancements")             
        if not dolphinGFXSettings.has_section("Hardware"):
            dolphinGFXSettings.add_section("Hardware")  
            
        dolphinGFXSettings.set("Settings", "AspectRatio", str(getGfxRatioFromConfig(system.config, gameResolution)))

        # Show fps
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinGFXSettings.set("Settings", "ShowFPS", '"True"')
        else:
            dolphinGFXSettings.set("Settings", "ShowFPS", '"False"')

        # HiResTextures
        if system.isOptSet('hires_textures') and not system.getOptBoolean('hires_textures'):
            dolphinGFXSettings.set("Settings", "HiresTextures",      '"False"')
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", '"False"')
        else:
            dolphinGFXSettings.set("Settings", "HiresTextures",      '"True"')
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", '"True"')

        # Widescreen Hack
        if system.isOptSet('widescreen_hack') and system.getOptBoolean('widescreen_hack'):
            # Prefer Cheats than Hack 
            if system.isOptSet('enable_cheats') and system.getOptBoolean('enable_cheats'):
                dolphinGFXSettings.set("Settings", "wideScreenHack", '"False"')
            else:
                dolphinGFXSettings.set("Settings", "wideScreenHack", '"True"')
        else:
            dolphinGFXSettings.set("Settings", "wideScreenHack", '"False"')

        # Various performance hacks - Default Off
        if system.isOptSet('perf_hacks') and system.getOptBoolean('perf_hacks'):
            dolphinGFXSettings.set("Hacks", "BBoxEnable", '"False"')
            dolphinGFXSettings.set("Hacks", "DeferEFBCopies", '"True"')
            dolphinGFXSettings.set("Hacks", "EFBEmulateFormatChanges", '"False"')
            dolphinGFXSettings.set("Hacks", "EFBScaledCopy", '"True"')
            dolphinGFXSettings.set("Hacks", "EFBToTextureEnable", '"True"')
            dolphinGFXSettings.set("Hacks", "SkipDuplicateXFBs", '"True"')
            dolphinGFXSettings.set("Hacks", "XFBToTextureEnable", '"True"')
            dolphinGFXSettings.set("Enhancements", "ForceFiltering", '"True"')
            dolphinGFXSettings.set("Enhancements", "ArbitraryMipmapDetection", '"True"')
            dolphinGFXSettings.set("Enhancements", "DisableCopyFilter", '"True"')
            dolphinGFXSettings.set("Enhancements", "ForceTrueColor", '"True"')            
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

        # Internal resolution settings
        if system.isOptSet('internalresolution'):
            dolphinGFXSettings.set("Settings", "InternalResolution", system.config["internalresolution"])
        else:
            dolphinGFXSettings.set("Settings", "InternalResolution", '"1"')

        # VSync
        if system.isOptSet('vsync'):
            dolphinGFXSettings.set("Hardware", "VSync", str(system.getOptBoolean('vsync')))
        else:
            dolphinGFXSettings.set("Hardware", "VSync", '"True"')

        # Anisotropic filtering
        if system.isOptSet('anisotropic_filtering'):
            dolphinGFXSettings.set("Enhancements", "MaxAnisotropy", system.config["anisotropic_filtering"])
        else:
            dolphinGFXSettings.set("Enhancements", "MaxAnisotropy", '"0"')

		# Anti aliasing
        if system.isOptSet('antialiasing'):
            dolphinGFXSettings.set("Settings", "MSAA", system.config["antialiasing"])
        else:
            dolphinGFXSettings.set("Settings", "MSAA", '"0"')

		# Save gfx.ini
        with open(batoceraFiles.dolphinGfxIni, 'w') as configfile:
            dolphinGFXSettings.write(configfile)

        # Update SYSCONF
        try:
            dolphinSYSCONF.update(system.config, batoceraFiles.dolphinSYSCONF, gameResolution)
        except Exception:
            pass # don't fail in case of SYSCONF update

        commandArray = ["dolphin-emu", "-e", rom]
        if system.isOptSet('platform'):
            commandArray = ["dolphin-emu-nogui", "-p", system.config["platform"], "-e", rom]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})


def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9  ; 0: auto
    if "ratio" in config:
        if config["ratio"] == "4/3":
            return 2
        if config["ratio"] == "16/9":
            return 1
    return 0

# Seem to be only for the gamecube. However, while this is not in a gamecube section
# It may be used for something else, so set it anyway
def getGameCubeLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": 0, "de_DE": 1, "fr_FR": 2, "es_ES": 3, "it_IT": 4, "nl_NL": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
