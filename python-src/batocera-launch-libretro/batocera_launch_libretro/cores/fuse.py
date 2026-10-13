from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Fuse(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_zxspec', '769')  # 769 = Sinclair 1 controller - most used on games

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_zxspec', '1025')  # 1025 = Sinclair 2 controller

    @cached_property
    def player3_device_type(self) -> str | None:
        return self.config.get_str('controller3_zxspec', '259')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # The most common configuration same as ZX Spectrum+
        core_options.set_from_config('fuse_machine', 'fuse_machine', default='Spectrum 128K')

        # Video border size
        default = 'none' if self.config.get('fuse_hide_border') == 'enabled' else 'full'
        core_options.set_from_config('fuse_size_border', 'fuse_size_border', default=default)
