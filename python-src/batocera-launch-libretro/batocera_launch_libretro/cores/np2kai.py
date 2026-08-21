from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class Np2kai(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # https://github.com/AZO234/NP2kai/blob/6e8f651a72c2ece37cc52e17cdaf4fdb87a6b2f9/sdl/libretro/libretro_core_options.h
        # Use the American keyboard
        core_options.set('np2kai_keyboard', 'Us')
        # Fast memcheck at startup
        core_options.set('np2kai_FastMC', 'ON')
        # Sound Generator: Use "fmgen" for enhanced sound rendering, not "Default"
        # core_options.set('np2kai_usefmgen', 'fmgen')
        # PC Model
        core_options.set_from_config('np2kai_model', default='PC-9801VX')

        # CPU Feature
        core_options.set_from_config('np2kai_cpu_feature', default='Intel 80386')

        # CPU Clock Multiplier
        core_options.set_from_config('np2kai_clk_mult', default='4')

        # RAM Size
        core_options.set_from_config('np2kai_ExMemory', default='3')

        # GDC
        core_options.set_from_config('np2kai_gdc', default='uPD7220')

        # Remove Scanlines (255 lines)
        scanlines = self.config.get('np2kai_skipline', 'Full 255 lines')
        if scanlines == 'True':
            scanlines = 'ON'
        elif scanlines == 'False':
            scanlines = 'OFF'
        core_options.set('np2kai_skipline', scanlines)

        # Real Palettes
        core_options.set_bool_from_config('np2kai_realpal', values=('ON', 'OFF'))

        # Sound Board
        core_options.set_from_config('np2kai_SNDboard', default='PC9801-26K + 86')

        # JAST SOUND
        core_options.set_bool_from_config('np2kai_jast_snd', values=('ON', 'OFF'))

        # Joypad to Keyboard Mapping
        core_options.set_from_config('np2kai_joymode', default='Arrows')
