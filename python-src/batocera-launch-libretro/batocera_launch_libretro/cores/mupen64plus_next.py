# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_libretro import GLCoreOverrideMixin, RACore

from ._n64_core import N64ControllerRemapMixin

if TYPE_CHECKING:
    from batocera_launch import LibretroConfig


@cached_dataclass
class Mupen64PlusNext(GLCoreOverrideMixin, N64ControllerRemapMixin, RACore):
    force_slang_shaders: ClassVar = True
    n64_controller_option: ClassVar = 'mupen64plus'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Threaded Rendering
        core_options.set('mupen64plus-ThreadedRenderer', 'True')

        # Use High-Res Textures Pack
        # .htc files must be placed in 'Mupen64plus/cache'
        core_options.set('mupen64plus-txHiresEnable', 'True')

        # Video 4:3 Resolution
        core_options.set_from_config('mupen64plus-43screensize', default='320x240')

        # Video 16:9 Resolution
        core_options.set_from_config('mupen64plus-169screensize', default='640x360')

        # Widescreen Hack
        # Increases from 4:3 to 16:9 in 3D games (bad for 2D)
        if (
            self.config.get('mupen64plus-aspect') == '16:9 adjusted'
            and self.config.get('ratio') == '16/9'
            and self.config.get('bezel') == 'none'
        ):
            aspect = '16:9 adjusted'
        else:
            aspect = '4:3'

        core_options.set('mupen64plus-aspect', aspect)

        # Bilinear Filtering
        core_options.set_from_config('mupen64plus-BilinearMode', default='standard')

        # Anti-aliasing (MSA)
        core_options.set_from_config('mupen64plus-MultiSampling', default='0')

        # Texture Filtering
        core_options.set_from_config('mupen64plus-txFilterMode', default='None')

        # Texture Enhancement
        core_options.set_from_config('mupen64plus-txEnhancementMode', default='None')

        # Controller rumble settings
        for pak_number in range(1, 5):
            pak_default = 'memory' if pak_number == 1 else 'none'
            pak_key = f'mupen64plus-pak{pak_number}'
            pak_value = self.config.get(pak_key, pak_default)

            if pak_value == 'auto_rumble':
                pak_value = 'rumble' if self.metadata.get('controller_rumble') == 'true' else pak_default

            core_options.set(pak_key, pak_value)

        # RDP Plugin
        core_options.set_from_config('mupen64plus-rdp-plugin', 'mupen64plus-rdpPlugin', default='gliden64')

        # RSP Plugin
        core_options.set_from_config('mupen64plus-rsp-plugin', 'mupen64plus-rspPlugin', default='hle')

        # CPU Core
        core_options.set_from_config('mupen64plus-cpucore', 'mupen64plus-cpuCore', default='dynamic_recompiler')

        # Framerate
        core_options.set_from_config('mupen64plus-Framerate', default='Original')

        # Parallel-RDP Upscaling
        core_options.set_from_config('mupen64plus-parallel-rdp-upscaling', default='1x')

        # Joystick deadzone
        core_options.set_from_config(
            'mupen64plus-astick-deadzone',
            'mupen64plus-deadzone',
            default='0' if self.config.use_wheels and self.wheels else '15',
        )

        # Joystick sensitivity
        core_options.set_from_config('mupen64plus-astick-sensitivity', 'mupen64plus-sensitivity', default='100')
