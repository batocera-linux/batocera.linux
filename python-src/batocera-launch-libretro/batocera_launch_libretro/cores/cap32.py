from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Cap32(Core):
    supports_retroachievements: ClassVar = True

    @cached_property
    def player1_device_type(self) -> str | None:
        return '513'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Virtual Keyboard by default (select+start) change to (start+Y)
        core_options.set('cap32_combokey', 'y')

        # Auto Select Model
        if self.system == 'gx4000':
            core_options.set('cap32_model', '6128+ (experimental)')
        else:
            core_options.set_from_config('cap32_model', default='6128')

        # Ram size
        core_options.set_from_config('cap32_ram', default='128')

        # colour depth
        core_options.set_from_config('cap32_gfx_colors', 'cap32_colour', default='24bit')

        # language
        core_options.set_from_config('cap32_lang_layout', 'cap32_language', default='english')
