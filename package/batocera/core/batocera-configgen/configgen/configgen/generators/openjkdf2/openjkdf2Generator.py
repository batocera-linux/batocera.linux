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

import json
import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from ... import Command
from ...batoceraPaths import mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

# --- Default Template for Batocera.plr Creation ---
# Represents the file content when created for the first time
_DEFAULT_PLAYER_CONFIG_TEMPLATE: Final = [
    "version 1\n",
    "diff 1\n",
    "fullsubtitles 0\n",
    "disablecutscenes 0\n",
    "rotateoverlaymap 1\n",
    "drawstatus 1\n",
    "crosshair 0\n",
    "sabercam 0\n",
    "autoPickup 1\n",
    "autoSwitch 3\n",
    "autoReload 0\n",
    "multiAutoPickup 15\n",
    "multiAutoSwitch 3\n",
    "multiAutoReload 3\n",
    "autoAim 1\n",
    "flags=24\n",
    "bind 0 200 0x2\n",
    "bind 0 208 0x6\n",
    "bind 0 17 0x2\n",
    "bind 0 31 0x6\n",
    "bind 0 72 0x2\n",
    "bind 0 80 0x6\n",
    "bind 0 1 0x5\n",
    "bind 1 75 0x6\n",
    "bind 1 203 0x2\n",
    "bind 1 205 0x6\n",
    "bind 1 0 0x5\n",
    "bind 1 12 0xd 0.400000\n",
    "bind 2 30 0x6\n",
    "bind 2 32 0x2\n",
    "bind 2 79 0x6\n",
    "bind 2 81 0x2\n",
    "bind 2 264 0x6\n",
    "bind 2 266 0x2\n",
    "bind 3 184 0x2\n",
    "bind 3 56 0x2\n",
    "bind 4 78 0x2\n",
    "bind 4 45 0x2\n",
    "bind 4 259 0x2\n",
    "bind 4 281 0x2\n",
    "bind 5 46 0x2\n",
    "bind 6 42 0x2\n",
    "bind 6 54 0x2\n",
    "bind 7 58 0x2\n",
    "bind 8 201 0x6\n",
    "bind 8 209 0x2\n",
    "bind 8 265 0x6\n",
    "bind 8 267 0x2\n",
    "bind 8 13 0xd 0.300000\n",
    "bind 8 14 0x1 4.000000\n",
    "bind 9 199 0x2\n",
    "bind 9 76 0x2\n",
    "bind 10 157 0x2\n",
    "bind 10 29 0x2\n",
    "bind 10 256 0x2\n",
    "bind 10 280 0x2\n",
    "bind 11 44 0x2\n",
    "bind 11 82 0x2\n",
    "bind 11 257 0x2\n",
    "bind 11 282 0x2\n",
    "bind 12 57 0x2\n",
    "bind 12 258 0x2\n",
    "bind 13 2 0x2\n",
    "bind 14 3 0x2\n",
    "bind 15 4 0x2\n",
    "bind 16 5 0x2\n",
    "bind 17 6 0x2\n",
    "bind 18 7 0x2\n",
    "bind 19 8 0x2\n",
    "bind 20 9 0x2\n",
    "bind 21 10 0x2\n",
    "bind 22 11 0x2\n",
    "bind 23 67 0x2\n",
    "bind 25 19 0x2\n",
    "bind 25 27 0x2\n",
    "bind 25 260 0x2\n",
    "bind 26 26 0x2\n",
    "bind 27 28 0x2\n",
    "bind 27 262 0x2\n",
    "bind 28 53 0x2\n",
    "bind 28 34 0x2\n",
    "bind 29 52 0x2\n",
    "bind 30 40 0x2\n",
    "bind 30 18 0x2\n",
    "bind 31 39 0x2\n",
    "bind 31 16 0x2\n",
    "bind 32 33 0x2\n",
    "bind 33 15 0x2\n",
    "bind 34 13 0x2\n",
    "bind 35 12 0x2\n",
    "bind 36 47 0x2\n",
    "bind 37 59 0x2\n",
    "bind 38 20 0x2\n",
    "bind 39 87 0x2\n",
    "bind 40 88 0x2\n",
    "bind 41 41 0x2\n",
    "bind 42 63 0x2\n",
    "bind 43 64 0x2\n",
    "bind 44 65 0x2\n",
    "bind 45 66 0x2\n",
    "bind 56 62 0x2\n",
    "bind 57 61 0x2\n",
    "bind 58 60 0x2\n",
    "end.\n",
    "numCutscenes 1\n",
    "01-02a.smk 1\n"
]

# --- Helper to find line index in template ---
_DEFAULT_TEMPLATE_LINE_MAP: dict[str, int] = {}
for i, line in enumerate(_DEFAULT_PLAYER_CONFIG_TEMPLATE):
    stripped = line.strip()
    parts = stripped.split(" ", 1)
    if len(parts) > 1:
        # Use the first word (key)
        _DEFAULT_TEMPLATE_LINE_MAP[parts[0]] = i


class OpenJKDF2Generator(Generator):
    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "openjkdf2",
            "keys": {
                "exit": "KEY_F10",
                "save_state": "KEY_F9",
                "screenshot": "KEY_F12"
            }
        }

    def _update_player_config(self, config_file: Path, settings_to_set: dict[str, str]):

        output_lines: list[str] = []
        config_file.parent.mkdir(parents=True, exist_ok=True)
        if not config_file.exists():
            # --- Create file from Template ---
            _logger.debug("Config file %s not found. Creating from template.", config_file)
            output_lines = _DEFAULT_PLAYER_CONFIG_TEMPLATE[:]

            # Apply the settings provided onto the template
            for plr_key, new_line_content in settings_to_set.items():
                line_index = _DEFAULT_TEMPLATE_LINE_MAP.get(plr_key)
                if line_index is not None:
                    output_lines[line_index] = new_line_content
        else:
            # --- Modify Existing File ---
            _logger.debug("Config file %s exists. Modifying.", config_file)
            settings_processed = settings_to_set.copy()
            original_lines: list[str] = []
            processed_keys_in_file: set[str] = set()
            try:
                with config_file.open() as f_read:
                    original_lines = f_read.readlines()
            except OSError as e:
                _logger.error("Error reading existing player config file %s: %s. Cannot modify.", config_file, e)
                # Fallback to creation logic if read fails
                _logger.info("Falling back to creating %s from template due to read error.", config_file)
                output_lines = _DEFAULT_PLAYER_CONFIG_TEMPLATE[:]
                for plr_key, new_line_content in settings_to_set.items():
                    line_index = _DEFAULT_TEMPLATE_LINE_MAP.get(plr_key)
                    if line_index is not None:
                        output_lines[line_index] = new_line_content
                original_lines = []

            # Ensure "version 1" is present if file was malformed (and we didn't fallback)
            if original_lines and (not output_lines) and (not original_lines[0].strip().lower().startswith("version ")):
                 _logger.warning("Existing config %s missing 'version 1' at start. Prepending.", config_file)
                 output_lines.append("version 1\n")
                 # Add original lines after, skipping potential existing version line
                 start_index = 1 if original_lines and original_lines[0].strip().lower().startswith("version ") else 0
                 original_lines = original_lines[start_index:]

            if original_lines and not output_lines:
                for line in original_lines:
                    stripped_line = line.strip()
                    if stripped_line.lower().startswith("version "):
                        if not output_lines:
                           output_lines.append(line)
                        continue
                    found_match = False
                    keys_to_check = list(settings_processed.keys())
                    for setting_key in keys_to_check:
                        prefix = setting_key + " "
                        if stripped_line.startswith(prefix):
                            output_lines.append(settings_processed[setting_key])
                            processed_keys_in_file.add(setting_key)
                            del settings_processed[setting_key] # Remove processed key
                            found_match = True
                            #_logger.debug(f"  Applying setting: Replaced line for '{setting_key}' with '{settings_to_set[setting_key].strip()}'")
                            break
                    if not found_match:
                        output_lines.append(line)
                # Append any settings that were not found in the original file
                if settings_processed:
                     _logger.warning("Settings %s were not found in existing file %s. Appending them.", list(settings_processed.keys()), config_file)
                     output_lines.extend(settings_processed.values())

        # --- Write the final output ---
        try:
            with config_file.open('w') as f_write:
                f_write.writelines(output_lines)
            _logger.debug("Successfully wrote player config file: %s", config_file)
        except OSError as e:
            _logger.error("Error writing player config file %s: %s", config_file, e)

    def _update_json_config(self, config_file: Path, settings_to_set: dict[str, Any]):
        config_file.parent.mkdir(parents=True, exist_ok=True)
        existing_data = {}
        if config_file.exists():
            try:
                with config_file.open() as f_read:
                    content = f_read.read()
                    if content.strip():
                        existing_data = json.loads(content)
                    else:
                         _logger.warning("JSON config file %s is empty.", config_file)
            except (OSError, json.JSONDecodeError) as e:
                _logger.error("Error reading/parsing JSON config file %s: %s. Starting fresh.", config_file, e)
                existing_data = {}

        existing_data.update(settings_to_set)

        try:
            with config_file.open("w") as f_write:
                json.dump(existing_data, f_write, indent=4)
        except OSError as e:
            _logger.error("Error writing JSON config file %s: %s", config_file, e)

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # --- Setup Paths ---
        romdir = rom.parent
        binary_src = Path("/usr/bin/openjkdf2")
        binary_dest = romdir / "openjkdf2"
        openjkdf2_config_dir = romdir / "player" / "Batocera"
        openjkdf2_config_file = openjkdf2_config_dir / "openjkdf2.json"
        openjkdf2_cvar_file = openjkdf2_config_dir / "openjkdf2_cvars.json"
        openjkdf2_player_file = openjkdf2_config_dir / "Batocera.plr"

        mkdir_if_not_exists(openjkdf2_config_dir) # Ensure base dir exists

        # --- Player Config (.plr) Generation ---
        try:
            _logger.debug("Preparing settings for player config: %s", openjkdf2_player_file)
            # Map Batocera config keys to PLR keys AND the default value from the TEMPLATE
            # These defaults are only used if the Batocera key is MISSING
            settings_map = {
                # Batocera Key        # PLR Key             # Template Default Value
                "jkdf2_difficulty"  : ("diff",              "1"),
                "jkdf2_subs"        : ("fullsubtitles",     "0"),
                "jkdf2_scenes"      : ("disablecutscenes",  "0"),
                "jkdf2_map_rotate"  : ("rotateoverlaymap",  "1"),
                "jkdf2_drawstatus"  : ("drawstatus",        "1"),
                "jkdf2_crosshair"   : ("crosshair",         "0"),
                "jkdf2_saber_camera": ("sabercam",          "0"),
                "jkdf2_aiming"      : ("autoAim",           "1")
            }

            target_settings: dict[str, str] = {}

            for config_key, (plr_key, template_default_value) in settings_map.items():
                value = system.config.get_str(config_key, template_default_value)
                target_settings[plr_key] = f"{plr_key} {value}\n"

            # Calculate additional bitwise aggregated values
            autoPickup = (system.config.get_int("jkdf2_pickup", 1) * 1 +
                        system.config.get_int("jkdf2_dangerous", 0) * 2 +
                        system.config.get_int("jkdf2_weaker", 0) * 4 +
                        system.config.get_int("jkdf2_saber", 0) * 8)

            autoSwitch = (system.config.get_int("jkdf2_switch", 1) * 1 +
                        system.config.get_int("jkdf2_switch_dangerous", 1) * 2)

            autoReload = (system.config.get_int("jkdf2_reload", 0) * 1 +
                        system.config.get_int("jkdf2_reload_saber", 0) * 2)

            # Multimap defaults are different
            multiPickup = (system.config.get_int("jkdf2_pickup", 1) * 1 +
                        system.config.get_int("jkdf2_dangerous", 1) * 2 +
                        system.config.get_int("jkdf2_weaker", 1) * 4 +
                        system.config.get_int("jkdf2_saber", 1) * 8)

            multiSwitch = (system.config.get_int("jkdf2_switch", 1) * 1 +
                        system.config.get_int("jkdf2_switch_dangerous", 1) * 2)

            multiReload = (system.config.get_int("jkdf2_reload", 1) * 1 +
                        system.config.get_int("jkdf2_reload_saber", 1) * 2)

            # Add to single user settings
            target_settings["autoPickup"] = f"autoPickup {autoPickup}\n"
            target_settings["autoSwitch"] = f"autoSwitch {autoSwitch}\n"
            target_settings["autoReload"] = f"autoReload {autoReload}\n"
            # Add to multi-user settings
            target_settings["multiAutoPickup"] = f"multiAutoPickup {multiPickup}\n"
            target_settings["multiAutoSwitch"] = f"multiAutoSwitch {multiSwitch}\n"
            target_settings["multiAutoReload"] = f"multiAutoReload {multiReload}\n"

            self._update_player_config(openjkdf2_player_file, target_settings)

        except Exception as e:
            _logger.exception("Error preparing player configuration for %s: %s", openjkdf2_player_file, e)

        def _convert_to_json_value(config_key: str, default_value: bool | float, /) -> bool | float | str:
            config_value = system.config.get(config_key)
            target_type = type(default_value)
            final_value = default_value

            if config_value is not system.config.MISSING:
                try:
                    if target_type is bool:
                        parsed_value = system.config.get_bool(config_key)
                    elif target_type is int:
                        if isinstance(config_value, bool):
                            parsed_value = 1 if config_value else 0
                        else:
                            parsed_value = int(float(config_value))
                    elif target_type is float:
                            if isinstance(config_value, bool):
                                parsed_value = 1.0 if config_value else 0.0
                            else:
                                parsed_value = float(config_value)
                    elif target_type is str:
                        parsed_value = str(config_value)
                    else:
                            _logger.warning("Unhandled target type '%s' for key '%s'. Using raw string.", target_type.__name__, config_key)
                            parsed_value = str(config_value)
                    final_value = parsed_value
                except (ValueError, TypeError) as e:
                    _logger.warning("Conversion failed for '%s' to %s. Using default '%s'. Error: %s", config_value, target_type.__name__, default_value, e)
                    final_value = default_value

            return final_value

        # --- JSON Config (openjkdf2.json) Generation ---
        try:
            _logger.debug("Generating JSON config: %s", openjkdf2_config_file)
            json_settings_map = {
                "jkdf2_waggle"       : ("bDisableWeaponWaggle"    , False),
                "jkdf2_jkgm"         : ("bEnableJkgm"             , True),
                "jkdf2_cache"        : ("bEnableTexturePrecache"  , True),
                "jkdf2_start"        : ("bFastMissionText"        , False),
                "jkdf2_janky"        : ("bJankyPhysics"           , False),
                "jkdf2_corpses"      : ("bKeepCorpses"            , False),
                "jkdf2_physics"      : ("bUseOldPlayerPhysics"    , False),
                "jkdf2_cogtickrate"  : ("canonicalCogTickrate"    , 0.019999999552965164),
                "jkdf2_phystickrate" : ("canonicalPhysTickrate"   , 0.03999999910593033),
                "jkdf2_cross_line"   : ("crosshairLineWidth"      , 1.0),
                "jkdf2_cross_size"   : ("crosshairScale"          , 1.0),
                "jkdf2_bloom"        : ("enablebloom"             , False),
                "jkdf2_ssao"         : ("enablessao"              , 0),
                "jkdf2_vsync"        : ("enablevsync"             , False),
                "jkdf2_fov"          : ("fov"                     , 90),
                "jkdf2_fov_vert"     : ("fovisvertical"           , True),
                "jkdf2_fps"          : ("fpslimit"                , 0),
                "jkdf2_gamma"        : ("gamma"                   , 1.0),
                "jkdf2_hud_scale"    : ("hudScale"                , 2.0),
                "jkdf2_aspect"       : ("originalaspect"          , False),
                "jkdf2_fist_cross"   : ("setCrosshairOnFist"      , True),
                "jkdf2_saber_cross"  : ("setCrosshairOnLightsaber", True),
                "jkdf2_ssaa_multiple": ("ssaamultiple"            , 1.0),
                "jkdf2_texture"      : ("texturefiltering"        , False),
                "jkdf2_fullscreen"   : ("windowfullscreen"        , True),
                "jkdf2_hidpi"        : ("windowishidpi"           , True),
            }

            self._update_json_config(openjkdf2_config_file, {
                # Special case: jkdf2_ssao (bool in config, but int in JSON)
                json_key: system.config.get_bool(config_key, return_values=(1, 0)) if config_key == "jkdf2_ssao"
                else  _convert_to_json_value(config_key, generator_default_value)
                for config_key, (json_key, generator_default_value) in json_settings_map.items()
            })

        except Exception as e:
            _logger.exception("Error preparing JSON configuration for %s: %s", openjkdf2_config_file, e)

        # --- CVAR JSON Config Generation ---
        try:
            _logger.debug("Generating CVAR JSON config: %s", openjkdf2_cvar_file)
            cvar_settings_map = {
                "jkdf2_janky"        : ("g_bJankyPhysics"             , False),
                "jkdf2_corpses"      : ("g_bKeepCorpses"              , False),
                "jkdf2_physics"      : ("g_bUseOldPlayerPhysics"      , False),
                "jkdf2_cogtickrate"  : ("g_canonicalCogTickrate"      , 0.019999999552965164),
                "jkdf2_phystickrate" : ("g_canonicalPhysTickrate"     , 0.03999999910593033),
                "jkdf2_cross_line"   : ("hud_crosshairLineWidth"      , 1.0),
                "jkdf2_cross_size"   : ("hud_crosshairScale"          , 1.0),
                "jkdf2_waggle"       : ("hud_disableWeaponWaggle"     , False),
                "jkdf2_hud_scale"    : ("hud_scale"                   , 2.0),
                "jkdf2_fist_cross"   : ("hud_setCrosshairOnFist"      , True),
                "jkdf2_saber_cross"  : ("hud_setCrosshairOnLightsaber", True),
                "jkdf2_start"        : ("menu_bFastMissionText"       , False),
                "jkdf2_jkgm"         : ("r_bEnableJkgm"               , True),
                "jkdf2_cache"        : ("r_bEnableTexturePrecache"    , True),
                "jkdf2_bloom"        : ("r_enableBloom"               , False),
                "jkdf2_aspect"       : ("r_enableOrigAspect"          , False),
                "jkdf2_ssao"         : ("r_enableSSAO"                , False),
                "jkdf2_texture"      : ("r_enableTextureFilter"       , False),
                "jkdf2_vsync"        : ("r_enableVsync"               , False),
                "jkdf2_fov"          : ("r_fov"                       , 90),
                "jkdf2_fov_vert"     : ("r_fovIsVertical"             , True),
                "jkdf2_fps"          : ("r_fpslimit"                  , 0),
                "jkdf2_fullscreen"   : ("r_fullscreen"                , True),
                "jkdf2_gamma"        : ("r_gamma"                     , 1.0),
                "jkdf2_hidpi"        : ("r_hidpi"                     , True),
                "jkdf2_ssaa_multiple": ("r_ssaaMultiple"              , 1.0)
            }

            self._update_json_config(openjkdf2_cvar_file, {
                json_key: _convert_to_json_value(config_key, generator_default_value)
                for config_key, (json_key, generator_default_value) in cvar_settings_map.items()
            })

        except Exception as e:
            _logger.exception("Error preparing CVAR JSON configuration for %s: %s", openjkdf2_cvar_file, e)

        # Check if the binary exists in the destination and if it is outdated
        if not binary_dest.exists() or binary_src.stat().st_mtime > binary_dest.stat().st_mtime:
            shutil.copy2(binary_src, binary_dest)
            binary_dest.chmod(0o755)

        # --- Change Directory & Prepare Command ---
        os.chdir(romdir)

        commandArray = [str(binary_dest)]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    # Show mouse on screen for the Config Screen
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get_bool("jkdf2_aspect"):
            return 4/3
        return 16/9
