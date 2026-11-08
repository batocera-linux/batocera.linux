# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CONFIGS
from batocera_common.vulkan import get_vulkan_info
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path
    from typing import Any

    from batocera_launch import Controller
    from batocera_launch.devices.gun import Gun

_logger: Final = logging.getLogger(__name__)

_STEER: Final = ['joystick1left']
_GAS: Final = ['r2', 'right_trigger']
_BRAKE: Final = ['l2', 'left_trigger']
_PADDLE_LEFT: Final = ['pageup', 'l1', 'left_shoulder']
_PADDLE_RIGHT: Final = ['pagedown', 'r1', 'right_shoulder']

# per wheel game: es's inputs, odin's own defaults kept in front of them, and whether the control is analog
_WHEEL_CONTROLS: Final = {
    'sgnascar': {
        'steering_wheel': (_STEER, 'pad:leftx', True),
        'gas_pedal': (_GAS, 'pad:righttrigger, joy:gas, key:Up', True),
        'brake_pedal': (_BRAKE, 'pad:lefttrigger, joy:brake, key:Down', True),
        'gear_up': (_PADDLE_RIGHT, 'key:C, pad:rightshoulder, joy:paddle_right', False),
        'gear_down': (_PADDLE_LEFT, 'key:X, pad:leftshoulder, joy:paddle_left', False),
        'start': (['start'], 'key:1, pad:start, joy:start', False),
    },
    'atvtrack': {
        'handlebar': (_STEER, 'pad:leftx', True),
        'throttle': (_GAS, 'pad:righttrigger, joy:gas, key:Up', True),
        'left_brake': (_PADDLE_LEFT, 'key:Z, pad:lefttrigger, joy:paddle_left', False),
        'right_brake': (_PADDLE_RIGHT, 'key:X, pad:rightshoulder, joy:paddle_right', False),
        'start': (['start'], 'key:1, pad:start, joy:start', False),
    },
    'smashdrv': {
        'wheel': (_STEER, 'pad:leftx', True),
        'gas_pedal': (_GAS, 'key:Up, pad:righttrigger, joy:gas', False),
        'brake_pedal': (_BRAKE, 'key:Down, pad:lefttrigger, joy:brake', False),
        'horn': (['start'], 'key:1, pad:start, joy:start', False),
    },
}
_COIN: Final = (['select'], 'key:5, pad:back, joy:select', False)

_CABINETS: Final = {
    'sgnascar': 'odin_nascar_cabinet',
    'swracer': 'odin_swracer_cabinet',
    'atvtrack': 'odin_atvtrack_cabinet',
    'smashdrv': 'odin_smashdrv_cabinet',
}

# keys only: hotkeygen turns the pad's hotkeys into these keys, and odin's own guide combos would act twice.
# Closing the game would leave odin in its library rather than back in es.
_HOTKEYS: Final = {
    'menu': 'Escape, F10',
    'pause': 'P',
    'save_state': 'F2',
    'load_state': 'F4',
    'reset': 'Ctrl+R',
    'fullscreen': 'F11, Alt+Return',
    'card': 'F6',
    'light_gun': 'F7',
    'close_game': 'none',
    'quit': 'Ctrl+Q',
}

# the versions of a game in odin's list, set as their parent
_PARENTS: Final = {
    'airtrixo': 'airtrix',
    'sgnascaro': 'sgnascar',
    'atvtracka': 'atvtrack',
    'smashdrvb': 'smashdrv',
    'smashdrvs': 'smashdrv',
}


def _set_ini(text: str, section: str, key: str, value: str, /) -> str:
    # odin.ini keeps each default as a "# key = value" comment, which configparser would drop
    lines = text.splitlines()
    setting = f'{key} = {value}'
    header = f'[{section}]'
    key_line = re.compile(rf'^#?\s*{re.escape(key)}\s*=')
    if header not in lines:
        return '\n'.join([*lines, header, setting]) + '\n'
    start = lines.index(header) + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith('[')), len(lines))
    for i in range(start, end):
        if key_line.match(lines[i]):
            lines[i] = setting
            break
    else:
        lines.insert(end, setting)
    return '\n'.join(lines) + '\n'


def _wheel_input(
    wheel: Controller, controls: Mapping[str, tuple[list[str], str, bool]], control: str, relaxed: Mapping[str, Any], /
) -> str | None:
    names, _, analog = controls[control]
    for name in names:
        if (input := wheel.inputs.get(name)) is None:
            continue
        if input.type == 'button':
            return f'joy:button{input.id}'
        if input.type != 'axis':
            continue
        if names is _STEER:
            return f'joy:axis{input.id}'
        # a pedal sharing its axis with another, or pressing a button, takes the half es saw pressed
        shared = any(
            (o := wheel.inputs.get(n)) is not None and o.type == 'axis' and o.id == input.id
            for other, (others, _, _) in controls.items()
            if other != control
            for n in others
        )
        if shared or not analog:
            return f'joy:{"-" if int(input.value) < 0 else "+"}axis{input.id}'
        reversed_ = (axis := relaxed.get(name)) is not None and axis['reversed']
        return f'joy:axis{input.id}{":invert" if reversed_ else ""}'
    return None


def _gun_identities(guns: Sequence[Gun], /) -> list[str]:
    # as odin names an evdev pointer: serial, else vid:pid, else port, else node
    import evdev

    identities: list[str] = []
    for gun in guns:
        try:
            device = evdev.InputDevice(gun.node)
        except OSError:
            identities.append(f'node:{gun.node}')
            continue
        uniq, phys, info = (device.uniq or '').strip(), (device.phys or '').strip(), device.info
        identity = (
            f'uniq:{uniq}'
            if len(uniq) >= 8
            else f'vidpid:{info.vendor:04x}:{info.product:04x}'
            if info.vendor and info.product
            else f'path:{phys}'
            if phys
            else f'node:{gun.node}'
        )
        # two of a kind take their port, then their node
        if identity in identities and phys:
            identity = f'path:{phys}'
        if identity in identities:
            identity = f'node:{gun.node}'
        identities.append(identity)
        device.close()
    return identities


@cached_dataclass
class Odin(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'odin',
            'keys': {
                'exit': ['KEY_LEFTCTRL', 'KEY_Q'],
                'menu': 'KEY_F10',
                'pause': 'KEY_P',
                'save_state': 'KEY_F2',
                'restore_state': 'KEY_F4',
                'reset': ['KEY_LEFTCTRL', 'KEY_R'],
                'coin': 'KEY_5',
            },
        }

    async def configure(self) -> Command:
        game = self.rom.stem
        parent = _PARENTS.get(game, game)
        players = f'players.{game}'
        config_path = self.config_dir / 'odin.ini'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        text = config_path.read_text() if config_path.exists() else ''

        api = self.config.get_str('odin_api', 'vulkan')
        vulkan_info = await get_vulkan_info() if api == 'vulkan' else None
        discrete_gpu = vulkan_info.active_discrete_gpu if vulkan_info else None
        display = {
            'api': api,
            # empty: the best card; odin falls back to opengl itself without vulkan
            'gpu': (discrete_gpu.name or '') if discrete_gpu else '',
            'fullscreen': 'on',
            'vsync': self.config.get_str('odin_vsync', 'off'),
            'upscale_mode': self.config.get_str('odin_upscale_mode', 'raw'),
            'bezel': 'off',  # batocera draws its own bezels
            'filter': self.config.get_str('odin_filter', 'none'),
            'show_speed': 'off',  # the title only; batocera's hud shows the fps
        }
        for key, value in display.items():
            text = _set_ini(text, 'display', key, value)
        for key, value in _HOTKEYS.items():
            text = _set_ini(text, 'hotkeys', key, value)
        # beside the saves, not in odin's folder under configs
        states_dir = self.saves_dir / 'states'
        states_dir.mkdir(parents=True, exist_ok=True)
        text = _set_ini(text, 'paths', 'states', str(states_dir))

        wheel = next(
            (pad for pad in self.controllers if self.config.use_wheels and pad.device_path in self.wheels), None
        )
        # odin otherwise takes the pads in the order they were plugged in, not es's
        pads = [pad for pad in self.controllers if pad.type == 'joystick' and pad is not wheel][:2]
        # the paths tell two pads of a make apart, as they share their guid
        for i in range(2):
            text = _set_ini(text, players, f'p{i + 1}', f'{pads[i].guid} {pads[i].real_name}' if i < len(pads) else '')
            text = _set_ini(text, players, f'p{i + 1}_path', pads[i].device_path if i < len(pads) else '')

        text = _set_ini(text, players, 'joy1', f'{wheel.guid} {wheel.real_name}' if wheel else '')
        text = _set_ini(text, players, 'joy1_path', wheel.device_path if wheel else '')
        if wheel or pads:
            text = _set_ini(text, players, 'device1', 'joystick' if wheel else 'pad')
        if wheel is not None and parent in _WHEEL_CONTROLS:
            relaxed = wheel.get_mapping_axis_relaxed_values()
            controls = {**_WHEEL_CONTROLS[parent], 'coin1': _COIN}
            for control, (_, defaults, _) in controls.items():
                if (joy := _wheel_input(wheel, controls, control, relaxed)) is not None:
                    text = _set_ini(text, f'controls.{game}', control, f'{defaults}, {joy}')
            # batocera has already narrowed the wheel to the rotation wanted
            rotation = '0' if 'wheel_rotation' in self.config else self.config.get_str('odin_wheel_rotation', '0')
            text = _set_ini(text, players, 'wheel_rotation', rotation)
            text = _set_ini(text, players, 'wheel_force', self.config.get_str('odin_wheel_force', '100'))

        if (cabinet := _CABINETS.get(parent)) is not None:
            text = _set_ini(text, players, 'cabinet', self.config.get_str(cabinet, 'standard'))

        if parent == 'pharrier':
            inverted = self.config.get_str('odin_pharrier_stick') == 'inverted'
            text = _set_ini(text, players, 'invert', 'stick_v' if inverted else '')

        if parent == 'braveff':
            guns: Sequence[Gun] = self.guns[:2] if self.config.use_guns else ()
            identities = _gun_identities(guns) if guns else []
            for i in range(2):
                text = _set_ini(
                    text, players, f'gun{i + 1}', f'{identities[i]} {guns[i].name}' if i < len(guns) else ''
                )
            text = _set_ini(text, players, 'hide_cursor', self.config.get_str('odin_light_gun_mode', 'on'))
            text = _set_ini(text, players, 'sinden_border', 'off')  # batocera draws the borders of the guns

        if parent in ('braveff', 'swracer', 'sgnascar', 'atvtrack', 'smashdrv'):
            text = _set_ini(text, players, 'vibration', self.config.get_str('odin_vibration', 'on'))
            text = _set_ini(text, players, 'vibration_force', self.config.get_str('odin_vibration_force', '100'))

        config_path.write_text(text)

        args: list[str | Path] = [
            '/usr/bin/odin',
            '-R',
            self.rom.parent,
            '-B',
            BIOS,
            '-r',
            self.rom.stem,
            '-f',
            '-x',
            self.config.get_str('odin_scale', '1'),
        ]
        if (anisotropy := self.config.get_str('odin_anisotropy', '1')) != '1':
            args.extend(['-a', anisotropy])

        return Command(
            args,
            env={
                'XDG_DATA_HOME': CONFIGS,
                'ODIN_SAVES': self.saves_dir,
            },
        )
