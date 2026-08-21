from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.paths import ROMS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_DATA_DIR: Final = ROMS / 'tyrian' / 'data'


@cached_dataclass
class Tyrian(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'tyrian',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def data_dir(self) -> Path:
        return self.roms_dir / 'data'

    @property
    def execution_path(self) -> Path | None:
        return self.data_dir

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        if not self.data_dir.is_dir():
            _logger.error('ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.')

        return Command(['opentyrian'])
