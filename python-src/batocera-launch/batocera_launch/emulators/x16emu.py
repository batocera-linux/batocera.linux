from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.paths import BIOS, CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class X16emu(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'x16emu',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.config.get_str('x16emu_ratio') == '16:9' else 4 / 3

    async def configure(self) -> Command:
        rom_dir = self.rom.parent
        args: list[str | Path] = [
            'x16emu',
            '-rom',
            BIOS / 'commanderx16' / 'rom.bin',
            '-fsroot',
            rom_dir,
            '-ram',
            '2048',
            '-rtc',
        ]

        if self.rom.suffix == '.img':
            args.extend(['-sdcard', self.rom])
        elif self.rom.suffix == '.bas':
            args.extend(['-bas', self.rom])
        else:
            args.extend(['-prg', self.rom, '-run'])

        autorun_cmd = rom_dir / 'autorun.cmd'
        if autorun_cmd.exists():
            args.extend(['-bas', autorun_cmd])

        args.extend(['-scale', self.config.get_str('x16emu_scale', '2')])

        if quality := self.config.get_str('x16emu_quality'):
            args.extend(['-quality', quality])

        if self.config.get_str('x16emu_ratio') == '16:9':
            args.append('-widescreen')

        for nplayer, _ in enumerate(self.controllers[:4], start=1):
            args.append(f'-joy{nplayer}')

        return Command(
            args,
            env={
                'XDG_DATA_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
