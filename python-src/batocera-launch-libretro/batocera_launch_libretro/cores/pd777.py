from __future__ import annotations

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig


@cached_dataclass
class Pd777(DisableRewindMixin, DisableRunaheadMixin, Core):
    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Course selection switch visual feedback
        core_options.set_from_config(
            'pd777_announce_course_switch', 'cassettevision_announce_course_switch', default='enabled'
        )
