import os

from ... import batoceraFiles
from ... import Command
from ... import controllersConfig
from ...settings.unixSettings import UnixSettings
from ...utils.logger import get_logger
from ..Generator import Generator

eslog = get_logger(__name__)
CONFIGDIR  = batoceraFiles.CONF + '/applewin'
CONFIGFILE = CONFIGDIR + '/config.txt'

class AppleWinGenerator(Generator):
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if not os.path.exists(CONFIGDIR):
            os.makedirs(CONFIGDIR)

        config = UnixSettings(CONFIGFILE, separator=' ')

        rombase=os.path.basename(rom)
        romext=os.path.splitext(rombase)[1]

        config.write()
        commandArray = ["applewin" ]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
