from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Gearcoleco(DisableRewindMixin, DisableRunaheadMixin, Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Refresh Rate (requires restart)
        core_options.set_from_config('gearcoleco_timing', default='Auto')

        # Aspect Ratio
        core_options.set_from_config('gearcoleco_aspect_ratio', default='1:1 PAR')

        # Overscan
        core_options.set_from_config('gearcoleco_overscan', default='Disabled')

        # Allow Up+Down / Left+Right
        core_options.set_from_config('gearcoleco_up_down_allowed', default='Disabled')

        # No Sprite Limit
        core_options.set_from_config('gearcoleco_no_sprite_limit', default='Disabled')

        # Spinner support
        core_options.set_from_config('gearcoleco_spinners', default='Disabled')

        # Spinner Sensitivity
        core_options.set_from_config('gearcoleco_spinner_sensitivity', default='1')
