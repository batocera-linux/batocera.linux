from __future__ import annotations

import shutil
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator
from . import dolphinTriforceControllers
from .dolphinTriforcePaths import (
    DOLPHIN_TRIFORCE_CONFIG,
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
            "name": "dolphin-triforce",
            "keys": { "exit":          ["KEY_LEFTALT", "KEY_F4"],
                      "menu":          ["KEY_LEFTALT", "KEY_ENTER"],
                      "restore_state": "KEY_F1",
                      "save_state":    ["KEY_LEFTSHIFT", "KEY_F1"] }
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
            dolphinTriforceSettings.set("Core", "MemcardAPath", str(DOLPHIN_TRIFORCE_SAVES / "GC" / "MemoryCardA.USA.raw"))
            dolphinTriforceSettings.set("Core", "MemcardBPath", str(DOLPHIN_TRIFORCE_SAVES / "GC" / "MemoryCardB.USA.raw"))

        # Draw or not FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinTriforceSettings.set("General", "ShowLag", "True")
            dolphinTriforceSettings.set("General", "ShowFrameCount", "True")
        else:
            dolphinTriforceSettings.set("General", "ShowLag", "False")
            dolphinTriforceSettings.set("General", "ShowFrameCount", "False")

        # Don't ask about statistics
        dolphinTriforceSettings.set("Analytics", "PermissionAsked", "True")

        # PanicHandlers displaymessages
        dolphinTriforceSettings.set("Interface", "UsePanicHandlers",        "False")

        # Disable OSD Messages
        if system.isOptSet("triforce_osd_messages") and system.getOptBoolean("triforce_osd_messages"):
            dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", "False")
        else:
            dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", "True")

        # Don't confirm at stop
        dolphinTriforceSettings.set("Interface", "ConfirmStop", "False")

        # Fixes gui display
        dolphinTriforceSettings.set("Display", "RenderToMain", "False")
        dolphinTriforceSettings.set("Display", "Fullscreen", "False")

        # Enable Cheats
        dolphinTriforceSettings.set("Core", "EnableCheats", "True")

        # Dual Core
        if system.isOptSet("triforce_dual_core") and system.getOptBoolean("triforce_dual_core"):
            dolphinTriforceSettings.set("Core", "CPUThread", "True")
        else:
            dolphinTriforceSettings.set("Core", "CPUThread", "False")

        # Gpu Sync
        if system.isOptSet("triforce_gpu_sync") and system.getOptBoolean("triforce_gpu_sync"):
            dolphinTriforceSettings.set("Core", "SyncGPU", "True")
        else:
            dolphinTriforceSettings.set("Core", "SyncGPU", "False")

        # Language
        dolphinTriforceSettings.set("Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment())) # Wii
        dolphinTriforceSettings.set("Core", "GameCubeLanguage", str(getGameCubeLangFromEnvironment())) # GC

        # Enable MMU
        if system.isOptSet("triforce_enable_mmu") and system.getOptBoolean("triforce_enable_mmu"):
            dolphinTriforceSettings.set("Core", "MMU", "True")
        else:
            dolphinTriforceSettings.set("Core", "MMU", "False")

        # Backend - Default OpenGL
        if system.isOptSet("triforce_api"):
            dolphinTriforceSettings.set("Core", "GFXBackend", system.config["triforce_api"])
        else:
            dolphinTriforceSettings.set("Core", "GFXBackend", "OGL")

        # Serial Port 1 to AM-Baseband
        dolphinTriforceSettings.set("Core", "SerialPort1", "6")

        # Gamecube pads forced as AM-Baseband
        dolphinTriforceSettings.set("Core", "SIDevice0", "11")
        dolphinTriforceSettings.set("Core", "SIDevice1", "11")

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
        if system.isOptSet('triforce_aspect_ratio'):
            dolphinTriforceGFXSettings.set("Settings", "AspectRatio", system.config["triforce_aspect_ratio"])
        else:
            dolphinTriforceGFXSettings.set("Settings", "AspectRatio", "0")

        # Show fps
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinTriforceGFXSettings.set("Settings", "ShowFPS", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "ShowFPS", "False")

        # HiResTextures
        if system.isOptSet('triforce_hires_textures') and system.getOptBoolean('triforce_hires_textures'):
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
        if system.isOptSet('triforce_perf_hacks') and system.getOptBoolean('triforce_perf_hacks'):
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
        if system.isOptSet('triforce_resolution'):
            dolphinTriforceGFXSettings.set("Settings", "EFBScale", system.config["triforce_resolution"])
        else:
            dolphinTriforceGFXSettings.set("Settings", "EFBScale", "2")

        # VSync
        if system.isOptSet('triforce_vsync'):
            dolphinTriforceGFXSettings.set("Hardware", "VSync", str(system.getOptBoolean('triforce_vsync')))
        else:
            dolphinTriforceGFXSettings.set("Hardware", "VSync", "True")

        # Anisotropic filtering
        if system.isOptSet('triforce_filtering'):
            filtering = system.config["triforce_filtering"].split('/')
            dolphinTriforceGFXSettings.set("Enhancements", "MaxAnisotropy", filtering[0])
            dolphinTriforceGFXSettings.set("Enhancements", "ForceTextureFiltering", filtering[1])
        else:
            dolphinTriforceGFXSettings.set("Enhancements", "MaxAnisotropy", "0")
            dolphinTriforceGFXSettings.set("Enhancements", "ForceTextureFiltering", "0")

        if system.isOptSet('triforce_resampling'):
            dolphinTriforceGFXSettings.set("Enhancements", "OutputResampling", system.config["triforce_resampling"])
        else:
            dolphinTriforceGFXSettings.set("Enhancements", "OutputResampling", "0")

        # Anti aliasing
        if system.isOptSet('triforce_antialiasing'):
            msaa, ssaa = system.config["triforce_antialiasing"].split('/')
            dolphinTriforceGFXSettings.set("Settings", "MSAA", msaa)
            dolphinTriforceGFXSettings.set("Settings", "SSAA", ssaa)
        else:
            dolphinTriforceGFXSettings.set("Settings", "MSAA", "0x00000000")
            dolphinTriforceGFXSettings.set("Settings", "SSAA", "False")

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

        # These ini files are required to launch Triforce games, and thus should always be present and enabled.
        mkdir_if_not_exists(DOLPHIN_TRIFORCE_GAME_SETTINGS)
        source_dir = Path("/usr/share/triforce")
        for source_path in source_dir.iterdir():
            destination_path = DOLPHIN_TRIFORCE_GAME_SETTINGS / source_path.name

            # Check if the destination file exists and if it is older than the source file
            if destination_path.exists() and source_path.stat().st_mtime <= destination_path.stat().st_mtime:
                continue

            shutil.copy(source_path, destination_path)

        commandArray = ["dolphin-triforce", "-b", "-u", str(DOLPHIN_TRIFORCE_CONFIG), "-e", rom]

        return Command.Command(
            array=commandArray,
            env={
                "QT_QPA_PLATFORM":"xcb",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if (
            (ratio := config.get('triforce_aspect_ratio'))
            and (
                ratio == '1'
                or (
                    ratio == '3'
                    and (gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1))
                )
            )
        ):
            return 16/9
        return 4/3

# Seem to be only for the gamecube. However, while this is not in a gamecube section
# It may be used for something else, so set it anyway
def getGameCubeLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": 0, "de_DE": 1, "fr_FR": 2, "es_ES": 3, "it_IT": 4, "nl_NL": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
