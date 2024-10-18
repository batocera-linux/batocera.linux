from __future__ import annotations

from os import environ
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, mkdir_if_not_exists
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator
from . import dolphinTriforceControllers
from .dolphinTriforcePaths import (
    DOLPHIN_TRIFORCE_GAME_SETTINGS,
    DOLPHIN_TRIFORCE_GFX_INI,
    DOLPHIN_TRIFORCE_INI,
    DOLPHIN_TRIFORCE_LOGGER_INI,
    DOLPHIN_TRIFORCE_SAVES,
)

if TYPE_CHECKING:
    from ...types import HotkeysContext


class DolphinTriforceGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dolphin",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(DOLPHIN_TRIFORCE_INI.parent)

        # Dir required for saves
        mkdir_if_not_exists(DOLPHIN_TRIFORCE_SAVES / "StateSaves")

        dolphinTriforceControllers.generateControllerConfig(system, playersControllers, rom)

        ## dolphin.ini ##

        dolphinTriforceSettings = CaseSensitiveConfigParser(interpolation=None)
        if DOLPHIN_TRIFORCE_INI.exists():
            dolphinTriforceSettings.read(DOLPHIN_TRIFORCE_INI)

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

        # Disable OSD Messages
        if system.isOptSet("disable_osd_messages") and system.getOptBoolean("disable_osd_messages"):
            dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", "False")
        else:
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
        # F-Zero GX exception, it needs to not be using the AM-Baseband to function.
        # This cannot be set in the game's INI for some reason.
        if rom == "F-Zero GX (USA).iso":
            dolphinTriforceSettings.set("Core", "SerialPort1", "255")
        else:
            dolphinTriforceSettings.set("Core", "SerialPort1", "6")

        # Gamecube pads forced as AM-Baseband
        # F-Zero GX exception, it needs it to be a regular pad instead.
        if rom == "F-Zero GX (USA).iso":
            dolphinTriforceSettings.set("Core", "SIDevice0", "6")
        else:
            dolphinTriforceSettings.set("Core", "SIDevice0", "11")

        # Save dolphin.ini
        with DOLPHIN_TRIFORCE_INI.open('w') as configfile:
            dolphinTriforceSettings.write(configfile)

        ## gfx.ini ##

        dolphinTriforceGFXSettings = CaseSensitiveConfigParser(interpolation=None)
        dolphinTriforceGFXSettings.read(DOLPHIN_TRIFORCE_GFX_INI)

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
            dolphinTriforceGFXSettings.set("Settings", "EFBScale", system.config["internal_resolution"])
        else:
            dolphinTriforceGFXSettings.set("Settings", "EFBScale", "2")

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

        # Save gfx.ini
        with DOLPHIN_TRIFORCE_GFX_INI.open('w') as configfile:
            dolphinTriforceGFXSettings.write(configfile)

        ## logger settings ##

        dolphinTriforceLogSettings = CaseSensitiveConfigParser(interpolation=None)
        dolphinTriforceLogSettings.read(DOLPHIN_TRIFORCE_LOGGER_INI)

        # Sections
        if not dolphinTriforceLogSettings.has_section("Logs"):
            dolphinTriforceLogSettings.add_section("Logs")

        # Prevent the constant log spam.
        dolphinTriforceLogSettings.set("Logs", "DVD", "False")

        # Save Logger.ini
        with DOLPHIN_TRIFORCE_LOGGER_INI.open('w') as configfile:
            dolphinTriforceLogSettings.write(configfile)

        ## game settings ##

        # These cheat files are required to launch Triforce games, and thus should always be present and enabled.

        mkdir_if_not_exists(DOLPHIN_TRIFORCE_GAME_SETTINGS)

        # GFZE01 F-Zero GX (convert to F-Zero AX)
        GFZE01_ini = DOLPHIN_TRIFORCE_GAME_SETTINGS / "GFZE01.ini"
        if not GFZE01_ini.exists():
            dolphinTriforceGameSettingsGFZE01 = GFZE01_ini.open("w")
            dolphinTriforceGameSettingsGFZE01.write("""[Gecko]
$AX
06003F30 00000284
818D831C 280C0000
41820274 3C6C000B
3863FADC 3883000C
38A0000C 4BFFF5F5
3CAC0019 8085D550
64844001 9085D550
3CAC0018 BBC30040
BFC511DC 3C6C0010
A0032A86 280000A4
4082000C 380000A2
B0032A86 380000C0
98035D26 A0A32A7E
3C006000 280500AD
4082000C 3C8C0033
9004DE1C 28050010
408200CC 3C630022
90037B90 3C630003
3800002A B003C754
3800002C B003C758
38000029 B003C778
3800002B B003C77C
3C6C0034 3C006000
9003CE94 3C803C00
60803FA0 9003D000
60803FCC 9003D008
3C809001 608000D0
9003D004 608000D4
9003D00C 3C004800
6000010C 9003D010
3C003CE0 60004323
9003D024 3C0090E1
600000C8 9003D054
3C003800 6000007F
9003D11C 38003F40
B003D122 3C009061
600000EC 9003D124
3C804BFF 6080FEEC
9003D128 6080F9E8
9003D478 380000D7
98035817 3800002C
9803582B 280500AC
40820054 3C8C0032
3C003C60 60008000
90046E44 3C003863
60003F1E 90046E48
3C003806 60000001
90046E54 3C007000
6000FFFE 90046E5C
3C0080ED 60008A9C
90044A64 3C8C0033
3C00809F 600032C0
9004B5D0 280500B0
40820010 3C8C0033
80044E04 900D8A9C
2805009C 40820038
3C6C0032 38000002
98034FBB 9803509B
980351A7 980352DB
980353B3 3800000E
98034FFB 980350DF
980351E7 9803531B
980353F7 3C8C000C
38845404 38640028
38A00018 4BFFF415
38000001 980C0133
3C6CFFF8 3C003800
6000000D 9003FB50
3C808000 80043F24
28000000 4082001C
3C00000B 6000002E
90043F20 3C000039
6000001D 90043F24
3C6C0007 A0043F20
B0030CEE A0043F22
B0030CF6 A0043F24
B0030CFE 38003860
B0030D04 A0043F26
B0030D06 3C6C0009
3C004E80 60000020
90037428 80010014
48016DF4 00000000
0401AFA0 4BFE8F90
[Gecko_Enabled]
$AX
""")
            dolphinTriforceGameSettingsGFZE01.close()

        # GVSJ8P Virtua Striker 2002
        GVSJ8P_ini = DOLPHIN_TRIFORCE_GAME_SETTINGS / "GVSJ8P.ini"
        if not GVSJ8P_ini.exists():
            dolphinTriforceGameSettingsGVSJ8P = GVSJ8P_ini.open("w")
            dolphinTriforceGameSettingsGVSJ8P.write("""[OnFrame]
$DI Seed Blanker
0x80000000:dword:0x00000000
0x80000004:dword:0x00000000
0x80000008:dword:0x00000000
[OnFrame_Enabled]
$DI Seed Blanker
""")
            dolphinTriforceGameSettingsGVSJ8P.close()

        # GGPE01 Mario Kart GP 1

        GGPE01_ini = DOLPHIN_TRIFORCE_GAME_SETTINGS / "GGPE01.ini"
        if not GGPE01_ini.exists():
            dolphinTriforceGameSettingsGGPE01 = GGPE01_ini.open("w")
            dolphinTriforceGameSettingsGGPE01.write("""[OnFrame]
$Disable crypto
0x8023D828:dword:0x93A30008
0x8023D82C:dword:0x93C3000C
0x8023D830:dword:0x93E30010
0x8023E088:dword:0x4E800020
$Loop fix
0x800790A0:dword:0x98650025
0x8024F95C:dword:0x60000000
0x80031BF0:dword:0x60000000
0x80031BFC:dword:0x60000000
0x800BE10C:dword:0x4800002C
0x8009F1E0:dword:0x60000000
0x800319D0:dword:0x60000000
[OnFrame_Enabled]
$Disable crypto
$Loop fix
[EmuState]
EmulationIssues = AM-Baseboard
""")
            dolphinTriforceGameSettingsGGPE01.close()

        # GGPE02 Mario Kart GP 2

        GGPE02_ini = DOLPHIN_TRIFORCE_GAME_SETTINGS / "GGPE02.ini"
        if not GGPE02_ini.exists():
            dolphinTriforceGameSettingsGGPE02 = GGPE02_ini.open("w")
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
99 credits
""")
            dolphinTriforceGameSettingsGGPE02.close()

        # # Cheats aren't in key = value format, so the allow_no_value option is needed.
        # dolphinTriforceGameSettingsGGPE01 = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True,delimiters=';')
        # GGPE01_ini = DOLPHIN_TRIFORCE_GAME_SETTINGS / "GGPE01.ini"
        # if GGPE01_ini.exists():
            # dolphinTriforceGameSettingsGGPE01.read(GGPE01_ini)

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
        # with GGPE01_ini.open('w') as configfile:
            # dolphinTriforceGameSettingsGGPE01.write(configfile)

        commandArray = ["dolphin-triforce", "-b", "-U", "/userdata/system/configs/dolphin-triforce", "-e", rom]
        if system.isOptSet('platform'):
            commandArray = ["dolphin-triforce-nogui", "-b", "-U", "/userdata/system/configs/dolphin-triforce", "-p", system.config["platform"], "-e", rom]

        # No environment variables work for now, paths are coded in above.
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":CONFIGS, "XDG_DATA_HOME":SAVES, "QT_QPA_PLATFORM":"xcb"})
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
