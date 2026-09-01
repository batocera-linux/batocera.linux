from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_MODEL_MAPPING: Final = {
    '520st_auto': ('st', 'auto'),
    '520st_100': ('st', '100'),
    '520st_102': ('st', '102'),
    '520st_104': ('st', '104'),
    '520st_etos256': ('st', 'etos256'),
    '1040ste_auto': ('ste', 'auto'),
    '1040ste_106': ('ste', '106'),
    '1040ste_162': ('ste', '162'),
    '1040ste_etos256': ('ste', 'etos256'),
    'megaste_auto': ('megaste', 'auto'),
    'megaste_205': ('megaste', '205'),
    'megaste_206': ('megaste', '206'),
    'megaste_etos256': ('megaste', 'etos256'),
    'tt_auto': ('tt', 'auto'),
    'tt_306': ('tt', '306'),
    'tt_etos512': ('tt', 'etos512'),
    'falcon_auto': ('falcon', 'auto'),
    'falcon_400': ('falcon', '400'),
    'falcon_402': ('falcon', '402'),
    'falcon_404': ('falcon', '404'),
    'falcon_etos512': ('falcon', 'etos512'),
}

# all languages by preference, when value is "auto"
_ALL_LANGUAGES: Final = ('us', 'uk', 'de', 'es', 'fr', 'it', 'nl', 'ru', 'se', '')

# machine bioses by prefered orders, when value is "auto"
_ALL_MACHINES_BIOS: Final = {
    'st': ('etos256', '104', '102', '100'),
    'ste': ('etos256', '162', '106'),
    'megaste': ('etos256', '206', '205'),
    'tt': ('etos512', '306'),
    'falcon': ('etos512', '404', '402', '400'),
}
_PAD_MAPPING: Final = {1: 'y', 2: 'b', 3: 'a'}


def _find_best_tos(bios_dir: Path, machine: str, tos_version: str, language: str, /) -> Path:
    if machine not in _ALL_MACHINES_BIOS:
        raise BatoceraException(f'No bios found for machine {machine}')

    tos_versions = [tos_version] if tos_version != 'auto' else []
    tos_versions.extend(_ALL_MACHINES_BIOS[machine])

    for version in tos_versions:
        languages = [language] if language != 'auto' else []
        languages.extend(_ALL_LANGUAGES)
        for lang in languages:
            bios_version = version if 'etos' in version else f'tos{version}'
            tos_path = bios_dir / f'{bios_version}{lang}.img'
            if tos_path.exists():
                _logger.debug('tos filename: %s', tos_path.name)
                return tos_path
            _logger.warning('tos filename %s not found', tos_path.name)

    raise BatoceraException(f'No bios found for machine {machine}')


@cached_dataclass
class Hatari(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'hatari',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        # Machine can be st (default), ste, megaste, tt, falcon
        # st should use TOS 1.00 to TOS 1.04 (tos100 / tos102 / tos104 / emutos192k)
        # ste should use TOS 1.06 at least (tos106 / tos162 / tos206 / emutos192K)
        # megaste should use TOS 2.XX series (tos206 / emutos256k)
        # tt should use tos 3.XX / emutos512k
        # falcon should use tos 4.XX / emutos512k

        machine, tos_version = _MODEL_MAPPING.get(self.config.get_str('model', 'none'), ('st', 'auto'))
        tos_lang = self.config.get_str('language', 'us')

        args: list[str | Path] = [
            'hatari',
            # Start emulator fullscreen
            '--fullscreen',
            '--machine',
            machine,
            '--tos',
            _find_best_tos(BIOS, machine, tos_version, tos_lang),
            # RAM (ST Ram) options (0 for 512k, 1 for 1MB)
            '--memsize',
            self.config.get_str('ram', '0'),
        ]

        suffix = self.rom.suffix.lower()
        if suffix == '.hd':
            drive = '--acsi' if self.config.get_str('hatari_drive') == 'ACSI' else '--ide-master'
            args.extend([drive, self.rom])
        elif suffix == '.gemdos':
            self.config_dir.mkdir(parents=True, exist_ok=True)
            blank_file = self.config_dir / 'blank.st'
            if not blank_file.exists():
                blank_file.touch()
            args.extend(['--harddrive', self.rom, blank_file])
        else:
            args.extend(
                [
                    # Floppy (A) options
                    '--disk-a',
                    self.rom,
                    # Floppy (B) options
                    '--drive-b',
                    'off',
                ]
            )

        config = CaseSensitiveConfigParser(interpolation=None)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / 'hatari.cfg'
        if config_file.is_file():
            config.read(config_file)

        for i in range(1, 6):
            section = f'Joystick{i}'
            if config.has_section(section):
                config.set(section, 'nJoyId', '-1')
                config.set(section, 'nJoystickMode', '0')

        # pads
        # disable previous configuration
        for pad in self.controllers[:5]:  # 1 to 5 included
            section = f'Joystick{pad.player_number}'
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, 'nJoyId', str(pad.index))
            config.set(section, 'nJoystickMode', '1')

            for button, name in _PAD_MAPPING.items():
                key = f'nButton{button}'
                if name in pad.inputs:
                    config.set(section, key, str(pad.inputs[name].id))
                else:
                    config.set(section, key, str(button - 1))

        # Log
        if not config.has_section('Log'):
            config.add_section('Log')
        config.set('Log', 'bConfirmQuit', 'FALSE')

        # Screen
        if not config.has_section('Screen'):
            config.add_section('Screen')
        config.set('Screen', 'bShowStatusbar', str(self.config.show_fps).upper())

        with config_file.open('w') as fp:
            config.write(fp)

        return Command(args)
