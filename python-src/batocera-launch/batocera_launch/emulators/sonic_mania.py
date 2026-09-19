from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import ROMS
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

_BINARY_SRC: Final = Path('/usr/bin/sonic-mania')
_MODS_SRC: Final = Path('/usr/share/sonic-mania/mods')


def _set_ini_values(path: Path, values: Mapping[str, Mapping[str, str]], /) -> None:
    # Edit lines in place: RSDK can write duplicate [Keyboard Map N] sections, which configparser can't round-trip.
    # Its iniparser keeps the last duplicate key or section, so every occurrence is set.
    lines = path.read_text(errors='surrogateescape').splitlines()
    missing = {section: dict(keys) for section, keys in values.items() if keys}
    first_end: dict[str, int] = {}

    section: str | None = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('['):
            if section is not None and section in missing and section not in first_end:
                first_end[section] = i
            section = stripped[1:-1] if stripped.endswith(']') else None
            continue
        key, sep, _ = line.partition('=')
        key = key.strip()
        if sep and section is not None and key in values.get(section, {}) and not key.startswith(';'):
            lines[i] = f'{key}={values[section][key]}'
            if section in missing:
                missing[section].pop(key, None)
    if section is not None and section in missing and section not in first_end:
        first_end[section] = len(lines)

    # Insert from the bottom up so earlier positions stay valid
    for section, end in sorted(first_end.items(), key=lambda item: item[1], reverse=True):
        start = end
        while start > 0 and not lines[start - 1].strip():
            start -= 1
        lines[start:start] = [f'{key}={value}' for key, value in missing.pop(section).items()]
    for section, keys in missing.items():
        if keys:
            lines += ['', f'[{section}]', *(f'{key}={value}' for key, value in keys.items())]

    path.write_text('\n'.join(lines) + '\n', errors='surrogateescape')


@cached_dataclass
class SonicMania(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.roms_dir / 'gamecontrollerdb.txt'

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sonic_mania',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ENTER',
                'pause': 'KEY_ENTER',
            },
        }

    @cached_property
    def roms_dir(self) -> Path:
        return ROMS / 'sonic-mania'

    @property
    def execution_path(self) -> Path | None:
        return self.roms_dir

    @cached_property
    def is_4_3(self) -> bool:
        return self.config.get_str('smania_ratio') == '4:3'

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3 if self.is_4_3 else 16 / 9

    async def configure(self) -> Command:
        destination_file = self.roms_dir / 'sonic-mania'
        if not destination_file.exists():
            shutil.copy(_BINARY_SRC, destination_file)

        # The screen shaders only work through the GLShaders mod
        if (_MODS_SRC / 'GLShaders').is_dir():
            mods_dir = self.roms_dir / 'mods'
            shutil.copytree(_MODS_SRC / 'GLShaders', mods_dir / 'GLShaders', dirs_exist_ok=True)
            mod_config = mods_dir / 'modconfig.ini'
            if mod_config.is_file() and mod_config.stat().st_size:
                _set_ini_values(mod_config, {'Mods': {'GLShaders': 'y'}})
            else:
                mod_config.write_text('[Mods]\nGLShaders=y\n')

        # Only fullscreen and the ES options are enforced, so other in-game changes persist
        forced = {
            'Game': {
                'devMenu': self.config.get_str('smania_devmenu', 'y'),
                'language': self.config.get_str('smania_language', '0'),
            },
            'Video': {
                'windowed': 'n',
                'border': 'n',
                'exclusiveFS': 'y',
                'vsync': self.config.get_str('smania_vsync', 'y'),
                'tripleBuffering': self.config.get_str('smania_buffering', 'n'),
                'shaderSupport': 'y',
                'screenShader': self.config.get_str('smania_shader', '0'),
                # The width follows the display between pixWidth and maxPixWidth (0 = no limit)
                'pixWidth': '320' if self.is_4_3 else '424',
                'maxPixWidth': '320' if self.is_4_3 else '0',
            },
        }

        settings_file = self.roms_dir / 'Settings.ini'
        if settings_file.is_file() and settings_file.stat().st_size:
            _set_ini_values(settings_file, forced)
        else:
            # Without a Settings.ini the game creates its own, which starts windowed.
            # Older builds also left it empty on exit.
            config = CaseSensitiveConfigParser(interpolation=None)
            config['Game'] = {
                'faceButtonFlip': 'n',
                'enableControllerDebugging': 'n',
                'disableFocusPause': 'n',
                'region': '-1',
            }
            config['Video'] = {
                'winWidth': '848',
                'winHeight': '480',
                'refreshRate': '60',
            }
            config['Audio'] = {
                'streamsEnabled': 'y',
                'streamVolume': '1.000000',
                'sfxVolume': '1.000000',
            }
            for section, keys in forced.items():
                config[section].update(keys)

            with settings_file.open('w') as configfile:
                config.write(configfile)

        return Command(
            [destination_file],
            env={'SDL_JOYSTICK_HIDAPI': '0'},
        )
