from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CACHE, CONFIGS, LOGS, SCREENSHOTS
from batocera_launch import (
    Command,
    Controller,
    Emulator,
    HotkeysContext,
)

if TYPE_CHECKING:
    from pathlib import Path

_EXTRA_DIR: Final = BIOS / 'scummvm' / 'extra'
_GAME_ID_RE: Final = re.compile(r'^(?:[a-z0-9-]+:)?[a-z0-9-]+$')
_ASPECT_STRETCH_MODES: Final = {'fit_force_aspect', 'pixel-perfect'}


@cached_dataclass
class ScummVM(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'scummvm',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': ['KEY_LEFTCTRL', 'KEY_F5'],
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3 if self.config.get('scumm_stretch') in _ASPECT_STRETCH_MODES else 16 / 9

    async def configure(self) -> Command:
        _EXTRA_DIR.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        config_file = self.config_dir / 'scummvm.ini'
        config = CaseSensitiveConfigParser(interpolation=None)
        if config_file.exists():
            config.read(config_file)

        if not config.has_section('scummvm'):
            config.add_section('scummvm')
        config.set('scummvm', 'gui_browser_native', 'false')

        with config_file.open('w') as file:
            config.write(file)

        # 1. If a .scummvm file exists and contains a valid <game id>, use the <game id>
        # 2. If an empty <game id>.scummvm file exists, use the <game id>
        # 3. Otherwise, auto detect the game
        if self.rom.is_dir():
            # squashfs: find a <game name>.scummvm file
            rom_file = next(self.rom.glob('*.scummvm'), None)
            rom_path = self.rom
        else:
            rom_file = self.rom
            rom_path = self.rom.parent

        target = '--auto-detect'
        if rom_file is not None:
            game_id = rom_file.read_text().strip().lower() or rom_file.stem
            if _GAME_ID_RE.match(game_id) is not None:
                target = game_id

        joystick_id = 0
        if pad := Controller.find_player_number(self.controllers, 1):
            joystick_id = pad.index

        args: list[str | Path] = [
            '/usr/bin/scummvm',
            '-f',
            f'--window-size={self.resolution.width},{self.resolution.height}',
            f'--scale-factor={self.config.get_str("scumm_scale", "3")}',
            f'--scaler={self.config.get_str("scumm_scaler_mode", "normal")}',
        ]

        if stretch := self.config.get_str('scumm_stretch'):
            args.append(f'--stretch-mode={stretch}')

        args.append(f'--renderer={self.config.get_str("scumm_renderer", "opengl")}')

        if language := self.config.get_str('scumm_language'):
            args.extend(['-q', language])

        args.extend(
            [
                f'--logfile={LOGS / "scummvm.log"}',
                f'--joystick={joystick_id}',
                f'--screenshotspath={SCREENSHOTS}',
                f'--extrapath={_EXTRA_DIR}',
                f'--savepath={self.saves_dir}',
                f'--path={rom_path}',
                target,
            ]
        )

        return Command(
            args,
            env={
                'SDL_VIDEODRIVER': 'wayland' if 'WAYLAND_DISPLAY' in os.environ else 'x11',
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
            },
        )
