from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig


@cached_dataclass
class BeetleSaturn(Core):
    supports_retroachievements: ClassVar = True
    gun_mapping: ClassVar = {'default': {'device': 260, 'p1': 0, 'p2': 1}}

    @cached_property
    def player1_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        # wheel
        if self.config.use_wheels:
            return '517'  # Arcade Racer

        return self.config.get_str('controller1_saturn', '1')  # 1 = Saturn pad

    @cached_property
    def player2_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        return self.config.get_str('controller2_saturn', '1')  # 1 = Saturn pad

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # gun cross / wheel
        # gun
        core_options.set_from_config(
            'beetle_saturn_virtuagun_crosshair',
            'beetle-saturn_crosshair',
            default='Cross' if self.emulator.guns_need_crosses else 'Off',
        )

        # wheel
        core_options.set(
            'beetle_saturn_analog_stick_deadzone', '0%' if self.config.use_wheels and self.wheels else '15%'
        )
