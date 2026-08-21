from __future__ import annotations

import logging
from pathlib import Path
from shlex import split
from typing import Final

from batocera_common.paths import CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

_logger = logging.getLogger(__name__)

_IGNORE_CONFIG_KEYS: Final = {'FullScreenWidth', 'FullScreenHeight', 'JoystickEnabled'}
_DEFAULT_CONFIG: Final = """\
Vid_FullScreen = 1;
Vid_Aspect = 0;
Vid_Vsync = 1;
QuitOnEscape = 1;
"""


@cached_dataclass
class ECWolf(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ecwolf',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F8',
                'restore_state': 'KEY_F9',
            },
        }

    @property
    def saves_path(self) -> Path:
        return SAVES / 'ecwolf' / self.rom.name

    @property
    def execution_path(self) -> Path | None:
        return self._launch_info[0]

    @cached_property
    def _launch_info(self) -> tuple[Path | None, list[str]]:
        if self.rom.is_dir():
            return self.rom, []

        extra: list[str] = []
        cwd: Path | None = None
        suffix = self.rom.suffix.lower()

        if self.rom.is_file():
            cwd = self.rom.parent

            if suffix == '.ecwolf':
                extra = split(self.rom.read_text())

                # If first parameter isn't an argument then assume it's a path
                if extra and '--' not in extra[0]:
                    dataset_dir = Path(extra[0])
                    extra = extra[1:]
                    if dataset_dir.is_dir():
                        cwd = dataset_dir
                    else:
                        _logger.error("Error: couldn't go into directory %s", dataset_dir)

            elif suffix == '.pk3':
                extra = ['--file', self.rom.name]

        return cwd, extra

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.saves_path.mkdir(parents=True, exist_ok=True)

        config_file = self.config_dir / 'ecwolf.cfg'

        if not config_file.is_file():
            config_file.write_text(_DEFAULT_CONFIG)

        lines = [
            line
            for line in config_file.read_text().splitlines(keepends=True)
            if not _IGNORE_CONFIG_KEYS.intersection(line.split())
        ]
        lines.extend(
            [
                'JoystickEnabled = 1;\n',
                f'FullScreenWidth = {self.resolution.width};\n',
                f'FullScreenHeight = {self.resolution.height};\n',
            ]
        )
        config_file.write_text(''.join(lines))

        return Command(
            ['ecwolf', *self._launch_info[1], '--savedir', self.saves_path],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
            },
        )
