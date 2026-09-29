from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import RACore

from ._megadrive_core import MegadriveControllerRemapMixin

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Picodrive(MegadriveControllerRemapMixin, RACore):
    megadrive_controller_option: ClassVar = 'pd'

    @cached_property
    def can_rewind(self) -> bool:
        if self.system == 'sega32x':
            return False

        return super().can_rewind

    @cached_property
    def runahead(self) -> int:
        if self.system == 'sega32x':
            return 0

        return super().runahead

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Reduce sprite flickering
        core_options.set_from_config('picodrive_sprlim', default='enabled')

        # Crop Overscan: the setting in picodrive shows overscan when enabled
        core_options.set_bool_from_config(
            'picodrive_overscan', 'picodrive_cropoverscan', default=True, values=('disabled', 'enabled')
        )

        # 6 Button Controller 1
        core_options.set_from_config('picodrive_input1', 'picodrive_controller1', default='6 button pad')

        # 6 Button Controller 2
        core_options.set_from_config('picodrive_input2', 'picodrive_controller2', default='6 button pad')

        # Sega MegaCD
        # Emulate the Backup RAM Cartridge for games save (ex: Shining Force CD)
        core_options.set('picodrive_ramcart', 'enabled' if self.system == 'megacd' else 'disabled')
