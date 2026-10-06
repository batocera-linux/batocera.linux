from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from batocera_common.asyncio import run
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch import Command, Emulator, HotkeysContext

_logger = logging.getLogger(__name__)

_ARCHIVE_SUFFIXES: Final = {'.zip', '.7z'}
_DISK_SUFFIXES: Final = {'.rom', '.dsk', '.cas', '.ccc', '.wav'}
_DEFAULT_MACHINES: Final = {'mc10': 'mc10', 'dragon64': 'dragon64'}


@cached_dataclass
class Xroar(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'xroar',
            'keys': {'exit': ['KEY_LEFTCTRL', 'KEY_Q']},
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 4 / 3

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        conf_file = self.config_dir / 'xroar.conf'

        default_machine = _DEFAULT_MACHINES.get(self.system, 'coco2bus')
        lines = [
            f'rompath {BIOS / "xroar"}',
            f'default-machine {self.config.get_str("xroar_machine", default_machine)}',
            'ao-volume 100',
        ]

        if self.config.get_bool('xroar_cartauto'):
            lines.append('cart-autorun')
        if self.config.get_bool('xroar_vsync'):
            lines.append('vo-vsync')
        if ram := self.config.get_str('xroar_ram'):
            lines.append(f'ram {ram}')
        if tv_type := self.config.get_str('xroar_tv_type'):
            lines.append(f'tv-type {tv_type}')
        if tv_input := self.config.get_str('xroar_tv_input'):
            lines.append(f'tv-input {tv_input}')
        if self.config.get_bool('xroar_kbd_translate'):
            lines.append('kbd-translate')

        lines.append('fs')
        conf_file.write_text('\n'.join(lines) + '\n')

        rom_path: str | Path = self.rom
        if self.rom.suffix.lower() in _ARCHIVE_SUFFIXES:
            try:
                proc = await run('batocera-xtract', 'l', self.rom, text=True)
                if proc.returncode == 10:
                    for line in proc.stdout.splitlines():
                        if Path(line).suffix.lower() in _DISK_SUFFIXES:
                            await run('batocera-xtract', 'pyx', self.rom, '/tmp', line, check=True)
                            rom_path = Path('/tmp') / line
                            break

                if rom_path == self.rom:
                    raise RuntimeError("Can't find a matching file in archive")
            except Exception:
                _logger.exception('7z error')

        return Command(
            ['xroar', '-c', conf_file, rom_path],
            env={'SDL_JOYSTICK_HIDAPI': '0'},
        )
