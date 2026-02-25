from __future__ import annotations

from typing import TYPE_CHECKING

from ..command import Command
from ..dataclasses import cached_dataclass
from ..emulator import Emulator
from ..functools import cached_property

if TYPE_CHECKING:
    from ..types import HotkeysContext


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

    async def configure(self) -> Command:
        # in case of squashfs, the root directory is passed
        run_sh = self.rom / 'run.sh'
        rom = run_sh if run_sh.exists() else self.rom
        return Command(['/bin/bash', rom])
