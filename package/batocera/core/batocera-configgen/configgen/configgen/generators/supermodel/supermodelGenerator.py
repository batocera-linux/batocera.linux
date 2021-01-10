#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import shutil
import os.path

class SupermodelGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["supermodel", "-legacy3d", "-fullscreen", "-res=1024,768", rom]
        return Command.Command(array=commandArray, env={'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)})
        
# Set resolution manually currently - 1024x768 should be fine for most systems.
# Set -legacy3d for older GPU's - will need to look at an option here too in future.
