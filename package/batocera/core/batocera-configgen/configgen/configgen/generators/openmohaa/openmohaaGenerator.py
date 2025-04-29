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
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class OpenMOHAAGenerator(Generator):
    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "openmohaa",
            "keys": {
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "save_state": "KEY_F5",
                "restore_state": "KEY_F9",
                "menu": "KEY_ESC",
                "pause": "KEY_PAUSE"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Setup the paths variations
        romdir = rom.parent

        config_path = CONFIGS / "openmohaa"
        mkdir_if_not_exists(config_path)

        # Change Directory & Prepare Command
        os.chdir(romdir)

        # Setup version to play
        rom_name_lower = rom.name.lower()
        variant_subdir = "main"
        target_game = "0"

        if "spear" in rom_name_lower:
            _logger.info("Found Spearhead!")
            variant_subdir = "mainta"
            target_game = "1"
        elif "break" in rom_name_lower:
            _logger.info("Found Breakthrough!")
            variant_subdir = "maintt"
            target_game = "2"

        # Construct paths based on the determined variant sub-directory
        variant_config_path = config_path / variant_subdir / "configs"
        mkdir_if_not_exists(variant_config_path)
        config_file_path = variant_config_path / "omconfig.cfg"

        # Define the default options to add or modify
        options_to_set = {
            "seta r_mode": "-1",
            "seta r_fullscreen": "1",
            "seta r_allowResize": "0",
            "seta r_centerWindow": "1",
            "seta r_customheight": f'"{gameResolution["height"]}"',
            "seta r_customwidth": f'"{gameResolution["width"]}"',
            "seta r_customaspect": "1",
            "bind [": "weapprev",
            "bind ]": "weapnext"
        }

        # -= Video Options =-

        # Colour Depth
        options_to_set["seta r_colorbits"] = system.config.get_str("mohaa_colour", "0")
        # Texture Detail
        options_to_set["seta r_picmip"] = system.config.get_str("mohaa_texture", "1")
        # Texture Colour Depth
        options_to_set["seta r_texturebits"] = system.config.get_str("mohaa_texture_colour", "0")
        # Texture Filter
        options_to_set["seta r_textureMode"] = system.config.get_str("mohaa_texture_filter", "GL_LINEAR_MIPMAP_NEAREST")
        # Wall Decals
        options_to_set["seta cg_marks_add"] = system.config.get_str("mohaa_decals", "0")
        # Weather Effects
        options_to_set["seta cg_rain"] = system.config.get_str("mohaa_weather", "0")
        # Brightnes
        options_to_set["seta r_gamma"] = system.config.get_str("mohaa_brightness", "1.000000")
        # Texture Compression
        options_to_set["seta r_ext_compressed_textures"] = system.config.get_str("mohaa_compression", "0")

        # -= Advanced Options =-

        # View Model
        options_to_set["seta cg_drawviewmodel"] = system.config.get_str("mohaa_view", "2")
        # Shadows
        options_to_set["seta cg_shadows"] = system.config.get_str("mohaa_shadows", "1")

        # Terrain Detail
        match system.config.get_str("mohaa_terrain"):
            case "0":
                ter_maxlod = "3"
                ter_error = "10"
            case "1":
                ter_maxlod = "4"
                ter_error = "9"
            case "2":
                ter_maxlod = "5"
                ter_error = "7"
            case _:
                ter_maxlod = "6"
                ter_error = "4"

        options_to_set["seta ter_maxlod"] = ter_maxlod
        options_to_set["seta ter_error"] = ter_error

        # Model Detail
        match system.config.get_str("mohaa_model"):
            case "0":
                r_lodviewmodelcap = "0.25"
                r_lodcap = "0.25"
                r_lodscale = "0.25"
            case "1":
                r_lodviewmodelcap = "0.25"
                r_lodcap = "0.35"
                r_lodscale = "0.35"
            case "2":
                r_lodviewmodelcap = "0.45"
                r_lodcap = "0.35"
                r_lodscale = "0.45"
            case "3":
                r_lodviewmodelcap = "0.55"
                r_lodcap = "0.5"
                r_lodscale = "0.55"
            case "4":
                r_lodviewmodelcap = "0.9"
                r_lodcap = "0.9"
                r_lodscale = "0.9"
            case _:
                r_lodviewmodelcap = "0.25"
                r_lodcap = "0.35"
                r_lodscale = "5"

        options_to_set["seta r_lodviewmodelcap"] = r_lodviewmodelcap
        options_to_set["seta r_lodcap"] = r_lodcap
        options_to_set["seta r_lodscale"] = r_lodscale

        # Effects Detail
        match system.config.get_str("mohaa_effects"):
            case "1":
                cg_effectdetail = "0.3"
                vss_maxcount = "23"
            case "2":
                cg_effectdetail = "0.5"
                vss_maxcount = "22"
            case "3":
                cg_effectdetail = "0.7"
                vss_maxcount = "20"
            case "4":
                cg_effectdetail = "0.8"
                vss_maxcount = "18"
            case "5":
                cg_effectdetail = "0.95"
                vss_maxcount = "15"
            case "6":
                cg_effectdetail = "1.0"
                vss_maxcount = "10"
            case _:
                cg_effectdetail = "0.2"
                vss_maxcount = "22"

        options_to_set["seta cg_effectdetail"] = cg_effectdetail
        options_to_set["seta vss_maxcount"] = vss_maxcount

        # Curve Detail
        match system.config.get_str("mohaa_curve"):
            case "0":
                r_subdivisions = "20"
            case "1":
                r_subdivisions = "10"
            case "3":
                r_subdivisions = "3"
            case _:
                r_subdivisions = "4"

        options_to_set["seta r_subdivisions"] = r_subdivisions

        # Subtitles
        options_to_set["seta g_subtitle"] = system.config.get_str("mohaa_subtitles", "0")
        # Real Dynamic Lighting
        options_to_set["seta r_fastdlights"] = system.config.get_str("mohaa_dynamic_lighting", "1")
        # Full Entity Lighting
        options_to_set["seta r_fastentlight"] = system.config.get_str("mohaa_entity_lighting", "1")
        # Volumetric Smoke
        options_to_set["seta vss_draw"] = system.config.get_str("mohaa_smoke", "0")
        # Weapons Bar
        options_to_set["seta ui_weaponsbar"] = system.config.get_str("mohaa_weapons", "1")
        # Crosshair
        options_to_set["seta ui_crosshair"] = system.config.get_str("mohaa_crosshair", "1")

        # Check if the omconfig.cfg file exists
        if config_file_path.is_file():
            with config_file_path.open('r') as config_file:
                lines = config_file.readlines()

            # Loop through the options and update the lines
            options_in_file = set()
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                for key, value in options_to_set.items():
                    if stripped_line.startswith(key + " "):
                        lines[i] = f"{key} \"{value}\"\n"
                        options_in_file.add(key)
                        break
            # Add options that weren't found at all
            for key, value in options_to_set.items():
                if key not in options_in_file:
                    lines.append(f"{key} \"{value}\"\n")

            # Write the modified content back to the file
            with config_file_path.open('w') as config_file:
                config_file.writelines(lines)
        else:
            # File doesn't exist, create it and add the options
            with config_file_path.open('w') as config_file:
                for key, value in options_to_set.items():
                    config_file.write(f"{key} \"{value}\"\n")

        # Now let's run
        return Command.Command(array=[
            "/usr/bin/openmohaa/openmohaa",
            # Not the full config_path
            "+set", "com_homepath", "configs/openmohaa",
            # Set the target game via command line argument
            "+set", "com_target_game", target_game
        ])

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
