from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final, TypedDict

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


class _PadConfig(TypedDict):
    Joystick: int
    Buttons: list[str]


_UNUSED_BUTTONS: Final = ['Not used'] * 14

_KEY_MAPPING: Final[list[_PadConfig]] = [
    {
        'Joystick': -1,
        'Buttons': [
            'UP',
            'DOWN',
            'LEFT',
            'RIGHT',
            'a',
            's',
            'd',
            'z',
            'x',
            'c',
            'RETURN',
            'f',
            'v',
            'q',
        ],
    },
    {
        'Joystick': -1,
        'Buttons': [
            'KP_8',
            'KP_5',
            'KP_4',
            'KP_6',
            'p',
            'LBRACKET',
            'RBRACKET',
            'SEMICOLON',
            'QUOTE',
            'BACKSLASH',
            'SLASH',
            'o',
            'l',
            'PERIOD',
        ],
    },
    {'Joystick': -1, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': -1, 'Buttons': list(_UNUSED_BUTTONS)},
]

_JOY_MAPPING: Final[list[_PadConfig]] = [
    {'Joystick': 0, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': 1, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': 2, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': 3, 'Buttons': list(_UNUSED_BUTTONS)},
]


@cached_dataclass
class Ikemen(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ikemen',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'menu': 'KEY_ESC'},
        }

    @property
    def execution_path(self) -> Path | None:
        return self.rom

    async def configure(self) -> Command:
        config_path = self.rom / 'save' / 'config.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            conf: dict[str, object] = json.loads(config_path.read_text())
        except OSError, json.JSONDecodeError:
            conf = {}

        # Joystick configuration seems completely broken in 0.98.2 Linux
        # so let's force keyboard and use a pad2key
        conf['KeyConfig'] = _KEY_MAPPING
        conf['JoystickConfig'] = _JOY_MAPPING
        conf['Fullscreen'] = True

        config_path.write_text(json.dumps(conf, indent=2))

        return Command(
            ['/usr/bin/ikemen'],
            env={'MESA_GL_VERSION_OVERRIDE': '2.1'},
        )
