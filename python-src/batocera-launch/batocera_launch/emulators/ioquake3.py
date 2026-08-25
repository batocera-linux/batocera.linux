from __future__ import annotations

import shutil
import stat
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, ROMS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from collections.abc import Iterable

_SOURCE_DIR: Final = Path('/usr/bin/ioquake3')

# basic controller config
_CONTROLS: Final = (
    'bind PAD0_A "+moveup"\n',
    'bind PAD0_X "+movedown"\n',
    'bind PAD0_Y "+button2"\n',
    'bind PAD0_LEFTSHOULDER "weapnext"\n',
    'bind PAD0_RIGHTSHOULDER "weapprev"\n',
    'bind PAD0_LEFTSTICK_LEFT "+moveleft"\n',
    'bind PAD0_LEFTSTICK_RIGHT "+moveright"\n',
    'bind PAD0_LEFTSTICK_UP "+forward"\n',
    'bind PAD0_LEFTSTICK_DOWN "+back"\n',
    'bind PAD0_RIGHTSTICK_LEFT "+left"\n',
    'bind PAD0_RIGHTSTICK_RIGHT "+right"\n',
    'bind PAD0_RIGHTSTICK_UP "+lookup"\n',
    'bind PAD0_RIGHTSTICK_DOWN "+lookdown"\n',
    'bind PAD0_LEFTTRIGGER "+speed"\n',
    'bind PAD0_RIGHTTRIGGER "+attack"\n',
)


@cached_dataclass
class IOQuake3(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ioquake3',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': ['KEY_LEFTSHIFT', 'KEY_ESC'],
            },
        }

    @cached_property
    def roms_dir(self) -> Path:
        return ROMS / 'quake3'

    @cached_property
    def config_dir(self) -> Path:
        # Shared by ioquake3 and vkquake3 entry points.
        return CONFIGS / 'ioquake3'

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.resolution.width / self.resolution.height > ((16.0 / 9.0) - 0.1) else 4 / 3

    def _write_cfg_file(
        self,
        filename: Path,
        init_line: str,
        defaults: Iterable[str],
        controls: Iterable[str],
        /,
    ) -> None:
        if not filename.is_file():
            filename.parent.mkdir(parents=True, exist_ok=True)
            with filename.open('w') as file:
                file.write(init_line)
                file.writelines(defaults)
                file.write(f'seta com_hunkMegs "{self.config.get_str("ioquake3_mem", "256")}"\n')
                if self.core == 'vkquake3':
                    file.write(f'seta cl_renderer "{self.config.get_str("vkquake3_api", "opengl2")}"\n')
                file.writelines(controls)
            return

        with filename.open('r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            for line in lines:
                ## Set defaults every time
                # resolution
                if line.startswith('seta r_mode'):
                    line = 'seta r_mode "-1"\n'
                elif line.startswith('seta r_customwidth'):
                    line = f'seta r_customwidth "{self.resolution.width}"\n'
                elif line.startswith('seta r_customheight'):
                    line = f'seta r_customheight "{self.resolution.height}"\n'
                # controllers
                elif line.startswith('seta in_joystickUseAnalog'):
                    line = 'seta in_joystickUseAnalog "1"\n'
                elif line.startswith('seta in_joystick'):
                    line = 'seta in_joystick "1"\n'
                # network downloads
                elif line.startswith('seta cl_allowDownload'):
                    line = 'seta cl_allowDownload "1"\n'
                ## User options
                # Memory
                elif line.startswith('seta com_hunkMegs'):
                    line = f'seta com_hunkMegs "{self.config.get_str("ioquake3_mem", "256")}"\n'
                # API
                elif line.startswith('seta cl_renderer'):
                    if self.core == 'vkquake3':
                        line = f'seta cl_renderer "{self.config.get_str("vkquake3_api", "opengl2")}"\n'
                    else:
                        # ioquake3 doesn't use this, so remove it if a vkquake3 setting gets added
                        continue

                file.write(line)

            # Add the missing lines at the end of the file
            for line in defaults:
                if line not in lines:
                    file.write(line)
            for line in controls:
                if line not in lines:
                    file.write(line)

    def _write_cfg_files(self) -> None:
        # create the cfg files for each quake3 rom / mod folder
        # minimum defaults
        defaults = [
            'seta r_mode "-1"\n',
            f'seta r_customwidth "{self.resolution.width}"\n',
            f'seta r_customheight "{self.resolution.height}"\n',
            'seta in_joystickUseAnalog "1"\n',
            'seta in_joystick "1"\n',
            'seta cl_allowDownload "1"\n',
        ]

        if not self.roms_dir.is_dir():
            return

        # get the immediate subdirectories within rom directory
        for subdirectory in (path.name for path in self.roms_dir.iterdir() if path.is_dir()):
            self._write_cfg_file(
                self.config_dir / subdirectory / 'q3config.cfg',
                '// generated by quake, do not modify\n',
                defaults,
                _CONTROLS,
            )

    async def configure(self) -> Command:
        self._write_cfg_files()

        # ioquake3 looks for folder either in config or from where it's launched
        binary = self.roms_dir / 'ioquake3'
        source_file = _SOURCE_DIR / 'ioquake3'

        # therefore copy latest ioquake3 file to rom directory
        if not binary.is_file() or source_file.stat().st_mtime > binary.stat().st_mtime:
            shutil.copytree(_SOURCE_DIR, self.roms_dir, dirs_exist_ok=True)

            # Mark the copied executable file as executable (chmod +x)
            if binary.is_file():
                binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # get the game / mod to launch
        command_line = self.rom.read_text().splitlines()[0].strip().split()
        return Command([binary, *command_line])
