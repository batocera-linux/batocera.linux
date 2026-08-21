from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.paths import BIOS
from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig

from ._hatari_core import HatariConfigMixin

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Hatarib(DisableRewindMixin, DisableRunaheadMixin, HatariConfigMixin, Core):
    @cached_property
    def rom_argument(self) -> str | Path | None:
        if self.rom.suffix.lower() in {'.hd', '.gemdos'}:
            # don't pass hd drive as parameter, it need to be added in configuration
            return None

        return self.rom

    def generate_special_configs(self) -> None:
        super().generate_special_configs()

        biosdir = BIOS / 'hatarib'
        if not biosdir.exists():
            biosdir.mkdir()

        targetlink = biosdir / 'hdd'

        # retroarch can't use hdd files outside his system directory (/userdata/bios)
        if targetlink.exists():
            targetlink.unlink()

        if self.rom.suffix.lower() in {'.hd', '.gemdos'}:
            targetlink.unlink(missing_ok=True)
            targetlink.symlink_to(self.rom)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Defaults
        core_options.set('hatarib_statusbar', '0')
        core_options.set('hatarib_fast_floppy', '1')
        core_options.set('hatarib_show_welcome', '0')
        core_options.set('hatarib_tos', '<etos1024k>')

        # Machine Type
        core_options.set_from_config('hatarib_machine', 'hatarib_machine', default='0')

        # Language/Region
        core_options.set_from_config('hatarib_region', 'hatarib_language', default='127')

        # CPU
        core_options.set_from_config('hatarib_cpu', 'hatarib_cpu', default='-1')

        # CPU Clock
        core_options.set_from_config('hatarib_cpu_clock', 'hatarib_cpu_clock', default='-1')

        # ST Memory Size
        core_options.set_from_config('hatarib_memory', 'hatarib_memory', default='1024')

        # Pause Screen
        core_options.set_from_config('hatarib_pause_osk', 'hatarib_pause', default='2')

        # Aspect Ratio
        core_options.set_from_config('hatarib_aspect', 'hatarib_ratio', default='0')

        # Borders
        core_options.set_from_config('hatarib_borders', 'hatarib_borders', default='0')

        # Harddrive image support
        rom_extension = self.rom.suffix.lower()
        if rom_extension == '.hd':
            core_options.set('hatarib_hardimg', 'hatarib/hdd')
            core_options.set('hatarib_hardboot', '1')
            core_options.set('hatarib_hard_readonly', '1')
            match self.config.get('hatarib_drive'):
                case 'ACSI':
                    core_options.set('hatarib_hardtype', '2')
                case 'SCSI':
                    core_options.set('hatarib_hardtype', '3')
                case _:
                    core_options.set('hatarib_hardtype', '4')
        elif rom_extension == '.gemdos':
            core_options.set('hatarib_hardimg', 'hatarib/hdd')
            core_options.set('hatarib_hardboot', '1')
            core_options.set('hatarib_hardtype', '0')
            core_options.set('hatarib_hard_readonly', '0')
        else:
            core_options.set('hatarib_hardimg', None)
            core_options.set('hatarib_hardtype', '0')
            core_options.set('hatarib_hardboot', '0')
            core_options.set('hatarib_hard_readonly', '1')
