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
            'r_mode': '-1',
            'r_fullscreen': '1',
            'r_allowResize': '0',
            'r_centerWindow': '1',
            'r_customheight': str(self.resolution.height),
            'r_customwidth': str(self.resolution.width),
            'cg_scopeReticleStyle': self.config.get_str('etlegacy_scope_style', '0'),
            'cg_scopeReticleColor': scope_color,
            'cg_scopeReticleDotColor': scope_color,
            'cg_weapzoomSensitivityScale': self.config.get_str('etlegacy_zoom_sens', '1.0'),
            'cl_lang': language,
            'ui_cl_lang': language,
        }

        if not _LEGACY_DEST.exists() or _LEGACY_SOURCE.stat().st_mtime > _LEGACY_DEST.stat().st_mtime:
            shutil.copy(_LEGACY_SOURCE, _LEGACY_DEST)

        # +set is applied after the profile config is executed, so it wins over profiles/<name>/etconfig.cfg
        args: list[str | Path] = ['etl']
        for key, value in options_to_set.items():
            args.extend(['+set', key, value])

        return Command(args)
