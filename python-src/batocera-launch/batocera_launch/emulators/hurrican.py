from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.paths import ROMS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_ROM_DIR: Final = ROMS / 'hurrican'


@cached_dataclass
class Hurrican(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'hurrican',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def execution_path(self) -> Path | None:
        return _ROM_DIR

    async def configure(self) -> Command:
        if not (_ROM_DIR / 'data' / 'levels').is_dir():
            _logger.error('ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.')

        return Command(['hurrican'])
