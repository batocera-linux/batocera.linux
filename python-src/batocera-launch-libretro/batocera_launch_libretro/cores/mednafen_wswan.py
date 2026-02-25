from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class MednafenWswan(Core):
    supports_retroachievements: ClassVar = True

    @cached_property
    def _wswan_orientation(self) -> str:
        # If set manually, proritize that.
        # Otherwise, set to portrait for games listed as 90 degrees, manual (default) if not.
        if (rotate_display := self.config.get('wswan_rotate_display')) is not None:
            return rotate_display
        return 'portrait' if self.emulator.decoration_id == '90' else 'manual'

    def set_config(self, custom_config: LibretroConfig, /) -> None:
        super().set_config(custom_config)
        custom_config.set('wswan_rotate_display', self._wswan_orientation)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Display rotation
        core_options.set('wswan_rotate_display', self._wswan_orientation)
