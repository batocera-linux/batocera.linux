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

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import BatoceraException
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_ASSET_DIRS: Final = [
    'music/world/Standard',
    'music/game/Standard/Special',
    'music/game/Standard/Menu',
    'filters',
    'worlds/KingdomHigh',
    'worlds/MrIsland',
    'worlds/Sky World',
    'worlds/Smb3',
    'worlds/Simple',
    'worlds/screenshots',
    'worlds/Flurry World',
    'worlds/MixedRiver',
    'worlds/Contest',
    'gfx/skins',
    'gfx/packs/Retro/fonts',
    'gfx/packs/Retro/modeobjects',
    'gfx/packs/Retro/eyecandy',
    'gfx/packs/Retro/awards',
    'gfx/packs/Retro/powerups',
    'gfx/packs/Retro/menu',
    'gfx/packs/Classic/projectiles',
    'gfx/packs/Classic/fonts',
    'gfx/packs/Classic/modeobjects',
    'gfx/packs/Classic/world',
    'gfx/packs/Classic/world/thumbnail',
    'gfx/packs/Classic/world/preview',
    'gfx/packs/Classic/modeskins',
    'gfx/packs/Classic/hazards',
    'gfx/packs/Classic/blocks',
    'gfx/packs/Classic/backgrounds',
    'gfx/packs/Classic/tilesets/SMB2',
    'gfx/packs/Classic/tilesets/Expanded',
    'gfx/packs/Classic/tilesets/SMB1',
    'gfx/packs/Classic/tilesets/Classic',
    'gfx/packs/Classic/tilesets/SMB3',
    'gfx/packs/Classic/tilesets/SuperMarioWorld',
    'gfx/packs/Classic/tilesets/YoshisIsland',
    'gfx/packs/Classic/eyecandy',
    'gfx/packs/Classic/awards',
    'gfx/packs/Classic/powerups',
    'gfx/packs/Classic/menu',
    'gfx/leveleditor',
    'gfx/docs',
    'sfx/packs/Classic',
    'sfx/announcer/Mario',
    'maps/tour',
    'maps/cache',
    'maps/screenshots',
    'maps/special',
    'tours',
]


@cached_dataclass
class Superbroswar(Core):
    @cached_property
    def rom_argument(self) -> str | Path | None:
        # super mario wars - verify assets from Content Downloader
        romdir = self.rom.absolute().parent

        if not all((romdir / assetdir).is_dir() for assetdir in _ASSET_DIRS):
            _logger.error('ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.')
            raise BatoceraException('Game assets not installed. You can get them from the Batocera Content Downloader.')

        return self.rom
