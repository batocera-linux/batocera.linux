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

from pathlib import Path
from typing import Final

from batocera_common.paths import CONFIGS

PID_FILE: Final = Path('/var/run/hotkeygen.pid')
CONTEXT_FILE: Final = Path('/var/run/hotkeygen.state')

CONFIG_USERDIR: Final = CONFIGS / 'hotkeygen'
CONFIG_SYSTEMDIR: Final = Path('/usr/share/hotkeygen')
CONFIG_DEFAULTDIR: Final = Path('/etc/hotkeygen')

SYSTEM_DEFAULT_MAPPING: Final = CONFIG_DEFAULTDIR / 'default_mapping.conf'

DEVICE_NAME: Final = 'batocera hotkeys'
