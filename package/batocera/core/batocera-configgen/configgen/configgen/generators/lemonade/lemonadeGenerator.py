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

_logger = logging.getLogger(__name__)

class LemonadeGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        LemonadeGenerator.writeLEMONADEConfig(CONFIGS / "lemonade-emu" / "qt-config.ini", system, playersControllers)

        if Path('/usr/bin/lemonade-qt').exists():
            commandArray = ['/usr/bin/lemonade-qt', rom]
        else:
            commandArray = ['/usr/bin/lemonade', rom]
        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":CONFIGS,
            "XDG_DATA_HOME":SAVES / "3ds",
            "XDG_CACHE_HOME":CACHE,
            "XDG_RUNTIME_DIR":SAVES / "3ds" / "lemonade-emu",
            "QT_QPA_PLATFORM":"xcb",
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse on screen
    def getMouseMode(self, config, rom):
        return config.get("lemonade_screen_layout") != "1-false"

    @staticmethod
    def writeLEMONADEConfig(lemonadeConfigFile: Path, system: Emulator, playersControllers: Controllers):
        # Pads
        lemonadeButtons = {
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

        lemonadeAxis = {
            "circle_pad":    "joystick1",
            "c_stick":       "joystick2"
        }

        # ini file
        lemonadeConfig = CaseSensitiveRawConfigParser(strict=False)
        if lemonadeConfigFile.exists():
            lemonadeConfig.read(lemonadeConfigFile)

        ## [LAYOUT]
        if not lemonadeConfig.has_section("Layout"):
            lemonadeConfig.add_section("Layout")
        # Screen Layout
        lemonadeConfig.set("Layout", "custom_layout", "false")
        lemonadeConfig.set("Layout", r"custom_layout\default", "true")
        layout_option, swap_screen = system.config.get_str('lemonade_screen_layout', '0-false').split('-')
        lemonadeConfig.set("Layout", "swap_screen",   swap_screen)
        lemonadeConfig.set("Layout", "layout_option", layout_option)
        lemonadeConfig.set("Layout", r"swap_screen\default", "false")
        lemonadeConfig.set("Layout", r"layout_option\default", "false")

        ## [SYSTEM]
        if not lemonadeConfig.has_section("System"):
            lemonadeConfig.add_section("System")
        # New 3DS Version
        lemonadeConfig.set("System", "is_new_3ds", system.config.get_bool("lemonade_is_new_3ds", return_values=("true", "false")))
        lemonadeConfig.set("System", r"is_new_3ds\default", "false")
        # Language
        lemonadeConfig.set("System", "region_value", str(getLemonadeLangFromEnvironment()))
        lemonadeConfig.set("System", r"region_value\default", "false")

        ## [UI]
        if not lemonadeConfig.has_section("UI"):
            lemonadeConfig.add_section("UI")
        # Start Fullscreen
        lemonadeConfig.set("UI", "fullscreen", "true")
        lemonadeConfig.set("UI", r"fullscreen\default", "false")

        # Batocera - Defaults
        lemonadeConfig.set("UI", "displayTitleBars", "false")
        lemonadeConfig.set("UI", "displaytitlebars", "false") # Emulator Bug
        lemonadeConfig.set("UI", r"displayTitleBars\default", "false")
        lemonadeConfig.set("UI", "firstStart", "false")
        lemonadeConfig.set("UI", r"firstStart\default", "false")
        lemonadeConfig.set("UI", "hideInactiveMouse", "true")
        lemonadeConfig.set("UI", r"hideInactiveMouse\default", "false")
        lemonadeConfig.set("UI", "enable_discord_presence", "false")
        lemonadeConfig.set("UI", r"enable_discord_presence\default", "false")

        # Remove pop-up prompt on start
        lemonadeConfig.set("UI", "calloutFlags", "1")
        lemonadeConfig.set("UI", r"calloutFlags\default", "false")
        # Close without confirmation
        lemonadeConfig.set("UI", "confirmClose", "false")
        lemonadeConfig.set("UI", "confirmclose", "false") # Emulator Bug
        lemonadeConfig.set("UI", r"confirmClose\default", "false")

        # screenshots
        lemonadeConfig.set("UI", r"Paths\screenshotPath", "/userdata/screenshots")
        lemonadeConfig.set("UI", r"Paths\screenshotPath\default", "false")

        # don't check updates
        lemonadeConfig.set("UI", r"Updater\check_for_update_on_start", "false")
        lemonadeConfig.set("UI", r"Updater\check_for_update_on_start\default", "false")

        ## [RENDERER]
        if not lemonadeConfig.has_section("Renderer"):
            lemonadeConfig.add_section("Renderer")
        # Force Hardware Rrendering / Shader or nothing works fine
        lemonadeConfig.set("Renderer", "use_hw_renderer", "true")
        lemonadeConfig.set("Renderer", "use_hw_shader",   "true")
        lemonadeConfig.set("Renderer", "use_shader_jit",  "true")
        # Software, OpenGL (default) or Vulkan
        lemonadeConfig.set("Renderer", "graphics_api", system.config.get("lemonade_graphics_api", "1"))
        # Set Vulkan as necessary
        if system.config.get("lemonade_graphics_api") == "2" and vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            if vulkan.has_discrete_gpu():
                _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                discrete_index = vulkan.get_discrete_gpu_index()
                if discrete_index:
                    _logger.debug("Using Discrete GPU Index: %s for Lemonade", discrete_index)
                    lemonadeConfig.set("Renderer", "physical_device", discrete_index)
                else:
                    _logger.debug("Couldn't get discrete GPU index")
            else:
                _logger.debug("Discrete GPU is not available on the system. Using default.")
        # Use VSYNC
        lemonadeConfig.set("Renderer", "use_vsync_new", system.config.get_bool("lemonade_use_vsync_new", True, return_values=("true", "false")))
        lemonadeConfig.set("Renderer", r"use_vsync_new\default", "true")
        # Resolution Factor
        lemonadeConfig.set("Renderer", "resolution_factor", system.config.get("lemonade_resolution_factor", "1"))
        lemonadeConfig.set("Renderer", r"resolution_factor\default", "false")
        # Async Shader Compilation
        lemonadeConfig.set("Renderer", "async_shader_compilation", system.config.get_bool("lemonade_async_shader_compilation", return_values=("true", "false")))
        lemonadeConfig.set("Renderer", r"async_shader_compilation\default", "false")
        # Use Frame Limit
        lemonadeConfig.set("Renderer", "use_frame_limit", system.config.get_bool("lemonade_use_frame_limit", True, return_values=("true", "false")))

        ## [WEB SERVICE]
        if not lemonadeConfig.has_section("WebService"):
            lemonadeConfig.add_section("WebService")
        lemonadeConfig.set("WebService", "enable_telemetry",  "false")

        ## [UTILITY]
        if not lemonadeConfig.has_section("Utility"):
            lemonadeConfig.add_section("Utility")
        # Disk Shader Cache
        lemonadeConfig.set("Utility", "use_disk_shader_cache", system.config.get_bool("lemonade_use_disk_shader_cache", return_values=("true", "false")))
        lemonadeConfig.set("Utility", r"use_disk_shader_cache\default", "false")
        # Custom Textures
        match system.config.get('lemonade_custom_textures'):
            case '0' | system.config.MISSING:
                lemonadeConfig.set("Utility", "custom_textures",  "false")
                lemonadeConfig.set("Utility", "preload_textures", "false")
            case _ as textures:
                tab = textures.split('-')
                lemonadeConfig.set("Utility", "custom_textures",  "true")
                if tab[1] == 'normal':
                    lemonadeConfig.set("Utility", "async_custom_loading", "true")
                    lemonadeConfig.set("Utility", "preload_textures", "false")
                else:
                    lemonadeConfig.set("Utility", "async_custom_loading", "false")
                    lemonadeConfig.set("Utility", "preload_textures", "true")

        lemonadeConfig.set("Utility", "async_custom_loading\\default", "true")
        lemonadeConfig.set("Utility", "custom_textures\\default", "false")
        lemonadeConfig.set("Utility", "preload_textures\\default", "false")

        ## [CONTROLS]
        if not lemonadeConfig.has_section("Controls"):
            lemonadeConfig.add_section("Controls")

        # Options required to load the functions when the configuration file is created
        if not lemonadeConfig.has_option("Controls", "profiles\\size"):
            lemonadeConfig.set("Controls", "profile", "0")
            lemonadeConfig.set("Controls", "profile\\default", "true")
            lemonadeConfig.set("Controls", "profiles\\1\\name", "default")
            lemonadeConfig.set("Controls", "profiles\\1\\name\\default", "true")
            lemonadeConfig.set("Controls", "profiles\\size", "1")

        if controller := Controller.find_player_number(playersControllers, 1):
            for x in lemonadeButtons:
                lemonadeConfig.set("Controls", rf"profiles\1\{x}", f'"{LemonadeGenerator.setButton(lemonadeButtons[x], controller.guid, controller.inputs)}"')
            for x in lemonadeAxis:
                lemonadeConfig.set("Controls", rf"profiles\1\{x}", f'"{LemonadeGenerator.setAxis(lemonadeAxis[x], controller.guid, controller.inputs)}"')

        ## Update the configuration file
        with ensure_parents_and_open(lemonadeConfigFile, 'w') as configfile:
            lemonadeConfig.write(configfile)

    @staticmethod
    def setButton(key: str, padGuid: str, padInputs: InputMapping):
        # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return f"button:{input.id},guid:{padGuid},engine:sdl"
            if input.type == "hat":
                return f"engine:sdl,guid:{padGuid},hat:{input.id},direction:{LemonadeGenerator.hatdirectionvalue(input.value)}"
            if input.type == "axis":
                # Untested, need to configure an axis as button / triggers buttons to be tested too
                return f"engine:sdl,guid:{padGuid},axis:{input.id},direction:+,threshold:{0.5}"

        return None

    @staticmethod
    def setAxis(key: str, padGuid: str, padInputs: InputMapping):
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
    def hatdirectionvalue(value: str):
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
def getLemonadeLangFromEnvironment():
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
