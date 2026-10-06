from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)


@cached_dataclass
class CatacombGL(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'catacombgl',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': ['KEY_F3'],
                'restore_state': ['KEY_F4'],
                'menu': 'KEY_ESC',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'CatacombGL'

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'CatacombGL'

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        self.saves_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Path to the ini file
        config_file = self.config_dir / 'CatacombGL.ini'

        # Check if the ini file exists, and if not, create and adjust it
        if not config_file.exists():
            _logger.debug('CatacombGL.ini not found, creating the file.')
            config_file.touch()  # Create the file if it doesn't exist

        # Define the paths to be added or adjusted in the ini file
        required_paths = {
            'pathabyssv113': self.roms_dir / 'Abyss_sw13',
            'pathabyssv124': self.roms_dir / 'Abyss',
            'patharmageddonv102': self.roms_dir / 'Armageddon',
            'pathapocalypsev101': self.roms_dir / 'Apocalypse',
            'pathcatacomb3dv122': self.roms_dir / 'Cat3D',
            'screenmode': 'fullscreen',
            'WindowedScreenWidth': str(self.resolution.width),
            'WindowedScreenHeight': str(self.resolution.height),
        }

        # Read the existing file content
        ini_content = config_file.read_text().splitlines() if config_file.exists() else []
        ini_dict: dict[str, str | Path] = {
            line.split('=')[0]: line.split('=')[1] for line in ini_content if '=' in line
        }
        ini_dict.update(required_paths)

        # Update or add required paths
        with config_file.open('w') as ini_file:
            for key, value in ini_dict.items():
                ini_file.write(f'{key}={value}\n')

        # Run command
        args = ['/usr/bin/CatacombGL', '--savedir', self.saves_dir]

        # Version
        rom_file_name = self.rom.id.lower()

        # Check and extend the command array with specific arguments
        for keyword, argument in {
            'abyss': '--abyss',
            'abyss_sw13': '--abyss_sw13',
            'descent': '--descent',
            'cat3d': '--descent',
            'armageddon': '--armageddon',
            'apocalypse': '--apocalypse',
        }.items():
            if keyword in rom_file_name:
                _logger.debug('Version requested: %s', keyword)
                args.append(argument)

        return Command(args, env={'SDL_JOYSTICK_HIDAPI': '0'})
