from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import AssociatedMouseMixin, Core, DisableAnalogModeMixin, LibretroConfig


@cached_dataclass
class Azahar(AssociatedMouseMixin, DisableAnalogModeMixin, Core):
    @property
    def disables_bezel(self) -> bool:
        return self.config.get('3ds_screen_layout', 'default') != 'default'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # 3DS System Model
        core_options.set_from_config('citra_is_new_3ds', '3ds_system_model', default='New 3DS')

        # 3DS System Region
        core_options.set_from_config('citra_region_value', '3ds_system_region', default='Auto')

        # 3DS System Language
        core_options.set_from_config('citra_language_value', '3ds_system_language', default='English')

        # 3DS Internal Resolution
        core_options.set_from_config('citra_resolution_factor', '3ds_internal_resolution', default='1')

        # 3DS Texture Filter
        core_options.set_from_config('citra_texture_filter', '3ds_texture_filter', default='none')

        # 3DS Screen Layout
        core_options.set_from_config('citra_layout_option', '3ds_screen_layout', default='default')

        # 3DS Prominent Screen
        core_options.set_from_config('citra_swap_screen', '3ds_prominent_screen', default='Top')

        # 3DS Large Screen Proportion
        core_options.set_from_config('citra_large_screen_proportion', '3ds_large_screen_proportion', default='4.00')
