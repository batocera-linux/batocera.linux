#!/usr/bin/env python
import Command
from generators.Generator import Generator
import controllersConfig
import pathlib


class PyxelGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        if pathlib.Path(rom).suffix == '.pyxapp':
            cmd = 'play'
        else:
            cmd = 'run' 
	
        commandArray = ["/usr/bin/pyxel", cmd, rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
