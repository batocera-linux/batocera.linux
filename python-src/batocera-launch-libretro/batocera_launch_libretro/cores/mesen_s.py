from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, LibretroConfig, SquashFSMixin


@cached_dataclass
class MesenS(SquashFSMixin, Core):
    supports_retroachievements: ClassVar = True
    squashfs_rom_globs: ClassVar = {'satellaview': ('*.sfc', '*.smc')}
    gun_mapping: ClassVar = {'default': {'device': 262, 'p2': 0}}

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Force appropriate Game Boy mode for the system (unless overriden)
        gbmodel = self.config.get('mesen-s_gbmodel')
        if gbmodel is None:
            if self.system == 'sgb':
                gbmodel = 'Super Game Boy'
            elif self.system == 'gb':
                gbmodel = 'Game Boy'
            elif self.system == 'gbc':
                gbmodel = 'Game Boy Color'
            else:
                gbmodel = 'Auto'
        core_options.set('mesen-s_gbmodel', gbmodel)

        # SGB2 Enable (sgb only)
        if self.system == 'sgb':
            core_options.set_from_config('mesen-s_sgb2', default='enabled')

        # NTSC Filter
        core_options.set_from_config('mesen-s_ntsc_filter', default='disabled')

        # Blending for high-res mode (Kirby's Dream Land 3 pseudo-transparency)
        core_options.set_from_config('mesen-s_blend_high_res', default='disabled')

        # Change sound interpolation to cubic
        core_options.set_from_config('mesen-s_cubic_interpolation', default='disabled')

        # SNES CPU Overclock
        core_options.set_from_config('mesen-s_overclock', default='None')

        # Overclocking type (compatibility)
        core_options.set_from_config('mesen-s_overclock_type', default='Before NMI')

        # SuperFX Overclock
        core_options.set_from_config('mesen-s_superfx_overclock', default='100%')
