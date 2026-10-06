from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, ROMS
from batocera_launch import Command, Emulator, HotkeysContext

_LEGACY_DIR: Final = ROMS / 'etlegacy' / 'legacy'
_LEGACY_FILE: Final = 'legacy_2.85-dirty.pk3'
_LEGACY_SOURCE: Final = Path('/usr/share/etlegacy') / _LEGACY_FILE
_LEGACY_DEST: Final = _LEGACY_DIR / _LEGACY_FILE


@cached_dataclass
class ETLegacy(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'etlegacy',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'etlegacy' / 'legacy'

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        _LEGACY_DIR.mkdir(parents=True, exist_ok=True)

        scope_color = self.config.get_str('etlegacy_scope_color', '#000000FF')
        language = self.config.get_str('etlegacy_language', 'en')

        options_to_set = {
            'seta r_mode': '-1',
            'seta r_fullscreen': '1',
            'seta r_allowResize': '0',
            'seta r_centerWindow': '1',
            'seta r_customheight': str(self.resolution.height),
            'seta r_customwidth': str(self.resolution.width),
            'seta cg_scopeReticleStyle': self.config.get_str('etlegacy_scope_style', '0'),
            'seta cg_scopeReticleColor': scope_color,
            'seta cg_scopeReticleDotColor': scope_color,
            'seta cg_weapzoomSensitivityScale': self.config.get_str('etlegacy_zoom_sens', '1.0'),
            'seta cl_lang': language,
            'seta ui_cl_lang': language,
        }

        lines: list[str] = []
        config_file = self.config_dir / 'etconfig.cfg'

        if config_file.is_file():
            lines = config_file.read_text().splitlines()

            for key, value in options_to_set.items():
                option_line = f'{key} "{value}"'
                if any(key in line for line in lines):
                    lines = [option_line if key in line else line for line in lines]
                else:
                    lines.append(option_line)
        else:
            lines = [f'{key} "{value}"' for key, value in options_to_set.items()]

        if not lines or lines[-1] != '':
            # Ensure the file ends with a newline
            lines.append('')

        config_file.write_text('\n'.join(lines))

        if not _LEGACY_DEST.exists() or _LEGACY_SOURCE.stat().st_mtime > _LEGACY_DEST.stat().st_mtime:
            shutil.copy(_LEGACY_SOURCE, _LEGACY_DEST)

        return Command(['etl'])
