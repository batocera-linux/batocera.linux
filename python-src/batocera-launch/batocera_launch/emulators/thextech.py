from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class TheXTech(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'thextech',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'menu': 'KEY_ENTER', 'pause': 'KEY_ENTER'},
        }

    async def configure(self) -> Command:
        args: list[str | Path] = ['/usr/bin/thextech', '-u', self.saves_dir]

        if rendering_mode := self.config.get_str('rendering_mode'):
            args.extend(['-r', rendering_mode])

        args.append(self.config.get_bool('frameskip', True, return_values=('--frameskip', '--no-frameskip')))
        args.extend(['-c', f'{self.rom}/'])

        return Command(args)
