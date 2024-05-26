#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import controllersConfig
import subprocess

class WineGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if system.name == "windows_installers":
            commandArray = ["batocera-wine", "windows", "install", rom]
            return Command.Command(array=commandArray)
        elif system.name == "windows":
            commandArray = ["batocera-wine", "windows", "play", rom]
            
            environment = {}
            #system.language
            try:
                language = subprocess.check_output("batocera-settings-get system.language", shell=True, text=True).strip()
            except subprocess.CalledProcessError:
                language = 'en_US'
            if language:
                environment.update({
                    "LANG": language + ".UTF-8",
                    "LC_ALL": language + ".UTF-8"
                    }
                )
            # sdl controller option - default is on
            if not system.isOptSet("sdl_config") or system.getOptBoolean("sdl_config"):
                environment.update(
                    {
                        "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                        "SDL_JOYSTICK_HIDAPI": "0"
                    }
                )
            # ensure nvidia driver used for vulkan
            if os.path.exists('/var/tmp/nvidia.prime'):
                variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
                for variable_name in variables_to_remove:
                    if variable_name in os.environ:
                        del os.environ[variable_name]

                environment.update(
                    {
                        'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/nvidia_icd.i686.json',
                    }
                )
            
            return Command.Command(array=commandArray, env=environment)
        
        raise Exception("invalid system " + system.name)

    def getMouseMode(self, config, rom):
        if "force_mouse" in config and config["force_mouse"] == "0":
            return False
        else:
            return True
