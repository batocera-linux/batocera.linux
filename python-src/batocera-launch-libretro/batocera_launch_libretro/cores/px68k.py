from __future__ import annotations

from batocera_common.paths import BIOS, ROMS
from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Px68k(DisableRewindMixin, DisableRunaheadMixin, Core):
    def generate_special_configs(self) -> None:
        # Fresh config file
        keropi_config = BIOS / 'keropi' / 'config'
        keropi_sram = BIOS / 'keropi' / 'sram.dat'
        for f in [keropi_config, keropi_sram]:
            if f.exists():
                f.unlink()
        with keropi_config.open('w') as fd:
            fd.write('[WinX68k]\n')
            fd.write(f'StartDir={ROMS / "x68000"}\n')

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # To auto launch HDD games
        core_options.set('px68k_disk_path', 'disabled')

        # CPU Speed (Overclock)
        core_options.set_from_config('px68k_cpuspeed', default='33Mhz (OC)')

        # RAM Size
        core_options.set_from_config('px68k_ramsize', default='12MB')

        # Frame Skip
        core_options.set_from_config('px68k_frameskip', default='Full Frame')

        # Joypad Type for two players
        joytype = self.config.get('px68k_joytype', 'Default (2 Buttons)')
        core_options.set('px68k_joytype1', joytype)
        core_options.set('px68k_joytype2', joytype)
