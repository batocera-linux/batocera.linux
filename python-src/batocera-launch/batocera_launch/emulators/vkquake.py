from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class VKQuake(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'vkquake',
            'keys': {'exit': 'KEY_F10', 'save_state': 'KEY_F6', 'restore_state': 'KEY_F9'},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.resolution.width / self.resolution.height > ((16.0 / 9.0) - 0.1) else 4 / 3

    async def configure(self) -> Command:
        args: list[str | Path] = ['/usr/bin/vkquake', '-basedir', self.roms_dir]
        rom_name = self.rom.name.lower()

        if 'scourge' in rom_name:
            args.append('-hipnotic')
        if 'dissolution' in rom_name:
            args.append('-rogue')

        return Command(args, env={'SDL_JOYSTICK_HIDAPI': '0'})
