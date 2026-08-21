from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Opera(DisableRewindMixin, DisableRunaheadMixin, Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Audio Process on separate CPU thread
        core_options.set('opera_dsp_threaded', 'enabled')

        # High Resolution (640x480)
        core_options.set_from_config('opera_high_resolution', 'high_resolution', default='enabled')

        # CPU Overclock
        core_options.set_from_config('opera_cpu_overclock', 'cpu_overclock', default='1.0x (12.50Mhz)')

        # Active Input Devices Fix
        core_options.set_from_config('opera_active_devices', 'active_devices', default='1')

        # Additional game fixes
        timing_1 = 'disabled'
        timing_3 = 'disabled'
        timing_5 = 'disabled'
        timing_6 = 'disabled'

        match self.config.get('game_fixes_opera'):
            case 'timing_hack1':
                timing_1 = 'enabled'
            case 'timing_hack3':
                timing_3 = 'enabled'
            case 'timing_hack5':
                timing_5 = 'enabled'
            case 'timing_hack6':
                timing_6 = 'enabled'
            case _:
                pass

        core_options.set('opera_hack_timing_1', timing_1)
        core_options.set('opera_hack_timing_3', timing_3)
        core_options.set('opera_hack_timing_5', timing_5)
        core_options.set('opera_hack_timing_6', timing_6)

        # Shared nvram
        # If ROM includes the word Disc, assume it's a multi disc game, and enable shared nvram if the option isn't set.
        storage = self.config.get('opera_nvram_storage')

        if not storage:
            storage = 'shared' if 'disc' in str(self.rom).casefold() else 'per game'

        core_options.set('opera_nvram_storage', storage)
