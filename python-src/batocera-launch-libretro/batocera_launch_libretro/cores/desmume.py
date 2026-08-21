from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import AssociatedMouseMixin, Core, LibretroConfig


@cached_dataclass
class Desmume(AssociatedMouseMixin, Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Emulate Stylus on Right Stick
        core_options.set('desmume_pointer_device_r', 'emulated')

        # Internal Resolution
        core_options.set_from_config('desmume_internal_resolution', 'internal_resolution_desmume', default='256x192')

        # Anti-aliasing (MSAA)
        core_options.set_from_config('desmume_gfx_multisampling', 'multisampling', default='disabled')

        # Texture Smoothing
        core_options.set_from_config('desmume_gfx_texture_smoothing', 'texture_smoothing', default='disabled')

        # Textures Upscaling (XBRZ)
        core_options.set_from_config('desmume_gfx_texture_scaling', 'texture_scaling', default='1')

        # Frame Skip
        core_options.set_from_config('desmume_frameskip', 'frameskip_desmume', default='0')

        # Screen Layout
        core_options.set_from_config('desmume_screens_layout', 'screens_layout', default='top/bottom')
