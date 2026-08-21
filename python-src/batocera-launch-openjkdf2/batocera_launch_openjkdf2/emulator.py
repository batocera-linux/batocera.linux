from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from batocera_launch import SystemConfig

_logger = logging.getLogger(__name__)

_BINARY_SRC: Final = Path('/usr/bin/openjkdf2')

# Represents the file content when created for the first time
_DEFAULT_PLAYER_CONFIG_TEMPLATE: Final = [
    'version 1\n',
    'diff 1\n',
    'fullsubtitles 0\n',
    'disablecutscenes 0\n',
    'rotateoverlaymap 1\n',
    'drawstatus 1\n',
    'crosshair 0\n',
    'sabercam 0\n',
    'autoPickup 1\n',
    'autoSwitch 3\n',
    'autoReload 0\n',
    'multiAutoPickup 15\n',
    'multiAutoSwitch 3\n',
    'multiAutoReload 3\n',
    'autoAim 1\n',
    'flags=24\n',
    'bind 0 200 0x2\n',
    'bind 0 208 0x6\n',
    'bind 0 17 0x2\n',
    'bind 0 31 0x6\n',
    'bind 0 72 0x2\n',
    'bind 0 80 0x6\n',
    'bind 0 1 0x5\n',
    'bind 1 75 0x6\n',
    'bind 1 203 0x2\n',
    'bind 1 205 0x6\n',
    'bind 1 0 0x5\n',
    'bind 1 12 0xd 0.400000\n',
    'bind 2 30 0x6\n',
    'bind 2 32 0x2\n',
    'bind 2 79 0x6\n',
    'bind 2 81 0x2\n',
    'bind 2 264 0x6\n',
    'bind 2 266 0x2\n',
    'bind 3 184 0x2\n',
    'bind 3 56 0x2\n',
    'bind 4 78 0x2\n',
    'bind 4 45 0x2\n',
    'bind 4 259 0x2\n',
    'bind 4 281 0x2\n',
    'bind 5 46 0x2\n',
    'bind 6 42 0x2\n',
    'bind 6 54 0x2\n',
    'bind 7 58 0x2\n',
    'bind 8 201 0x6\n',
    'bind 8 209 0x2\n',
    'bind 8 265 0x6\n',
    'bind 8 267 0x2\n',
    'bind 8 13 0xd 0.300000\n',
    'bind 8 14 0x1 4.000000\n',
    'bind 9 199 0x2\n',
    'bind 9 76 0x2\n',
    'bind 10 157 0x2\n',
    'bind 10 29 0x2\n',
    'bind 10 256 0x2\n',
    'bind 10 280 0x2\n',
    'bind 11 44 0x2\n',
    'bind 11 82 0x2\n',
    'bind 11 257 0x2\n',
    'bind 11 282 0x2\n',
    'bind 12 57 0x2\n',
    'bind 12 258 0x2\n',
    'bind 13 2 0x2\n',
    'bind 14 3 0x2\n',
    'bind 15 4 0x2\n',
    'bind 16 5 0x2\n',
    'bind 17 6 0x2\n',
    'bind 18 7 0x2\n',
    'bind 19 8 0x2\n',
    'bind 20 9 0x2\n',
    'bind 21 10 0x2\n',
    'bind 22 11 0x2\n',
    'bind 23 67 0x2\n',
    'bind 25 19 0x2\n',
    'bind 25 27 0x2\n',
    'bind 25 260 0x2\n',
    'bind 26 26 0x2\n',
    'bind 27 28 0x2\n',
    'bind 27 262 0x2\n',
    'bind 28 53 0x2\n',
    'bind 28 34 0x2\n',
    'bind 29 52 0x2\n',
    'bind 30 40 0x2\n',
    'bind 30 18 0x2\n',
    'bind 31 39 0x2\n',
    'bind 31 16 0x2\n',
    'bind 32 33 0x2\n',
    'bind 33 15 0x2\n',
    'bind 34 13 0x2\n',
    'bind 35 12 0x2\n',
    'bind 36 47 0x2\n',
    'bind 37 59 0x2\n',
    'bind 38 20 0x2\n',
    'bind 39 87 0x2\n',
    'bind 40 88 0x2\n',
    'bind 41 41 0x2\n',
    'bind 42 63 0x2\n',
    'bind 43 64 0x2\n',
    'bind 44 65 0x2\n',
    'bind 45 66 0x2\n',
    'bind 56 62 0x2\n',
    'bind 57 61 0x2\n',
    'bind 58 60 0x2\n',
    'end.\n',
    'numCutscenes 1\n',
    '01-02a.smk 1\n',
]

_DEFAULT_TEMPLATE_LINE_MAP: Final[dict[str, int]] = {
    parts[0]: i
    for i, line in enumerate(_DEFAULT_PLAYER_CONFIG_TEMPLATE)
    if len(parts := line.strip().split(' ', 1)) > 1
}

_PLAYER_SETTINGS_MAP: Final = {
    # Batocera Key: (PLR Key, Template Default Value)
    'jkdf2_difficulty': ('diff', '1'),
    'jkdf2_subs': ('fullsubtitles', '0'),
    'jkdf2_scenes': ('disablecutscenes', '0'),
    'jkdf2_map_rotate': ('rotateoverlaymap', '1'),
    'jkdf2_drawstatus': ('drawstatus', '1'),
    'jkdf2_crosshair': ('crosshair', '0'),
    'jkdf2_saber_camera': ('sabercam', '0'),
    'jkdf2_aiming': ('autoAim', '1'),
}

_JSON_SETTINGS_MAP: Final = {
    'jkdf2_waggle': ('bDisableWeaponWaggle', False),
    'jkdf2_jkgm': ('bEnableJkgm', True),
    'jkdf2_cache': ('bEnableTexturePrecache', True),
    'jkdf2_start': ('bFastMissionText', False),
    'jkdf2_janky': ('bJankyPhysics', False),
    'jkdf2_corpses': ('bKeepCorpses', False),
    'jkdf2_physics': ('bUseOldPlayerPhysics', False),
    'jkdf2_cogtickrate': ('canonicalCogTickrate', 0.019999999552965164),
    'jkdf2_phystickrate': ('canonicalPhysTickrate', 0.03999999910593033),
    'jkdf2_cross_line': ('crosshairLineWidth', 1.0),
    'jkdf2_cross_size': ('crosshairScale', 1.0),
    'jkdf2_bloom': ('enablebloom', False),
    'jkdf2_ssao': ('enablessao', 0),
    'jkdf2_vsync': ('enablevsync', False),
    'jkdf2_fov': ('fov', 90),
    'jkdf2_fov_vert': ('fovisvertical', True),
    'jkdf2_fps': ('fpslimit', 0),
    'jkdf2_gamma': ('gamma', 1.0),
    'jkdf2_hud_scale': ('hudScale', 2.0),
    'jkdf2_aspect': ('originalaspect', False),
    'jkdf2_fist_cross': ('setCrosshairOnFist', True),
    'jkdf2_saber_cross': ('setCrosshairOnLightsaber', True),
    'jkdf2_ssaa_multiple': ('ssaamultiple', 1.0),
    'jkdf2_texture': ('texturefiltering', False),
    'jkdf2_fullscreen': ('windowfullscreen', True),
    'jkdf2_hidpi': ('windowishidpi', True),
}

_CVAR_SETTINGS_MAP: Final = {
    'jkdf2_janky': ('g_bJankyPhysics', False),
    'jkdf2_corpses': ('g_bKeepCorpses', False),
    'jkdf2_physics': ('g_bUseOldPlayerPhysics', False),
    'jkdf2_cogtickrate': ('g_canonicalCogTickrate', 0.019999999552965164),
    'jkdf2_phystickrate': ('g_canonicalPhysTickrate', 0.03999999910593033),
    'jkdf2_cross_line': ('hud_crosshairLineWidth', 1.0),
    'jkdf2_cross_size': ('hud_crosshairScale', 1.0),
    'jkdf2_waggle': ('hud_disableWeaponWaggle', False),
    'jkdf2_hud_scale': ('hud_scale', 2.0),
    'jkdf2_fist_cross': ('hud_setCrosshairOnFist', True),
    'jkdf2_saber_cross': ('hud_setCrosshairOnLightsaber', True),
    'jkdf2_start': ('menu_bFastMissionText', False),
    'jkdf2_jkgm': ('r_bEnableJkgm', True),
    'jkdf2_cache': ('r_bEnableTexturePrecache', True),
    'jkdf2_bloom': ('r_enableBloom', False),
    'jkdf2_aspect': ('r_enableOrigAspect', False),
    'jkdf2_ssao': ('r_enableSSAO', False),
    'jkdf2_texture': ('r_enableTextureFilter', False),
    'jkdf2_vsync': ('r_enableVsync', False),
    'jkdf2_fov': ('r_fov', 90),
    'jkdf2_fov_vert': ('r_fovIsVertical', True),
    'jkdf2_fps': ('r_fpslimit', 0),
    'jkdf2_fullscreen': ('r_fullscreen', True),
    'jkdf2_gamma': ('r_gamma', 1.0),
    'jkdf2_hidpi': ('r_hidpi', True),
    'jkdf2_ssaa_multiple': ('r_ssaaMultiple', 1.0),
}


def _apply_settings_to_template(settings_to_set: dict[str, str], /) -> list[str]:
    output_lines = _DEFAULT_PLAYER_CONFIG_TEMPLATE[:]
    for plr_key, new_line_content in settings_to_set.items():
        if (line_index := _DEFAULT_TEMPLATE_LINE_MAP.get(plr_key)) is not None:
            output_lines[line_index] = new_line_content
    return output_lines


def _update_player_config(config_file: Path, settings_to_set: dict[str, str], /) -> None:
    output_lines: list[str] = []
    config_file.parent.mkdir(parents=True, exist_ok=True)

    if not config_file.exists():
        _logger.debug('Config file %s not found. Creating from template.', config_file)
        output_lines = _apply_settings_to_template(settings_to_set)
    else:
        _logger.debug('Config file %s exists. Modifying.', config_file)
        settings_processed = settings_to_set.copy()
        original_lines: list[str] = []
        try:
            original_lines = config_file.read_text().splitlines(keepends=True)
        except OSError as e:
            _logger.error('Error reading existing player config file %s: %s. Cannot modify.', config_file, e)
            _logger.info('Falling back to creating %s from template due to read error.', config_file)
            output_lines = _apply_settings_to_template(settings_to_set)
            original_lines = []

        if original_lines and (not output_lines) and (not original_lines[0].strip().lower().startswith('version ')):
            _logger.warning("Existing config %s missing 'version 1' at start. Prepending.", config_file)
            output_lines.append('version 1\n')
            start_index = 1 if original_lines[0].strip().lower().startswith('version ') else 0
            original_lines = original_lines[start_index:]

        if original_lines and not output_lines:
            for line in original_lines:
                stripped_line = line.strip()
                if stripped_line.lower().startswith('version '):
                    if not output_lines:
                        output_lines.append(line)
                    continue
                found_match = False
                for setting_key in list(settings_processed):
                    if stripped_line.startswith(f'{setting_key} '):
                        output_lines.append(settings_processed[setting_key])
                        del settings_processed[setting_key]
                        found_match = True
                        break
                if not found_match:
                    output_lines.append(line)
            if settings_processed:
                _logger.warning(
                    'Settings %s were not found in existing file %s. Appending them.',
                    list(settings_processed.keys()),
                    config_file,
                )
                output_lines.extend(settings_processed.values())

    try:
        config_file.write_text(''.join(output_lines))
        _logger.debug('Successfully wrote player config file: %s', config_file)
    except OSError as e:
        _logger.error('Error writing player config file %s: %s', config_file, e)


def _update_json_config(config_file: Path, settings_to_set: dict[str, Any], /) -> None:
    config_file.parent.mkdir(parents=True, exist_ok=True)
    existing_data: dict[str, Any] = {}
    if config_file.exists():
        try:
            content = config_file.read_text()
            if content.strip():
                existing_data = json.loads(content)
            else:
                _logger.warning('JSON config file %s is empty.', config_file)
        except (OSError, json.JSONDecodeError) as e:
            _logger.error('Error reading/parsing JSON config file %s: %s. Starting fresh.', config_file, e)
            existing_data = {}

    existing_data.update(settings_to_set)

    try:
        config_file.write_text(json.dumps(existing_data, indent=4))
    except OSError as e:
        _logger.error('Error writing JSON config file %s: %s', config_file, e)


def _convert_to_json_value(
    config: SystemConfig,
    config_key: str,
    default_value: bool | float,
    /,
) -> bool | int | float:
    config_value = config.get(config_key)
    if config_value is None:
        return default_value

    try:
        if isinstance(default_value, bool):
            return config.get_bool(config_key)
        if isinstance(default_value, int):
            if isinstance(config_value, bool):
                return 1 if config_value else 0
            return int(float(config_value))
        if isinstance(config_value, bool):
            return 1.0 if config_value else 0.0
        return float(config_value)
    except (ValueError, TypeError) as e:
        _logger.warning(
            "Conversion failed for '%s' to %s. Using default '%s'. Error: %s",
            config_value,
            type(default_value).__name__,
            default_value,
            e,
        )
        return default_value


@cached_dataclass
class OpenJKDF2(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'openjkdf2',
            'keys': {
                'exit': 'KEY_F10',
                'save_state': 'KEY_F9',
                'screenshot': 'KEY_F12',
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return self.config.get_bool('jkdf2_aspect', return_values=(4 / 3, 16 / 9))

    @property
    def execution_path(self) -> Path | None:
        return self.rom.parent

    @cached_property
    def config_dir(self) -> Path:
        return self.rom.parent / 'player' / 'Batocera'

    async def configure(self) -> Command:
        rom_dir = self.rom.parent
        binary_dest = rom_dir / 'openjkdf2'
        config_file = self.config_dir / 'openjkdf2.json'
        cvar_file = self.config_dir / 'openjkdf2_cvars.json'
        player_file = self.config_dir / 'Batocera.plr'

        self.config_dir.mkdir(parents=True, exist_ok=True)

        try:
            _logger.debug('Preparing settings for player config: %s', player_file)
            target_settings = {
                plr_key: f'{plr_key} {self.config.get_str(config_key, template_default)}\n'
                for config_key, (plr_key, template_default) in _PLAYER_SETTINGS_MAP.items()
            }

            auto_pickup = (
                self.config.get_int('jkdf2_pickup', 1) * 1
                + self.config.get_int('jkdf2_dangerous', 0) * 2
                + self.config.get_int('jkdf2_weaker', 0) * 4
                + self.config.get_int('jkdf2_saber', 0) * 8
            )
            auto_switch = (
                self.config.get_int('jkdf2_switch', 1) * 1
                + self.config.get_int(
                    'jkdf2_switch_dangerous',
                    1,
                )
                * 2
            )
            auto_reload = (
                self.config.get_int('jkdf2_reload', 0) * 1
                + self.config.get_int(
                    'jkdf2_reload_saber',
                    0,
                )
                * 2
            )
            multi_pickup = (
                self.config.get_int('jkdf2_pickup', 1) * 1
                + self.config.get_int('jkdf2_dangerous', 1) * 2
                + self.config.get_int('jkdf2_weaker', 1) * 4
                + self.config.get_int('jkdf2_saber', 1) * 8
            )
            multi_switch = (
                self.config.get_int('jkdf2_switch', 1) * 1
                + self.config.get_int(
                    'jkdf2_switch_dangerous',
                    1,
                )
                * 2
            )
            multi_reload = (
                self.config.get_int('jkdf2_reload', 1) * 1
                + self.config.get_int(
                    'jkdf2_reload_saber',
                    1,
                )
                * 2
            )

            target_settings['autoPickup'] = f'autoPickup {auto_pickup}\n'
            target_settings['autoSwitch'] = f'autoSwitch {auto_switch}\n'
            target_settings['autoReload'] = f'autoReload {auto_reload}\n'
            target_settings['multiAutoPickup'] = f'multiAutoPickup {multi_pickup}\n'
            target_settings['multiAutoSwitch'] = f'multiAutoSwitch {multi_switch}\n'
            target_settings['multiAutoReload'] = f'multiAutoReload {multi_reload}\n'

            _update_player_config(player_file, target_settings)
        except Exception:
            _logger.exception('Error preparing player configuration for %s', player_file)

        try:
            _logger.debug('Generating JSON config: %s', config_file)
            _update_json_config(
                config_file,
                {
                    json_key: (
                        self.config.get_bool(config_key, return_values=(1, 0))
                        if config_key == 'jkdf2_ssao'
                        else _convert_to_json_value(self.config, config_key, default)
                    )
                    for config_key, (json_key, default) in _JSON_SETTINGS_MAP.items()
                },
            )
        except Exception:
            _logger.exception('Error preparing JSON configuration for %s', config_file)

        try:
            _logger.debug('Generating CVAR JSON config: %s', cvar_file)
            _update_json_config(
                cvar_file,
                {
                    json_key: _convert_to_json_value(self.config, config_key, default)
                    for config_key, (json_key, default) in _CVAR_SETTINGS_MAP.items()
                },
            )
        except Exception:
            _logger.exception('Error preparing CVAR JSON configuration for %s', cvar_file)

        registry_file = rom_dir / 'registry.json'
        if registry_file.exists():
            _logger.debug('Registry file found. Updating config: %s', registry_file)
            _update_json_config(
                registry_file,
                {
                    'playerShortName': 'Batocera',
                    'Window_isFullscreen': True,
                },
            )
        else:
            _logger.debug('Registry file %s does not exist yet. Skipping config update.', registry_file)

        if not binary_dest.exists() or _BINARY_SRC.stat().st_mtime > binary_dest.stat().st_mtime:
            shutil.copy2(_BINARY_SRC, binary_dest)
            binary_dest.chmod(0o755)

        return Command(
            [binary_dest],
            env={'SDL_JOYSTICK_HIDAPI': '0'},
        )
