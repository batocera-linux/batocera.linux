#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import shutil
import os.path

class SupermodelGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["supermodel", "-fullscreen", "-res=1024,768", rom]
        return Command.Command(array=commandArray, env={'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)})
