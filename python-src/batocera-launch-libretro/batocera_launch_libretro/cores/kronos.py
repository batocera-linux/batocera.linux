from __future__ import annotations

from typing import ClassVar

from batocera_launch import cached_dataclass
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, GLCoreOverrideMixin, LibretroConfig


@cached_dataclass
class Kronos(GLCoreOverrideMixin, DisableRewindMixin, DisableRunaheadMixin, Core):
    supports_retroachievements: ClassVar = True

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Set best OpenGL renderer
        core_options.set('kronos_videocoretype', 'opengl_cs')

        # Video Resolution
        core_options.set_from_config('kronos_resolution_mode', 'kronos_resolution', default='original')

        # Mesh mode
        core_options.set_from_config('kronos_meshmode', default='disabled')

        # Banding mode
        core_options.set_from_config('kronos_bandingmode', default='disabled')

        # Share saves with Beetle
        core_options.set_from_config('kronos_use_beetle_saves', default='enabled')

        # Multitap
        port1 = 'disabled'
        port2 = 'disabled'

        match self.config.get('kronos_multitap'):
            case 'port1':
                port1 = 'enabled'
            case 'port2':
                port2 = 'enabled'
            case 'port12':
                port1 = 'enabled'
                port2 = 'enabled'
            case _:
                pass

        core_options.set('kronos_multitap_port1', port1)
        core_options.set('kronos_multitap_port2', port2)

        # BIOS langauge
        core_options.set_from_config('kronos_language_id', default='English')
