from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from batocera_common.paths import CONFIGS, ROMS

from .base import FalloutBase

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_common.configparser import CaseSensitiveConfigParser


@dataclass(slots=True)
class Fallout1(FalloutBase):
    CONFIG_DIR: ClassVar[Path] = CONFIGS / 'fallout1'
    ROM_DIR: ClassVar[Path] = ROMS / 'fallout1-ce'

    CONFIG_FILE_NAME: ClassVar[str] = 'fallout.cfg'
    INI_FILE_NAME: ClassVar[str] = 'f1_res.ini'
    EXE_NAME: ClassVar[str] = 'fallout1-ce'

    SOUND_PATH: ClassVar[str] = 'DATA/SOUND/MUSIC/'
    CONFIG_PREFIX: ClassVar[str] = 'fout1'

    def _modify_config_file(self, cfg: CaseSensitiveConfigParser, /) -> None:
        cfg.set('system', 'critter_dat', 'CRITTER.DAT')
        cfg.set('system', 'critter_patches', 'DATA')
        cfg.set('system', 'master_dat', 'MASTER.DAT')
        cfg.set('system', 'master_patches', 'DATA')
