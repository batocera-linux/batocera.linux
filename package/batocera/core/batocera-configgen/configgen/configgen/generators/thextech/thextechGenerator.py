import Command
from generators.Generator import Generator
from utils.logger import get_logger
import os

eslog = get_logger(__name__)

class TheXTechGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        if not os.path.exists("/userdata/saves/thextech"):
                os.makedirs("/userdata/saves/thextech")

        commandArray = ["/usr/bin/thextech", "-u", "/userdata/saves/thextech"]

        # rendering_mode: sw, hw (default), vsync
        if system.isOptSet('rendering_mode'):
            commandArray.extend(["-r", system.config['rendering_mode']])

        if system.isOptSet('frameskip') and system.getOptBoolean('frameskip') == False:
            commandArray.extend(["--no-frameskip"])
        else:
            commandArray.extend(["--frameskip"])

        commandArray.extend(["-c", rom])

        return Command.Command(array=commandArray)
