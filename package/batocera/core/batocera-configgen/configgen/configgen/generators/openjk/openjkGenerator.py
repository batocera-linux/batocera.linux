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

from typing import TYPE_CHECKING, Any, Dict, List, Set, Optional, Tuple

import shutil
import os
import logging
from pathlib import Path
from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...config import Config
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...config import SystemConfig
    from ...types import HotkeysContext, Resolution

_logger = logging.getLogger(__name__)

class OpenJKGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "openjk",
            "keys": {
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "restore_state": "KEY_F9",
                "save_state": "KEY_F12"
            }
        }

    def generate(self, system, rom: Path, playersControllers: dict, metadata: dict, guns: list, wheels: list, gameResolution: Resolution):

        # Setup the paths variations
        romdir = rom.parent
        if "academy" in rom.name.lower():
            _logger.info("Found Jedi Academy!")
            binary_src_path = Path("/usr/bin/JediAcademy")
            binary_src = binary_src_path / "openjk_sp.x86_64"
            binary_dest = romdir / "openjk_sp.x86_64"
            config_path = CONFIGS / "openjk" / "base"
            config_file_path = config_path / "openjk_sp.cfg"
        elif "outcast" in rom.name.lower():
            _logger.info("Found Jedi Outcast!")
            binary_src_path = Path("/usr/bin/JediOutcast")
            binary_src = binary_src_path / "openjo_sp.x86_64"
            binary_dest = romdir / "openjo_sp.x86_64"
            config_path = CONFIGS / "openjo" / "base"
            config_file_path = config_path / "openjo_sp.cfg"
        else:
            _logger.info("Could not determine which game you're using!")
            _logger.info("Rename your .jedi file as per the _infot.txt file")
            return
        
        ## Configuration 
        mkdir_if_not_exists(config_path)
        # Set custom defaults
        options_to_set = {
            "seta r_mode": "-2",
            "seta r_fullscreen": "1",
            "seta r_centerWindow": "1",
            "seta r_customheight": f"{gameResolution['height']}",
            "seta r_customwidth": f"{gameResolution['width']}"
        }
        remove_keys = []

        # - Video options -
        # Colour Depth
        depth = system.config.get("openjk_colour")
        if depth and depth == "16":
            options_to_set["seta r_colorbits"] = depth
            options_to_set["seta r_depthbits"] = depth
        elif depth and depth == "32":
            options_to_set["seta r_colorbits"] = depth
            options_to_set["seta r_depthbits"] = "24"
        else:
            remove_keys += ["seta r_colorbits", "seta r_depthbits"]
        # Geometric Detail
        geometric = system.config.get("openjk_detail")
        if geometric == "Low":
            options_to_set["seta r_lodbias"] = "2"
            options_to_set["seta r_subdivisions"] = "20"
        elif geometric == "Medium":
            options_to_set["seta r_lodbias"] = "1"
            options_to_set["seta r_subdivisions"] = "12"  
        else:
            remove_keys += ["seta r_lodbias", "seta r_subdivisions"]
        # Texture Detail
        options_to_set["seta r_picmip"] = system.config.get("openjk_texture", "0")
        # Texture Quality
        texture_quality = system.config.get("openjk_texture_quality")
        if texture_quality and texture_quality != "0":
            options_to_set["seta r_texturebits"] = system.config.get("openjk_texture_quality")
        else:
            remove_keys += ["seta r_texturebits"]
        # Texture Filter
        options_to_set["seta r_textureMode"] = system.config.get("openjk_texture_filter", "GL_LINEAR_MIPMAP_LINEAR")
        # Detailed Shaders
        shaders = system.config.get("openjk_shaders")
        if shaders and shaders == "0":
            options_to_set["seta r_detailtextures"] = system.config.get("openjk_shaders")
        else:
            remove_keys += ["seta r_detailtextures"]
        # Video Sync
        vsync = system.config.get("openjk_vsync")
        if vsync == "1":
            options_to_set["seta r_swapInterval"] = system.config.get("openjk_vsync")
        else:
            remove_keys += ["seta r_swapInterval"]
        # - More Video options -
        # Brightness
        if system.config.get("openjk_brightness"):
            options_to_set["seta r_gamma"] = system.config.get("openjk_brightness")
        else:
            options_to_set["seta r_gamma"] = "1.000000"
        # Shadows
        if system.config.get("openjk_shadows"):
            options_to_set["seta cg_shadows"] = system.config.get("openjk_shadows")
        else:
            options_to_set["seta cg_shadows"] = "1"
        # Dynamic Lights
        if system.config.get("openjk_lights"):
            options_to_set["seta r_dynamiclight"] = system.config.get("openjk_lights")
        else:
            options_to_set["seta r_dynamiclight"] = "1"
        # Dynamic Glow
        if system.config.get_bool("openjk_glow"):
            options_to_set["seta r_DynamicGlow"] = "1"
        else:
            remove_keys += ["seta r_DynamicGlow"]
        # Light Flares
        options_to_set["seta r_flares"] = system.config.get("openjk_flares", "1")
        # Wall Marks
        options_to_set["seta cg_marks"] = system.config.get("openjk_wall", "1")
        # Anisotropic Filter
        options_to_set["seta r_ext_texture_filter_anisotropic"] = system.config.get("openjk_anistropic", "16.000000")
        # Draw Crosshair
        options_to_set["seta cg_drawCrosshair"] = system.config.get("openjk_crosshair", "1")
        # Identify Target
        options_to_set["seta cg_crosshairIdentifyTarget"] = system.config.get("openjk_target", "1")
        # Slow Motion Death
        options_to_set["seta d_slowmodeath"] = system.config.get("openjk_death", "3")
        # 1st Person Guns
        options_to_set["seta cg_gunAutoFirst"] = system.config.get("openjk_guns" ,"1")
        # Model Dismemberment
        options_to_set["seta g_dismemberment"] = system.config.get("openjk_dismember" ,"1")
        # View Swaying
        options_to_set["seta ui_disableWeaponSway"] = system.config.get("openjk_sway" ,"0")
        # Language
        options_to_set["seta se_language"] = system.config.get("openjk_text", "english")
        options_to_set["seta s_language"] = system.config.get("openjk_voice", "english")
        # Subtitles
        options_to_set["seta g_subtitles"] = system.config.get("openjk_subtitles", "0")

        # Check if the config file exists
        if config_file_path.is_file():
            with config_file_path.open('r') as config_file:
                lines = config_file.readlines()
            
            # Remove keys if defined
            lines = [line for line in lines if not any(key in line for key in remove_keys)]

            # Loop through the options and update the lines
            for key, value in options_to_set.items():
                option_exists = any(key in line for line in lines)
                if not option_exists:
                    lines.append(f"{key} \"{value}\"\n")
                else:
                    for i, line in enumerate(lines):
                        if key in line:
                            lines[i] = f"{key} \"{value}\"\n"

            # Write the modified content back to the file
            with config_file_path.open('w') as config_file:
                config_file.writelines(lines)
                _logger.info(f"OpenJK config file {config_file_path} updated.")
        else:
            # File doesn't exist, create it and add the options
            with config_file_path.open('w') as config_file:
                for key, value in options_to_set.items():
                    config_file.write(f"{key} \"{value}\"\n")
                    _logger.info(f"OpenJK config file {config_file_path} updated.")

        # Check if the binary exists in the destination and if it is outdated
        if not binary_dest.exists() or os.path.getmtime(binary_src) > os.path.getmtime(binary_dest):
            for item in binary_src_path.iterdir():
                src_item = item
                dest_item = romdir / item.name

                if src_item.is_dir():
                    shutil.copytree(src_item, dest_item, dirs_exist_ok=True)
                    _logger.debug(f"Copying {src_item} to {dest_item}")
                else:
                    shutil.copy2(src_item, dest_item)
                    _logger.debug(f"Copying {src_item} to {dest_item}")
            
            if binary_dest.exists() and binary_dest.is_file():
                os.chmod(binary_dest, 0o755)
        
        # Change Directory & Prepare Command
        os.chdir(romdir)

        commandArray = [str(binary_dest)]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
