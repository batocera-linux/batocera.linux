from __future__ import annotations

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Atari800(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return '513'

    @cached_property
    def player2_device_type(self) -> str | None:
        return '513'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        if self.system == 'atari800':
            # Select Atari 800
            # Let user overide Atari System
            core_options.set_from_config('atari800_system', default='800XL (64K)')

            # Video Standard
            core_options.set_from_config('atari800_ntscpal', default='NTSC')

            # SIO Acceleration
            core_options.set_from_config('atari800_sioaccel', default='enabled')

            # Hi-Res Artifacting
            core_options.set_from_config('atari800_artifacting', default='disabled')

            # Internal resolution
            core_options.set_from_config('atari800_resolution')  # Default : 336x240

            # Internal BASIC interpreter
            core_options.set_from_config('atari800_internalbasic', default='disabled')

            # WARNING: Now we must stop to use "atari800.cfg" because core options crush them

        else:
            # Select Atari 5200
            core_options.set('atari800_system', '5200')

            # Autodetect A5200 CartType (Off/On)
            core_options.set('atari800_CartType', 'enabled')

            # Joy Hack (for robotron)
            core_options.set_from_config('atari800_opt2', default='disabled')
