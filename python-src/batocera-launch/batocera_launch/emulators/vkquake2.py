from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext, cached_dataclass, cached_property

_SOURCE_DIR: Final = Path('/usr/bin/vkquake2')


@cached_dataclass
class VKQuake2(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'vkquake2',
            'keys': {'exit': 'KEY_F10', 'save_state': 'KEY_F6', 'restore_state': 'KEY_F7'},
        }

    @property
    def execution_path(self) -> Path | None:
        return self.roms_dir

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.resolution.width / self.resolution.height > ((16.0 / 9.0) - 0.1) else 4 / 3

    async def configure(self) -> Command:
        if not _SOURCE_DIR.exists():
            raise BatoceraException(f'Source directory {_SOURCE_DIR} does not exist.')

        shutil.copytree(_SOURCE_DIR, self.roms_dir, dirs_exist_ok=True, copy_function=shutil.copy2)

        args: list[str | Path] = [self.roms_dir / 'quake2']
        rom_name = self.rom.name.lower()

        if 'zero' in rom_name:
            args.extend(['+set', 'game', 'rogue'])
        if 'reckoning' in rom_name:
            args.extend(['+set', 'game', 'xatrix'])
        if 'zaero' in rom_name:
            args.extend(['+set', 'game', 'zaero'])
        if 'destruction' in rom_name:
            args.extend(['+set', 'game', 'smd'])

        return Command(args, env={'SDL_JOYSTICK_HIDAPI': '0'})
