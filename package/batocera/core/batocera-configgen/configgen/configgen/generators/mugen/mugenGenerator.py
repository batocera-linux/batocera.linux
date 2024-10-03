from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command, controllersConfig
from ...batoceraPaths import mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class MugenGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "mugen",
            "keys": { "exit": ["KEY_ESC"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        settings_path = rom_path / "data" / "mugen.cfg"
        with settings_path.open('r', encoding='utf-8-sig') as f:
            contents = f.read()

        #clean up
        contents = re.sub(r'^[ ]*;', ';', contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*FullScreen[ ]*=.*', 'FullScreen = 1', contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*GameWidth[ ]*=.*', 'GameWidth = '+str(gameResolution["width"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*GameHeight[ ]*=.*', 'GameHeight = '+str(gameResolution["height"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Width[ ]*=.*', 'Width = '+str(gameResolution["width"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Height[ ]*=.*', 'Height = '+str(gameResolution["height"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Language[ ]*=.*', 'Language = "en"', contents, 0, re.MULTILINE)
        with settings_path.open('w') as f:
            f.write(contents)

        # Save config
        mkdir_if_not_exists(settings_path.parent)

        environment={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        }
        # ensure nvidia driver used for vulkan
        if Path('/var/tmp/nvidia.prime').exists():
            variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
            for variable_name in variables_to_remove:
                if variable_name in os.environ:
                    del os.environ[variable_name]

            environment.update(
                {
                    'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                    'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d'
                }
            )

        commandArray = ["batocera-wine", "mugen", "play", rom_path]
        return Command.Command(
            array=commandArray,
            env=environment
        )
