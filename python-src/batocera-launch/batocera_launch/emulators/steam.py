from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Steam(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'steam',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    async def configure(self) -> Command:
        args: list[str | Path] = ['batocera-steam']
        if self.rom.name != 'Steam.steam':
            args.append(self.rom.read_text().strip())

        # Fix for Xbox Bluetooth controllers not working with Steam (issue #12731)
        # xpadneo fixes mappings at evdev level, but Steam reads raw HIDAPI data
        return Command(args, env={'SDL_JOYSTICK_HIDAPI_XBOX': '0'})
