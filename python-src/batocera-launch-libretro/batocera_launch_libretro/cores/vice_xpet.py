from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class ViceXpet(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Enable Automatic Load Warp
        core_options.set('vice_autoloadwarp', 'enabled')
        # Disable Datasette Hotkeys
        core_options.set('vice_datasette_hotkeys', 'disabled')
        # Not Read 'vicerc'
        core_options.set('vice_read_vicerc', 'disabled')
        # Select Joystick Type
        core_options.set('vice_Controller', 'joystick')
        # Disable Turbo Fire
        core_options.set('vice_turbo_fire', 'disabled')

        # Model type
        core_options.set_from_config('vice_pet_model', 'pet_model', default='8032')

        # Aspect Ratio
        core_options.set_from_config('vice_aspect_ratio', default='pal')

        # Zoom Mode
        zoom_mode = self.config.get('vice_zoom_mode', 'auto_disable')
        core_options.set('vice_crop', 'auto' if zoom_mode == 'automatic' else zoom_mode)
        core_options.set('vice_zoom_mode', 'deprecated')

        # External palette
        core_options.set_from_config('vice_pet_external_palette', default='default')

        # Button options
        core_options.set_from_config('vice_retropad_options', default='disabled')

        # Select Controller Port
        core_options.set_from_config('vice_joyport', default='2')

        # Select Controller Type
        core_options.set_from_config('vice_joyport_type', default='1')

        # Keyboard Pass-through for Pad2Key
        core_options.set_from_config(
            'vice_physical_keyboard_pass_through', 'vice_keyboard_pass_through', default='disabled'
        )
