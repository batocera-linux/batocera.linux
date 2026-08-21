from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, LibretroConfig

if TYPE_CHECKING:
    from batocera_launch import Controller


@cached_dataclass
class Prboom(DisableRewindMixin, DisableRunaheadMixin, Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        return self.config.get_str('prboom_controller1') or '1'

    def get_analog_mode(self, controller: Controller, /) -> Literal['0', '1']:
        if controller.player_number == 1 and (controller1 := self.config.get('prboom_controller1')):
            return '0' if controller1 != '1' else '1'

        return super().get_analog_mode(controller)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Internal resolution
        core_options.set_from_config('prboom-resolution', 'prboom-resolution', default='320x200')
