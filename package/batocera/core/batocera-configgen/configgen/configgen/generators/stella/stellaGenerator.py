from ... import Command
from ... import controllersConfig
from ...utils.logger import get_logger
from ..Generator import Generator

eslog = get_logger(__name__)

class StellaGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Launch Stella
        commandArray = ["stella " , rom ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
