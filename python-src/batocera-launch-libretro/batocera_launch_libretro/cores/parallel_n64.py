from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRunaheadMixin, GLOverrideMixin, LibretroConfig

from ._n64_core import N64ControllerRemapMixin


@cached_dataclass
class ParallelN64(GLOverrideMixin, DisableRunaheadMixin, N64ControllerRemapMixin, Core):
    supports_retroachievements: ClassVar = True
    n64_controller_option: ClassVar = 'parallel-n64'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        core_options.set('parallel-n64-64dd-hardware', 'disabled')
        core_options.set('parallel-n64-boot-device', 'Default')

        # Graphics Plugin
        core_options.set_from_config(
            'parallel-n64-gfxplugin',
            default='parallel' if self.config.get('gfxbackend') == 'vulkan' else 'auto',
        )  # vulkan doesn't work with auto

        # Video Resolution
        core_options.set_from_config('parallel-n64-screensize', default='320x240')

        # Widescreen Hack
        # Increases from 4:3 to 16:9 in 3D games (bad for 2D)
        if (
            self.config.get('parallel-n64-aspectratiohint') == 'widescreen'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
        ):
            aspect = 'widescreen'
        else:
            aspect = 'normal'

        core_options.set('parallel-n64-aspectratiohint', aspect)

        # Texture Filtering
        core_options.set_from_config('parallel-n64-filtering', default='automatic')

        # Framerate
        core_options.set_from_config('parallel-n64-framerate', default='automatic')

        # Controller rumble settings
        for pak_number in range(1, 5):
            pak_default = 'memory' if pak_number == 1 else 'none'
            pak_key = f'parallel-n64-pak{pak_number}'
            pak_value = self.config.get(pak_key, pak_default)

            if pak_value == 'auto_rumble':
                pak_value = 'rumble' if self.metadata.get('controller_rumble') == 'true' else pak_default

            core_options.set(pak_key, pak_value)

        # Joystick deadzone
        core_options.set_from_config(
            'parallel-n64-astick-deadzone',
            'parallel-n64-deadzone',
            default='0' if self.config.use_wheels and self.wheels else '15',
        )

        # Joystick sensitivity
        core_options.set_from_config('parallel-n64-astick-sensitivity', 'parallel-n64-sensitivity', default='100')

        # Nintendo 64-DD
        if self.system == 'n64dd':
            # 64DD Hardware
            core_options.set('parallel-n64-64dd-hardware', 'enabled')
            # Boot device
            core_options.set('parallel-n64-boot-device', '64DD IPL')
