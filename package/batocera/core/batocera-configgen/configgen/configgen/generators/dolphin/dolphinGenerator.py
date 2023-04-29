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
import controllersConfig

class DolphinGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        if not os.path.exists(os.path.dirname(batoceraFiles.dolphinIni)):
            os.makedirs(os.path.dirname(batoceraFiles.dolphinIni))

        # Dir required for saves
        if not os.path.exists(batoceraFiles.dolphinData + "/StateSaves"):
            os.makedirs(batoceraFiles.dolphinData + "/StateSaves")
        
        # Generate the controller config(s)
        dolphinControllers.generateControllerConfig(system, playersControllers, rom, guns)

        ## [ dolphin.ini ] ##
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
        if not dolphinSettings.has_section("Display"):
            dolphinSettings.add_section("Display")
        if not dolphinSettings.has_section("GBA"):
            dolphinSettings.add_section("GBA")

        # Define default games path
        if "ISOPaths" not in dolphinSettings["General"]:
            dolphinSettings.set("General", "ISOPath0", "/userdata/roms/wii")
            dolphinSettings.set("General", "ISOPath1", "/userdata/roms/gamecube")
            dolphinSettings.set("General", "ISOPaths", "2")

        # Draw or not FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinSettings.set("General", "ShowLag",        "True")
            dolphinSettings.set("General", "ShowFrameCount", "True")
        else:
            dolphinSettings.set("General", "ShowLag",        "False")
            dolphinSettings.set("General", "ShowFrameCount", "False")

        # Don't ask about statistics
        dolphinSettings.set("Analytics", "PermissionAsked", "True")

        # PanicHandlers displaymessages
        dolphinSettings.set("Interface", "UsePanicHandlers",        "False")
        dolphinSettings.set("Interface", "OnScreenDisplayMessages", "True")

        # Don't confirm at stop
        dolphinSettings.set("Interface", "ConfirmStop", "False")

        # only 1 window (fixes exit and gui display)
        dolphinSettings.set("Display", "RenderToMain", "True")
        dolphinSettings.set("Display", "Fullscreen", "True")

        # Enable Cheats
        if system.isOptSet("enable_cheats") and system.getOptBoolean("enable_cheats"):
            dolphinSettings.set("Core", "EnableCheats", "True")
        else:
            dolphinSettings.set("Core", "EnableCheats", "False")

        # Speed up disc transfer rate
        if system.isOptSet("enable_fastdisc") and system.getOptBoolean("enable_fastdisc"):
            dolphinSettings.set("Core", "FastDiscSpeed", "True")
        else:
            dolphinSettings.set("Core", "FastDiscSpeed", "False")

        # Dual Core
        if system.isOptSet("dual_core") and system.getOptBoolean("dual_core"):
            dolphinSettings.set("Core", "CPUThread", "True")
        else:
            dolphinSettings.set("Core", "CPUThread", "False")

        # Gpu Sync
        if system.isOptSet("gpu_sync") and system.getOptBoolean("gpu_sync"):
            dolphinSettings.set("Core", "SyncGPU", "True")
        else:
            dolphinSettings.set("Core", "SyncGPU", "False")

        # Language
        dolphinSettings.set("Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment())) # Wii
        dolphinSettings.set("Core", "GameCubeLanguage", str(getGameCubeLangFromEnvironment())) # GC

        # Enable MMU
        if system.isOptSet("enable_mmu") and system.getOptBoolean("enable_mmu"):
            dolphinSettings.set("Core", "MMU", "True")
        else:
            dolphinSettings.set("Core", "MMU", "False")

        # Backend - Default OpenGL
        if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == 'Vulkan':
            dolphinSettings.set("Core", "GFXBackend", "Vulkan")
        else:
            dolphinSettings.set("Core", "GFXBackend", "OGL")

        # Wiimote scanning
        dolphinSettings.set("Core", "WiimoteContinuousScanning", "True")

        # Gamecube ports
        # Create a for loop going 1 through to 4 and iterate through it:
        for i in range(1,5):
            if system.isOptSet("dolphin_port_" + str(i) + "_type"):
                # Sub in the appropriate values from es_features, accounting for the 1 integer difference.
                dolphinSettings.set("Core", "SIDevice" + str(i - 1), system.config["dolphin_port_" + str(i) + "_type"])
            else:
                dolphinSettings.set("Core", "SIDevice" + str(i - 1), "6")

        # HiResTextures for guns part 1/2 (see below the part 2)
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0 and ((system.isOptSet('dolphin-lightgun-hide-crosshair') == False and controllersConfig.gunsNeedCrosses(guns) == False) or system.getOptBoolean('dolphin-lightgun-hide-crosshair' == True)):
            dolphinSettings.set("General", "CustomTexturesPath", "/usr/share/DolphinCrosshairsPack")
        else:
            dolphinSettings.remove_option("General", "CustomTexturesPath")

        # Change discs automatically
        dolphinSettings.set("Core", "AutoDiscChange", "True")

        # Save dolphin.ini
        with open(batoceraFiles.dolphinIni, 'w') as configfile:
            dolphinSettings.write(configfile)

        ## [ gfx.ini ] ##
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

        # Graphics setting Aspect Ratio
        if system.isOptSet('dolphin_aspect_ratio'):
            dolphinGFXSettings.set("Settings", "AspectRatio", system.config["dolphin_aspect_ratio"])
        else:
            # set to zero, which is 'Auto' in Dolphin & Batocera
            dolphinGFXSettings.set("Settings", "AspectRatio", "0")

        # Show fps
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinGFXSettings.set("Settings", "ShowFPS", "True")
        else:
            dolphinGFXSettings.set("Settings", "ShowFPS", "False")

        # HiResTextures
        if system.isOptSet('hires_textures') and system.getOptBoolean('hires_textures'):
            dolphinGFXSettings.set("Settings", "HiresTextures",      "True")
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", "True")
        else:
            dolphinGFXSettings.set("Settings", "HiresTextures",      "False")
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", "False")

        # HiResTextures for guns part 2/2 (see upper part1)
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0 and (system.isOptSet('dolphin-lightgun-hide-crosshair') == False or system.getOptBoolean('dolphin-lightgun-hide-crosshair' == True)):
            # erase what can be set by the option hires_textures
            dolphinGFXSettings.set("Settings", "HiresTextures",      "True")
            dolphinGFXSettings.set("Settings", "CacheHiresTextures", "True")

        # Widescreen Hack
        if system.isOptSet('widescreen_hack') and system.getOptBoolean('widescreen_hack'):
            # Prefer Cheats than Hack
            if system.isOptSet('enable_cheats') and system.getOptBoolean('enable_cheats'):
                dolphinGFXSettings.set("Settings", "wideScreenHack", "False")
            else:
                dolphinGFXSettings.set("Settings", "wideScreenHack", "True")
        else:
            dolphinGFXSettings.set("Settings", "wideScreenHack", "False")

        # Ubershaders (synchronous_ubershader by default)
        if system.isOptSet('ubershaders') and system.config["ubershaders"] != "no_ubershader":
            if system.config["ubershaders"] == "exclusive_ubershader":
                dolphinGFXSettings.set("Settings", "ShaderCompilationMode", "1")
            elif system.config["ubershaders"] == "hybrid_ubershader":
                dolphinGFXSettings.set("Settings", "ShaderCompilationMode", "2")
            elif system.config["ubershaders"] == "skip_draw":
                dolphinGFXSettings.set("Settings", "ShaderCompilationMode", "3")
        else:
            dolphinGFXSettings.set("Settings", "ShaderCompilationMode", "0")

        # Shader pre-caching
        if system.isOptSet('wait_for_shaders') and system.getOptBoolean('wait_for_shaders'):
            dolphinGFXSettings.set("Settings", "WaitForShadersBeforeStarting", "True")
        else:
            dolphinGFXSettings.set("Settings", "WaitForShadersBeforeStarting", "False")

        # Various performance hacks - Default Off
        if system.isOptSet('perf_hacks') and system.getOptBoolean('perf_hacks'):
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

        # Internal resolution settings
        if system.isOptSet('internal_resolution'):
            dolphinGFXSettings.set("Settings", "InternalResolution", system.config["internal_resolution"])
        else:
            dolphinGFXSettings.set("Settings", "InternalResolution", "1")

        # VSync
        if system.isOptSet('vsync'):
            dolphinGFXSettings.set("Hardware", "VSync", str(system.getOptBoolean('vsync')))
        else:
            dolphinGFXSettings.set("Hardware", "VSync", "True")

        # Anisotropic filtering
        if system.isOptSet('anisotropic_filtering'):
            dolphinGFXSettings.set("Enhancements", "MaxAnisotropy", system.config["anisotropic_filtering"])
        else:
            dolphinGFXSettings.set("Enhancements", "MaxAnisotropy", "0")

        # Anti aliasing
        if system.isOptSet('antialiasing'):
            dolphinGFXSettings.set("Settings", "MSAA", system.config["antialiasing"])
        else:
            dolphinGFXSettings.set("Settings", "MSAA", "0")

        # Anti aliasing mode
        if system.isOptSet('use_ssaa') and system.getOptBoolean('use_ssaa'):
            dolphinGFXSettings.set("Settings", "SSAA", "True")
        else:
            dolphinGFXSettings.set("Settings", "SSAA", "False")

        # Save gfx.ini
        with open(batoceraFiles.dolphinGfxIni, 'w') as configfile:
            dolphinGFXSettings.write(configfile)

        # Update SYSCONF
        try:
            dolphinSYSCONF.update(system.config, batoceraFiles.dolphinSYSCONF, gameResolution)
        except Exception:
            pass # don't fail in case of SYSCONF update

        # Check what version we've got
        if os.path.isfile("/usr/bin/dolphin-emu"):
            commandArray = ["dolphin-emu", "-e", rom]
        else:
            commandArray = ["dolphin-emu-nogui", "-e", rom]
        
        return Command.Command(array=commandArray, \
            env={ "XDG_CONFIG_HOME":batoceraFiles.CONF, \
            "XDG_DATA_HOME":batoceraFiles.SAVES, \
            "QT_QPA_PLATFORM":"xcb"})

    def getInGameRatio(self, config, gameResolution, rom):

        dolphinGFXSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinGFXSettings.optionxform = str
        dolphinGFXSettings.read(batoceraFiles.dolphinGfxIni)

        dolphin_aspect_ratio = dolphinGFXSettings.get("Settings", "AspectRatio")
        # What if we're playing a GameCube game with the widescreen patch or not?
        if 'widescreen_hack' in config and config["widescreen_hack"] == "1":
            wii_tv_mode = 1
        else:
            wii_tv_mode = 0

        try:
            wii_tv_mode = dolphinSYSCONF.getRatioFromConfig(config, gameResolution)
        except:
            pass

        # Auto
        if dolphin_aspect_ratio == "0":
            if wii_tv_mode == 1:
                return 16/9
            return 4/3

        # Forced 16:9
        if dolphin_aspect_ratio == "1":
            return 16/9

        # Forced 4:3
        if dolphin_aspect_ratio == "2":
            return 4/3

        # Stretched (thus depends on physical screen geometry)
        if dolphin_aspect_ratio == "3":
            return gameResolution["width"] / gameResolution["height"]

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
