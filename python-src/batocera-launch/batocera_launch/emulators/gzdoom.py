from __future__ import annotations

import collections
import re
import shlex
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BATOCERA_SHARE_DIR, LOGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

# Default keyboard bindings, applied only on first start (missing keys only).
_DEFAULT_BINDINGS: Final = {
    '1': 'slot 1',
    '2': 'slot 2',
    '3': 'slot 3',
    '4': 'slot 4',
    '5': 'slot 5',
    '6': 'slot 6',
    '7': 'slot 7',
    '8': 'slot 8',
    '9': 'slot 9',
    '0': 'slot 0',
    'W': '+forward',
    'S': '+back',
    'A': '+moveleft',
    'D': '+moveright',
    'E': '+use',
    'T': 'messagemode',
    'LeftBracket': 'invprev',
    'RightBracket': 'invnext',
    'Enter': 'invuse',
    'Shift': '+speed',
    'X': 'crouch',
    'Space': '+jump',
    'Tab': 'togglemap',
    '`': 'toggleconsole',
    '\\': '+showscores',
    'CapsLock': 'toggle cl_run',
    'F1': 'menu_help',
    'F2': 'menu_save',
    'F3': 'menu_load',
    'F4': 'menu_options',
    'F5': 'menu_display',
    'F6': 'quicksave',
    'F7': 'menu_endgame',
    'F8': 'togglemessages',
    'F9': 'quickload',
    'F10': 'menu_quit',
    'F11': 'bumpgamma',
    'F12': 'spynext',
    'SysRq': 'screenshot',
    'Pause': 'pause',
    'Home': 'land',
    'PgUp': '+moveup',
    'End': 'centerview',
    'PgDn': '+lookup',
    'Ins': '+movedown',
    'Del': '+lookdown',
    'Mouse1': '+attack',
    'Mouse2': '+altattack',
    'MWheelUp': 'weapprev',
    'MWheelDown': 'weapnext',
    'MWheelRight': 'invnext',
    'MWheelLeft': 'invprev',
    'Axis3Plus': '+altattack',
    'Axis6Plus': '+attack',
    'DPadUp': 'togglemap',
    'DPadDown': 'invuse',
    'DPadLeft': 'invprev',
    'DPadRight': 'invnext',
    'Pad_Start': 'menu_main',
    'Pad_Back': 'pause',
    'LThumb': 'crouch',
    'LShoulder': 'weapprev',
    'RShoulder': 'weapnext',
    'LTrigger': '+altattack',
    'RTrigger': '+attack',
    'Pad_A': '+use',
    'Pad_Y': '+jump',
}

_DEFAULT_AUTOMAP_BINDINGS: Final = {
    '0': 'am_gobig',
    '=': '+am_zoomin',
    '-': '+am_zoomout',
    'P': 'am_toggletexture',
    'F': 'am_togglefollow',
    'G': 'am_togglegrid',
    'C': 'am_clearmarks',
    'M': 'am_setmark',
    'KP-': '+am_zoomout',
    'KP+': '+am_zoomin',
    'UpArrow': '+am_panup',
    'LeftArrow': '+am_panleft',
    'RightArrow': '+am_panright',
    'DownArrow': '+am_pandown',
    'POV1Up': '+am_panup',
    'POV1Right': '+am_panright',
    'POV1Down': '+am_pandown',
    'POV1Left': '+am_panleft',
    'MWheelUp': 'am_zoom 1.2',
    'MWheelDown': 'am_zoom -1.2',
    'DPadUp': '+am_panup',
    'DPadDown': '+am_pandown',
    'DPadLeft': '+am_panleft',
    'DPadRight': '+am_panright',
    'LShoulder': '+am_zoomout',
    'RShoulder': '+am_zoomin',
    'Pad_A': 'am_setmark',
    'Pad_B': 'am_clearmarks',
    'Pad_X': 'am_togglefollow',
}

# Dynamic controller bindings (override the Joy<n> defaults above every launch).
_JOY_BINDINGS: Final = {
    'b': '+use',
    'x': '+jump',
    'pageup': 'weapnext',
    'pagedown': 'weapprev',
    'l3': 'crouch',
    'start': 'menu_main',
    'select': 'pause',
}

_JOY_AUTOMAP_BINDINGS: Final = {
    'a': 'am_clearmarks',
    'b': 'am_setmark',
    'y': 'am_togglefollow',
    'pageup': 'am_zoomin',
    'pagedown': 'am_zoomout',
}

_JOY_BINDING_RE: Final = re.compile(r'Joy\d+\s*=')


class IniFileEditor:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.sections: dict[str, list[str]] = collections.defaultdict(list)
        if self.path.exists():
            self._parse()

    def _parse(self) -> None:
        current_section = ''
        with self.path.open('r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line.startswith('[') and stripped_line.endswith(']'):
                    current_section = stripped_line
                    # Ensure the section key exists even if it's empty
                    if current_section not in self.sections:
                        self.sections[current_section] = []
                elif current_section and stripped_line:
                    self.sections[current_section].append(line)

    def ensure_section_exists(self, section_name: str) -> None:
        if section_name not in self.sections:
            self.sections[section_name] = []

    def set_value(self, section: str, key: str, value: str) -> None:
        self.ensure_section_exists(section)
        full_line = f'{key}={value}\n'
        # Find and replace existing key
        for i, line in enumerate(self.sections[section]):
            if line.strip().startswith(f'{key}='):
                self.sections[section][i] = full_line
                return
        # Or add if it doesn't exist
        self.sections[section].append(full_line)

    def set_value_if_missing(self, section: str, key: str, value: str) -> None:
        self.ensure_section_exists(section)
        # Check if the key already exists
        for line in self.sections[section]:
            if line.strip().startswith(f'{key}='):
                return  # Key found, so we do nothing
        # Key was not found, add it
        self.sections[section].append(f'{key}={value}\n')

    def add_line_if_missing(self, section: str, line_to_add: str) -> None:
        self.ensure_section_exists(section)
        # Ensure the line ends with a newline
        line_with_newline = line_to_add.strip() + '\n'
        if line_with_newline not in self.sections[section]:
            self.sections[section].append(line_with_newline)

    def write(self) -> None:
        with self.path.open('w', encoding='utf-8') as f:
            for section_name, lines in self.sections.items():
                f.write(f'{section_name}\n')
                for line in lines:
                    f.write(line)
                f.write('\n')


@cached_dataclass
class GZDoom(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'gzdoom',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'save_store': 'KEY_F6', 'restore_store': 'KEY_F9'},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    def _determine_api_config(self) -> str:
        gzdoom_api = self.config.get_str('gz_api', '0')
        arch_path = BATOCERA_SHARE_DIR / 'batocera.arch'

        # Default to GLES on non-x86_64 architectures if API is auto ("0")
        if gzdoom_api == '0' and arch_path.exists():
            arch = arch_path.read_text().strip()
            if arch != 'x86_64':
                gzdoom_api = '3'

        if gzdoom_api == '3':
            # OpenGL ES settings for performance
            return 'gl_es 1\nvid_preferbackend 3\ngles_use_mapped_buffer true\n'
        return f'vid_preferbackend {gzdoom_api}\n'

    def _create_script_file(self, script_file: Path, api_config: str) -> None:
        content = (
            '# This file is automatically generated by batocera-launch\n'
            f'logfile "{LOGS / "gzdoom.log"}"\n'
            f'vid_fps {"true" if self.config.show_fps else "false"}\n'
            f'{api_config}'
            'echo BATOCERA\n'
        )
        script_file.write_text(content, encoding='utf-8')

    def _update_ini_file(self, ini_file: Path, sound_fonts_dir: Path, fm_banks_dir: Path) -> None:
        ini = IniFileEditor(ini_file)

        # Add ROM path to search directories
        rom_path_line = f'Path={self.rom.parent}'
        ini.add_line_if_missing('[IWADSearch.Directories]', rom_path_line)
        ini.add_line_if_missing('[FileSearch.Directories]', rom_path_line)

        # Add sound and music paths (system paths first, for precedence)
        sound_paths = [
            'Path=/usr/share/gzdoom/soundfonts',
            'Path=/usr/share/gzdoom/fm_banks',
            f'Path={sound_fonts_dir}',
            f'Path={fm_banks_dir}',
        ]
        for path_line in sound_paths:
            ini.add_line_if_missing('[SoundfontSearch.Directories]', path_line)

        # Vsync
        set_gz_vsync = self.config.get_bool('gz_vsync', return_values=('true', 'false'))
        ini.set_value('[GlobalSettings]', 'vid_vsync', set_gz_vsync)
        # Set joystick option
        ini.set_value('[GlobalSettings]', 'use_joystick', 'true')

        # 1. Apply default bindings if they are missing (first start)
        for key, value in _DEFAULT_BINDINGS.items():
            ini.set_value_if_missing('[Doom.Bindings]', key, value)
        for key, value in _DEFAULT_AUTOMAP_BINDINGS.items():
            ini.set_value_if_missing('[Doom.AutomapBindings]', key, value)

        # 2. Set/Overwrite dynamic controller bindings
        # First, clear any existing Joy<number> bindings to prevent conflicts from previous runs.
        ini.sections['[Doom.Bindings]'] = [
            line for line in ini.sections['[Doom.Bindings]'] if not _JOY_BINDING_RE.match(line.strip())
        ]
        ini.sections['[Doom.AutomapBindings]'] = [
            line for line in ini.sections['[Doom.AutomapBindings]'] if not _JOY_BINDING_RE.match(line.strip())
        ]

        # GZDoom's internal joystick handler for controllers is not dynamic.
        # We need to set the Joy values for controllers i.e. Joy1=+use Joy4=+jump etc
        for n, pad in enumerate(self.controllers):
            # Only enable the first pad
            if n == 0:
                ini.set_value(f'[Joy:JS:{n}]', 'Enabled', '1')
                for name, input_ in pad.inputs.items():
                    # Set the Joy values +1 from the input id values
                    joynum = int(input_.id) + 1
                    if name in _JOY_BINDINGS and input_.type == 'button':
                        ini.set_value('[Doom.Bindings]', f'Joy{joynum}', _JOY_BINDINGS[name])
                    if name in _JOY_AUTOMAP_BINDINGS and input_.type == 'button':
                        ini.set_value('[Doom.AutomapBindings]', f'Joy{joynum}', _JOY_AUTOMAP_BINDINGS[name])
            else:
                ini.set_value(f'[Joy:JS:{n}]', 'Enabled', '0')

        ini.write()

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        sound_fonts_dir = self.config_dir / 'soundfonts'
        fm_banks_dir = self.config_dir / 'fm_banks'
        sound_fonts_dir.mkdir(parents=True, exist_ok=True)
        fm_banks_dir.mkdir(parents=True, exist_ok=True)

        script_file = self.config_dir / 'gzdoom.cfg'
        ini_file = self.config_dir / 'gzdoom.ini'

        api_config = self._determine_api_config()
        self._create_script_file(script_file, api_config)
        self._update_ini_file(ini_file, sound_fonts_dir, fm_banks_dir)

        args: list[str | Path] = ['gzdoom']

        if self.rom.suffix == '.gzdoom':
            args.extend(shlex.split(self.rom.read_text()))
        else:
            args.extend(['-iwad', self.rom.name])

        args.extend(
            [
                '-exec',
                script_file,
                '-width',
                str(self.resolution.width),
                '-height',
                str(self.resolution.height),
            ]
        )

        if self.config.get_bool('nologo'):
            args.append('-nologo')

        return Command(args, env={'SDL_JOYSTICK_HIDAPI': '0'})
