from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class ScummVM(DisableRewindMixin, DisableRunaheadMixin, Core):
    @cached_property
    def rom_argument(self) -> str | Path | None:
        rom = self.rom.parent / self.rom.name

        if rom.stat().st_size == 0:
            return rom.with_suffix('')

        return rom

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Analog Deadzone
        core_options.set_from_config('scummvm_analog_deadzone', 'scummvm_analog_deadzone', default='15')

        # Gamepad Cursor Speed
        core_options.set_from_config('scummvm_gamepad_cursor_speed', 'scummvm_gamepad_cursor_speed', default='1.0')

        # Speed Hack (safe)
        core_options.set_from_config('scummvm_speed_hack', 'scummvm_speed_hack', default='enabled')
