from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_launch.command import Command
from batocera_launch.emulator import Emulator

if TYPE_CHECKING:
    from batocera_launch.types import HotkeysContext


@dataclass(slots=True)
class FalloutBase(Emulator):
    needs_sdl_game_controller_config = True

    CONFIG_DIR: ClassVar[Path]
    ROM_DIR: ClassVar[Path]

    CONFIG_FILE_NAME: ClassVar[str]
    INI_FILE_NAME: ClassVar[str]
    EXE_NAME: ClassVar[str]

    SOUND_PATH: ClassVar[str]
    CONFIG_PREFIX: ClassVar[str]

    @property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'fallout1' if self.system == 'fallout1-ce' else 'fallout2',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F7',
            },
        }

    @property
    def execution_path(self) -> Path:
        return self.ROM_DIR

    @property
    def needs_mouse(self) -> bool:
        return True

    def _modify_config_file(self, cfg: CaseSensitiveConfigParser, /) -> None:
        pass

    def _modify_ini_file(self, ini: CaseSensitiveConfigParser, /) -> None:
        pass

    def configure(self, prepared_rom: Path, /) -> Command:
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        ROM_BIN_FILE = self.ROM_DIR / self.EXE_NAME
        SRC_BIN_FILE = Path('/usr/bin') / self.EXE_NAME

        # Copy latest binary to the rom directory
        if not ROM_BIN_FILE.exists() or SRC_BIN_FILE.stat().st_mtime > ROM_BIN_FILE.stat().st_mtime:
            shutil.copy(SRC_BIN_FILE, ROM_BIN_FILE)

        CONFIG_FILE = self.CONFIG_DIR / self.CONFIG_FILE_NAME
        SRC_CONFIG = self.ROM_DIR / self.CONFIG_FILE_NAME
        # Copy cfg file to the config directory
        if not CONFIG_FILE.exists() and SRC_CONFIG.exists():
            shutil.copy(SRC_CONFIG, CONFIG_FILE)

        INI_FILE = self.CONFIG_DIR / self.INI_FILE_NAME
        SRC_INI = self.ROM_DIR / self.INI_FILE_NAME
        # Now copy the ini file to the config directory
        if not INI_FILE.exists() and SRC_INI.exists():
            shutil.copy(SRC_INI, INI_FILE)

        ## Configure

        ## CFG Configuration
        cfg = CaseSensitiveConfigParser()
        if CONFIG_FILE.exists():
            cfg.read(CONFIG_FILE)

        if not cfg.has_section('debug'):
            cfg.add_section('debug')
        if not cfg.has_section('preferences'):
            cfg.add_section('preferences')
        if not cfg.has_section('sound'):
            cfg.add_section('sound')
        if not cfg.has_section('system'):
            cfg.add_section('system')

        # fix linux path issues
        cfg.set('sound', 'music_path1', self.SOUND_PATH)
        cfg.set('sound', 'music_path2', self.SOUND_PATH)

        self._modify_config_file(cfg)

        cfg.set('preferences', 'game_difficulty', self.config.get(f'{self.CONFIG_PREFIX}_game_difficulty', '1'))
        cfg.set('preferences', 'combat_difficulty', self.config.get(f'{self.CONFIG_PREFIX}_combat_difficulty', '1'))
        cfg.set('preferences', 'violence_level', self.config.get(f'{self.CONFIG_PREFIX}_violence_level', '2'))
        cfg.set('preferences', 'subtitles', self.config.get(f'{self.CONFIG_PREFIX}_subtitles', '0'))
        cfg.set('system', 'language', self.config.get(f'{self.CONFIG_PREFIX}_language', 'english'))

        with CONFIG_FILE.open('w') as configfile:
            cfg.write(configfile)

        ## INI Configuration
        ini = CaseSensitiveConfigParser()
        if INI_FILE.exists():
            ini.read(INI_FILE)

        # [MAIN]
        if not ini.has_section('MAIN'):
            ini.add_section('MAIN')

        # Note: This will increase the minimum resolution to from 640x480 to 1280x960.
        ini.set('MAIN', 'SCALE_2X', '1' if self.resolution.width >= 1280 and self.resolution.height >= 960 else '0')
        ini.set('MAIN', 'SCR_WIDTH', f'{self.resolution.width}')
        ini.set('MAIN', 'SCR_HEIGHT', f'{self.resolution.height}')

        # fullscreen
        ini.set('MAIN', 'WINDOWED', '0')

        self._modify_ini_file(ini)

        with INI_FILE.open('w') as configfile:
            ini.write(configfile)

        return Command([ROM_BIN_FILE])
