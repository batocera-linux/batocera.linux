import pathlib

from ... import Command
from ... import controllersConfig
from ..Generator import Generator


class PyxelGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
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
