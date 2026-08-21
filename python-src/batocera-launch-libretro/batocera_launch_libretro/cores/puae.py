from __future__ import annotations

from typing import Final

from batocera_common.paths import BIOS
from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

# Functional mapping for Amiga system
# If you want to change them, you can add some strings to batocera.conf by using
# this syntax: SYSTEMNAME.retroarchcore.puae_mapper_BUTTONNAME=VALUE
_A500_A1200_MAPPING: Final = {
    'aspect_ratio_toggle': '---',
    'mouse_toggle': 'RETROK_RCTRL',
    'statusbar': 'RETROK_F11',
    'vkbd': '---',
    'reset': '---',
    'crop_toggle': 'RETROK_F12',
    'zoom_mode_toggle': '---',
    'a': '---',
    'b': '---',
    'x': 'RETROK_LALT',
    'y': 'RETROK_SPACE',
    'l': 'RETROK_ESCAPE',
    'l2': 'MOUSE_LEFT_BUTTON',
    'l3': 'SWITCH_JOYMOUSE',
    'ld': '---',
    'll': '---',
    'lr': '---',
    'lu': '---',
    'r': 'RETROK_F1',
    'r2': 'MOUSE_RIGHT_BUTTON',
    'r3': 'TOGGLE_STATUSBAR',
    'rd': '---',
    'rl': '---',
    'rr': '---',
    'ru': '---',
    'select': 'TOGGLE_VKBD',
    'start': 'RETROK_RETURN',
}

_CD32_MAPPING: Final = {
    'aspect_ratio_toggle': '---',
    'mouse_toggle': 'RETROK_RCTRL',
    'statusbar': 'RETROK_F11',
    'vkbd': '---',
    'reset': '---',
    'crop_toggle': 'RETROK_F12',
    'zoom_mode_toggle': '---',
    'a': '---',
    'b': '---',
    'x': '---',
    'y': '---',
    'l': '---',
    'l2': 'MOUSE_LEFT_BUTTON',
    'l3': 'SWITCH_JOYMOUSE',
    'ld': '---',
    'll': '---',
    'lr': '---',
    'lu': '---',
    'r': '---',
    'r2': 'MOUSE_RIGHT_BUTTON',
    'r3': 'TOGGLE_STATUSBAR',
    'rd': '---',
    'rl': '---',
    'rr': '---',
    'ru': '---',
    'select': '---',
    'start': '---',
}

_MODEL_MAPPING: Final = {
    'amiga1200': 'A1200',
    'amigacd32': 'CD32FR',
    'amigacdtv': 'CDTV',
}


@cached_dataclass
class Puae(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        if self.system == 'amigacd32':
            return '517'  # CD 32 Pad

        return self.config.get_str('controller1_puae', '1')

    @cached_property
    def player2_device_type(self) -> str | None:
        if self.system == 'amigacd32':
            return None

        return self.config.get_str('controller2_puae', '1')

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        # AMIGA BIOS files are in /userdata/bios/amiga
        custom_config.set('system_directory', f'{BIOS / "amiga"}/')

        # D-pad = Left analog stick forcing on PUAE (New D2A system on RA doesn't work with these cores.)
        custom_config.set('input_player1_analog_dpad_mode', '3')
        custom_config.set('input_player2_analog_dpad_mode', '3')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        if (
            self.system != 'amigacd32'
            and self.config.get('controller1_puae') != '517'
            and self.config.get('controller2_puae') != '517'
        ):
            mapping = _A500_A1200_MAPPING
        else:
            mapping = _CD32_MAPPING

        for key, mapped_key in mapping.items():
            core_options.set(f'puae_mapper_{key}', mapped_key)

        # Show Video Options
        core_options.set('puae_video_options_display', 'enabled')

        # Amiga Model
        # Will default to A500 when booting floppy disks, A600 when booting hard drives on auto
        if (model := self.config.get('puae_model', 'automatic')) != 'automatic':
            core_options.set('puae_model', model)
        else:
            core_options.set('puae_model', _MODEL_MAPPING.get(self.system, 'auto'))

        # CPU Compatibility
        core_options.set_from_config('puae_cpu_compatibility', 'cpu_compatibility', default='normal')

        # CPU Multiplier (Overclock)
        core_options.set_from_config('puae_cpu_throttle', 'cpu_throttle', default='0.0')
        core_options.set('puae_cpu_multiplier', '0')

        # CPU Cycle Exact Speed (Overclock)
        if self.config.get('cpu_compatibility') == 'exact':
            core_options.set('puae_cpu_throttle', '0.0')
            core_options.set_from_config('puae_cpu_multiplier', 'cpu_multiplier', default='0')

        # Standard Video
        core_options.set_from_config('puae_video_standard', 'video_standard', default='PAL auto')

        # Video Resolution
        core_options.set_from_config('puae_video_resolution', 'video_resolution', default='hires')

        # Zoom Mode
        zoom_mode = self.config.get('zoom_mode', 'automatic')
        core_options.set('puae_crop', 'auto' if zoom_mode == 'automatic' else zoom_mode)
        core_options.set('puae_zoom_mode', 'deprecated')

        # Frameskip
        core_options.set_from_config('puae_gfx_framerate', 'gfx_framerate', default='disabled')

        # Mouse Speed
        core_options.set_from_config('puae_mouse_speed', 'mouse_speed', default='200')

        # Jump on B
        core_options.set_from_config(
            'puae_retropad_options',
            'pad_options',
            default='disabled' if self.system == 'amigacdtv' else 'jump',
        )

        if self.system in {'amiga500', 'amiga1200'}:
            # Floppy Turbo Speed
            core_options.set_from_config('puae_floppy_speed', default='100')

            # 2P Gamepad Mapping (Keyrah)
            core_options.set_from_config('puae_keyrah_keypad_mappings', 'keyrah_mapping', default='enabled')

            # Whdload Launcher
            core_options.set_from_config('puae_use_whdload_prefs', 'whdload', default='config')

            # Disable Emulator Joystick for Pad2Key
            core_options.set_from_config('puae_physical_keyboard_pass_through', 'disable_joystick', default='disabled')

        if self.system in {'amigacd32', 'amigacdtv'}:
            # Boot animation first inserting CD
            core_options.set_from_config('puae_cd_startup_delayed_insert', default='disabled')

            # CD Turbo Speed
            core_options.set_from_config('puae_cd_speed', default='100')

        if self.system == 'amigacd32':
            # Jump on A (Blue)
            core_options.set_from_config('puae_cd32pad_options', default='disabled')
