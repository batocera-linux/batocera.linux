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

from batocera_launch_libretro import Core, DisableAnalogModeMixin

if TYPE_CHECKING:
    from batocera_launch import Controller, LibretroConfig


_VALID_N64_CONTROLLER_GUIDS: Final = {
    '050000007e0500001920000001800000',  # official nintendo switch n64 controller
    '05000000c82d00006928000000010000',  # 8bitdo n64 modkit
    '030000007e0500001920000011810000',
    '05000000c82d00001930000001000000',  # 8bitdo n64 bt
    '03000000c82d00001930000011010000',  # 8bitdo n64 wired
}

_VALID_N64_CONTROLLER_NAMES: Final = {
    'N64 Controller',
    'Nintendo Co., Ltd. N64 Controller',
    '8BitDo N64 Modkit',
    '8BitDo 64 BT',
    '8BitDo 8BitDo 64 Bluetooth Controller',
}

_N64_REMAP_VALUES: Final = {
    'btn_a': '1',
    'btn_b': '0',
    'btn_x': '23',
    'btn_y': '21',
    'btn_l2': '22',
    'btn_r2': '20',
    'btn_select': '12',
}


class N64ControllerRemapMixin(DisableAnalogModeMixin, Core):
    n64_controller_option: ClassVar[str]

    def set_button_mappings(self, controller: Controller, button_mappings: dict[str, str], /) -> None:
        super().set_button_mappings(controller, button_mappings)

        # Some input adaptations for some cores...
        # Z is important, in case l2 (z) is not available for this pad, use l1
        if self.system == 'n64' and 'r2' not in controller.inputs:
            button_mappings['pageup'] = 'l2'
            button_mappings['l2'] = 'l'

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        option = self.n64_controller_option
        for pad in self.controllers[:4]:
            if (pad.guid in _VALID_N64_CONTROLLER_GUIDS and pad.name in _VALID_N64_CONTROLLER_NAMES) or (
                self.config.get(f'{option}-controller{pad.player_number}', 'retropad') != 'retropad'
            ):
                for btn, value in _N64_REMAP_VALUES.items():
                    custom_config.set(f'input_player{pad.player_number}_{btn}', value)
