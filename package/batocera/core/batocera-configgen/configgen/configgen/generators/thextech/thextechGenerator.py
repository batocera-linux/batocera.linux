import Command
from generators.Generator import Generator
from utils.logger import get_logger

eslog = get_logger(__name__)

class TheXTechGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        commandArray = ["/usr/bin/thextech", "-c", rom]

        return Command.Command(array=commandArray)
