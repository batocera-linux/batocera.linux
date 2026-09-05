from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext

_logger = logging.getLogger(__name__)

_FONT_PATH: Final = Path('/usr/share/fonts/dejavu/DejaVuSans.ttf')

_ASSET_DIR_NAMES: Final = ['ANIMS', 'DATA', 'INTRO', 'LEVELS', 'QDATA']

_LANGUAGE_MAPPING: Final = {
    'en_US': 'en',
    'en_GB': 'en',
    'fr_FR': 'fr',
    'oc_FR': 'fr',
    'de_DE': 'de',
    'es_ES': 'es',
    'es_MX': 'es',
    'it_IT': 'it',
    'nl_NL': 'nl',
    'ru_RU': 'ru',
    'sv_SE': 'sv',
    'cs_CZ': 'cs',
    'fi_FI': 'fi',
    'pl_PL': 'pl',
    'hu_HU': 'hu',
    'pt_PT': 'pt',
    'pt_BR': 'br',
    'zh_CN': 'zh(s)',
    'zh_TW': 'zh(t)',
    'ko_KR': 'ko',
    'nb_NO': 'nb',
    'nn_NO': 'nb',
}


@cached_dataclass
class CorsixTH(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'corsixth',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': ['KEY_RIGHTSHIFT', 'KEY_Q'],
                'reset': ['KEY_RIGHTSHIFT', 'KEY_F10'],
                'save_state': ['KEY_LEFTALT', 'KEY_LEFTSHIFT', 'KEY_S'],
                'restore_state': ['KEY_LEFTALT', 'KEY_LEFTSHIFT', 'KEY_L'],
            },
        }

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        if not all((self.roms_dir / name).is_dir() for name in _ASSET_DIR_NAMES):
            _logger.error('ERROR: Game assets not installed. You can get them from the game Theme Hospital.')

        language = _LANGUAGE_MAPPING.get(self.config.get_str('system.language', 'en_US'), 'en')
        music_dir = self.roms_dir / 'MP3'
        if music_dir.is_dir():
            audio_music = f'[[{music_dir}]]'
        else:
            _logger.warning(
                'NOTICE: Audio & Music system loaded, but found no external background tracks. Missing MP3 folder'
            )
            audio_music = 'nil'

        width, height = self.config.get_str(
            'cth_resolution', f'{self.resolution.width}x{self.resolution.height}'
        ).split('x')

        config_file = self.config_dir / 'config.txt'
        config_file.write_text(
            '\n'.join(
                [
                    'check_for_updates = false',
                    f'theme_hospital_install = [[{self.roms_dir}]]',
                    f'unicode_font = [[{_FONT_PATH}]]',
                    f'savegames = [[{self.saves_dir}]]',
                    f'screenshots = [[{SCREENSHOTS}]]',
                    'fullscreen = true',
                    f'width = {width}',
                    f'height = {height}',
                    f'ui_scale = {self.config.get_str("cth_ui_scale", "1")}',
                    f'use_new_graphics = {self.config.get_str("cth_new_graphics", "true")}',
                    f'free_build_mode = {self.config.get_str("cth_free_build_mode", "false")}',
                    f'play_intro = {self.config.get_str("cth_play_intro", "true")}',
                    f'language = [[{language}]]',
                    f'audio_music = {audio_music}',
                    '',
                ]
            ),
            encoding='utf-8',
        )

        return Command(['corsix-th', f'--config-file={config_file}'])
