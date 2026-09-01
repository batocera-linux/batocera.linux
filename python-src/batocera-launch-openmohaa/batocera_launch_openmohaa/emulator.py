from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_TERRAIN_DETAIL: Final[dict[str, tuple[str, str]]] = {
    '0': ('3', '10'),
    '1': ('4', '9'),
    '2': ('5', '7'),
}

_MODEL_DETAIL: Final[dict[str, tuple[str, str, str]]] = {
    '0': ('0.25', '0.25', '0.25'),
    '1': ('0.25', '0.35', '0.35'),
    '2': ('0.45', '0.35', '0.45'),
    '3': ('0.55', '0.5', '0.55'),
    '4': ('0.9', '0.9', '0.9'),
}

_EFFECTS_DETAIL: Final[dict[str, tuple[str, str]]] = {
    '1': ('0.3', '23'),
    '2': ('0.5', '22'),
    '3': ('0.7', '20'),
    '4': ('0.8', '18'),
    '5': ('0.95', '15'),
    '6': ('1.0', '10'),
}

_CURVE_DETAIL: Final[dict[str, str]] = {
    '0': '20',
    '1': '10',
    '3': '3',
}


def _update_config_file(file_path: Path, options_to_set: dict[str, str], /) -> None:
    if file_path.is_file():
        lines = file_path.read_text().splitlines(keepends=True)
        options_in_file: set[str] = set()
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            for key, value in options_to_set.items():
                if stripped_line.startswith(f'{key} '):
                    lines[i] = f'{key} "{value}"\n'
                    options_in_file.add(key)
                    break
        lines.extend(f'{key} "{value}"\n' for key, value in options_to_set.items() if key not in options_in_file)
        file_path.write_text(''.join(lines))
    else:
        file_path.write_text(''.join(f'{key} "{value}"\n' for key, value in options_to_set.items()))


@cached_dataclass
class OpenMOHAA(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'openmohaa',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F9',
                'menu': 'KEY_ESC',
                'pause': 'KEY_PAUSE',
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @property
    def execution_path(self) -> Path | None:
        return self.rom.parent

    async def configure(self) -> Command:
        rom_name = self.rom.name.lower()
        variant_subdir = 'main'
        target_game = '0'
        if 'spear' in rom_name:
            _logger.info('Found Spearhead!')
            variant_subdir = 'mainta'
            target_game = '1'
        elif 'break' in rom_name:
            _logger.info('Found Breakthrough!')
            variant_subdir = 'maintt'
            target_game = '2'

        config_file = self.config_dir / variant_subdir / 'configs' / 'omconfig.cfg'
        config_file.parent.mkdir(parents=True, exist_ok=True)

        ter_maxlod, ter_error = _TERRAIN_DETAIL.get(self.config.get_str('mohaa_terrain', ''), ('6', '4'))
        r_lodviewmodelcap, r_lodcap, r_lodscale = _MODEL_DETAIL.get(
            self.config.get_str('mohaa_model', ''),
            ('0.25', '0.35', '5'),
        )
        cg_effectdetail, vss_maxcount = _EFFECTS_DETAIL.get(
            self.config.get_str('mohaa_effects', ''),
            ('0.2', '22'),
        )

        options_to_set = {
            'seta r_mode': '-1',
            'seta r_fullscreen': '1',
            'seta r_allowResize': '0',
            'seta r_centerWindow': '1',
            'seta r_customheight': f'"{self.resolution.height}"',
            'seta r_customwidth': f'"{self.resolution.width}"',
            'seta r_customaspect': '1',
            'bind [': 'weapprev',
            'bind ]': 'weapnext',
            # -= Video Options =-
            'seta r_colorbits': self.config.get_str('mohaa_colour', '0'),
            'seta r_picmip': self.config.get_str('mohaa_texture', '1'),
            'seta r_texturebits': self.config.get_str('mohaa_texture_colour', '0'),
            'seta r_textureMode': self.config.get_str('mohaa_texture_filter', 'GL_LINEAR_MIPMAP_NEAREST'),
            'seta cg_marks_add': self.config.get_str('mohaa_decals', '0'),
            'seta cg_rain': self.config.get_str('mohaa_weather', '0'),
            'seta r_gamma': self.config.get_str('mohaa_brightness', '1.000000'),
            'seta r_ext_compressed_textures': self.config.get_str('mohaa_compression', '0'),
            # -= Advanced Options =-
            'seta cg_drawviewmodel': self.config.get_str('mohaa_view', '2'),
            'seta cg_shadows': self.config.get_str('mohaa_shadows', '1'),
            'seta ter_maxlod': ter_maxlod,
            'seta ter_error': ter_error,
            'seta r_lodviewmodelcap': r_lodviewmodelcap,
            'seta r_lodcap': r_lodcap,
            'seta r_lodscale': r_lodscale,
            'seta cg_effectdetail': cg_effectdetail,
            'seta vss_maxcount': vss_maxcount,
            'seta r_subdivisions': _CURVE_DETAIL.get(self.config.get_str('mohaa_curve', ''), '4'),
            'seta g_subtitle': self.config.get_str('mohaa_subtitles', '0'),
            'seta r_fastdlights': self.config.get_str('mohaa_dynamic_lighting', '1'),
            'seta r_fastentlight': self.config.get_str('mohaa_entity_lighting', '1'),
            'seta vss_draw': self.config.get_str('mohaa_smoke', '0'),
            'seta ui_weaponsbar': self.config.get_str('mohaa_weapons', '1'),
            'seta ui_crosshair': self.config.get_str('mohaa_crosshair', '1'),
        }

        _update_config_file(config_file, options_to_set)

        return Command(
            [
                '/usr/bin/openmohaa/openmohaa',
                '+set',
                'com_homepath',
                # Not the full config_path
                'configs/openmohaa',
                # Set the target game via command line argument
                '+set',
                'com_target_game',
                target_game,
            ]
        )
