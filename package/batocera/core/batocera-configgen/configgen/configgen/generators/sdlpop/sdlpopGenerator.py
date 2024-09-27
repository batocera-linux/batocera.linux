import os
import shutil

from ... import batoceraFiles
from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class SdlPopGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "sdlpop",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "save_state": "KEY_F6", "restore_state": "KEY_F9" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["SDLPoP"]

        # create sdlpop config directory
        if not os.path.exists(batoceraFiles.sdlpopConfigDir):
            os.makedirs(batoceraFiles.sdlpopConfigDir)
        if not os.path.exists(batoceraFiles.sdlpopSrcCfg):
            shutil.copyfile('/usr/share/sdlpop/cfg/SDLPoP.cfg', batoceraFiles.sdlpopSrcCfg)
        if not os.path.exists(batoceraFiles.sdlpopSrcIni):
            shutil.copyfile('/usr/share/sdlpop/cfg/SDLPoP.ini', batoceraFiles.sdlpopSrcIni)
        # symbolic link cfg files
        if not os.path.exists(batoceraFiles.sdlpopDestCfg):
            os.symlink(batoceraFiles.sdlpopSrcCfg, batoceraFiles.sdlpopDestCfg)
        if not os.path.exists(batoceraFiles.sdlpopDestIni):
            os.symlink(batoceraFiles.sdlpopSrcIni, batoceraFiles.sdlpopDestIni)
        # symbolic link screenshot folder too
        if not os.path.exists('/userdata/screenshots/sdlpop'):
            os.makedirs('/userdata/screenshots/sdlpop')
            os.symlink('/userdata/screenshots/sdlpop', '/usr/share/sdlpop/screenshots', target_is_directory = True)

        # pad number
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.append(f"joynum={pad.index}")
            nplayer += 1

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })
