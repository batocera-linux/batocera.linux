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

SUYU_CONFIG: Final = CONFIGS / 'suyu'

class SuyuGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "suyu",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        mkdir_if_not_exists(SUYU_CONFIG)

        SuyuGenerator.writeSuyuConfig(SUYU_CONFIG / "qt-config.ini", system, playersControllers)

        commandArray = ["/usr/bin/suyu", "-f", "-g", rom ]
        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":CONFIGS, \
            "XDG_DATA_HOME":SAVES / "switch", \
            "XDG_CACHE_HOME":CACHE, \
            "QT_QPA_PLATFORM":"xcb"})

    @staticmethod
    def writeSuyuConfig(suyuConfigFile: Path, system: Emulator, playersControllers: Controllers):
        # pads
        suyuButtonsMapping = {
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

        suyuAxisMapping = {
            "lstick":    "joystick1",
            "rstick":    "joystick2"
        }

        # ini file
        suyuConfig = CaseSensitiveRawConfigParser()
        if suyuConfigFile.exists():
            suyuConfig.read(suyuConfigFile)

        # UI section
        if not suyuConfig.has_section("UI"):
            suyuConfig.add_section("UI")
        suyuConfig.set("UI", "fullscreen", "true")
        suyuConfig.set("UI", "fullscreen\\default", "true")
        suyuConfig.set("UI", "confirmClose", "false")
        suyuConfig.set("UI", "confirmClose\\default", "false")
        suyuConfig.set("UI", "firstStart", "false")
        suyuConfig.set("UI", "firstStart\\default", "false")
        suyuConfig.set("UI", "displayTitleBars", "false")
        suyuConfig.set("UI", "displayTitleBars\\default", "false")
        suyuConfig.set("UI", "enable_discord_presence", "false")
        suyuConfig.set("UI", "enable_discord_presence\\default", "false")
        suyuConfig.set("UI", "calloutFlags", "1")
        suyuConfig.set("UI", "calloutFlags\\default", "false")
        suyuConfig.set("UI", "confirmStop", "2")
        suyuConfig.set("UI", "confirmStop\\default", "false")

        # Single Window Mode
        suyuConfig.set("UI", "singleWindowMode", system.config.get("suyu_single_window", "true"))
        suyuConfig.set("UI", "singleWindowMode\\default", "false")

        suyuConfig.set("UI", "hideInactiveMouse", "true")
        suyuConfig.set("UI", "hideInactiveMouse\\default", "false")

        # Roms path (need for load update/dlc)
        suyuConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan", "true")
        suyuConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan\\default", "false")
        suyuConfig.set("UI", "Paths\\gamedirs\\1\\expanded", "true")
        suyuConfig.set("UI", "Paths\\gamedirs\\1\\expanded\\default", "false")
        suyuConfig.set("UI", "Paths\\gamedirs\\1\\path", "/userdata/roms/switch")
        suyuConfig.set("UI", "Paths\\gamedirs\\size", "1")

        suyuConfig.set("UI", "Screenshots\\enable_screenshot_save_as", "true")
        suyuConfig.set("UI", "Screenshots\\enable_screenshot_save_as\\default", "false")
        suyuConfig.set("UI", "Screenshots\\screenshot_path", "/userdata/screenshots")
        suyuConfig.set("UI", "Screenshots\\screenshot_path\\default", "false")

        # Change controller exit
        suyuConfig.set("UI", "Shortcuts\\Main%20Window\\Continue\\Pause%20Emulation\\Controller_KeySeq", "Home+Minus")
        suyuConfig.set("UI", "Shortcuts\\Main%20Window\\Exit%20suyu\\Controller_KeySeq", "Home+Plus")

        # Data Storage section
        if not suyuConfig.has_section("Data%20Storage"):
            suyuConfig.add_section("Data%20Storage")
        suyuConfig.set("Data%20Storage", "dump_directory", "/userdata/system/configs/suyu/dump")
        suyuConfig.set("Data%20Storage", "dump_directory\\default", "false")

        suyuConfig.set("Data%20Storage", "load_directory", "/userdata/system/configs/suyu/load")
        suyuConfig.set("Data%20Storage", "load_directory\\default", "false")

        suyuConfig.set("Data%20Storage", "nand_directory", "/userdata/system/configs/suyu/nand")
        suyuConfig.set("Data%20Storage", "nand_directory\\default", "false")

        suyuConfig.set("Data%20Storage", "sdmc_directory", "/userdata/system/configs/suyu/sdmc")
        suyuConfig.set("Data%20Storage", "sdmc_directory\\default", "false")

        suyuConfig.set("Data%20Storage", "tas_directory", "/userdata/system/configs/suyu/tas")
        suyuConfig.set("Data%20Storage", "tas_directory\\default", "false")

        suyuConfig.set("Data%20Storage", "use_virtual_sd", "true")
        suyuConfig.set("Data%20Storage", "use_virtual_sd\\default", "false")

        # Core section
        if not suyuConfig.has_section("Core"):
            suyuConfig.add_section("Core")

        # Multicore
        suyuConfig.set("Core", "use_multi_core", "true")
        suyuConfig.set("Core", "use_multi_core\\default", "false")

        # Renderer section
        if not suyuConfig.has_section("Renderer"):
            suyuConfig.add_section("Renderer")

        # Aspect ratio
        suyuConfig.set("Renderer", "aspect_ratio", system.config.get("suyu_ratio", "0"))
        suyuConfig.set("Renderer", "aspect_ratio\\default", "false")

        # Graphical backend
        if backend := system.config.get('suyu_backend'):
            suyuConfig.set("Renderer", "backend", backend)
            # Add vulkan logic
            if backend == "1" and vulkan.is_available():
                _logger.debug("Vulkan driver is available on the system.")
                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_index = vulkan.get_discrete_gpu_index()
                    if discrete_index:
                        _logger.debug("Using Discrete GPU Index: %s for Suyu", discrete_index)
                        suyuConfig.set("Renderer", "vulkan_device", discrete_index)
                        suyuConfig.set("Renderer", "vulkan_device\\default", "true")
                    else:
                        _logger.debug("Couldn't get discrete GPU index, using default")
                        suyuConfig.set("Renderer", "vulkan_device", "0")
                        suyuConfig.set("Renderer", "vulkan_device\\default", "true")
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
                    suyuConfig.set("Renderer", "vulkan_device", "0")
                    suyuConfig.set("Renderer", "vulkan_device\\default", "true")
        else:
            suyuConfig.set("Renderer", "backend", "0")
        suyuConfig.set("Renderer", "backend\\default", "false")

        # Async Shader compilation
        suyuConfig.set("Renderer", "use_asynchronous_shaders", system.config.get("suyu_async_shaders", "true"))
        suyuConfig.set("Renderer", "use_asynchronous_shaders\\default", "false")

        # Assembly shaders
        suyuConfig.set("Renderer", "shader_backend", system.config.get("suyu_shaderbackend", "0"))
        suyuConfig.set("Renderer", "shader_backend\\default", "false")

        # Async Gpu Emulation
        suyuConfig.set("Renderer", "use_asynchronous_gpu_emulation", system.config.get("suyu_async_gpu", "true"))
        suyuConfig.set("Renderer", "use_asynchronous_gpu_emulation\\default", "false")

        # NVDEC Emulation
        suyuConfig.set("Renderer", "nvdec_emulation", system.config.get("suyu_nvdec_emu", "2"))
        suyuConfig.set("Renderer", "nvdec_emulation\\default", "false")

        # GPU Accuracy
        suyuConfig.set("Renderer", "gpu_accuracy", system.config.get("suyu_accuracy", "0"))
        suyuConfig.set("Renderer", "gpu_accuracy\\default", "true")

        # Vsync
        suyuConfig.set("Renderer", "use_vsync", system.config.get("suyu_vsync", "1"))
        suyuConfig.set("Renderer", "use_vsync\\default", "false")

        # Max anisotropy
        suyuConfig.set("Renderer", "max_anisotropy", system.config.get("suyu_anisotropy", "0"))
        suyuConfig.set("Renderer", "max_anisotropy\\default", "false")

        # Resolution scaler
        suyuConfig.set("Renderer", "resolution_setup", system.config.get("suyu_scale", "2"))
        suyuConfig.set("Renderer", "resolution_setup\\default", "false")

        # Scaling filter
        suyuConfig.set("Renderer", "scaling_filter", system.config.get("suyu_scale_filter", "1"))
        suyuConfig.set("Renderer", "scaling_filter\\default", "false")

        # Anti aliasing method
        suyuConfig.set("Renderer", "anti_aliasing", system.config.get("suyu_aliasing_method", "0"))
        suyuConfig.set("Renderer", "anti_aliasing\\default", "false")

        # CPU Section
        if not suyuConfig.has_section("Cpu"):
            suyuConfig.add_section("Cpu")

        # CPU Accuracy
        suyuConfig.set("Cpu", "cpu_accuracy", system.config.get("suyu_cpuaccuracy", "0"))
        suyuConfig.set("Cpu", "cpu_accuracy\\default", "false")

        # System section
        if not suyuConfig.has_section("System"):
            suyuConfig.add_section("System")

        # Language
        suyuConfig.set("System", "language_index", system.config.get("suyu_language") or str(SuyuGenerator.getSuyuLangFromEnvironment()))
        suyuConfig.set("System", "language_index\\default", "false")

        # Region
        suyuConfig.set("System", "region_index", system.config.get("suyu_region") or str(SuyuGenerator.getSuyuRegionFromEnvironment()))
        suyuConfig.set("System", "region_index\\default", "false")

         # controls section
        if not suyuConfig.has_section("Controls"):
            suyuConfig.add_section("Controls")

        # Dock Mode
        suyuConfig.set("Controls", "use_docked_mode", system.config.get("suyu_dock_mode", "true"))
        suyuConfig.set("Controls", "use_docked_mode\\default", "false")

        # Sound Mode
        suyuConfig.set("Controls", "sound_index", system.config.get("suyu_sound_mode", "1"))
        suyuConfig.set("Controls", "sound_index\\default", "false")

        # Timezone
        suyuConfig.set("Controls", "time_zone_index", system.config.get("suyu_timezone", "0"))
        suyuConfig.set("Controls", "time_zone_index\\default", "false")

        # controllers
        for nplayer, pad in enumerate(playersControllers):
            suyuConfig.set("Controls", f"player_{nplayer}_type", system.config.get(f"p{nplayer+1}_pad", "0"))
            suyuConfig.set("Controls", rf"player_{nplayer}_type\default", "false")

            for x in suyuButtonsMapping:
                suyuConfig.set("Controls", f"player_{nplayer}_{x}", f'"{SuyuGenerator.setButton(suyuButtonsMapping[x], pad.guid, pad.inputs, nplayer)}"')
            for x in suyuAxisMapping:
                suyuConfig.set("Controls", f"player_{nplayer}_{x}", f'"{SuyuGenerator.setAxis(suyuAxisMapping[x], pad.guid, pad.inputs, nplayer)}"')
            suyuConfig.set("Controls", f"player_{nplayer}_motionleft", '"[empty]"')
            suyuConfig.set("Controls", f"player_{nplayer}_motionright", '"[empty]"')
            suyuConfig.set("Controls", f"player_{nplayer}_connected", "true")
            suyuConfig.set("Controls", f"player_{nplayer}_connected\\default", "false")
            suyuConfig.set("Controls", f"player_{nplayer}_vibration_enabled", "true")
            suyuConfig.set("Controls", f"player_{nplayer}_vibration_enabled\\default", "false")

        suyuConfig.set("Controls", "vibration_enabled", "true")
        suyuConfig.set("Controls", "vibration_enabled\\default", "false")

        for y in range(len(playersControllers), 9):
            suyuConfig.set("Controls", f"player_{y-1}_connected", "false")
            suyuConfig.set("Controls", rf"player_{y-1}_connected\default", "false")

        # telemetry section
        if not suyuConfig.has_section("WebService"):
            suyuConfig.add_section("WebService")
        suyuConfig.set("WebService", "enable_telemetry", "false")
        suyuConfig.set("WebService", "enable_telemetry\\default", "false")

        # Services section
        if not suyuConfig.has_section("Services"):
            suyuConfig.add_section("Services")
        suyuConfig.set("Services", "bcat_backend", "none")
        suyuConfig.set("Services", "bcat_backend\\default", "none")

        ### update the configuration file
        with ensure_parents_and_open(suyuConfigFile, 'w') as configfile:
            suyuConfig.write(configfile)

    @staticmethod
    def setButton(key: str, padGuid: str, padInputs: InputMapping, port: int) -> str:
        # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return f"engine:sdl,button:{input.id},guid:{padGuid},port:{port}"
            if input.type == "hat":
                return f"engine:sdl,hat:{input.id},direction:{SuyuGenerator.hatdirectionvalue(input.value)},guid:{padGuid},port:{port}"
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
    def getSuyuLangFromEnvironment():
        lang = environ['LANG'][:5]
        availableLanguages = { "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "nl_NL": 8, "pt_PT": 9 }
        if lang in availableLanguages:
            return availableLanguages[lang]
        return availableLanguages["en_US"]

    @staticmethod
    def getSuyuRegionFromEnvironment():
        lang = environ['LANG'][:5]
        availableRegions = { "en_US": 1, "ja_JP": 0 }
        if lang in availableRegions:
            return availableRegions[lang]
        return 2 # europe
