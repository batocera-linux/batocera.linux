from __future__ import annotations

from typing import ClassVar, Final

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig

_C64_MAPPING: Final = {
    'a': '---',
    'aspect_ratio_toggle': '---',
    'b': '---',
    'joyport_switch': 'RETROK_F10',
    'l': 'RETROK_ESCAPE',
    'l2': 'RETROK_F11',
    'l3': 'SWITCH_JOYPORT',
    'ld': '---',
    'll': '---',
    'lr': '---',
    'lu': '---',
    'r': 'RETROK_PAGEUP',
    'r2': 'RETROK_LSHIFT',
    'rd': 'RETROK_F7',
    'reset': '---',
    'rl': 'RETROK_F3',
    'rr': 'RETROK_F5',
    'ru': 'RETROK_F1',
    'select': 'TOGGLE_VKBD',
    'start': 'RETROK_RETURN',
    'statusbar': 'RETROK_F9',
    'vkbd': 'RETROK_F12',
    'warp_mode': 'RETROK_F11',
    'turbo_fire_toggle': 'RETROK_RCTRL',
    'x': 'RETROK_RCTRL',
    'y': 'RETROK_SPACE',
}


@cached_dataclass
class ViceX64(Core):
    gun_mapping: ClassVar = {
        'default': {
            'gameDependant': [
                {
                    'key': 'type',
                    'value': 'stack_light_rifle',
                    'mapcorekey': 'vice_joyport_type',
                    'mapcorevalue': '15',
                }
            ]
        }
    }

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        # D-pad = Left analog stick forcing on VICE (New D2A system on RA doesn't work with these cores.)
        custom_config.set('input_player1_analog_dpad_mode', '3')
        custom_config.set('input_player2_analog_dpad_mode', '3')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Activate Jiffydos
        core_options.set('vice_jiffydos', 'enabled')
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

        for key, mapping_key in _C64_MAPPING.items():
            core_options.set(f'vice_mapper_{key}', mapping_key)

        # Model type
        core_options.set_from_config('vice_c64_model', 'c64_model', default='C64 PAL auto')

        # Aspect Ratio
        core_options.set_from_config('vice_aspect_ratio', default='pal')

        # Zoom Mode
        zoom_mode = self.config.get('vice_zoom_mode', 'auto_disable')
        core_options.set('vice_crop', 'auto' if zoom_mode == 'automatic' else zoom_mode)
        core_options.set('vice_zoom_mode', 'deprecated')

        # External palette
        core_options.set_from_config('vice_external_palette', default='colodore')

        # Button options
        core_options.set_from_config('vice_retropad_options', default='jump')

        # Select Controller Port
        core_options.set_from_config('vice_joyport', default='2')

        # Select Controller Type
        # gun
        if self.config.use_guns and self.guns:
            core_options.set('vice_joyport_type', '14')
        else:
            core_options.set_from_config('vice_joyport_type', default='1')

        # RAM Expansion Unit (REU)
        core_options.set_from_config('vice_ram_expansion_unit', default='none')

        # Keyboard Pass-through for Pad2Key
        core_options.set_from_config(
            'vice_physical_keyboard_pass_through', 'vice_keyboard_pass_through', default='disabled'
        )


@cached_dataclass
class ViceX64sc(ViceX64):
    gun_mapping: ClassVar = None

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        return None
