from ... import Command
from ... import controllersConfig
from ..Generator import Generator


class AbuseGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["abuse", "-datadir", "/userdata/roms/abuse/abuse_data"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
