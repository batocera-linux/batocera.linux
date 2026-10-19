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
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Final, cast

if TYPE_CHECKING:
    from pathlib import Path

    from ..rom import Rom

_logger = logging.getLogger(__name__)
_input_re: Final = re.compile(r'^/dev/input/event([0-9]*)$')


@dataclass(slots=True, kw_only=True)
class Gun:
    mouse_buttons_to_code: ClassVar[Mapping[str, int]]

    node: str
    mouse_index: int
    needs_cross: bool
    needs_borders: bool
    name: str
    buttons: list[str]
    button_map: Mapping[str, int] = field(init=False)

    def __post_init__(self) -> None:
        if not hasattr(Gun, '_mouse_buttons_to_code'):
            # delay initialization of the map so we don't have
            # to import evdev until we need it
            import evdev

            Gun.mouse_buttons_to_code = {
                'left': evdev.ecodes.BTN_LEFT,
                'right': evdev.ecodes.BTN_RIGHT,
                'middle': evdev.ecodes.BTN_MIDDLE,
                '1': evdev.ecodes.BTN_1,
                '2': evdev.ecodes.BTN_2,
                '3': evdev.ecodes.BTN_3,
                '4': evdev.ecodes.BTN_4,
                '5': evdev.ecodes.BTN_5,
                '6': evdev.ecodes.BTN_6,
                '7': evdev.ecodes.BTN_7,
                '8': evdev.ecodes.BTN_8,
            }

        self.button_map = {
            button: self.mouse_buttons_to_code[button]
            for button in self.buttons
            if button in self.mouse_buttons_to_code
        }

    @staticmethod
    def get_all() -> GunList:
        import evdev
        import pyudev

        guns: GunList = []
        context = pyudev.Context()

        # guns are mouses, just filter on them
        mouses = {
            int(match.group(1)): mouse
            for mouse in context.list_devices(subsystem='input')
            if mouse.device_node is not None
            and (match := _input_re.match(mouse.device_node)) is not None
            and mouse.properties.get('ID_INPUT_MOUSE') == '1'
        }

        mouse_code_to_button = {
            evdev.ecodes.BTN_LEFT: 'left',
            evdev.ecodes.BTN_RIGHT: 'right',
            evdev.ecodes.BTN_MIDDLE: 'middle',
            evdev.ecodes.BTN_1: '1',
            evdev.ecodes.BTN_2: '2',
            evdev.ecodes.BTN_3: '3',
            evdev.ecodes.BTN_4: '4',
            evdev.ecodes.BTN_5: '5',
            evdev.ecodes.BTN_6: '6',
            evdev.ecodes.BTN_7: '7',
            evdev.ecodes.BTN_8: '8',
        }
        mouse_button_codes = set(mouse_code_to_button.keys())

        for mouse_index, (_, mouse) in enumerate(sorted(mouses.items(), key=lambda item: item[0])):
            _logger.info('found mouse %s at %s with id_mouse=%s', mouse_index, mouse.device_node, mouse_index)
            if mouse.properties.get('ID_INPUT_GUN') != '1':
                continue

            device = evdev.InputDevice(cast('str', mouse.device_node))
            device_codes = set(device.capabilities()[evdev.ecodes.EV_KEY]) & mouse_button_codes

            gun = Gun(
                node=cast('str', mouse.device_node),
                # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE
                # (TOUCHPAD are listed after mouses)
                mouse_index=mouse_index,
                needs_cross=mouse.properties.get('ID_INPUT_GUN_NEED_CROSS') == '1',
                needs_borders=mouse.properties.get('ID_INPUT_GUN_NEED_BORDERS') == '1',
                name=device.name,
                buttons=[button for code, button in mouse_code_to_button.items() if code in device_codes],
            )
            guns.append(gun)
            _logger.info(
                'found gun %s at %s with id_mouse=%s (%s)', len(guns) - 1, mouse.device_node, mouse_index, gun.name
            )

        if not guns:
            _logger.info('no gun found')

        return guns


def guns_need_crosses(guns: Guns, /) -> bool:
    # no gun, enable the cross for joysticks, mouses...
    if not guns:
        return True

    return any(gun.needs_cross for gun in guns)


def precalibrate_reicast_guns(system: str, rom: Rom, precalibration_dir: Path, saves_dir: Path, /) -> None:
    if system not in {'atomiswave', 'naomi'}:
        return

    suffixes = {'nvmem', 'nvmem2'} if system == 'atomiswave' else {'nvmem', 'eeprom'}

    for suffix in suffixes:
        filename = f'{rom.name}.{suffix}'
        src = precalibration_dir / 'reicast' / filename
        dest = saves_dir / filename

        if src.exists() and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.copy(dest)


type Guns = Sequence[Gun]
type GunList = list[Gun]
