from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS

from .base import FalloutBase

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_common.configparser import CaseSensitiveConfigParser


@cached_dataclass
class Fallout1(FalloutBase):
    CONFIG_FILE_NAME: ClassVar[str] = 'fallout.cfg'
    INI_FILE_NAME: ClassVar[str] = 'f1_res.ini'
    EXE_NAME: ClassVar[str] = 'fallout1-ce'

    SOUND_PATH: ClassVar[str] = 'DATA/SOUND/MUSIC/'
    CONFIG_PREFIX: ClassVar[str] = 'fout1'

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'fallout1'

    def _modify_config_file(self, cfg: CaseSensitiveConfigParser, /) -> None:
        cfg.set('system', 'critter_dat', 'CRITTER.DAT')
        cfg.set('system', 'critter_patches', 'DATA')
        cfg.set('system', 'master_dat', 'MASTER.DAT')
        cfg.set('system', 'master_patches', 'DATA')
