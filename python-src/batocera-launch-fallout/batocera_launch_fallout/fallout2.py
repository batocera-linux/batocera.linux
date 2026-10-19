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

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS

from .base import FalloutBase

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_common.configparser import CaseSensitiveConfigParser


@cached_dataclass
class Fallout2(FalloutBase):
    CONFIG_FILE_NAME: ClassVar[str] = 'fallout2.cfg'
    INI_FILE_NAME: ClassVar[str] = 'f2_res.ini'
    EXE_NAME: ClassVar[str] = 'fallout2-ce'

    SOUND_PATH: ClassVar[str] = 'sound/music/'
    CONFIG_PREFIX: ClassVar[str] = 'fout2'

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'fallout2'

    def _modify_ini_file(self, ini: CaseSensitiveConfigParser, /) -> None:
        # fix path
        ini.set('MAIN', 'f2_res_patches', 'data/')
