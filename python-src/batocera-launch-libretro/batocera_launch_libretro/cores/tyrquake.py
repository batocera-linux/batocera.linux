from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from batocera_common.paths import ROMS
from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controller


@cached_dataclass
class Tyrquake(DisableRewindMixin, DisableRunaheadMixin, Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('tyrquake_controller1') or '1'

    @cached_property
    def rom_argument(self) -> str | Path | None:
        if self.system != 'quake':
            return self.rom

        # tyrquake - set directory
        name = self.rom.name.lower()

        if 'scourge' in name:
            return ROMS / 'quake' / 'hipnotic' / 'pak0.pak'

        if 'dissolution' in name:
            return ROMS / 'quake' / 'rogue' / 'pak0.pak'

        return ROMS / 'quake' / 'id1' / 'pak0.pak'

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1 and (controller1 := self.config.get('tyrquake_controller1')):
            return '0' if controller1 in {'773', '3'} else '1'
        return super().get_analog_mode(controller)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Resolution
        core_options.set_from_config('tyrquake_resolution', 'tyrquake_resolution', default='640x480')

        # Frame rate
        framerate = self.config.get('tyrquake_framerate', 'automatic')
        core_options.set('tyrquake_framerate', 'Auto' if framerate == 'automatic' else framerate)

        # Rumble
        core_options.set_from_config('tyrquake_rumble', 'tyrquake_rumble', default='disabled')
