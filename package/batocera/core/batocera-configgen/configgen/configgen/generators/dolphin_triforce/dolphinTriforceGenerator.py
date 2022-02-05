#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
from os import environ
import configparser
from . import dolphinTriforceControllers

class DolphinTriforceGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(os.path.dirname(batoceraFiles.dolphinTriforceIni)):
            os.makedirs(os.path.dirname(batoceraFiles.dolphinTriforceIni))

        # Dir required for saves
        if not os.path.exists(batoceraFiles.dolphinTriforceData + "/StateSaves"):
            os.makedirs(batoceraFiles.dolphinTriforceData + "/StateSaves")

        dolphinTriforceControllers.generateControllerConfig(system, playersControllers, rom)

        ## dolphin.ini ##

        dolphinTriforceSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinTriforceSettings.optionxform = str
        if os.path.exists(batoceraFiles.dolphinTriforceIni):
            dolphinTriforceSettings.read(batoceraFiles.dolphinTriforceIni)

        # Sections
        if not dolphinTriforceSettings.has_section("General"):
            dolphinTriforceSettings.add_section("General")
        if not dolphinTriforceSettings.has_section("Core"):
            dolphinTriforceSettings.add_section("Core")
        if not dolphinTriforceSettings.has_section("Interface"):
            dolphinTriforceSettings.add_section("Interface")
        if not dolphinTriforceSettings.has_section("Analytics"):
            dolphinTriforceSettings.add_section("Analytics")
        if not dolphinTriforceSettings.has_section("Display"):
            dolphinTriforceSettings.add_section("Display")

        # Define default games path
        if "ISOPaths" not in dolphinTriforceSettings["General"]:
            dolphinTriforceSettings.set("General", "ISOPath0", "/userdata/roms/triforce")
            dolphinTriforceSettings.set("General", "ISOPaths", "1")

        # Draw or not FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinTriforceSettings.set("General", "ShowLag",        "True")
            dolphinTriforceSettings.set("General", "ShowFrameCount", "True")
        else:
            dolphinTriforceSettings.set("General", "ShowLag",        "False")
            dolphinTriforceSettings.set("General", "ShowFrameCount", "False")

        # Don't ask about statistics
        dolphinTriforceSettings.set("Analytics", "PermissionAsked", "True")

        # PanicHandlers displaymessages
        dolphinTriforceSettings.set("Interface", "UsePanicHandlers",        "False")
        dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", "True")

        # Don't confirm at stop
        dolphinTriforceSettings.set("Interface", "ConfirmStop", "False")

        # only 1 window (fixes exit and gui display)
        dolphinTriforceSettings.set("Display", "RenderToMain", "True")
        dolphinTriforceSettings.set("Display", "Fullscreen", "True")

        # Enable Cheats
        dolphinTriforceSettings.set("Core", "EnableCheats", "True")

        # Dual Core
        if system.isOptSet("dual_core") and system.getOptBoolean("dual_core"):
            dolphinTriforceSettings.set("Core", "CPUThread", "True")
        else:
            dolphinTriforceSettings.set("Core", "CPUThread", "False")

        # Gpu Sync
        if system.isOptSet("gpu_sync") and system.getOptBoolean("gpu_sync"):
            dolphinTriforceSettings.set("Core", "SyncGPU", "True")
        else:
            dolphinTriforceSettings.set("Core", "SyncGPU", "False")

        # Language
        dolphinTriforceSettings.set("Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment())) # Wii
        dolphinTriforceSettings.set("Core", "GameCubeLanguage", str(getGameCubeLangFromEnvironment())) # GC

        # Enable MMU
        if system.isOptSet("enable_mmu") and system.getOptBoolean("enable_mmu"):
            dolphinTriforceSettings.set("Core", "MMU", "True")
        else:
            dolphinTriforceSettings.set("Core", "MMU", "False")

        # Backend - Default OpenGL
        dolphinTriforceSettings.set("Core", "GFXBackend", "OGL")

        # Serial Port 1 to AM-Baseband
        dolphinTriforceSettings.set("Core", "SerialPort1", "6")

        # Gamecube pads forced as AM-Baseband
        dolphinTriforceSettings.set("Core", "SIDevice0", "11")

        # Save dolphin.ini
        with open(batoceraFiles.dolphinTriforceIni, 'w') as configfile:
            dolphinTriforceSettings.write(configfile)

        ## gfx.ini ##

        dolphinTriforceGFXSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinTriforceGFXSettings.optionxform = str
        dolphinTriforceGFXSettings.read(batoceraFiles.dolphinTriforceGfxIni)

        # Add Default Sections
        if not dolphinTriforceGFXSettings.has_section("Settings"):
            dolphinTriforceGFXSettings.add_section("Settings")
        if not dolphinTriforceGFXSettings.has_section("Hacks"):
            dolphinTriforceGFXSettings.add_section("Hacks")
        if not dolphinTriforceGFXSettings.has_section("Enhancements"):
            dolphinTriforceGFXSettings.add_section("Enhancements")             
        if not dolphinTriforceGFXSettings.has_section("Hardware"):
            dolphinTriforceGFXSettings.add_section("Hardware")  
            
        # Graphics setting Aspect Ratio
        if system.isOptSet('dolphin_aspect_ratio'):
            dolphinTriforceGFXSettings.set("Settings", "AspectRatio", system.config["dolphin_aspect_ratio"])
        else:
            # set to zero, which is 'Auto' in Dolphin & Batocera
            dolphinTriforceGFXSettings.set("Settings", "AspectRatio", "0")
        
        # Show fps
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinTriforceGFXSettings.set("Settings", "ShowFPS", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "ShowFPS", "False")

        # HiResTextures
        if system.isOptSet('hires_textures') and system.getOptBoolean('hires_textures'):
            dolphinTriforceGFXSettings.set("Settings", "HiresTextures",      "True")
            dolphinTriforceGFXSettings.set("Settings", "CacheHiresTextures", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "HiresTextures",      "False")
            dolphinTriforceGFXSettings.set("Settings", "CacheHiresTextures", "False")

        # Widescreen Hack
        if system.isOptSet('widescreen_hack') and system.getOptBoolean('widescreen_hack'):
            # Prefer Cheats than Hack 
            if system.isOptSet('enable_cheats') and system.getOptBoolean('enable_cheats'):
                dolphinTriforceGFXSettings.set("Settings", "wideScreenHack", "False")
            else:
                dolphinTriforceGFXSettings.set("Settings", "wideScreenHack", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "wideScreenHack", "False")

        # Ubershaders (synchronous_ubershader by default)
        if system.isOptSet('ubershaders') and system.config["ubershaders"] != "no_ubershader":
            if system.config["ubershaders"] == "exclusive_ubershader":
                dolphinTriforceGFXSettings.set("Settings", "ShaderCompilationMode", "1")
            elif system.config["ubershaders"] == "hybrid_ubershader":
                dolphinTriforceGFXSettings.set("Settings", "ShaderCompilationMode", "2")
            elif system.config["ubershaders"] == "skip_draw":
                dolphinTriforceGFXSettings.set("Settings", "ShaderCompilationMode", "3")
        else:
            dolphinTriforceGFXSettings.set("Settings", "ShaderCompilationMode", "0")

        # Shader pre-caching
        if system.isOptSet('wait_for_shaders') and system.getOptBoolean('wait_for_shaders'):
            dolphinTriforceGFXSettings.set("Settings", "WaitForShadersBeforeStarting", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "WaitForShadersBeforeStarting", "False")

        # Various performance hacks - Default Off
        if system.isOptSet('perf_hacks') and system.getOptBoolean('perf_hacks'):
            dolphinTriforceGFXSettings.set("Hacks", "BBoxEnable", "False")
            dolphinTriforceGFXSettings.set("Hacks", "DeferEFBCopies", "True")
            dolphinTriforceGFXSettings.set("Hacks", "EFBEmulateFormatChanges", "False")
            dolphinTriforceGFXSettings.set("Hacks", "EFBScaledCopy", "True")
            dolphinTriforceGFXSettings.set("Hacks", "EFBToTextureEnable", "True")
            dolphinTriforceGFXSettings.set("Hacks", "SkipDuplicateXFBs", "True")
            dolphinTriforceGFXSettings.set("Hacks", "XFBToTextureEnable", "True")
            dolphinTriforceGFXSettings.set("Enhancements", "ForceFiltering", "True")
            dolphinTriforceGFXSettings.set("Enhancements", "ArbitraryMipmapDetection", "True")
            dolphinTriforceGFXSettings.set("Enhancements", "DisableCopyFilter", "True")
            dolphinTriforceGFXSettings.set("Enhancements", "ForceTrueColor", "True")            
        else:
            if dolphinTriforceGFXSettings.has_section("Hacks"):
                dolphinTriforceGFXSettings.remove_option("Hacks", "BBoxEnable")
                dolphinTriforceGFXSettings.remove_option("Hacks", "DeferEFBCopies")
                dolphinTriforceGFXSettings.remove_option("Hacks", "EFBEmulateFormatChanges")
                dolphinTriforceGFXSettings.remove_option("Hacks", "EFBScaledCopy")
                dolphinTriforceGFXSettings.remove_option("Hacks", "EFBToTextureEnable")
                dolphinTriforceGFXSettings.remove_option("Hacks", "SkipDuplicateXFBs")
                dolphinTriforceGFXSettings.remove_option("Hacks", "XFBToTextureEnable")
            if dolphinTriforceGFXSettings.has_section("Enhancements"):
                dolphinTriforceGFXSettings.remove_option("Enhancements", "ForceFiltering")
                dolphinTriforceGFXSettings.remove_option("Enhancements", "ArbitraryMipmapDetection")
                dolphinTriforceGFXSettings.remove_option("Enhancements", "DisableCopyFilter")
                dolphinTriforceGFXSettings.remove_option("Enhancements", "ForceTrueColor")  

        # Internal resolution settings
        if system.isOptSet('internal_resolution'):
            dolphinTriforceGFXSettings.set("Settings", "InternalResolution", system.config["internal_resolution"])
        else:
            dolphinTriforceGFXSettings.set("Settings", "InternalResolution", "1")

        # VSync
        if system.isOptSet('vsync'):
            dolphinTriforceGFXSettings.set("Hardware", "VSync", str(system.getOptBoolean('vsync')))
        else:
            dolphinTriforceGFXSettings.set("Hardware", "VSync", "True")

        # Anisotropic filtering
        if system.isOptSet('anisotropic_filtering'):
            dolphinTriforceGFXSettings.set("Enhancements", "MaxAnisotropy", system.config["anisotropic_filtering"])
        else:
            dolphinTriforceGFXSettings.set("Enhancements", "MaxAnisotropy", "0")

        # Anti aliasing
        if system.isOptSet('antialiasing'):
            dolphinTriforceGFXSettings.set("Settings", "MSAA", system.config["antialiasing"])
        else:
            dolphinTriforceGFXSettings.set("Settings", "MSAA", "0")

        # Anti aliasing mode
        if system.isOptSet('use_ssaa') and system.getOptBoolean('use_ssaa'):
            dolphinTriforceGFXSettings.set("Settings", "SSAA", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "SSAA", "False")

        # Save gfx.ini
        with open(batoceraFiles.dolphinTriforceGfxIni, 'w') as configfile:
            dolphinTriforceGFXSettings.write(configfile)

        commandArray = ["dolphin-triforce.AppImage", "-e", rom]
        if system.isOptSet('platform'):
            commandArray = ["dolphin-triforce.AppImage-nogui", "-p", system.config["platform"], "-e", rom]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})
            
    def getInGameRatio(self, config, gameResolution, rom):
        return 4/3

# Seem to be only for the gamecube. However, while this is not in a gamecube section
# It may be used for something else, so set it anyway
def getGameCubeLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": 0, "de_DE": 1, "fr_FR": 2, "es_ES": 3, "it_IT": 4, "nl_NL": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
