from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from batocera_common.paths import CONFIGS, ROMS

from .base import FalloutBase

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_common.configparser import CaseSensitiveConfigParser


@dataclass(slots=True)
class Fallout2(FalloutBase):
    CONFIG_DIR: ClassVar[Path] = CONFIGS / 'fallout2'
    ROM_DIR: ClassVar[Path] = ROMS / 'fallout2-ce'

    CONFIG_FILE_NAME: ClassVar[str] = 'fallout2.cfg'
    INI_FILE_NAME: ClassVar[str] = 'f2_res.ini'
    EXE_NAME: ClassVar[str] = 'fallout2-ce'

    SOUND_PATH: ClassVar[str] = 'sound/music/'
    CONFIG_PREFIX: ClassVar[str] = 'fout2'

    def _modify_ini_file(self, ini: CaseSensitiveConfigParser, /) -> None:
        # fix path
        ini.set('MAIN', 'f2_res_patches', 'data/')
