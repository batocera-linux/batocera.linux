from __future__ import annotations

from batocera_launch import cached_property

from ..core import Core


class Snes9xControllersMixin(Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        if (controller := self.config.get_str('controller1_snes9x')) is not None:
            return controller
        if (controller := self.config.get_str('controller1_snes9x_next')) is not None:
            return controller
        return '1'

    @cached_property
    def player2_device_type(self) -> str | None:
        if (controller := self.config.get_str('controller2_snes9x')) is not None:
            return controller
        if (controller := self.config.get_str('controller2_snes9x_next')) is not None:
            return controller
        if len(self.controllers) > 2:  # More than 2 controller connected
            return '257'
        return '1'

    @cached_property
    def player3_device_type(self) -> str | None:
        return self.config.get('controller3_snes9x', '1')
