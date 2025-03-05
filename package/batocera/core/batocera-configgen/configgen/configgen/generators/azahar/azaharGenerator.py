from __future__ import annotations

import logging
from os import environ
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, ensure_parents_and_open
from ...controller import Controller, generate_sdl_game_controller_config
from ...utils import vulkan
from ...utils.configparser import CaseSensitiveRawConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...input import InputMapping
    from ...types import HotkeysContext


_logger = logging.getLogger(__name__)

class AzaharGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "azahar",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F4", "reset": "KEY_F6" }
        }

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        AzaharGenerator.writeAZAHARConfig(CONFIGS / "azahar" / "qt-config.ini", system, playersControllers)

        commandArray = ['/usr/bin/azahar', rom]

        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":CONFIGS,
            "XDG_DATA_HOME":SAVES / "3ds",
            "XDG_CACHE_HOME":CACHE,
            "XDG_RUNTIME_DIR":SAVES / "3ds" / "azahar",
            "QT_QPA_PLATFORM":"xcb",
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse on screen
    def getMouseMode(self, config, rom):
        if "azahar_screen_layout" in config and config["azahar_screen_layout"] == "1-false":
            return False
        else:
            return True

    @staticmethod
    def writeAZAHARConfig(
        azaharConfigFile: Path,
        system: Emulator,
        playersControllers: Controllers
    ) -> None:
        # Pads
        azaharButtons = {
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

        azaharAxis = {
            "circle_pad":    "joystick1",
            "c_stick":       "joystick2"
        }

        # ini file
        azaharConfig = CaseSensitiveRawConfigParser(strict=False)
        if azaharConfigFile.exists():
            azaharConfig.read(azaharConfigFile)

        ## [LAYOUT]
        if not azaharConfig.has_section("Layout"):
            azaharConfig.add_section("Layout")
        # Screen Layout
        azaharConfig.set("Layout", "custom_layout", "false")
        if system.isOptSet('azahar_screen_layout'):
            tab = system.config["azahar_screen_layout"].split('-')
            azaharConfig.set("Layout", "swap_screen",   tab[1])
            azaharConfig.set("Layout", "layout_option", tab[0])
        else:
            azaharConfig.set("Layout", "swap_screen", "false")
            azaharConfig.set("Layout", "layout_option", "0")

        ## [SYSTEM]
        if not azaharConfig.has_section("System"):
            azaharConfig.add_section("System")
        # New 3DS Version
        if system.isOptSet('azahar_is_new_3ds') and system.config["azahar_is_new_3ds"] == '1':
            azaharConfig.set("System", "is_new_3ds", "true")
        else:
            azaharConfig.set("System", "is_new_3ds", "false")
        # Language
        azaharConfig.set("System", "region_value", str(getAzaharLangFromEnvironment()))

        ## [UI]
        if not azaharConfig.has_section("UI"):
            azaharConfig.add_section("UI")
        # Start Fullscreen
        azaharConfig.set("UI", "fullscreen", "true")

        # Batocera - Defaults
        azaharConfig.set("UI", "displayTitleBars", "false")
        azaharConfig.set("UI", "firstStart", "false")
        azaharConfig.set("UI", "hideInactiveMouse", "true")
        azaharConfig.set("UI", "enable_discord_presence", "false")

        # Remove pop-up prompt on start
        azaharConfig.set("UI", "calloutFlags", "1")
        # Close without confirmation
        azaharConfig.set("UI", "confirmClose", "false")
        azaharConfig.set("UI", "confirmclose", "false") # Emulator Bug

        # screenshots
        azaharConfig.set("UI", r"Paths\screenshotPath", "/userdata/screenshots")

        # don't check updates
        azaharConfig.set("UI", r"Updater\check_for_update_on_start", "false")

        ## [RENDERER]
        if not azaharConfig.has_section("Renderer"):
            azaharConfig.add_section("Renderer")
        # Force Hardware Rrendering / Shader or nothing works fine
        azaharConfig.set("Renderer", "use_hw_renderer", "true")
        azaharConfig.set("Renderer", "use_hw_shader",   "true")
        azaharConfig.set("Renderer", "use_shader_jit",  "true")
        # Software, OpenGL (default) or Vulkan
        if system.isOptSet('azahar_graphics_api'):
            azaharConfig.set("Renderer", "graphics_api", system.config["azahar_graphics_api"])
        else:
            azaharConfig.set("Renderer", "graphics_api", "1")
        # Set Vulkan as necessary
        if system.isOptSet("azahar_graphics_api") and system.config["azahar_graphics_api"] == "2":
            if vulkan.is_available():
                _logger.debug("Vulkan driver is available on the system.")
                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_index = vulkan.get_discrete_gpu_index()
                    if discrete_index:
                        _logger.debug("Using Discrete GPU Index: %s for Azahar", discrete_index)
                        azaharConfig.set("Renderer", "physical_device", discrete_index)
                    else:
                        _logger.debug("Couldn't get discrete GPU index")
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
        # Use VSYNC
        if system.isOptSet('azahar_use_vsync_new') and system.config["azahar_use_vsync_new"] == '0':
            azaharConfig.set("Renderer", "use_vsync_new", "false")
        else:
            azaharConfig.set("Renderer", "use_vsync_new", "true")
        # Resolution Factor
        if system.isOptSet('azahar_resolution_factor'):
            azaharConfig.set("Renderer", "resolution_factor", system.config["azahar_resolution_factor"])
        else:
            azaharConfig.set("Renderer", "resolution_factor", "1")
        # Async Shader Compilation
        if system.isOptSet('azahar_async_shader_compilation') and system.config["azahar_async_shader_compilation"] == '1':
            azaharConfig.set("Renderer", "async_shader_compilation", "true")
        else:
            azaharConfig.set("Renderer", "async_shader_compilation", "false")
        # Use Frame Limit
        if system.isOptSet('azahar_use_frame_limit') and system.config["azahar_use_frame_limit"] == '0':
            azaharConfig.set("Renderer", "use_frame_limit", "false")
        else:
            azaharConfig.set("Renderer", "use_frame_limit", "true")

        ## [WEB SERVICE]
        if not azaharConfig.has_section("WebService"):
            azaharConfig.add_section("WebService")
        azaharConfig.set("WebService", "enable_telemetry",  "false")

        ## [UTILITY]
        if not azaharConfig.has_section("Utility"):
            azaharConfig.add_section("Utility")
        # Disk Shader Cache
        if system.isOptSet('azahar_use_disk_shader_cache') and system.config["azahar_use_disk_shader_cache"] == '1':
            azaharConfig.set("Utility", "use_disk_shader_cache", "true")
        else:
            azaharConfig.set("Utility", "use_disk_shader_cache", "false")
        # Custom Textures
        if system.isOptSet('azahar_custom_textures') and system.config["azahar_custom_textures"] != '0':
            tab = system.config["azahar_custom_textures"].split('-')
            azaharConfig.set("Utility", "custom_textures",  "true")
            if tab[1] == 'normal':
                azaharConfig.set("Utility", "async_custom_loading", "true")
                azaharConfig.set("Utility", "preload_textures", "false")
            else:
                azaharConfig.set("Utility", "async_custom_loading", "false")
                azaharConfig.set("Utility", "preload_textures", "true")
        else:
            azaharConfig.set("Utility", "custom_textures",  "false")
            azaharConfig.set("Utility", "preload_textures", "false")

        ## [CONTROLS]
        if not azaharConfig.has_section("Controls"):
            azaharConfig.add_section("Controls")

        # Options required to load the functions when the configuration file is created
        if not azaharConfig.has_option("Controls", r"profiles\size"):
            azaharConfig.set("Controls", "profile", "0")
            azaharConfig.set("Controls", r"profiles\1\name", "default")
            azaharConfig.set("Controls", r"profiles\size", "1")

        if controller := Controller.find_player_number(playersControllers, 1):
            for x in azaharButtons:
                azaharConfig.set("Controls", f"profiles\\1\\{x}", f'"{AzaharGenerator.setButton(azaharButtons[x], controller.guid, controller.inputs)}"')
            for x in azaharAxis:
                azaharConfig.set("Controls", f"profiles\\1\\{x}", f'"{AzaharGenerator.setAxis(azaharAxis[x], controller.guid, controller.inputs)}"')

        ## Update the configuration file
        with ensure_parents_and_open(azaharConfigFile, 'w') as configfile:
            azaharConfig.write(configfile)

    @staticmethod
    def setButton(key: str, padGuid: str, padInputs: InputMapping) -> str | None:
        # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return f"button:{input.id},guid:{padGuid},engine:sdl"
            elif input.type == "hat":
                return f"engine:sdl,guid:{padGuid},hat:{input.id},direction:{AzaharGenerator.hatdirectionvalue(input.value)}"
            elif input.type == "axis":
                # Untested, need to configure an axis as button / triggers buttons to be tested too
                return f"engine:sdl,guid:{padGuid},axis:{input.id},direction:+,threshold:0.5"

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
            return "";

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
def getAzaharLangFromEnvironment():
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
    else:
        return region["AUTO"]
