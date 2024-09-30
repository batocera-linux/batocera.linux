import os

from ... import Command
from ... import controllersConfig
from ...utils.logger import get_logger
from ..Generator import Generator

eslog = get_logger(__name__)

class HclGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "hcl",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        try:
            os.chdir("/userdata/roms/hcl/data/map")
            os.chdir("/userdata/roms/hcl/")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the Batocera Content Downloader.")
        commandArray = ["hcl", "-d"]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
