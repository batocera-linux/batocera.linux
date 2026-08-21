from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Literal

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

if TYPE_CHECKING:
    from batocera_launch import Controller


@cached_dataclass
class MednafenPsx(Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('beetle_psx_hw_Controller1') or None

    @cached_property
    def player2_device_type(self) -> str | None:
        return self.config.get_str('beetle_psx_hw_Controller2') or None

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1 and (psx_controller_1 := self.config.get('beetle_psx_hw_Controller1')):
            return '0' if psx_controller_1 != '1' else '1'

        if controller.player_number == 2 and (psx_controller_2 := self.config.get('beetle_psx_hw_Controller2')):
            return '0' if psx_controller_2 != '1' else '1'

        return super().get_analog_mode(controller)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # CPU Frequency Scaling (Overclock)
        core_options.set_from_config(
            'beetle_psx_hw_cpu_freq_scale', default='110%'
        )  # If not 110% NO options are working!

        # Show official Bootlogo
        core_options.set_from_config('beetle_psx_hw_skip_bios', default='disabled')

        # Video Resolution
        core_options.set_from_config('beetle_psx_hw_internal_resolution', default='1x(native)')

        # Widescreen Hack
        if (
            self.config.get('beetle_psx_hw_widescreen_hack') == 'enabled'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
        ):
            core_options.set('beetle_psx_hw_widescreen_hack', 'enabled')
        else:
            core_options.set('beetle_psx_hw_widescreen_hack', 'disabled')

        # Frame Duping (Speedup)
        core_options.set_from_config('beetle_psx_hw_frame_duping', default='disabled')

        # CPU Dynarec (Speedup)
        core_options.set_from_config('beetle_psx_hw_cpu_dynarec', default='disabled')

        # Dynarec Code Invalidation
        core_options.set_from_config('beetle_psx_hw_dynarec_invalidate', default='full')

        # Analog Stick self calibration
        core_options.set('beetle_psx_hw_analog_calibration', 'enabled')

        # Multitap
        match self.config.get('multitap_mednafen'):
            case 'port1':
                core_options.set('beetle_psx_hw_enable_multitap_port1', 'enabled')
                core_options.set('beetle_psx_hw_enable_multitap_port2', 'disabled')
            case 'port2':
                core_options.set('beetle_psx_hw_enable_multitap_port1', 'disabled')
                core_options.set('beetle_psx_hw_enable_multitap_port2', 'enabled')
            case 'port12':
                core_options.set('beetle_psx_hw_enable_multitap_port1', 'enabled')
                core_options.set('beetle_psx_hw_enable_multitap_port2', 'enabled')
            case _:
                core_options.set('beetle_psx_hw_enable_multitap_port1', 'disabled')
                core_options.set('beetle_psx_hw_enable_multitap_port2', 'disabled')
