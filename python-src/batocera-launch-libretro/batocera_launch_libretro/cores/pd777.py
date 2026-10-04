from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import Core

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Pd777(Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Course selection switch visual feedback
        core_options.set_from_config(
            'pd777_announce_course_switch', 'cassettevision_announce_course_switch', default='enabled'
        )
