from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from ..core import Core

if TYPE_CHECKING:
    from ..config import LibretroConfig

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
