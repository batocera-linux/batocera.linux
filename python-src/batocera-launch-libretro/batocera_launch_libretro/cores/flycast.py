from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import (
    Core,
    DisableAnalogModeMixin,
    DisableRewindMixin,
    DisableRunaheadMixin,
    LibretroConfig,
)

if TYPE_CHECKING:
    from batocera_launch import Controller, Gun


@cached_dataclass
class FlycastVL(DisableAnalogModeMixin, DisableRewindMixin, DisableRunaheadMixin, Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 4, 'p1': 0, 'p2': 1, 'p3': 2, 'p4': 3}}


@cached_dataclass
class Flycast(FlycastVL):
    @property
    def can_rewind(self) -> bool:
        return self.config.get_bool('rewind')

    def set_button_mappings(self, controller: Controller, button_mappings: dict[str, str], /) -> None:
        # Some input adaptations for some cores...
        # Z is important, in case l2 (z) is not available for this pad, use l1
        if self.system == 'dreamcast' and 'r2' not in controller.inputs:
            button_mappings['pageup'] = 'l2'
            button_mappings['l2'] = 'l'
            button_mappings['pagedown'] = 'r2'
            button_mappings['r2'] = 'r'

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        ## Sega Dreamcast controller
        ## Left Analog To Dpad (Forced) is convenient for Arcade Systems (Atomiswave, Naomi 1 and 2)
        for player_number in range(1, 5):
            dc_val = self.config.get(f'controller{player_number}_dc', '1')
            if dc_val == '5':  # "Gamepad using left analog stick"
                custom_config.set(f'input_libretro_device_p{player_number}', '1')
                custom_config.set(f'input_player{player_number}_analog_dpad_mode', '3')
            else:
                custom_config.set(f'input_libretro_device_p{player_number}', dc_val)
                custom_config.set(f'input_player{player_number}_analog_dpad_mode', '0')

        # wheel
        if self.config.use_wheels and self.wheels:
            custom_config.set('input_libretro_device_p1', '2049')  # Race Controller

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # force vmu all, to save in saves (otherwise, it saves in game_dir, which is bios)
        core_options.set('reicast_per_content_vmus', 'All VMUs')

        # Synchronous rendering
        core_options.set_from_config('reicast_synchronous_rendering', default='enabled')

        # DSP audio
        core_options.set_from_config('reicast_enable_dsp', 'reicast_dsp', default='disabled')

        # Threaded Rendering
        core_options.set('reicast_threaded_rendering', 'enabled')

        # Enable controller force feedback
        core_options.set('reicast_enable_purupuru', 'enabled')

        # Crossbar Colors
        need_crosses = self.emulator.guns_need_crosses
        core_options.set_from_config('reicast_lightgun1_crosshair', default='Red' if need_crosses else 'disabled')
        core_options.set_from_config('reicast_lightgun2_crosshair', default='Blue' if need_crosses else 'disabled')
        core_options.set_from_config('reicast_lightgun3_crosshair', default='Green' if need_crosses else 'disabled')
        core_options.set_from_config('reicast_lightgun4_crosshair', default='White' if need_crosses else 'disabled')

        # Video resolution
        core_options.set_from_config('reicast_internal_resolution', default='640x480')

        # Textures Mip-mapping (blur)
        core_options.set_from_config('reicast_mipmapping', default='disabled')

        # Anisotropic Filtering
        core_options.set_from_config('reicast_anisotropic_filtering', default='off')

        # Texture Upscaling (xBRZ)
        core_options.set_from_config('reicast_texupscale', default='1')

        # Frame Skip
        core_options.set_from_config('reicast_frame_skipping', default='disabled')

        # Force Windows CE Mode
        core_options.set_from_config('reicast_force_wince', default='disabled')

        # Widescreen Cheat
        if (
            self.config.get('reicast_widescreen_cheats') == 'enabled'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
        ):
            widescreen_cheat = 'enabled'
        else:
            widescreen_cheat = 'disabled'

        core_options.set('reicast_widescreen_cheats', widescreen_cheat)

        # Widescreen Hack (prefer Cheat)
        if (
            self.config.get('reicast_widescreen_hack') == 'enabled'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
            and self.config.get('reicast_widescreen_cheats') == 'disabled'
        ):
            widescreen_hack = 'enabled'
        else:
            widescreen_hack = 'disabled'

        core_options.set('reicast_widescreen_hack', widescreen_hack)

        # Bios
        core_options.set_from_config('reicast_language', default='Default')
        core_options.set_from_config('reicast_region', default='Default')

        # Native Depth Interpolation
        core_options.set_from_config('reicast_native_depth_interpolation', default='disabled')

        ## Atomiswave / Naomi

        # Screen Orientation
        if self.system == 'atomiswave':
            rotation = self.config.get('screen_rotation_atomiswave', 'horizontal')
        elif self.system == 'naomi':
            rotation = self.config.get('screen_rotation_naomi', 'horizontal')
        else:
            rotation = 'horizontal'

        core_options.set('reicast_screen_rotation', rotation)

        # wheel
        core_options.set(
            'reicast_analog_stick_deadzone', '0%' if self.config.use_wheels and self.wheels else '15%'
        )  # 15% = default value

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        if self.config.get_bool('flycast_offscreen_reload'):
            return super().get_pedal_config_name_for_player(player_number)
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        if self.config.get_bool('flycast_offscreen_reload'):
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_select_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 3)
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', 4)
            custom_config.set(f'input_player{player_number}_gun_select_mbtn', 5)
        else:
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
