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

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.paths import CONFIGS
from batocera_launch_libretro import Core


class HatariConfigMixin(Core):
    def generate_special_configs(self) -> None:
        super().generate_special_configs()

        # Create/update hatari.cfg
        if self.system == 'atarist':
            hatari_conf = CONFIGS / 'hatari' / 'hatari.cfg'
            hatari_config = CaseSensitiveConfigParser(interpolation=None)

            if hatari_conf.exists():
                hatari_config.read(hatari_conf)

            # update the configuration file
            hatari_conf.parent.mkdir(parents=True, exist_ok=True)
            with hatari_conf.open('w') as configfile:
                hatari_config.write(configfile)
