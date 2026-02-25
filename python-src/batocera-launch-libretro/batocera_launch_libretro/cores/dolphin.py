from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

if TYPE_CHECKING:
    from batocera_launch import Gun

# Dolphin uses Wiimote/Nunchuk via RetroArch joypad, not RETRO_DEVICE_LIGHTGUN
_WIIMOTE_TO_RA: Final = {
    'b': 'b',
    'a': 'a',
    '1': 'start',
    '2': 'select',
    '+': 'r',
    '-': 'l',
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
    'c': 'x',
    'z': 'y',
    'shake': 'r2',
    'tiltforward': 'l3',
}

# Gun button names to Wiimote buttons (defaults)
_ACTION_TO_WIIMOTE: Final = {
    'trigger': 'b',
    'action': 'a',
    'start': '+',
    'select': '-',
    'sub1': '1',
    'sub2': '2',
    'up': 'up',
    'down': 'down',
    'left': 'left',
    'right': 'right',
}

# Gun button names to virtual light gun mapping in RetroArch
_ACTION_TO_GUN: Final = {
    'trigger': 1,
    'action': 2,
    'start': 3,
    'select': 4,
    'sub1': 5,
    'sub2': 6,
    'up': 8,
    'down': 9,
    'left': 10,
    'right': 11,
}

_GUN_MBTN_KEYS: Final = (
    'gun_trigger',
    'gun_offscreen_shot',
    'gun_aux_a',
    'gun_aux_b',
    'gun_aux_c',
    'gun_start',
    'gun_select',
    'gun_dpad_up',
    'gun_dpad_down',
    'gun_dpad_left',
    'gun_dpad_right',
)


@cached_dataclass
class Dolphin(Core):
    gun_mapping: ClassVar = {'default': {'device': 769, 'p1': 0, 'p2': 1, 'p3': 2, 'p4': 3}}

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_wii', '1')

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_wii', '1')

    @cached_property
    def player3_device_type(self) -> str | None:
        return self.config.get_str('controller3_wii', '1')

    @cached_property
    def player4_device_type(self) -> str | None:
        return self.config.get_str('controller4_wii', '1')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Wii System Languages
        core_options.set_from_config('dolphin_language', 'wii_language', default='1')

        # Wii Resolution Scale
        core_options.set_from_config('dolphin_efb_scale', 'wii_resolution', default='1')

        # Anisotropic Filtering
        core_options.set_from_config('dolphin_max_anisotropy', 'wii_anisotropic', default='0')

        # Wii Tv Mode
        core_options.set_from_config('dolphin_widescreen', 'wii_widescreen', default='enabled')

        # Widescreen Hack
        core_options.set_from_config('dolphin_widescreen_hack', 'wii_widescreen_hack', default='disabled')

        # Shader Compilation Mode
        core_options.set_from_config('dolphin_shader_compilation_mode', 'wii_shader_mode', default='0')

        # OSD
        core_options.set_from_config('dolphin_osd_enabled', 'wii_osd', default='enabled')

        # Light gun
        core_options.set('dolphin_ir_mode', '3' if self.config.use_guns and self.guns else '1')

    def set_gun_core_options(self, core_options: LibretroConfig, /) -> None:
        # Dolphin IR calibration from metadata
        core_options.set('dolphin_ir_offset', self.metadata.get('gun_vertical_offset', '10'))
        core_options.set('dolphin_ir_yaw', self.metadata.get('gun_yaw', '25'))
        core_options.set('dolphin_ir_pitch', self.metadata.get('gun_pitch', '20'))

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        # Dolphin uses Wiimote via RetroArch joypad, not RETRO_DEVICE_LIGHTGUN

        # Clear all gun-specific mappings
        for gun_key in _GUN_MBTN_KEYS:
            custom_config.set(f'input_player{player_number}_{gun_key}_mbtn', '')

        # Override with game-specific metadata
        action_to_wiimote = dict(_ACTION_TO_WIIMOTE)
        for action in action_to_wiimote:
            if gun_action := self.metadata.get(f'gun_{action}'):
                action_to_wiimote[action] = gun_action

        # Apply mapping to RetroArch config
        for action, wiimote in action_to_wiimote.items():
            ra_button = _WIIMOTE_TO_RA.get(wiimote)
            gun_button = _ACTION_TO_GUN.get(action)
            if ra_button is not None and gun_button is not None:
                custom_config.set(f'input_player{player_number}_{ra_button}_mbtn', gun_button)
