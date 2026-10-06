from __future__ import annotations

import logging
import platform
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
    parse_build_engine_args,
)

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_GAME_NAMES: Final = (
    'Blood',
    'Duke',
    'Exhumed',
    'Nam',
    'Redneck',
    'ShadowWarrior',
    'WW2GI',
)

_CONSOLE_DEFAULTS: Final = {
    'hud_size': 8,
    'm_sensitivity_x': 6.0,
    'm_sensitivity_y': 5.5,
}

_BINDING_DEFAULTS: Final = {
    'F6': 'quicksave',
    'F9': 'quickload',
    'F12': 'screenshot',
    'C': 'toggleconsole',
    'Tab': 'togglemap',
    'E': '+Move_Forward',
    'D': '+Move_Backward',
    'S': '+Strafe_Left',
    'F': '+Strafe_Right',
    'PgUp': '+Quick_Kick',
    'PgDn': '+Alt_Fire',
    'Del': 'toggle cl_autorun',
    'Ins': '+toggle_crouch',
    'UpArrow': 'weapprev',
    'DownArrow': 'weapnext',
    'LeftArrow': 'invprev',
    'RightArrow': 'invnext',
    'X': 'invuse',
    'B': '+jump',
    'Y': '+open',
    'A': '+open',
    'Pad_Start': 'menu_endgame',
    'Pad_Back': 'togglemap',
    'Pad_A': '+open',
    'Pad_Y': '+jump',
    'Pad_B': '+Quick_Kick',
    'Pad_X': '+crouch',
    'LThumb': '+Run',
    'RThumb': '+toggle_crouch',
    'LShoulder': 'weapprev',
    'RShoulder': 'weapnext',
    'LTrigger': '+altattack',
    'RTrigger': '+fire',
    'DPadDown': 'invuse',
    'DPadLeft': 'invprev',
    'DPadRight': 'invnext',
}

_AUTOMAP_BINDING_DEFAULTS: Final = {
    'PgUp': '+Shrink_Screen',
    'PgDn': '+Enlarge_Screen',
    'UpArrow': '+am_panup',
    'DownArrow': '+am_pandown',
    'LeftArrow': '+am_panleft',
    'RightArrow': '+am_panright',
    'Del': 'togglefollow',
    'Ins': 'togglerotate',
    'LThumb': '+enlarge_Screen',
    'RThumb': '+shrink_screen',
}

_INTEL_ARCHES: Final = frozenset({'x86_64', 'amd64', 'i686', 'i386'})


def _build_config_defaults() -> dict[str, dict[str, object]]:
    # Raze does not support global bindings; set defaults per game series (first boot only).
    defaults: dict[str, dict[str, object]] = {}
    for name in _GAME_NAMES:
        defaults[f'{name}.ConsoleVariables'] = dict(_CONSOLE_DEFAULTS)
        defaults[f'{name}.Bindings'] = dict(_BINDING_DEFAULTS)
        defaults[f'{name}.AutomapBindings'] = dict(_AUTOMAP_BINDING_DEFAULTS)
    return defaults


_CONFIG_DEFAULTS: Final = _build_config_defaults()


def _gl_es_line(raze_api: str | None, architecture: str, current: str, /) -> str:
    if raze_api and raze_api != '2':
        if raze_api == '0':
            value = 'false' if architecture in _INTEL_ARCHES else 'true'
            return f'gl_es={value}\n'
        return current
    return 'gl_es=true\n'


@cached_dataclass
class Raze(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'raze',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F9',
                'screenshot': 'KEY_F12',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        architecture = platform.uname().machine
        _logger.debug('*** Detected architecture is: %s ***', architecture)

        self.config_dir.mkdir(parents=True, exist_ok=True)

        config_file = self.config_dir / 'raze.ini'
        script_file = self.config_dir / 'raze.cfg'

        if not config_file.exists():
            sections: list[str] = []
            for section, values in _CONFIG_DEFAULTS.items():
                sections.append(f'[{section}]')
                sections.extend(f'{key}={value}' for key, value in values.items())
                sections.append('')
            config_file.write_text('\n'.join(sections))

        config_backup = config_file.read_text().splitlines(keepends=True)
        raze_api = self.config.get_str('raze_api')

        with config_file.open('w') as out:
            global_settings_found = False
            for line in config_backup:
                if line.strip() == '[GlobalSettings]':
                    global_settings_found = True

                if global_settings_found:
                    stripped = line.strip()
                    if stripped.startswith('gl_es='):
                        line = _gl_es_line(raze_api, architecture, line)
                    elif stripped.startswith('vid_preferbackend='):
                        line = f'vid_preferbackend={raze_api or "2"}\n'
                    elif stripped.startswith('use_joystick='):
                        line = 'use_joystick=true\n'

                out.write(line)

            if not global_settings_found:
                _logger.debug('Global Settings NOT found')
                out.write('[GlobalSettings]\n')
                # Preserve original first-boot quirk: gl_es is only derived when api is OpenGL.
                if raze_api == '0':
                    if architecture in _INTEL_ARCHES:
                        _logger.debug('*** Architecture is intel; gl_es=false ***')
                    else:
                        _logger.debug(
                            '*** Architecture is not intel (%s); gl_es=true ***',
                            architecture,
                        )
                out.write(f'vid_preferbackend={raze_api or "2"}\n')
                out.write('use_joystick=true\n')

        script_file.write_text(
            '\n'.join(
                [
                    '# This file is automatically generated by batocera-launch',
                    f'vid_fps {"true" if self.config.show_fps else "false"}',
                    'echo BATOCERA',
                    '',
                ]
            )
        )

        args: list[str | Path] = ['raze', *parse_build_engine_args(self.rom)]
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

        return Command(args)
