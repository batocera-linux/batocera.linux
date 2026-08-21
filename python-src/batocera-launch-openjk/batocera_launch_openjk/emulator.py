from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Final

from batocera_common.paths import CONFIGS
from batocera_launch import (
    BatoceraException,
    Command,
    Emulator,
    HotkeysContext,
    cached_dataclass,
    cached_property,
)

_logger = logging.getLogger(__name__)

_JEDI_ACADEMY: Final = Path('/usr/bin/JediAcademy')
_JEDI_OUTCAST: Final = Path('/usr/bin/JediOutcast')


def _update_config_file(file_path: Path, options_to_set: dict[str, str], remove_keys: list[str], /) -> None:
    if file_path.is_file():
        lines = file_path.read_text().splitlines(keepends=True)
        lines = [line for line in lines if not any(key in line for key in remove_keys)]

        for key, value in options_to_set.items():
            option_line = f'{key} "{value}"\n'
            if any(key in line for line in lines):
                lines = [option_line if key in line else line for line in lines]
            else:
                lines.append(option_line)

        file_path.write_text(''.join(lines))
    else:
        file_path.write_text(''.join(f'{key} "{value}"\n' for key, value in options_to_set.items()))

    _logger.info('OpenJK config file %s updated.', file_path)


def _copy_binaries(src_dir: Path, dest_dir: Path, binary_dest: Path, /) -> None:
    binary_src = src_dir / binary_dest.name
    if binary_dest.exists() and binary_src.stat().st_mtime <= binary_dest.stat().st_mtime:
        return

    for item in src_dir.iterdir():
        dest_item = dest_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest_item)
        _logger.debug('Copying %s to %s', item, dest_item)

    if binary_dest.is_file():
        binary_dest.chmod(0o755)


@cached_dataclass
class OpenJK(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'openjk',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'restore_state': 'KEY_F9',
                'save_state': 'KEY_F12',
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
        if 'academy' in rom_name:
            _logger.info('Found Jedi Academy!')
            binary_src_path = _JEDI_ACADEMY
            binary_dest = self.rom.parent / 'openjk_sp.x86_64'
            config_file = CONFIGS / 'openjk' / 'base' / 'openjk_sp.cfg'
        elif 'outcast' in rom_name:
            _logger.info('Found Jedi Outcast!')
            binary_src_path = _JEDI_OUTCAST
            binary_dest = self.rom.parent / 'openjo_sp.x86_64'
            config_file = CONFIGS / 'openjo' / 'base' / 'openjo_sp.cfg'
        else:
            _logger.info("Could not determine which game you're using!")
            _logger.info('Rename your .jedi file as per the _infot.txt file')
            raise BatoceraException('Could not determine game')

        config_file.parent.mkdir(parents=True, exist_ok=True)

        options_to_set = {
            'seta r_mode': '-2',
            'seta r_fullscreen': '1',
            'seta r_centerWindow': '1',
            'seta r_customheight': str(self.resolution.height),
            'seta r_customwidth': str(self.resolution.width),
        }
        remove_keys: list[str] = []

        depth = self.config.get_str('openjk_colour')
        if depth == '16':
            options_to_set['seta r_colorbits'] = depth
            options_to_set['seta r_depthbits'] = depth
        elif depth == '32':
            options_to_set['seta r_colorbits'] = depth
            options_to_set['seta r_depthbits'] = '24'
        else:
            remove_keys.extend(['seta r_colorbits', 'seta r_depthbits'])

        geometric = self.config.get_str('openjk_detail')
        if geometric == 'Low':
            options_to_set['seta r_lodbias'] = '2'
            options_to_set['seta r_subdivisions'] = '20'
        elif geometric == 'Medium':
            options_to_set['seta r_lodbias'] = '1'
            options_to_set['seta r_subdivisions'] = '12'
        else:
            remove_keys.extend(['seta r_lodbias', 'seta r_subdivisions'])

        options_to_set['seta r_picmip'] = self.config.get_str('openjk_texture', '0')

        if (texture_quality := self.config.get_str('openjk_texture_quality', '0')) != '0':
            options_to_set['seta r_texturebits'] = texture_quality
        else:
            remove_keys.append('seta r_texturebits')

        options_to_set['seta r_textureMode'] = self.config.get_str(
            'openjk_texture_filter',
            'GL_LINEAR_MIPMAP_LINEAR',
        )

        if not self.config.get_bool('openjk_shaders', True):
            options_to_set['seta r_detailtextures'] = '0'
        else:
            remove_keys.append('seta r_detailtextures')

        if self.config.get_bool('openjk_vsync'):
            options_to_set['seta r_swapInterval'] = '1'
        else:
            remove_keys.append('seta r_swapInterval')

        options_to_set['seta r_gamma'] = self.config.get_str('openjk_brightness', '1.000000')
        options_to_set['seta cg_shadows'] = self.config.get_str('openjk_shadows', '1')
        options_to_set['seta r_dynamiclight'] = self.config.get_str('openjk_lights', '1')

        if self.config.get_bool('openjk_glow'):
            options_to_set['seta r_DynamicGlow'] = '1'
        else:
            remove_keys.append('seta r_DynamicGlow')

        options_to_set['seta r_flares'] = self.config.get_str('openjk_flares', '1')
        options_to_set['seta cg_marks'] = self.config.get_str('openjk_wall', '1')
        options_to_set['seta r_ext_texture_filter_anisotropic'] = self.config.get_str(
            'openjk_anistropic',
            '16.000000',
        )
        options_to_set['seta cg_drawCrosshair'] = self.config.get_str('openjk_crosshair', '1')
        options_to_set['seta cg_crosshairIdentifyTarget'] = self.config.get_str('openjk_target', '1')
        options_to_set['seta d_slowmodeath'] = self.config.get_str('openjk_death', '3')
        options_to_set['seta cg_gunAutoFirst'] = self.config.get_str('openjk_guns', '1')
        options_to_set['seta g_dismemberment'] = self.config.get_str('openjk_dismember', '1')
        options_to_set['seta ui_disableWeaponSway'] = self.config.get_str('openjk_sway', '0')
        options_to_set['seta se_language'] = self.config.get_str('openjk_text', 'english')
        options_to_set['seta s_language'] = self.config.get_str('openjk_voice', 'english')
        options_to_set['seta g_subtitles'] = self.config.get_str('openjk_subtitles', '0')

        _update_config_file(config_file, options_to_set, remove_keys)
        _copy_binaries(binary_src_path, self.rom.parent, binary_dest)

        return Command(
            [binary_dest],
            env={
                'XDG_DATA_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
