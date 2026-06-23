#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
from __future__ import annotations

import logging
import os
import sys
import json
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils import vulkan
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class shadPS4Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "shadps4",
            "keys": {"exit": ["KEY_LEFTALT", "KEY_F4"]}
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Set the paths using Path objects
        json_path = CONFIGS / "shadPS4"
        json_file = json_path / "config.json"
        input_path = json_path / "input_config"
        savesPath = Path("/userdata/saves/shadps4")
        romDir = Path("/userdata/roms/ps4")
        dlcPath = romDir / "DLC"

        mkdir_if_not_exists(json_path)
        mkdir_if_not_exists(savesPath)
        mkdir_if_not_exists(input_path) # fixes hang if folder not present

        # Check Vulkan first before doing anything
        discrete_index = -1
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            vulkan_version = vulkan.get_version()
            if vulkan_version > "1.3":
                _logger.debug("Using Vulkan version: %s", vulkan_version)
                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_index = vulkan.get_discrete_gpu_index()
                    if discrete_index is not None and discrete_index != -1:
                        _logger.debug("Using Discrete GPU Index: %s for shadPS4", discrete_index)
                    else:
                        _logger.debug("Couldn't get discrete GPU index")
                        discrete_index = 0
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
            else:
                _logger.debug("Vulkan version: %s is not compatible with shadPS4", vulkan_version)
        else:
            _logger.debug("*** Vulkan driver required is not available on the system!!! ***")
            sys.exit(1)

        # Adjust the config.json file
        config: dict[str, dict[str, object]] = {}

        # Check if the file exists
        if json_file.is_file():
            try:
                with json_file.open("r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                 _logger.error("Failed to load existing shadps4 config: %s. Will create default.", e)

        # If config is empty, create default structure
        if not config:
             _logger.info("Creating default shadps4 config at %s", json_file)
             config = {
                "Audio": {
                    "audio_backend": 0,
                    "openal_main_output_device": "Default Device",
                    "openal_mic_device": "Default Device",
                    "openal_padSpk_output_device": "Default Device",
                    "sdl_main_output_device": "Default Device",
                    "sdl_mic_device": "Default Device",
                    "sdl_padSpk_output_device": "Default Device"
                },
                "Debug": {
                    "config_version": "GITDIR-NOTFOUND",
                    "debug_dump": False,
                    "shader_collect": False
                },
                "GPU": {
                    "copy_gpu_buffers": False,
                    "direct_memory_access_enabled": False,
                    "dump_shaders": False,
                    "fsr_enabled": False,
                    "full_screen": True,
                    "full_screen_mode": "Windowed",
                    "hdr_allowed": False,
                    "internal_screen_height": 720,
                    "internal_screen_width": 1280,
                    "null_gpu": False,
                    "patch_shaders": False,
                    "present_mode": "Mailbox",
                    "rcas_attenuation": 250,
                    "rcas_enabled": True,
                    "readback_linear_images_enabled": False,
                    "readbacks_mode": 0,
                    "vblank_frequency": 60,
                    "window_height": int(gameResolution["height"]),
                    "window_width": int(gameResolution["width"])
                },
                "General": {
                    "addon_install_dir": str(dlcPath),
                    "big_picture_scale": 1000,
                    "connected_to_network": False,
                    "console_language": 1,
                    "dev_kit_mode": False,
                    "discord_rpc_enabled": False,
                    "extra_dmem_in_mbytes": 0,
                    "font_dir": "",
                    "home_dir": str(savesPath),
                    "install_dirs": [{"enabled": True, "path": str(romDir)}],
                    "neo_mode": False,
                    "shad_net_enabled": False,
                    "shadnet_server": "",
                    "show_fps_counter": False,
                    "show_splash": False,
                    "sys_modules_dir": "",
                    "trophy_notification_duration": 6.0,
                    "trophy_notification_side": "right",
                    "trophy_popup_disabled": False,
                    "volume_slider": 100
                },
                "Input": {
                    "background_controller_input": False,
                    "camera_id": -1,
                    "cursor_hide_timeout": 5,
                    "cursor_state": 1,
                    "default_controller_id": "",
                    "ime_accessibility_enabled": False,
                    "ime_url_mail_short_panel": False,
                    "is_circle_enter": False,
                    "motion_controls_enabled": True,
                    "special_pad_class": 1,
                    "usb_device_backend": 0,
                    "use_special_pad": False,
                    "use_unified_input_config": True
                },
                "Log": {
                    "append": False,
                    "enable": True,
                    "filter": "",
                    "max_skip_duration": 5000,
                    "separate": False,
                    "size_limit": 104857600,
                    "skip_duplicate": True,
                    "sync": True
                },
                "Vulkan": {
                    "gpu_id": int(discrete_index),
                    "pipeline_cache_archived": False,
                    "pipeline_cache_enabled": False,
                    "renderdoc_enabled": False,
                    "vkcrash_diagnostic_enabled": False,
                    "vkguest_markers": False,
                    "vkhost_markers": False,
                    "vkvalidation_core_enabled": True,
                    "vkvalidation_enabled": False,
                    "vkvalidation_gpu_enabled": False,
                    "vkvalidation_sync_enabled": False
                }
             }

        # --- Apply Batocera Specific Overrides ---
        general_config = config.setdefault("General", {})
        general_config["discord_rpc_enabled"] = False
        general_config["addon_install_dir"] = str(dlcPath)
        general_config["install_dirs"] = [{"enabled": True, "path": str(romDir)}]
        general_config["home_dir"] = str(savesPath)

        # GPU
        gpu_config = config.setdefault("GPU", {})
        gpu_config["full_screen"] = True
        gpu_config["full_screen_mode"] = "Fullscreen (Borderless)"
        gpu_config["window_width"] = int(gameResolution["width"])
        gpu_config["window_height"] = int(gameResolution["height"])

        # Vulkan - Set the detected GPU ID
        vulkan_config = config.setdefault("Vulkan", {})
        vulkan_config["gpu_id"] = int(discrete_index)
        vulkan_config["pipeline_cache_enabled"] = True

        # Options - GRAPHICS
        gpu_config["fsr_enabled"] = system.config.get_bool("shadps4_fsr")
        gpu_config["rcas_enabled"] = system.config.get_bool("shadps4_rcas")
        gpu_config["hdr_allowed"] = system.config.get_bool("shadps4_hdr")

        # Options - DISPLAY
        gpu_config["present_mode"] = system.config.get("shadps4_present_mode") or "Mailbox"
        gpu_config["vblank_frequency"] = int(system.config.get("shadps4_vblank_freq") or 60)
        general_config["show_fps_counter"] = system.config.get_bool("shadps4_show_fps")

        # Options - SYSTEM
        general_config["neo_mode"] = system.config.get_bool("shadps4_neo_mode")
        general_config["console_language"] = int(system.config.get("shadps4_console_lang") or 1)

        # Options - ADVANCED
        gpu_config["copy_gpu_buffers"] = system.config.get_bool("shadps4_copy_gpu_buffers")
        gpu_config["readbacks_mode"] = int(system.config.get("shadps4_readbacks_mode") or 0)
        gpu_config["direct_memory_access_enabled"] = system.config.get_bool("shadps4_dma")
        vulkan_config["pipeline_cache_archived"] = system.config.get_bool("shadps4_pipeline_cache")

        log_config = config.setdefault("Log", {})
        log_config["enable"] = system.config.get_bool("shadps4_logging")

        # Create necessary directories if they do not exist
        mkdir_if_not_exists(json_file.parent)

        # Now write the updated json
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # Determine the path/command based on rom type
        if rom == "config" or str(rom) == "config":
            commandArray: list[str | Path] = [
                "/usr/bin/shadPS4QtLauncher"
            ]
        else:
            if rom.is_dir():
                eboot_path = rom / "eboot.bin"
            else:
                eboot_path = rom.parent / "eboot.bin"
            
            commandArray: list[str | Path] = [
                "/usr/bin/shadps4",
                "--game",
                eboot_path,
                "--fullscreen",
                "true"
            ]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
                "XDG_DATA_HOME": CONFIGS
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
