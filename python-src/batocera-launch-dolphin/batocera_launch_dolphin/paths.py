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

from typing import Final

from batocera_common.paths import BIOS, CONFIGS, SAVES

# These deliberately don't match the emulator's own launch name ("dolphin") - kept
# as their own historical directory name ("dolphin-emu") so existing users' saved
# settings aren't silently relocated.
DOLPHIN_CONFIG: Final = CONFIGS / 'dolphin-emu'
DOLPHIN_INI: Final = DOLPHIN_CONFIG / 'Dolphin.ini'
DOLPHIN_GFX_INI: Final = DOLPHIN_CONFIG / 'GFX.ini'
DOLPHIN_QT_INI: Final = DOLPHIN_CONFIG / 'Qt.ini'

DOLPHIN_SAVES: Final = SAVES / 'dolphin-emu'
DOLPHIN_SYSCONF: Final = DOLPHIN_SAVES / 'Wii' / 'shared2' / 'sys' / 'SYSCONF'

DOLPHIN_BIOS: Final = BIOS / 'GC'
