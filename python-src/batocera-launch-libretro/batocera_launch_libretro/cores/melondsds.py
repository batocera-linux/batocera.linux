from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import AssociatedMouseMixin, Core, LibretroConfig


@cached_dataclass
class MelonDSDS(AssociatedMouseMixin, Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # System Settings
        core_options.set_from_config('melonds_console_mode', 'melondsds_console_mode', default='DS')

        # Video Settings
        core_options.set_from_config('melonds_render_mode', 'melondsds_render_mode', default='software')
        core_options.set_from_config('melonds_opengl_resolution', 'melondsds_resolution', default='1')
        core_options.set_from_config('melonds_opengl_better_polygons', 'melondsds_poygon', default='disabled')
        core_options.set_from_config('melonds_opengl_filtering', 'melondsds_filtering', default='nearest')

        # Screen Settings
        core_options.set_from_config('melonds_show_cursor', 'melondsds_cursor', default='nearest')
        core_options.set_from_config('melonds_cursor_timeout', 'melondsds_cursor_timeout', default='3')
        core_options.set_from_config('melonds_touch_mode', 'melondsds_touchmode', default='auto')
        # set 1 screen for now top/botton
        core_options.set('melonds_number_of_screen_layouts', '1')
        core_options.set('melonds_screen_gap', '0')
        core_options.set('melonds_screen_layout1', 'top-bottom')

        # Firmware Settings
        core_options.set_from_config('melonds_firmware_wfc_dns', 'melondsds_dns', default='178.62.43.212')
        core_options.set_from_config('melonds_firmware_language', 'melondsds_language', default='default')
        core_options.set_from_config('melonds_firmware_favorite_color', 'melondsds_colour', default='default')
        core_options.set_from_config('melonds_firmware_birth_month', 'melondsds_month', default='default')
        core_options.set_from_config('melonds_firmware_birth_day', 'melondsds_day', default='default')

        # Onscreen Display
        core_options.set_from_config(
            'melonds_show_unsupported_features', 'melondsds_show_unsupported', default='disabled'
        )
        core_options.set_from_config('melonds_show_bios_warnings', 'melondsds_show_bios', default='disabled')
        core_options.set_from_config('melonds_show_current_layout', 'melondsds_show_layout', default='disabled')
        core_options.set_from_config('melonds_show_mic_state', 'melondsds_show_mic', default='disabled')
        core_options.set_from_config('melonds_show_camera_state', 'melondsds_show_camera', default='disabled')
        core_options.set_from_config('melonds_show_lid_state', 'melondsds_show_lid', default='disabled')
