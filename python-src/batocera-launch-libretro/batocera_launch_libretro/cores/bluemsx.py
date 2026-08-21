from __future__ import annotations

from typing import ClassVar, Final

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

_SYSTEMS_WITH_CONTROLLER_DEVICE_TYPES: Final = {'msx', 'msx1', 'msx2', 'colecovision'}


@cached_dataclass
class BlueMSX(Core):
    supports_retroachievements: ClassVar = True

    @cached_property
    def player1_device_type(self) -> str | None:
        return '1' if self.system in _SYSTEMS_WITH_CONTROLLER_DEVICE_TYPES else None

    @cached_property
    def player2_device_type(self) -> str | None:
        return '1' if self.system in _SYSTEMS_WITH_CONTROLLER_DEVICE_TYPES else None

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Auto Select Core
        if self.system == 'colecovision':
            core_options.set('bluemsx_msxtype', 'ColecoVision')
        elif self.system == 'msx1':
            core_options.set('bluemsx_msxtype', 'MSX')
        elif self.system == 'msx2':
            core_options.set('bluemsx_msxtype', 'MSX2')
        elif self.system == 'msx2+':
            core_options.set('bluemsx_msxtype', 'MSX2+')
        elif self.system == 'msxturbor':
            core_options.set('bluemsx_msxtype', 'MSXturboR')

        # Forces cropping of overscanned frames
        core_options.set('bluemsx_overscan', 'enabled' if self.system in {'colecovision', 'msx1'} else 'MSX2')

        # Reduce Sprite Flickering
        core_options.set_bool_from_config('bluemsx_nospritelimits', default=True, values=('ON', 'OFF'))

        # Zoom, Hide Video Border
        core_options.set_from_config('bluemsx_overscan', default='MSX2')
