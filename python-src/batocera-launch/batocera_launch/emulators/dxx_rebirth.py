from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.paths import CONFIGS
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext, cached_dataclass, cached_property

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

        replacements = {
            'ResolutionX=': f'ResolutionX={self.resolution.width}',
            'ResolutionY=': f'ResolutionY={self.resolution.height}',
            'WindowMode=': 'WindowMode=0',
            'VSync=': f'VSync={self.config.get_str("rebirth_vsync", "0")}',
            'TexFilt=': f'TexFilt={self.config.get_str("rebirth_filtering", "0")}',
            'TexAnisotropy=': f'TexAnisotropy={self.config.get_str("rebirth_anisotropy", "0")}',
            'Multisample=': f'Multisample={self.config.get_str("rebirth_multisample", "0")}',
        }

        if config_file.is_file():
            lines = config_file.read_text().splitlines(keepends=True)

            for i, line in enumerate(lines):
                for prefix, replacement in replacements.items():
                    if line.startswith(prefix):
                        lines[i] = f'{replacement}\n'
                        break

            config_file.write_text(''.join(lines))
        else:
            config_file.write_text(
                '\n'.join(
                    [
                        f'ResolutionX={self.resolution.width}',
                        f'ResolutionY={self.resolution.height}',
                        'WindowMode=0',
                        'VSync=0',
                        'TexFilt=0',
                        'TexAnisotropy=0',
                        'Multisample=0',
                        '',
                    ]
                ),
            )

        return Command([self.rom_binary, '-hogdir', self.rom.parent])
