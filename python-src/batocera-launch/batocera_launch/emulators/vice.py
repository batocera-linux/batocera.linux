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

from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from io import TextIOWrapper
    from pathlib import Path

    from batocera_launch import Input

# Map each core binary to the vicerc section name it uses for its settings
_SYSTEM_CORE_MAP: Final = {
    'x64': 'C64',
    'x64dtv': 'C64DTV',
    'xplus4': 'PLUS4',
    'xscpu64': 'SCPU64',
    'xvic': 'VIC20',
    'xpet': 'PET',
}

# Map each core to its emulated video chip(s) as documented in the manual
_CORE_CHIP_MAP: Final = {
    'C64': ['VICII'],
    'C64DTV': ['VICII'],
    'PLUS4': ['TED'],
    'SCPU64': ['VICII'],
    'VIC20': ['VIC'],
    'PET': ['Crtc'],
    'C128': ['VICII', 'VDC'],
}

# VICE joymap lines are 'joynum inputtype inputindex action [args]', the port comes from JoyDevice1/2
# inputtype: 0 axis (index axis*2, +1 for negative), 1 button, 2 hat (index hat*4 + up/down/left/right)
# action: 1 pin = joystick (1/2/4/8/16/32/64 = u/d/l/r/fire/fire2/fire3), 4 = UI activate
_VICE_PINS: Final = {
    'up': 1,
    'down': 2,
    'left': 4,
    'right': 8,
    'b': 16,  # Fire button
    'a': 32,  # Space
    'y': 64,
}

# JoyDevice values: 0 none, 4 onwards the host joysticks
_JOYDEV_NONE: Final = 0
_JOYDEV_REALJOYSTICK_MIN: Final = 4

# SDL hat value -> VICE hat direction offset
_HAT_DIRECTION: Final = {'1': 0, '4': 1, '8': 2, '2': 3}


def _joymap_input(input: Input, /) -> str | None:
    if input.type == 'button':
        return f'1 {input.id}'
    if input.type == 'hat' and input.value in _HAT_DIRECTION:
        return f'2 {int(input.id) * 4 + _HAT_DIRECTION[input.value]}'
    if input.type == 'axis':
        return f'0 {int(input.id) * 2 + (int(input.value) < 0)}'
    return None


class _EqualsSpaceRemover:
    def __init__(self, new_output_file: TextIOWrapper) -> None:
        self.output_file = new_output_file

    def write(self, what: str) -> None:
        self.output_file.write(what.replace(' = ', '=', 1))


@cached_dataclass
class Vice(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {'name': 'vice', 'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']}}

    def _write_vicerc(self) -> Path:
        vicerc = self.config_dir / 'sdl-vicerc'
        joymap = self.config_dir / 'sdl-joymap.vjm'

        config = CaseSensitiveRawConfigParser(interpolation=None)
        if vicerc.exists():
            config.read(vicerc)

        system_core = _SYSTEM_CORE_MAP.get(self.core, 'C128')

        if not config.has_section(system_core):
            config.add_section(system_core)

        config.set(system_core, 'SaveResourcesOnExit', '0')
        config.set(system_core, 'SoundDeviceName', 'alsa')

        # Determine border and aspect values
        if self.config.get_bool('noborder'):
            aspect_mode = '0'
            border_mode = '3'
        else:
            aspect_mode = '2'
            border_mode = '0'

        # Dynamically apply settings to the correct video chip(s)
        chips = _CORE_CHIP_MAP.get(system_core, ['VICII'])
        for chip in chips:
            # Fullscreen configurations
            config.set(system_core, f'{chip}Fullscreen', '1')
            config.set(system_core, f'{chip}FullscreenMode', '0')  # 0 = Use desktop resolution

            # Aspect Ratio Mode
            config.set(system_core, f'{chip}AspectMode', aspect_mode)

            # Border display mode (Only VIC-II, VIC-I, and TED chips support borders)
            if chip in ('VICII', 'VIC', 'TED'):
                config.set(system_core, f'{chip}BorderMode', border_mode)

        if self.config.use_guns and self.guns:
            if self.metadata.get('gun_type') == 'stack_light_rifle':
                joyport1 = '15'
            else:
                joyport1 = '14'
        else:
            joyport1 = '1'
        config.set(system_core, 'JoyPort1Device', joyport1)

        # VICE gives a pad to one port only, so P1 takes port 2 that most games read (the VIC-20 has just port 1)
        devices = [_JOYDEV_REALJOYSTICK_MIN + pad.index for pad in self.controllers[:2]]
        player_ports = (1,) if system_core == 'VIC20' else (2, 1)
        port_devices = dict(zip(player_ports, devices, strict=False))
        for port in sorted(player_ports):
            config.set(system_core, f'JoyDevice{port}', str(port_devices.get(port, _JOYDEV_NONE)))
        config.set(system_core, 'JoyMapFile', str(joymap))

        # custom : allow the user to configure directly sdl-vicerc via batocera.conf via lines like : vice.section.option=value
        for section_option, user_config_value in self.config.items(starts_with='vice.'):
            custom_section, _, custom_option = section_option.partition('.')
            if not config.has_section(custom_section):
                config.add_section(custom_section)
            config.set(custom_section, custom_option, user_config_value)

        with vicerc.open('w') as configfile:
            config.write(_EqualsSpaceRemover(configfile))

        return joymap

    def _write_joymap(self, joymap: Path) -> None:
        lines = ['# Batocera configured controllers', '', '!CLEAR']
        for pad in self.controllers:
            lines.append('')
            lines.append(f'# {pad.real_name}')
            for input_name, input_value in pad.inputs.items():
                if (source := _joymap_input(input_value)) is None:
                    continue
                if input_name in _VICE_PINS:
                    lines.append(f'{pad.index} {source} 1 {_VICE_PINS[input_name]}')
                elif input_name == 'select':
                    lines.append(f'{pad.index} {source} 4')
            lines.append('')

        joymap.write_text('\n'.join(lines) + '\n')

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        joymap = self._write_vicerc()
        self._write_joymap(joymap)

        return Command(
            [self.core, self.rom],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
