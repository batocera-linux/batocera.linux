from __future__ import annotations

import logging
from os import environ
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, ensure_parents_and_open, mkdir_if_not_exists
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

CITRON_CONFIG: Final = CONFIGS / 'citron'

class CitronGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "citron",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        mkdir_if_not_exists(CITRON_CONFIG)

        CitronGenerator.writeCitronConfig(CITRON_CONFIG / "qt-config.ini", system, playersControllers)

        commandArray = ["/usr/bin/citron", "-f", "-g", rom ]
        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":CONFIGS, \
            "XDG_DATA_HOME":SAVES / "switch", \
            "XDG_CACHE_HOME":CACHE, \
            "QT_QPA_PLATFORM":"xcb"})

    @staticmethod
    def writeCitronConfig(citronConfigFile: Path, system: Emulator, playersControllers: Controllers):
        # pads
        citronButtonsMapping = {
            "button_a":      "a",
            "button_b":      "b",
            "button_x":      "x",
            "button_y":      "y",
            "button_dup":    "up",
            "button_ddown":  "down",
            "button_dleft":  "left",
            "button_dright": "right",
            "button_l":      "pageup",
            "button_r":      "pagedown",
            "button_plus":   "start",
            "button_minus":  "select",
            "button_sl":     "l",
            "button_sr":     "r",
            "button_zl":     "l2",
            "button_zr":     "r2",
            "button_lstick": "l3",
            "button_rstick": "r3",
            "button_home":   "hotkey"
        }

        citronAxisMapping = {
            "lstick":    "joystick1",
            "rstick":    "joystick2"
        }

        # ini file
        citronConfig = CaseSensitiveRawConfigParser()
        if citronConfigFile.exists():
            citronConfig.read(citronConfigFile)

        # UI section
        if not citronConfig.has_section("UI"):
            citronConfig.add_section("UI")
        citronConfig.set("UI", "fullscreen", "true")
        citronConfig.set("UI", "fullscreen\\default", "true")
        citronConfig.set("UI", "confirmClose", "false")
        citronConfig.set("UI", "confirmClose\\default", "false")
        citronConfig.set("UI", "firstStart", "false")
        citronConfig.set("UI", "firstStart\\default", "false")
        citronConfig.set("UI", "displayTitleBars", "false")
        citronConfig.set("UI", "displayTitleBars\\default", "false")
        citronConfig.set("UI", "enable_discord_presence", "false")
        citronConfig.set("UI", "enable_discord_presence\\default", "false")
        citronConfig.set("UI", "calloutFlags", "1")
        citronConfig.set("UI", "calloutFlags\\default", "false")
        citronConfig.set("UI", "confirmStop", "2")
        citronConfig.set("UI", "confirmStop\\default", "false")

        # Single Window Mode
        citronConfig.set("UI", "singleWindowMode", system.config.get("citron_single_window", "true"))
        citronConfig.set("UI", "singleWindowMode\\default", "false")

        citronConfig.set("UI", "hideInactiveMouse", "true")
        citronConfig.set("UI", "hideInactiveMouse\\default", "false")

        # Roms path (need for load update/dlc)
        citronConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan", "true")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan\\default", "false")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\expanded", "true")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\expanded\\default", "false")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\path", "/userdata/roms/switch")
        citronConfig.set("UI", "Paths\\gamedirs\\size", "1")

        citronConfig.set("UI", "Screenshots\\enable_screenshot_save_as", "true")
        citronConfig.set("UI", "Screenshots\\enable_screenshot_save_as\\default", "false")
        citronConfig.set("UI", "Screenshots\\screenshot_path", "/userdata/screenshots")
        citronConfig.set("UI", "Screenshots\\screenshot_path\\default", "false")

        # Change controller exit
        citronConfig.set("UI", "Shortcuts\\Main%20Window\\Continue\\Pause%20Emulation\\Controller_KeySeq", "Home+Minus")
        citronConfig.set("UI", "Shortcuts\\Main%20Window\\Exit%20citron\\Controller_KeySeq", "Home+Plus")

        # Data Storage section
        if not citronConfig.has_section("Data%20Storage"):
            citronConfig.add_section("Data%20Storage")
        citronConfig.set("Data%20Storage", "dump_directory", "/userdata/system/configs/citron/dump")
        citronConfig.set("Data%20Storage", "dump_directory\\default", "false")

        citronConfig.set("Data%20Storage", "load_directory", "/userdata/system/configs/citron/load")
        citronConfig.set("Data%20Storage", "load_directory\\default", "false")

        citronConfig.set("Data%20Storage", "nand_directory", "/userdata/system/configs/citron/nand")
        citronConfig.set("Data%20Storage", "nand_directory\\default", "false")

        citronConfig.set("Data%20Storage", "sdmc_directory", "/userdata/system/configs/citron/sdmc")
        citronConfig.set("Data%20Storage", "sdmc_directory\\default", "false")

        citronConfig.set("Data%20Storage", "tas_directory", "/userdata/system/configs/citron/tas")
        citronConfig.set("Data%20Storage", "tas_directory\\default", "false")

        citronConfig.set("Data%20Storage", "use_virtual_sd", "true")
        citronConfig.set("Data%20Storage", "use_virtual_sd\\default", "false")

        # Core section
        if not citronConfig.has_section("Core"):
            citronConfig.add_section("Core")

        # Multicore
        citronConfig.set("Core", "use_multi_core", "true")
        citronConfig.set("Core", "use_multi_core\\default", "false")

        # Renderer section
        if not citronConfig.has_section("Renderer"):
            citronConfig.add_section("Renderer")

        # Aspect ratio
        citronConfig.set("Renderer", "aspect_ratio", system.config.get("citron_ratio", "0"))
        citronConfig.set("Renderer", "aspect_ratio\\default", "false")

        # Graphical backend
        if backend := system.config.get('citron_backend'):
            citronConfig.set("Renderer", "backend", backend)
            # Add vulkan logic
            if backend == "1" and vulkan.is_available():
                _logger.debug("Vulkan driver is available on the system.")
                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_index = vulkan.get_discrete_gpu_index()
                    if discrete_index:
                        _logger.debug("Using Discrete GPU Index: %s for Citron", discrete_index)
                        citronConfig.set("Renderer", "vulkan_device", discrete_index)
                        citronConfig.set("Renderer", "vulkan_device\\default", "true")
                    else:
                        _logger.debug("Couldn't get discrete GPU index, using default")
                        citronConfig.set("Renderer", "vulkan_device", "0")
                        citronConfig.set("Renderer", "vulkan_device\\default", "true")
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
                    citronConfig.set("Renderer", "vulkan_device", "0")
                    citronConfig.set("Renderer", "vulkan_device\\default", "true")
        else:
            citronConfig.set("Renderer", "backend", "0")
        citronConfig.set("Renderer", "backend\\default", "false")

        # Async Shader compilation
        citronConfig.set("Renderer", "use_asynchronous_shaders", system.config.get("citron_async_shaders", "true"))
        citronConfig.set("Renderer", "use_asynchronous_shaders\\default", "false")

        # Assembly shaders
        citronConfig.set("Renderer", "shader_backend", system.config.get("citron_shaderbackend", "0"))
        citronConfig.set("Renderer", "shader_backend\\default", "false")

        # Async Gpu Emulation
        citronConfig.set("Renderer", "use_asynchronous_gpu_emulation", system.config.get("citron_async_gpu", "true"))
        citronConfig.set("Renderer", "use_asynchronous_gpu_emulation\\default", "false")

        # NVDEC Emulation
        citronConfig.set("Renderer", "nvdec_emulation", system.config.get("citron_nvdec_emu", "2"))
        citronConfig.set("Renderer", "nvdec_emulation\\default", "false")

        # GPU Accuracy
        citronConfig.set("Renderer", "gpu_accuracy", system.config.get("citron_accuracy", "0"))
        citronConfig.set("Renderer", "gpu_accuracy\\default", "true")

        # Vsync
        citronConfig.set("Renderer", "use_vsync", system.config.get("citron_vsync", "1"))
        citronConfig.set("Renderer", "use_vsync\\default", "false")

        # Max anisotropy
        citronConfig.set("Renderer", "max_anisotropy", system.config.get("citron_anisotropy", "0"))
        citronConfig.set("Renderer", "max_anisotropy\\default", "false")

        # Resolution scaler
        citronConfig.set("Renderer", "resolution_setup", system.config.get("citron_scale", "2"))
        citronConfig.set("Renderer", "resolution_setup\\default", "false")

        # Scaling filter
        citronConfig.set("Renderer", "scaling_filter", system.config.get("citron_scale_filter", "1"))
        citronConfig.set("Renderer", "scaling_filter\\default", "false")

        # Anti aliasing method
        citronConfig.set("Renderer", "anti_aliasing", system.config.get("citron_aliasing_method", "0"))
        citronConfig.set("Renderer", "anti_aliasing\\default", "false")

        # CPU Section
        if not citronConfig.has_section("Cpu"):
            citronConfig.add_section("Cpu")

        # CPU Accuracy
        citronConfig.set("Cpu", "cpu_accuracy", system.config.get("citron_cpuaccuracy", "0"))
        citronConfig.set("Cpu", "cpu_accuracy\\default", "false")

        # System section
        if not citronConfig.has_section("System"):
            citronConfig.add_section("System")

        # Language
        citronConfig.set("System", "language_index", system.config.get("citron_language") or str(CitronGenerator.getCitronLangFromEnvironment()))
        citronConfig.set("System", "language_index\\default", "false")

        # Region
        citronConfig.set("System", "region_index", system.config.get("citron_region") or str(CitronGenerator.getCitronRegionFromEnvironment()))
        citronConfig.set("System", "region_index\\default", "false")

         # controls section
        if not citronConfig.has_section("Controls"):
            citronConfig.add_section("Controls")

        # Dock Mode
        citronConfig.set("Controls", "use_docked_mode", system.config.get("citron_dock_mode", "true"))
        citronConfig.set("Controls", "use_docked_mode\\default", "false")

        # Sound Mode
        citronConfig.set("Controls", "sound_index", system.config.get("citron_sound_mode", "1"))
        citronConfig.set("Controls", "sound_index\\default", "false")

        # Timezone
        citronConfig.set("Controls", "time_zone_index", system.config.get("citron_timezone", "0"))
        citronConfig.set("Controls", "time_zone_index\\default", "false")

        # controllers
        for nplayer, pad in enumerate(playersControllers):
            citronConfig.set("Controls", f"player_{nplayer}_type", system.config.get(f"p{nplayer+1}_pad", "0"))
            citronConfig.set("Controls", rf"player_{nplayer}_type\default", "false")

            for x in citronButtonsMapping:
                citronConfig.set("Controls", f"player_{nplayer}_{x}", f'"{CitronGenerator.setButton(citronButtonsMapping[x], pad.guid, pad.inputs, nplayer)}"')
            for x in citronAxisMapping:
                citronConfig.set("Controls", f"player_{nplayer}_{x}", f'"{CitronGenerator.setAxis(citronAxisMapping[x], pad.guid, pad.inputs, nplayer)}"')
            citronConfig.set("Controls", f"player_{nplayer}_motionleft", '"[empty]"')
            citronConfig.set("Controls", f"player_{nplayer}_motionright", '"[empty]"')
            citronConfig.set("Controls", f"player_{nplayer}_connected", "true")
            citronConfig.set("Controls", f"player_{nplayer}_connected\\default", "false")
            citronConfig.set("Controls", f"player_{nplayer}_vibration_enabled", "true")
            citronConfig.set("Controls", f"player_{nplayer}_vibration_enabled\\default", "false")

        citronConfig.set("Controls", "vibration_enabled", "true")
        citronConfig.set("Controls", "vibration_enabled\\default", "false")

        for y in range(len(playersControllers), 9):
            citronConfig.set("Controls", f"player_{y-1}_connected", "false")
            citronConfig.set("Controls", rf"player_{y-1}_connected\default", "false")

        # telemetry section
        if not citronConfig.has_section("WebService"):
            citronConfig.add_section("WebService")
        citronConfig.set("WebService", "enable_telemetry", "false")
        citronConfig.set("WebService", "enable_telemetry\\default", "false")

        # Services section
        if not citronConfig.has_section("Services"):
            citronConfig.add_section("Services")
        citronConfig.set("Services", "bcat_backend", "none")
        citronConfig.set("Services", "bcat_backend\\default", "none")

        ### update the configuration file
        with ensure_parents_and_open(citronConfigFile, 'w') as configfile:
            citronConfig.write(configfile)

    @staticmethod
    def setButton(key: str, padGuid: str, padInputs: InputMapping, port: int) -> str:
        # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return f"engine:sdl,button:{input.id},guid:{padGuid},port:{port}"
            if input.type == "hat":
                return f"engine:sdl,hat:{input.id},direction:{CitronGenerator.hatdirectionvalue(input.value)},guid:{padGuid},port:{port}"
            if input.type == "axis":
                return f"engine:sdl,threshold:0.5,axis:{input.id},guid:{padGuid},port:{port},invert:+"
        return ""

    @staticmethod
    def setAxis(key: str, padGuid: str, padInputs: InputMapping, port: int) -> str:
        inputx = "0"
        inputy = "0"

        if key == "joystick1" and "joystick1left" in padInputs:
            inputx = padInputs["joystick1left"]
        elif key == "joystick2" and "joystick2left" in padInputs:
            inputx = padInputs["joystick2left"]

        if key == "joystick1" and "joystick1up" in padInputs:
                inputy = padInputs["joystick1up"]
        elif key == "joystick2" and "joystick2up" in padInputs:
            inputy = padInputs["joystick2up"]
        return f"engine:sdl,range:1.000000,deadzone:0.100000,invert_y:+,invert_x:+,offset_y:-0.000000,axis_y:{inputy},offset_x:-0.000000,axis_x:{inputx},guid:{padGuid},port:{port}"

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

    @staticmethod
    def getCitronLangFromEnvironment():
        lang = environ['LANG'][:5]
        availableLanguages = { "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "nl_NL": 8, "pt_PT": 9 }
        if lang in availableLanguages:
            return availableLanguages[lang]
        return availableLanguages["en_US"]

    @staticmethod
    def getCitronRegionFromEnvironment():
        lang = environ['LANG'][:5]
        availableRegions = { "en_US": 1, "ja_JP": 0 }
        if lang in availableRegions:
            return availableRegions[lang]
        return 2 # europe
