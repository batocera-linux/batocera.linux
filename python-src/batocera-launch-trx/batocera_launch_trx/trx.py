from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from batocera_launch.command import Command
from batocera_launch.emulator import Emulator
from batocera_launch.functools import cached_property

if TYPE_CHECKING:
    from batocera_launch.types import HotkeysContext

_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TRX(Emulator):
    needs_sdl_game_controller_config = True

    @property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'trx',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'save_state': 'KEY_F5', 'restore_state': 'KEY_F6'},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.resolution.width / self.resolution.height > ((16.0 / 9.0) - 0.1) else 4 / 3

    def configure(self, prepared_rom: Path, /) -> Command:
        rom_dir = prepared_rom.parent
        config_path = rom_dir / 'cfg' / 'TRX.json5'
        source_path = Path('/usr/bin/trx')

        # Copy files & folders if they don't exist
        for item in source_path.iterdir():
            dest = rom_dir / item.name
            try:
                if item.is_dir():
                    if not dest.exists():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        for sub_item in item.rglob('*'):
                            sub_dest = dest / sub_item.relative_to(item)
                            if sub_item.is_dir():
                                sub_dest.mkdir(parents=True, exist_ok=True)
                            else:
                                shutil.copy2(sub_item, sub_dest)
                else:
                    shutil.copy2(item, dest)
            except PermissionError as e:
                _logger.debug('Permission error while copying %s -> %s: %s', item, dest, e)
            except Exception as e:
                _logger.debug('Error copying %s -> %s: %s', item, dest, e)

        # Configuration
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_data: dict[str, Any] = {}

        if config_path.exists():
            try:
                config_data = json.loads(config_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError:
                _logger.debug('Invalid JSON format in %s, overwriting with default settings.', config_path)

        # Update settings
        config_data.update({'is_fullscreen': True, 'width': self.resolution.width, 'height': self.resolution.height})

        config_path.write_text(json.dumps(config_data, indent=2), encoding='utf-8')

        return Command([rom_dir / 'trx'], {'SDL_JOYSTICK_HIDAPI': '0'})
