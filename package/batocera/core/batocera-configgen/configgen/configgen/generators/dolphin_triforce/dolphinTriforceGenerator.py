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

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
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
        dolphinTriforceSettings.set("General", "ShowLag", str(system.config.show_fps))
        dolphinTriforceSettings.set("General", "ShowFrameCount", str(system.config.show_fps))

        # Don't ask about statistics
        dolphinTriforceSettings.set("Analytics", "PermissionAsked", "True")

        # PanicHandlers displaymessages
        dolphinTriforceSettings.set("Interface", "UsePanicHandlers",        "False")

        # Disable OSD Messages
        dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", str(not system.config.get_bool("triforce_osd_messages")))

        # Don't confirm at stop
        dolphinTriforceSettings.set("Interface", "ConfirmStop", "False")

        # Fixes gui display
        dolphinTriforceSettings.set("Display", "RenderToMain", "False")
        dolphinTriforceSettings.set("Display", "Fullscreen", "False")

        # Enable Cheats
        dolphinTriforceSettings.set("Core", "EnableCheats", "True")

        # Dual Core
        dolphinTriforceSettings.set("Core", "CPUThread", str(system.config.get_bool("triforce_dual_core")))

        # Gpu Sync
        dolphinTriforceSettings.set("Core", "SyncGPU", str(system.config.get_bool("triforce_gpu_sync")))

        # Language
        dolphinTriforceSettings.set("Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment())) # Wii
        dolphinTriforceSettings.set("Core", "GameCubeLanguage", str(getGameCubeLangFromEnvironment())) # GC

        # Enable MMU
        dolphinTriforceSettings.set("Core", "MMU", str(system.config.get_bool("triforce_enable_mmu")))

        # Backend - Default OpenGL
        dolphinTriforceSettings.set("Core", "GFXBackend", system.config.get("triforce_api", "OGL"))

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
        dolphinTriforceGFXSettings.set("Settings", "AspectRatio", system.config.get("triforce_aspect_ratio", "0"))

        # Show fps
        dolphinTriforceGFXSettings.set("Settings", "ShowFPS", str(system.config.show_fps))

        # HiResTextures
        hires_textures = str(system.config.get_bool('triforce_hires_textures'))
        dolphinTriforceGFXSettings.set("Settings", "HiresTextures",      hires_textures)
        dolphinTriforceGFXSettings.set("Settings", "CacheHiresTextures", hires_textures)

        # Widescreen Hack
        dolphinTriforceGFXSettings.set(
            "Settings",
            "wideScreenHack",
            str(
                system.config.get_bool('widescreen_hack') and
                # Prefer Cheats than Hack
                not system.config.get_bool('enable_cheats')
            )
        )

        # Various performance hacks - Default Off
        if system.config.get_bool('triforce_perf_hacks'):
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
        dolphinTriforceGFXSettings.set("Settings", "EFBScale", system.config.get("triforce_resolution", "2"))

        # VSync
        dolphinTriforceGFXSettings.set("Hardware", "VSync", str(system.config.get_bool('triforce_vsync', True)))

        # Anisotropic filtering
        filtering = system.config.get("triforce_filtering", "0/0").split('/')
        dolphinTriforceGFXSettings.set("Enhancements", "MaxAnisotropy", filtering[0])
        dolphinTriforceGFXSettings.set("Enhancements", "ForceTextureFiltering", filtering[1])

        dolphinTriforceGFXSettings.set("Enhancements", "OutputResampling", system.config.get("triforce_resampling", "0"))

        # Anti aliasing
        msaa, ssaa = system.config.get("triforce_antialiasing", "0x00000000/False").split('/')
        dolphinTriforceGFXSettings.set("Settings", "MSAA", msaa)
        dolphinTriforceGFXSettings.set("Settings", "SSAA", ssaa)

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
