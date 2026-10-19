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

from typing import TYPE_CHECKING, ClassVar, Final

from ..core import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig

_VALID_MEGADRIVE_CONTROLLER_GUIDS: Final = {
    # 8bitdo m30
    '05000000c82d00005106000000010000',
    '03000000c82d00000650000011010000',
    '050000005e0400008e02000030110000',
    # 8bitdo m30 modkit
    '03000000c82d00000150000011010000',
    '05000000c82d00000151000000010000',
    # Retrobit bt saturn
    '0500000049190000020400001b010000',
}

_VALID_MEGADRIVE_CONTROLLER_NAMES: Final = {
    '8BitDo M30 gamepad',
    '8Bitdo  8BitDo M30 gamepad',
    '8BitDo M30 Modkit',
    '8Bitdo  8BitDo M30 Modkit',
    'Retro Bit Bluetooth Controller',
}

# Remaps for Megadrive style controllers
_MEGADRIVE_REMAP_VALUES: Final = {
    'btn_a': '0',
    'btn_b': '1',
    'btn_x': '9',
    'btn_y': '10',
    'btn_l': '11',
    'btn_r': '8',
}


class MegadriveControllerRemapMixin(Core):
    megadrive_controller_option: ClassVar[str]

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        option = self.megadrive_controller_option
        for pad in self.controllers[:4]:
            if (
                pad.guid in _VALID_MEGADRIVE_CONTROLLER_GUIDS and pad.name in _VALID_MEGADRIVE_CONTROLLER_NAMES
            ) or self.config.get(f'{option}_controller{pad.player_number}_mapping', 'retropad') != 'retropad':
                for btn, value in _MEGADRIVE_REMAP_VALUES.items():
                    custom_config.set(f'input_player{pad.player_number}_{btn}', value)
