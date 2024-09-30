import os
import configparser

from ... import batoceraFiles
from ... import Command
from ..Generator import Generator
from . import fba2xConfig
from . import fba2xControllers

fbaRoot = batoceraFiles.CONF + '/fba/'
fbaCustom = fbaRoot + 'fba2x.cfg'

class Fba2xGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "fba2x",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        iniConfig = configparser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        iniConfig.optionxform = str
        if os.path.exists(fbaCustom):
            iniConfig.read(fbaCustom)

        fba2xConfig.updateFBAConfig(iniConfig, system)
        fba2xControllers.updateControllersConfig(iniConfig, rom, playersControllers)

        # save the ini file
        if not os.path.exists(os.path.dirname(fbaCustom)):
            os.makedirs(os.path.dirname(fbaCustom))
        with open(fbaCustom, 'w') as configfile:
            iniConfig.write(configfile)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--configfile", fbaCustom, '--logfile', batoceraFiles.logdir+"/fba2x.log"]
        commandArray.append(rom)
        return Command.Command(array=commandArray)
