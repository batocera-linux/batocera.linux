from __future__ import annotations

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Fuse(DisableRewindMixin, DisableRunaheadMixin, Core):
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

        # Zoom, Hide Video Border
        core_options.set_from_config('fuse_hide_border', 'fuse_hide_border', default='disabled')
