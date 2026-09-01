from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
)

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class DosBoxx(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dosboxx',
            'keys': {'exit': ['KEY_LEFTCTRL', 'KEY_F9']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'dosbox'

    async def configure(self) -> Command:
        game_conf_file = self.rom / 'dosbox.cfg'
        config_file = game_conf_file if game_conf_file.is_file() else (self.config_dir / 'dosboxx.conf')

        self.config_dir.mkdir(parents=True, exist_ok=True)

        ini_settings = CaseSensitiveConfigParser(interpolation=None)
        custom_config_file = self.config_dir / 'dosboxx-custom.conf'

        # Copy config file to custom config file to avoid overwriting by dosbox-x
        if config_file.exists():
            shutil.copy2(config_file, custom_config_file)
            ini_settings.read(custom_config_file)

        if not ini_settings.has_section('sdl'):
            ini_settings.add_section('sdl')
        ini_settings.set('sdl', 'output', 'opengl')

        with custom_config_file.open('w') as config:
            ini_settings.write(config)

        # -fullscreen removed as it crashes on N2
        args: list[str | Path] = ['/usr/bin/dosbox-x', '-exit']

        autoexec_file = self.rom / 'dosbox.aut'
        if autoexec_file.exists():
            # Read dosbox.aut and append it to the custom config file
            with custom_config_file.open('a+') as f1:
                f1.write(autoexec_file.read_text())

            # Setting the defaultdir to the rom dir.
            # This way we can use relative paths to the rom directory
            # in dosbox.auto
            args.extend(['-defaultdir', str(self.rom)])
        else:
            # Otherwise, mount the rom directory as c: and run dosbox.bat
            args.extend(
                [
                    '-c',
                    f'mount c {self.rom}',
                    '-c',
                    'c:',
                    '-c',
                    'dosbox.bat',
                ]
            )

        args.extend(['-fastbioslogo', '-conf', str(custom_config_file)])

        return Command(args, env={'XDG_CONFIG_HOME': CONFIGS})
