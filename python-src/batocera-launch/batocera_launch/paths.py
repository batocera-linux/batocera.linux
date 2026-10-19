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

from batocera_common.paths import BATOCERA_SHARE_DIR, CONFIGS, HOME, USERDATA

DATAINIT_DIR: Final = BATOCERA_SHARE_DIR / 'datainit'

HOME_INIT: Final = DATAINIT_DIR / 'system'
CONF_INIT: Final = HOME_INIT / 'configs'

EVMAPY: Final = CONFIGS / 'evmapy'
EVMAPY_SHARE_DIR: Final = Path('/usr/share/evmapy')

LAUNCH_SHARE_DIR: Final = BATOCERA_SHARE_DIR / 'launch'
LAUNCH_DATA_DIR: Final = LAUNCH_SHARE_DIR / 'data'
LAUNCH_DEFAULTS_DIR: Final = LAUNCH_SHARE_DIR / 'defaults'

USER_ES_DIR: Final = CONFIGS / 'emulationstation'
SYSTEM_ES_DIR: Final = Path('/usr/share/emulationstation')

ES_SETTINGS: Final = USER_ES_DIR / 'es_settings.cfg'
# written by ES at each launch with the configs it resolved for the players
ES_PLAYERS_INPUT: Final = Path('/tmp/es_input_players.cfg')

ES_RESOURCES_DIR: Final = SYSTEM_ES_DIR / 'resources'

ES_GUNS_METADATA: Final = ES_RESOURCES_DIR / 'gungames.xml'
ES_WHEELS_METADATA: Final = ES_RESOURCES_DIR / 'wheelgames.xml'
ES_GAMES_METADATA: Final = ES_RESOURCES_DIR / 'gamesdb.xml'
ES_GUNS_ART_METADATA: Final = LAUNCH_DATA_DIR / 'gamesbuttonsdb.xml'

USER_SHADERS: Final = USERDATA / 'shaders'
BATOCERA_SHADERS: Final = BATOCERA_SHARE_DIR / 'shaders'

USER_DECORATIONS: Final = USERDATA / 'decorations'
SYSTEM_DECORATIONS: Final = DATAINIT_DIR / 'decorations'

USER_SCRIPTS: Final = HOME / 'scripts'

PRECALIBRATION_DIR: Final = BATOCERA_SHARE_DIR / 'guns-precalibrations'


def configure_emulator(rom: Path, /) -> bool:
    return str(rom) == 'config'
