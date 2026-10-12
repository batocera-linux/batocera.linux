from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_ROM_BINARIES: Final = {
    '.d1x': 'd1x-rebirth',
    '.d2x': 'd2x-rebirth',
}


@cached_dataclass
class DXXRebirth(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'dxx_rebirth',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_F2',
                'pause': 'KEY_F2',
                'save_state': ['KEY_LEFTALT', 'KEY_F2'],
                'restore_state': ['KEY_LEFTALT', 'KEY_LEFTSHIFT', 'KEY_F2'],
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @cached_property
    def rom_binary(self) -> str:
        if (dxx_rebirth := _ROM_BINARIES.get(self.rom.suffix)) is None:
            raise BatoceraException(f'Unknown rom type: {self.rom}')

        return dxx_rebirth

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / self.rom_binary

    async def configure(self) -> Command:
        config_file = self.config_dir / 'descent.cfg'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        options = {
            'ResolutionX': str(self.resolution.width),
            'ResolutionY': str(self.resolution.height),
            'WindowMode': '0',
            'VSync': self.config.get_str('rebirth_vsync', '0'),
            'TexFilt': self.config.get_str('rebirth_filtering', '0'),
            'TexAnisotropy': self.config.get_str('rebirth_anisotropy', '0'),
            'Multisample': self.config.get_str('rebirth_multisample', '0'),
        }

        lines = config_file.read_text().splitlines() if config_file.is_file() else []
        found: set[str] = set()
        for i, line in enumerate(lines):
            key = line.split('=', 1)[0]
            if key in options:
                lines[i] = f'{key}={options[key]}'
                found.add(key)
        lines.extend(f'{key}={value}' for key, value in options.items() if key not in found)
        config_file.write_text('\n'.join(lines) + '\n')

        return Command([self.rom_binary, '-hogdir', self.rom.parent])
