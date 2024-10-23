from __future__ import annotations

import logging
import subprocess
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, ensure_parents_and_open
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveRawConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...controller import ControllerMapping
    from ...Emulator import Emulator

eslog = logging.getLogger(__name__)

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
        if "lemonade_screen_layout" in config and config["lemonade_screen_layout"] == "1-false":
            return False
        else:
            return True

    @staticmethod
    def writeLEMONADEConfig(lemonadeConfigFile: Path, system: Emulator, playersControllers: ControllerMapping):
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
        if system.isOptSet('lemonade_screen_layout'):
            tab = system.config["lemonade_screen_layout"].split('-')
            lemonadeConfig.set("Layout", "swap_screen",   tab[1])
            lemonadeConfig.set("Layout", "layout_option", tab[0])
        else:
            lemonadeConfig.set("Layout", "swap_screen", "false")
            lemonadeConfig.set("Layout", "layout_option", "0")
        lemonadeConfig.set("Layout", r"swap_screen\default", "false")
        lemonadeConfig.set("Layout", r"layout_option\default", "false")

        ## [SYSTEM]
        if not lemonadeConfig.has_section("System"):
            lemonadeConfig.add_section("System")
        # New 3DS Version
        if system.isOptSet('lemonade_is_new_3ds') and system.config["lemonade_is_new_3ds"] == '1':
            lemonadeConfig.set("System", "is_new_3ds", "true")
        else:
            lemonadeConfig.set("System", "is_new_3ds", "false")
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
        if system.isOptSet('lemonade_graphics_api'):
            lemonadeConfig.set("Renderer", "graphics_api", system.config["lemonade_graphics_api"])
        else:
            lemonadeConfig.set("Renderer", "graphics_api", "1")
        # Set Vulkan as necessary
        if system.isOptSet("lemonade_graphics_api") and system.config["lemonade_graphics_api"] == "2":
            try:
                have_vulkan = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasVulkan"], text=True).strip()
                if have_vulkan == "true":
                    eslog.debug("Vulkan driver is available on the system.")
                    try:
                        have_discrete = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasDiscrete"], text=True).strip()
                        if have_discrete == "true":
                            eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                            try:
                                discrete_index = subprocess.check_output(["/usr/bin/batocera-vulkan", "discreteIndex"], text=True).strip()
                                if discrete_index != "":
                                    eslog.debug("Using Discrete GPU Index: {} for Lemonade".format(discrete_index))
                                    lemonadeConfig.set("Renderer", "physical_device", discrete_index)
                                else:
                                    eslog.debug("Couldn't get discrete GPU index")
                            except subprocess.CalledProcessError:
                                eslog.debug("Error getting discrete GPU index")
                        else:
                            eslog.debug("Discrete GPU is not available on the system. Using default.")
                    except subprocess.CalledProcessError:
                        eslog.debug("Error checking for discrete GPU.")
            except subprocess.CalledProcessError:
                eslog.debug("Error executing batocera-vulkan script.")
        # Use VSYNC
        if system.isOptSet('lemonade_use_vsync_new') and system.config["lemonade_use_vsync_new"] == '0':
            lemonadeConfig.set("Renderer", "use_vsync_new", "false")
        else:
            lemonadeConfig.set("Renderer", "use_vsync_new", "true")
        lemonadeConfig.set("Renderer", r"use_vsync_new\default", "true")
        # Resolution Factor
        if system.isOptSet('lemonade_resolution_factor'):
            lemonadeConfig.set("Renderer", "resolution_factor", system.config["lemonade_resolution_factor"])
        else:
            lemonadeConfig.set("Renderer", "resolution_factor", "1")
        lemonadeConfig.set("Renderer", r"resolution_factor\default", "false")
        # Async Shader Compilation
        if system.isOptSet('lemonade_async_shader_compilation') and system.config["lemonade_async_shader_compilation"] == '1':
            lemonadeConfig.set("Renderer", "async_shader_compilation", "true")
        else:
            lemonadeConfig.set("Renderer", "async_shader_compilation", "false")
        lemonadeConfig.set("Renderer", r"async_shader_compilation\default", "false")
        # Use Frame Limit
        if system.isOptSet('lemonade_use_frame_limit') and system.config["lemonade_use_frame_limit"] == '0':
            lemonadeConfig.set("Renderer", "use_frame_limit", "false")
        else:
            lemonadeConfig.set("Renderer", "use_frame_limit", "true")

        ## [WEB SERVICE]
        if not lemonadeConfig.has_section("WebService"):
            lemonadeConfig.add_section("WebService")
        lemonadeConfig.set("WebService", "enable_telemetry",  "false")

        ## [UTILITY]
        if not lemonadeConfig.has_section("Utility"):
            lemonadeConfig.add_section("Utility")
        # Disk Shader Cache
        if system.isOptSet('lemonade_use_disk_shader_cache') and system.config["lemonade_use_disk_shader_cache"] == '1':
            lemonadeConfig.set("Utility", "use_disk_shader_cache", "true")
        else:
            lemonadeConfig.set("Utility", "use_disk_shader_cache", "false")
        lemonadeConfig.set("Utility", r"use_disk_shader_cache\default", "false")
        # Custom Textures
        if system.isOptSet('lemonade_custom_textures') and system.config["lemonade_custom_textures"] != '0':
            tab = system.config["lemonade_custom_textures"].split('-')
            lemonadeConfig.set("Utility", "custom_textures",  "true")
            if tab[1] == 'normal':
                lemonadeConfig.set("Utility", "async_custom_loading", "true")
                lemonadeConfig.set("Utility", "preload_textures", "false")
            else:
                lemonadeConfig.set("Utility", "async_custom_loading", "false")
                lemonadeConfig.set("Utility", "preload_textures", "true")
        else:
            lemonadeConfig.set("Utility", "custom_textures",  "false")
            lemonadeConfig.set("Utility", "preload_textures", "false")
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

        for index in playersControllers :
            controller = playersControllers[index]
            # We only care about player 1
            if controller.player_number != 1:
                continue
            for x in lemonadeButtons:
                lemonadeConfig.set("Controls", "profiles\\1\\" + x, f'"{LemonadeGenerator.setButton(lemonadeButtons[x], controller.guid, controller.inputs)}"')
            for x in lemonadeAxis:
                lemonadeConfig.set("Controls", "profiles\\1\\" + x, f'"{LemonadeGenerator.setAxis(lemonadeAxis[x], controller.guid, controller.inputs)}"')
            break

        ## Update the configuration file
        with ensure_parents_and_open(lemonadeConfigFile, 'w') as configfile:
            lemonadeConfig.write(configfile)

    @staticmethod
    def setButton(key, padGuid, padInputs):
        # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("button:{},guid:{},engine:sdl").format(input.id, padGuid)
            elif input.type == "hat":
                return ("engine:sdl,guid:{},hat:{},direction:{}").format(padGuid, input.id, LemonadeGenerator.hatdirectionvalue(input.value))
            elif input.type == "axis":
                # Untested, need to configure an axis as button / triggers buttons to be tested too
                return ("engine:sdl,guid:{},axis:{},direction:{},threshold:{}").format(padGuid, input.id, "+", 0.5)

    @staticmethod
    def setAxis(key, padGuid, padInputs):
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

        return ("axis_x:{},guid:{},axis_y:{},engine:sdl").format(inputx.id, padGuid, inputy.id)

    @staticmethod
    def hatdirectionvalue(value):
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
    else:
        return region["AUTO"]
