from __future__ import annotations

import logging
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, ensure_parents_and_open
from ...controller import Controller, generate_sdl_game_controller_config
from ...utils import vulkan
from ...utils.configparser import CaseSensitiveRawConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...input import InputMapping
    from ...types import HotkeysContext


_logger = logging.getLogger(__name__)

class CitraGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "citra",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F4", "reset": "KEY_F6" }
        }

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        CitraGenerator.writeCITRAConfig(CONFIGS / "citra-emu" / "qt-config.ini", system, playersControllers)

        if Path('/usr/bin/citra-qt').exists():
            commandArray = ['/usr/bin/citra-qt', rom]
        else:
            commandArray = ['/usr/bin/citra', rom]
        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":CONFIGS,
            "XDG_DATA_HOME":SAVES / "3ds",
            "XDG_CACHE_HOME":CACHE,
            "XDG_RUNTIME_DIR":SAVES / "3ds" / "citra-emu",
            "QT_QPA_PLATFORM":"xcb",
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse on screen
    def getMouseMode(self, config, rom):
        return config.get("citra_screen_layout") != '1-false'

    @staticmethod
    def writeCITRAConfig(
        citraConfigFile: Path,
        system: Emulator,
        playersControllers: Controllers
    ) -> None:
        # Pads
        citraButtons = {
            "button_a":      "a",
            "button_b":      "b",
            "button_x":      "x",
            "button_y":      "y",
            "button_up":     "up",
            "button_down":   "down",
            "button_left":   "left",
            "button_right":  "right",
            "button_l":      "pageup",
            "button_r":      "pagedown",
            "button_start":  "start",
            "button_select": "select",
            "button_zl":     "l2",
            "button_zr":     "r2",
            "button_home":   "hotkey"
        }

        citraAxis = {
            "circle_pad":    "joystick1",
            "c_stick":       "joystick2"
        }

        # ini file
        citraConfig = CaseSensitiveRawConfigParser(strict=False)
        if citraConfigFile.exists():
            citraConfig.read(citraConfigFile)

        ## [LAYOUT]
        if not citraConfig.has_section("Layout"):
            citraConfig.add_section("Layout")
        # Screen Layout
        citraConfig.set("Layout", "custom_layout", "false")
        layout_option, swap_screen = system.config.get("citra_screen_layout", "0-false").split('-')
        citraConfig.set("Layout", "swap_screen",   swap_screen)
        citraConfig.set("Layout", "layout_option", layout_option)

        ## [SYSTEM]
        if not citraConfig.has_section("System"):
            citraConfig.add_section("System")
        # New 3DS Version
        citraConfig.set("System", "is_new_3ds", system.config.get_bool("citra_is_new_3ds", return_values=("true", "false")))
        # Language
        citraConfig.set("System", "region_value", str(getCitraLangFromEnvironment()))

        ## [UI]
        if not citraConfig.has_section("UI"):
            citraConfig.add_section("UI")
        # Start Fullscreen
        citraConfig.set("UI", "fullscreen", "true")

        # Batocera - Defaults
        citraConfig.set("UI", "displayTitleBars", "false")
        citraConfig.set("UI", "firstStart", "false")
        citraConfig.set("UI", "hideInactiveMouse", "true")
        citraConfig.set("UI", "enable_discord_presence", "false")

        # Remove pop-up prompt on start
        citraConfig.set("UI", "calloutFlags", "1")
        # Close without confirmation
        citraConfig.set("UI", "confirmClose", "false")
        citraConfig.set("UI", "confirmclose", "false") # Emulator Bug

        # screenshots
        citraConfig.set("UI", r"Paths\screenshotPath", "/userdata/screenshots")

        # don't check updates
        citraConfig.set("UI", r"Updater\check_for_update_on_start", "false")

        ## [RENDERER]
        if not citraConfig.has_section("Renderer"):
            citraConfig.add_section("Renderer")
        # Force Hardware Rrendering / Shader or nothing works fine
        citraConfig.set("Renderer", "use_hw_renderer", "true")
        citraConfig.set("Renderer", "use_hw_shader",   "true")
        citraConfig.set("Renderer", "use_shader_jit",  "true")
        # Software, OpenGL (default) or Vulkan
        citraConfig.set("Renderer", "graphics_api", system.config.get("citra_graphics_api", "1"))
        # Set Vulkan as necessary
        if system.config.get("citra_graphics_api") == "2" and vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            if vulkan.has_discrete_gpu():
                _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                discrete_index = vulkan.get_discrete_gpu_index()
                if discrete_index:
                    _logger.debug("Using Discrete GPU Index: %s for Citra", discrete_index)
                    citraConfig.set("Renderer", "physical_device", discrete_index)
                else:
                    _logger.debug("Couldn't get discrete GPU index")
            else:
                _logger.debug("Discrete GPU is not available on the system. Using default.")
        # Use VSYNC
        citraConfig.set("Renderer", "use_vsync_new", system.config.get_bool("citra_use_vsync_new", True, return_values=("true", "false")))
        # Resolution Factor
        citraConfig.set("Renderer", "resolution_factor", system.config.get("citra_resolution_factor", "1"))
        # Async Shader Compilation
        citraConfig.set("Renderer", "async_shader_compilation", system.config.get_bool("citra_async_shader_compilation", return_values=("true", "false")))
        # Use Frame Limit
        citraConfig.set("Renderer", "use_frame_limit", system.config.get_bool("citra_use_frame_limit", True, return_values=("true", "false")))

        ## [WEB SERVICE]
        if not citraConfig.has_section("WebService"):
            citraConfig.add_section("WebService")
        citraConfig.set("WebService", "enable_telemetry",  "false")

        ## [UTILITY]
        if not citraConfig.has_section("Utility"):
            citraConfig.add_section("Utility")
        # Disk Shader Cache
        citraConfig.set("Utility", "use_disk_shader_cache", system.config.get_bool("citra_use_disk_shader_cache", return_values=("true", "false")))
        # Custom Textures
        match system.config.get('citra_custom_textures'):
            case '0' | system.config.MISSING:
                citraConfig.set("Utility", "custom_textures",  "false")
                citraConfig.set("Utility", "preload_textures", "false")
            case _ as textures:
                tab = textures.split('-')
                citraConfig.set("Utility", "custom_textures",  "true")
                if tab[1] == 'normal':
                    citraConfig.set("Utility", "async_custom_loading", "true")
                    citraConfig.set("Utility", "preload_textures", "false")
                else:
                    citraConfig.set("Utility", "async_custom_loading", "false")
                    citraConfig.set("Utility", "preload_textures", "true")

        ## [CONTROLS]
        if not citraConfig.has_section("Controls"):
            citraConfig.add_section("Controls")

        # Options required to load the functions when the configuration file is created
        if not citraConfig.has_option("Controls", r"profiles\size"):
            citraConfig.set("Controls", "profile", "0")
            citraConfig.set("Controls", r"profiles\1\name", "default")
            citraConfig.set("Controls", r"profiles\size", "1")

        # We only care about player 1
        if controller := Controller.find_player_number(playersControllers, 1):
            for x in citraButtons:
                citraConfig.set("Controls", f"profiles\\1\\{x}", f'"{CitraGenerator.setButton(citraButtons[x], controller.guid, controller.inputs)}"')
            for x in citraAxis:
                citraConfig.set("Controls", f"profiles\\1\\{x}", f'"{CitraGenerator.setAxis(citraAxis[x], controller.guid, controller.inputs)}"')

        ## Update the configuration file
        with ensure_parents_and_open(citraConfigFile, 'w') as configfile:
            citraConfig.write(configfile)

    @staticmethod
    def setButton(key: str, padGuid: str, padInputs: InputMapping) -> str | None:
        # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return f"button:{input.id},guid:{padGuid},engine:sdl"
            if input.type == "hat":
                return f"engine:sdl,guid:{padGuid},hat:{input.id},direction:{CitraGenerator.hatdirectionvalue(input.value)}"
            if input.type == "axis":
                # Untested, need to configure an axis as button / triggers buttons to be tested too
                return f"engine:sdl,guid:{padGuid},axis:{input.id},direction:+,threshold:0.5"
        return None

    @staticmethod
    def setAxis(key: str, padGuid: str, padInputs: InputMapping) -> str:
        inputx = None
        inputy = None

        if key == "joystick1" and "joystick1left" in padInputs:
            inputx = padInputs["joystick1left"]
        elif key == "joystick2" and "joystick2left" in padInputs:
            inputx = padInputs["joystick2left"]

        if key == "joystick1" and "joystick1up" in padInputs:
            inputy = padInputs["joystick1up"]
        elif key == "joystick2" and "joystick2up" in padInputs:
            inputy = padInputs["joystick2up"]

        if inputx is None or inputy is None:
            return ""

        return f"axis_x:{inputx.id},guid:{padGuid},axis_y:{inputy.id},engine:sdl"

    @staticmethod
    def hatdirectionvalue(value: str) -> str:
        if int(value) == 1:
            return "up"
        if int(value) == 4:
            return "down"
        if int(value) == 2:
            return "right"
        if int(value) == 8:
            return "left"
        return "unknown"

# Language auto setting
def getCitraLangFromEnvironment():
    region = { "AUTO": -1, "JPN": 0, "USA": 1, "EUR": 2, "AUS": 3, "CHN": 4, "KOR": 5, "TWN": 6 }
    availableLanguages = {
        "ja_JP": "JPN",
        "en_US": "USA",
        "de_DE": "EUR",
        "es_ES": "EUR",
        "fr_FR": "EUR",
        "it_IT": "EUR",
        "hu_HU": "EUR",
        "pt_PT": "EUR",
        "ru_RU": "EUR",
        "en_AU": "AUS",
        "zh_CN": "CHN",
        "ko_KR": "KOR",
        "zh_TW": "TWN"
    }
    lang = environ['LANG'][:5]
    if lang in availableLanguages:
        return region[availableLanguages[lang]]
    return region["AUTO"]
