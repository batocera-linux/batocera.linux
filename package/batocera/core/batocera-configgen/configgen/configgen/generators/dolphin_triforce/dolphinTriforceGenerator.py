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

        #dolphinTriforceControllers.generateControllerConfig(system, playersControllers, rom)
        # Workaround to at least have X-input controllers working by default
        if not os.path.exists(batoceraFiles.dolphinTriforceConfig + "/Config/GCPadNew.ini"):
            dolphinTriforceGCPad = open(batoceraFiles.dolphinTriforceConfig + "/Config/GCPadNew.ini", "w")
            dolphinTriforceGCPad.write("""[GCPad1]
Device = SDL/0/Microsoft X-Box 360 pad
Buttons/A = `Button 0`
Buttons/B = `Button 2`
Buttons/Y = `Button 1`
Buttons/Z = `Button 5`
Buttons/Start = `Button 7`
Main Stick/Up = `Axis 1-`
Main Stick/Down = `Axis 1+`
Main Stick/Left = `Axis 0-`
Main Stick/Right = `Axis 0+`
C-Stick/Up = `Axis 4-`
C-Stick/Down = `Axis 4+`
C-Stick/Left = `Axis 3-`
C-Stick/Right = `Axis 3+`
Triggers/L-Analog = `Axis 2+`
Triggers/R-Analog = `Axis 5-+`
D-Pad/Up = `Hat 0 N`
D-Pad/Down = `Hat 0 S`
D-Pad/Left = `Hat 0 W`
D-Pad/Right = `Hat 0 E`
""")
            dolphinTriforceGCPad.close()

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
        if "GCMPathes" not in dolphinTriforceSettings["General"]:
            dolphinTriforceSettings.set("General", "GCMPath0", "/userdata/roms/triforce")
            dolphinTriforceSettings.set("General", "GCMPathes", "1")

        # Save file location
        if "MemcardAPath" not in dolphinTriforceSettings["Core"]:
            dolphinTriforceSettings.set("Core", "MemcardAPath", "/userdata/saves/dolphin-triforce/GC/MemoryCardA.USA.raw")
            dolphinTriforceSettings.set("Core", "MemcardBPath", "/userdata/saves/dolphin-triforce/GC/MemoryCardB.USA.raw")

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
        dolphinTriforceSettings.set("Display", "RenderToMain", "False")
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

        ## game settings ##

        # These cheat files are required to launch Triforce games, and thus should always be present and enabled.

        if not os.path.exists(batoceraFiles.dolphinTriforceGameSettings):
            os.makedirs(batoceraFiles.dolphinTriforceGameSettings)

        # GGPE01 Mario Kart GP 1

        if not os.path.exists(batoceraFiles.dolphinTriforceGameSettings + "/GGPE01.ini"):
            dolphinTriforceGameSettingsGGPE01 = open(batoceraFiles.dolphinTriforceGameSettings + "/GGPE01.ini", "w")
            dolphinTriforceGameSettingsGGPE01.write("""[OnFrame]
$1 credits
0x80690AC0:dword:0x00000001
$Emulation Bug Fixes
0x800319D0:dword:0x60000000
0x80031BF0:dword:0x60000000
0x80031BFC:dword:0x60000000
0x800BE10C:dword:0x4800002C
0x800790A0:dword:0x98650025
[OnFrame_Enabled]
$1 credits
$Emulation Bug Fixes
""")
            dolphinTriforceGameSettingsGGPE01.close()

        # GGPE02 Mario Kart GP 2

        if not os.path.exists(batoceraFiles.dolphinTriforceGameSettings + "/GGPE02.ini"):
            dolphinTriforceGameSettingsGGPE02 = open(batoceraFiles.dolphinTriforceGameSettings + "/GGPE02.ini", "w")
            dolphinTriforceGameSettingsGGPE02.write("""[Display]
ProgressiveScan = 0
[Wii]
Widescreen = False
DisableWiimoteSpeaker = 0
[Video]
PH_SZNear = 1
[EmuState]
EmulationStateId = 3
[OnFrame]
$DI Seed Blanker
0x80000000:dword:0x00000000
0x80000004:dword:0x00000000
0x80000008:dword:0x00000000
$DVDInquiry Patchok
0x80286388:dword:0x3C602100
0x8028638C:dword:0x4E800020
$Ignore CMD Encryption
0x80285CD0:dword:0x93A30008
0x80285CD4:dword:0x93C3000C
0x80285CD8:dword:0x93E30010
$Disable CARD
0x80073BF4:dword:0x98650023
0x80073C10:dword:0x98650023
$Disable CAM
0x80073BD8:dword:0x98650025
$Seat Loop patch
0x800BE10C:dword:0x4800002C
$Stuck loop patch
0x8002E100:dword:0x60000000
$60times Loop patch
0x8028B5D4:dword:0x60000000
$GameTestMode Patch
0x8002E340:dword:0x60000000
0x8002E34C:dword:0x60000000
$SeatLoopPatch
0x80084FC4:dword:0x4800000C
0x80085000:dword:0x60000000
$99 credits
0x80690AC0:dword:0x00000063
[OnFrame_Enabled]
$DI Seed Blanker
$DVDInquiry Patchok
$Ignore CMD Encryption
$Disable CARD
$Disable CAM
$Seat Loop patch
$Stuck loop patch
$60times Loop patch
$GameTestMode Patch
$SeatLoopPatch
$99 credits
""")
            dolphinTriforceGameSettingsGGPE02.close()
        
        # # Cheats aren't in key = value format, so the allow_no_value option is needed.
        # dolphinTriforceGameSettingsGGPE01 = configparser.ConfigParser(interpolation=None, allow_no_value=True,delimiters=';')
        # # To prevent ConfigParser from converting to lower case
        # dolphinTriforceGameSettingsGGPE01.optionxform = str
        # if os.path.exists(batoceraFiles.dolphinTriforceGameSettings + "/GGPE01.ini"):
            # dolphinTriforceGameSettingsGGPE01.read(batoceraFiles.dolphinTriforceGameSettings + "/GGPE01.ini")

        # # GGPE01 sections
        # if not dolphinTriforceGameSettingsGGPE01.has_section("OnFrame"):
            # dolphinTriforceGameSettingsGGPE01.add_section("OnFrame")
        # if not dolphinTriforceGameSettingsGGPE01.has_section("OnFrame_Enabled"):
            # dolphinTriforceGameSettingsGGPE01.add_section("OnFrame_Enabled")

        # # GGPE01 cheats
        # if "$1 credits" not in dolphinTriforceGameSettingsGGPE01["OnFrame"]:
            # dolphinTriforceGameSettingsGGPE01.set("OnFrame", "$1 credits\n0x80690AC0:dword:0x00000001")
        # if "$Emulation Bug Fixes" not in dolphinTriforceGameSettingsGGPE01["OnFrame"]:
            # dolphinTriforceGameSettingsGGPE01.set("OnFrame", "$Emulation Bug Fixes\n0x800319D0:dword:0x60000000\n0x80031BF0:dword:0x60000000\n0x80031BFC:dword::0x60000000\n0x800BE10C:dword:0x4800002C\n0x800790A0:dword:0x98650025")
        # if "$1 credits" not in dolphinTriforceGameSettingsGGPE01["OnFrame_Enabled"]:
            # dolphinTriforceGameSettingsGGPE01.set("OnFrame_Enabled", "$1 credits")
        # if "$Emulation Bug Fixes" not in dolphinTriforceGameSettingsGGPE01["OnFrame_Enabled"]:
            # dolphinTriforceGameSettingsGGPE01.set("OnFrame_Enabled", "$Emulation Bug Fixes")

        # # Save GGPE01.ini
        # with open(batoceraFiles.dolphinTriforceGameSettings + "/GGPE01.ini", 'w') as configfile:
            # dolphinTriforceGameSettingsGGPE01.write(configfile)

        commandArray = ["dolphin-triforce.AppImage", "-U", "/userdata/system/configs/dolphin-triforce", "-e", rom]
        if system.isOptSet('platform'):
            commandArray = ["dolphin-triforce.AppImage-nogui", "-U", "/userdata/system/configs/dolphin-triforce", "-p", system.config["platform"], "-e", rom]

        # No environment variables work for now, paths are coded in above.
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})
        #return Command.Command(array=commandArray)
            
    def getInGameRatio(self, config, gameResolution, rom):
        if 'dolphin_aspect_ratio' in config:
            if config['dolphin_aspect_ratio'] == "1":
                return 16/9
            elif config['dolphin_aspect_ratio'] == "3" and (gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1)):
                return 16/9
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
