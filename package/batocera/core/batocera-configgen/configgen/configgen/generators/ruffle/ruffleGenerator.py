from ... import Command
from ..Generator import Generator


class RuffleGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["ruffle", rom]
        return Command.Command(
            array=commandArray)

    def getMouseMode(self, config, rom):
        return True
