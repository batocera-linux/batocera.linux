from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.paths import CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_D3XP_MODS: Final = {'perfected_roe', 'sikkmodd3xp', 'bloodmod_roe'}


@cached_dataclass
class Dhewm3(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dhewm3',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F9',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        with self.rom.open(encoding='utf-8') as file:
            directory = file.readline().strip().split('/')[0]
            _logger.debug('Using directory: %s', directory)

        config_base_dir = self.config_dir / 'base'
        config_subdir = self.config_dir / directory
        config_base_file = config_base_dir / 'dhewm.cfg'
        config_file = config_subdir / 'dhewm.cfg'

        config_base_dir.mkdir(parents=True, exist_ok=True)
        config_subdir.mkdir(parents=True, exist_ok=True)

        options_to_set = {
            'seta r_mode': '-1',
            'seta r_fullscreen': '1',
            'seta r_customHeight': str(self.resolution.height),
            'seta r_customWidth': str(self.resolution.width),
            'bind "JOY_BTN_SOUTH"': '_moveUp',
            'bind "JOY_BTN_EAST"': '_moveDown',
            'bind "JOY_BTN_WEST"': '_impulse19',
            'bind "JOY_BTN_NORTH"': '_impulse13',
            'bind "JOY_BTN_LSTICK"': '_strafe',
            'bind "JOY_BTN_RSTICK"': '_speed',
            'bind "JOY_BTN_LSHOULDER"': '_impulse15',
            'bind "JOY_BTN_RSHOULDER"': '_impulse14',
            'bind "JOY_STICK1_UP"': '_forward',
            'bind "JOY_STICK1_DOWN"': '_back',
            'bind "JOY_STICK1_LEFT"': '_moveLeft',
            'bind "JOY_STICK1_RIGHT"': '_moveRight',
            'bind "JOY_STICK2_UP"': '_lookUp',
            'bind "JOY_STICK2_DOWN"': '_lookDown',
            'bind "JOY_STICK2_LEFT"': '_left',
            'bind "JOY_STICK2_RIGHT"': '_right',
            'bind "JOY_TRIGGER2"': '_attack',
            'seta r_brightness': self.config.get_str('dhewm3_brightness', '1'),
            'seta sys_lang': self.config.get_str('dhewm3_language', 'english'),
        }

        self._update_config_file(config_base_file, options_to_set)
        self._update_config_file(config_file, options_to_set)

        command: list[str | Path] = ['/usr/bin/dhewm3', '+set', 'fs_basepath', self.roms_dir]

        if directory in _D3XP_MODS:
            command.extend(['+set', 'fs_game_base', 'd3xp'])

        if directory == 'd3le':
            command.extend(['+set', 'fs_game_base', 'd3xp', '+seta', 'com_allowconsole', '1'])

        if directory != 'base':
            command.extend(['+set', 'fs_game', directory])

        return Command(
            command,
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )

    @staticmethod
    def _update_config_file(file_path: Path, options_to_set: dict[str, str], /) -> None:
        if file_path.is_file():
            lines = file_path.read_text(encoding='utf-8').splitlines(keepends=True)

            for key, value in options_to_set.items():
                option_line = f'{key} "{value}"\n'
                if any(key in line for line in lines):
                    lines = [option_line if key in line else line for line in lines]
                else:
                    lines.append(option_line)

            file_path.write_text(''.join(lines), encoding='utf-8')
        else:
            file_path.write_text(
                ''.join(f'{key} "{value}"\n' for key, value in options_to_set.items()),
                encoding='utf-8',
            )
