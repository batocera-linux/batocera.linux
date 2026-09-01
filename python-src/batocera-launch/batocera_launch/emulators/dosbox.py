from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
)

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class DosBox(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dosbox',
            'keys': {'exit': ['KEY_LEFTCTRL', 'KEY_F9']},
        }

    async def configure(self) -> Command:
        bat_file = self.rom / 'dosbox.bat'
        game_conf_file = self.rom / 'dosbox.cfg'

        self.config_dir.mkdir(parents=True, exist_ok=True)

        ini_settings = CaseSensitiveConfigParser(interpolation=None)

        # Use a separate file from dosbox.conf to avoid overwriting by dosbox
        custom_config_path = self.config_dir / 'dosbox-custom.conf'
        if custom_config_path.exists():
            ini_settings.read(custom_config_path)

        if not ini_settings.has_section('sdl'):
            ini_settings.add_section('sdl')
        ini_settings.set('sdl', 'output', 'opengl')

        if not ini_settings.has_section('cpu'):
            ini_settings.add_section('cpu')

        ini_settings.set('cpu', 'core', self.config.get_str('dosbox_cpu_core', 'auto'))
        ini_settings.set('cpu', 'cputype', self.config.get_str('dosbox_cpu_cputype', 'auto'))
        ini_settings.set('cpu', 'cycles', self.config.get_str('dosbox_cpu_cycles', 'auto'))

        with custom_config_path.open('w') as config:
            ini_settings.write(config)

        args: list[str | Path] = [
            '/usr/bin/dosbox',
            '-fullscreen',
            # This loads self.config_dir / dosbox.conf
            '-userconf',
            '-exit',
            bat_file,
            '-c',
            f'set ROOT={self.rom}',
        ]

        if game_conf_file.exists():
            # Then load game_conf_file if it exists
            args.extend(['-conf', game_conf_file])

        # Then load custom_config_path after all the others
        args.extend(['-conf', custom_config_path])

        return Command(args)
