from __future__ import annotations

import re
import shlex
from configparser import Error as ConfigParserError
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property

from ..command import Command
from ..emulator import Emulator
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from configparser import SectionProxy

    from ..types import HotkeysContext

_FIELD_CODE: Final = re.compile(r'%(.)')


def _strip_field_codes(arg: str) -> str:
    return _FIELD_CODE.sub(lambda m: '%' if m[1] == '%' else '', arg)


@cached_dataclass
class Sh(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'shell',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def is_desktop_entry(self) -> bool:
        return self.rom.is_file() and self.rom.suffix.lower() == '.desktop'

    @cached_property
    def desktop_entry(self) -> SectionProxy:
        parser = CaseSensitiveRawConfigParser(strict=False)

        try:
            parser.read(self.rom, encoding='utf-8')
        except ConfigParserError as e:
            raise BatoceraException(f'Unable to read desktop entry: {self.rom}') from e

        if not parser.has_section('Desktop Entry'):
            raise BatoceraException(f'Missing [Desktop Entry] section in {self.rom}')

        return parser['Desktop Entry']

    @property
    def execution_path(self) -> Path | None:
        if not self.is_desktop_entry:
            return None

        if path := self.desktop_entry.get('Path'):
            return Path(path)

        return self.rom.parent

    def _desktop_entry_args(self) -> list[str]:
        exec_line = self.desktop_entry.get('Exec')

        if not exec_line:
            raise BatoceraException(f'Missing Exec key in {self.rom}')

        return [stripped for arg in shlex.split(exec_line) if (stripped := _strip_field_codes(arg))]

    async def configure(self) -> Command:
        if self.is_desktop_entry:
            return Command(self._desktop_entry_args())

        # in case of squashfs, the root directory is passed
        run_sh = self.rom / 'run.sh'
        rom = run_sh if run_sh.exists() else self.rom
        return Command(['/bin/bash', rom])
