#!/usr/bin/env python
from generators.Generator import Generator
import Command
import os
import controllersConfig
import re

class MugenGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        settings_path = rom + "/data/mugen.cfg"
        with open(settings_path, 'r', encoding='utf-8-sig') as f:
            contents = f.read()

        #clean up
        contents = re.sub(r'^[ ]*;', ';', contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*FullScreen[ ]*=.*', 'FullScreen = 1', contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*GameWidth[ ]*=.*', 'GameWidth = '+str(gameResolution["width"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*GameHeight[ ]*=.*', 'GameHeight = '+str(gameResolution["height"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Width[ ]*=.*', 'Width = '+str(gameResolution["width"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Height[ ]*=.*', 'Height = '+str(gameResolution["height"]), contents, 0, re.MULTILINE)
        contents = re.sub(r'^[ ;]*Language[ ]*=.*', 'Language = "en"', contents, 0, re.MULTILINE)
        with open(settings_path, 'w') as f:
            f.write(contents)

        # Save config
        if not os.path.exists(os.path.dirname(settings_path)):
            os.makedirs(os.path.dirname(settings_path))

        environment={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        }
        # ensure nvidia driver used for vulkan
        if os.path.exists('/var/tmp/nvidia.prime'):
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

        commandArray = ["batocera-wine", "mugen", "play", rom]
        return Command.Command(
            array=commandArray,
            env=environment
        )
