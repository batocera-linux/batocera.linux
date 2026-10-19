# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch_libretro import Core

from ._hatari_core import HatariConfigMixin

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import LibretroConfig


@cached_dataclass
class Hatarib(HatariConfigMixin, Core):
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
        core_options.set_from_config('hatarib_emutos_region', 'hatarib_language', default='-1')

        # Monitor
        core_options.set_from_config('hatarib_monitor', default='1')

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
