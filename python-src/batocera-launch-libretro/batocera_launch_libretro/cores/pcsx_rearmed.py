from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

if TYPE_CHECKING:
    from batocera_launch import Controller, Gun


@cached_dataclass
class PcsxRearmed(Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {
        'default': {
            'device': 260,
            'p1': 0,
            'p2': 1,
            'gameDependant': [{'key': 'type', 'value': 'justifier', 'mapkey': 'device', 'mapvalue': '516'}],
        }
    }

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('controller1_pcsx') or None

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('controller2_pcsx') or None

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1 and (psx_controller_1 := self.config.get('controller1_pcsx')):
            return '0' if psx_controller_1 != '1' else '1'

        if controller.player_number == 2 and (psx_controller_2 := self.config.get('controller2_pcsx')):
            return '0' if psx_controller_2 != '1' else '1'

        return super().get_analog_mode(controller)

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)

        # wheel
        if self.config.use_wheels:
            for pad in self.controllers:
                if pad.device_path in self.wheels:
                    custom_config.set(f'input_player{pad.player_number}_analog_dpad_mode', '1')
                    if self.metadata.get('wheel_type') == 'negcon':
                        custom_config.set(f'input_libretro_device_p{pad.player_number}', 773)  # Negcon
                    else:
                        custom_config.set(f'input_libretro_device_p{pad.player_number}', 517)  # DualShock Controller

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Display Games Hack Options
        core_options.set('pcsx_rearmed_show_gpu_peops_settings', 'enabled')

        # Display Multitap/Gamepad Options
        core_options.set('pcsx_rearmed_show_other_input_settings', 'enabled')

        # Enable Vibration
        core_options.set('pcsx_rearmed_vibration', 'enabled')

        # Show Bios Bootlogo (Breaks some games)
        core_options.set_from_config('pcsx_rearmed_show_bios_bootlogo', 'show_bios_bootlogo', default='disabled')

        # Frameskip
        core_options.set_from_config('pcsx_rearmed_frameskip', 'frameskip_pcsx', default='0')

        # Enhanced resolution at the cost of lower performance
        match self.config.get('neon_enhancement'):
            case 'enabled':
                core_options.set('pcsx_rearmed_neon_enhancement_enable', 'enabled')
                core_options.set('pcsx_rearmed_neon_enhancement_no_main', 'disabled')
            case 'enabled_with_speedhack':
                core_options.set('pcsx_rearmed_neon_enhancement_enable', 'enabled')
                core_options.set('pcsx_rearmed_neon_enhancement_no_main', 'enabled')
            case _:
                core_options.set('pcsx_rearmed_neon_enhancement_enable', 'disabled')
                core_options.set('pcsx_rearmed_neon_enhancement_no_main', 'disabled')

        # Multitap
        core_options.set_from_config('pcsx_rearmed_multitap', 'pcsx_rearmed_multitap', default='disabled')

        # Additional game fixes
        core_options.set('pcsx_rearmed_idiablofix', 'disabled')
        core_options.set('pcsx_rearmed_pe2_fix', 'disabled')
        core_options.set('pcsx_rearmed_inuyasha_fix', 'disabled')
        core_options.set('pcsx_rearmed_gpu_peops_odd_even_bit', 'disabled')
        core_options.set('pcsx_rearmed_gpu_peops_expand_screen_width', 'disabled')
        core_options.set('pcsx_rearmed_gpu_peops_ignore_brightness', 'disabled')
        core_options.set('pcsx_rearmed_gpu_peops_lazy_screen_update', 'disabled')
        core_options.set('pcsx_rearmed_gpu_peops_repeated_triangles', 'disabled')
        if (fixes := self.config.get('game_fixes_pcsx')) != 'disabled':
            if fixes == 'Diablo_Music_Fix':
                core_options.set('pcsx_rearmed_idiablofix', 'enabled')
            elif fixes == 'Parasite_Eve':
                core_options.set('pcsx_rearmed_pe2_fix', 'enabled')
            elif fixes == 'InuYasha_Sengoku':
                core_options.set('pcsx_rearmed_inuyasha_fix', 'enabled')
            elif fixes == 'Chrono_Chross':
                core_options.set('pcsx_rearmed_gpu_peops_odd_even_bit', 'enabled')
            elif fixes == 'Capcom_fighting':
                core_options.set('pcsx_rearmed_gpu_peops_expand_screen_width', 'enabled')
            elif fixes == 'Lunar':
                core_options.set('pcsx_rearmed_gpu_peops_ignore_brightness', 'enabled')
            elif fixes == 'Pandemonium':
                core_options.set('pcsx_rearmed_gpu_peops_lazy_screen_update', 'enabled')
            elif fixes == 'Dark_Forces':
                core_options.set('pcsx_rearmed_gpu_peops_repeated_triangles', 'enabled')

        # gun cross
        # Crossbar Colors
        need_crosses = self.emulator.guns_need_crosses
        for player, color in enumerate(['red', 'blue'], start=1):
            core_options.set_from_config(
                f'pcsx_rearmed_crosshair{player}',
                f'pcsx_rearmed_crosshair{player}',
                default=color if need_crosses else 'disabled',
            )

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        if self.metadata.get('gun_type') == 'justifier':
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
        else:
            custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_start_mbtn', '')
            custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
            custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', 3)
