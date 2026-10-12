from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Mrboom(Core):
    @property
    def disables_bezel(self) -> bool:
        return True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Team mode
        legacy = self.config.get('mrboom-aspect', 'Native')
        core_options.set_from_config(
            'mrboom-teammode', 'mrboom-teammode', default='Selfie' if legacy == 'Native' else legacy
        )
