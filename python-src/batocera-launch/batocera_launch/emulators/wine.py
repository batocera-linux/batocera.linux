from __future__ import annotations

import os
from pathlib import Path

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext


@cached_dataclass
class Wine(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'wine',
            'keys': {'exit': '/usr/bin/batocera-wine windows stop'},
        }

    @property
    def needs_mouse(self) -> bool:
        return self.config.get_bool('force_mouse')

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        if self.system == 'windows_installers':
            return Command(['batocera-wine', 'windows', 'install', self.rom])

        if self.system != 'windows':
            raise BatoceraException(f'Invalid system: {self.system}')

        language = self.config.get_str('system.language', 'en_US')
        environment: dict[str, str | Path] = {
            'LANG': f'{language}.UTF-8',
            'LC_ALL': f'{language}.UTF-8',
        }

        if self.config.get_bool('sdl_config', True):
            environment.update(
                SDL_GAMECONTROLLERCONFIG=self.get_sdl_game_controller_config(),
                SDL_JOYSTICK_HIDAPI='0',
            )

        # ensure the nvidia driver gets used for vulkan
        if Path('/var/tmp/nvidia.prime').exists():
            for variable_name in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
                os.environ.pop(variable_name, None)

            environment['VK_ICD_FILENAMES'] = (
                '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/nvidia_icd.i686.json'
            )

        return Command(['batocera-wine', 'windows', 'play', self.rom], env=environment)
