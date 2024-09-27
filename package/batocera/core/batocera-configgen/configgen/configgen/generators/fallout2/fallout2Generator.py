import configparser
import os
import shutil

from ... import Command
from ... import controllersConfig
from ... import batoceraFiles
from ..Generator import Generator

fout2ConfigDir = batoceraFiles.CONF + "/fallout2"
fout2ConfigFile = fout2ConfigDir + "/fallout2.cfg"
fout2IniFile = fout2ConfigDir + "/f2_res.ini"
fout2RomDir = "/userdata/roms/fallout2-ce"
fout2SrcConfig = fout2RomDir + "/fallout2.cfg"
fout2SrcIni = fout2RomDir + "/f2_res.ini"
fout2ExeFile = fout2RomDir + "/fallout2-ce"
fout2SourceFile = '/usr/bin/fallout2-ce'

class Fallout2Generator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "fallout2",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "save_state": "KEY_F6", "restore_state": "KEY_F7" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Check if the directories exist, if not create them
        if not os.path.exists(fout2ConfigDir):
            os.makedirs(fout2ConfigDir)

        # Copy latest binary to the rom directory
        if not os.path.exists(fout2ExeFile):
            shutil.copy(fout2SourceFile, fout2ExeFile)
        else:
            source_version = os.path.getmtime(fout2SourceFile)
            destination_version = os.path.getmtime(fout2ExeFile)
            if source_version > destination_version:
                shutil.copy(fout2SourceFile, fout2ExeFile)

        # Copy cfg file to the config directory
        if not os.path.exists(fout2ConfigFile):
            if os.path.exists(fout2SrcConfig):
                shutil.copy(fout2SrcConfig , fout2ConfigFile)

        # Now copy the ini file to the config directory
        if not os.path.exists(fout2IniFile):
            if os.path.exists(fout2SrcIni):
                shutil.copy(fout2SrcIni , fout2IniFile)

        ## Configure

        ## CFG Configuration
        fout2Cfg = configparser.ConfigParser()
        fout2Cfg.optionxform = str
        if os.path.exists(fout2ConfigFile):
            fout2Cfg.read(fout2ConfigFile)

        if not fout2Cfg.has_section("debug"):
            fout2Cfg.add_section("debug")
        if not fout2Cfg.has_section("preferences"):
            fout2Cfg.add_section("preferences")
        if not fout2Cfg.has_section("sound"):
            fout2Cfg.add_section("sound")
        if not fout2Cfg.has_section("system"):
            fout2Cfg.add_section("system")

        # fix linux path issues
        fout2Cfg.set("sound", "music_path1", "sound/music/")
        fout2Cfg.set("sound", "music_path2", "sound/music/")

        #fout2Cfg.set("system", "critter_dat", "CRITTER.DAT")
        #fout2Cfg.set("system", "critter_patches", "DATA")
        #fout2Cfg.set("system", "master_dat", "MASTER.DAT")
        #fout2Cfg.set("system", "master_patches", "DATA")

        if system.isOptSet("fout2_game_difficulty"):
            fout2Cfg.set("preferences", "game_difficulty", system.config["fout2_game_difficulty"])
        else:
            fout2Cfg.set("preferences", "game_difficulty", "1")

        if system.isOptSet("fout2_combat_difficulty"):
            fout2Cfg.set("preferences", "combat_difficulty", system.config["fout2_combat_difficulty"])
        else:
            fout2Cfg.set("preferences", "combat_difficulty", "1")

        if system.isOptSet("fout2_violence_level"):
            fout2Cfg.set("preferences", "violence_level", system.config["fout2_violence_level"])
        else:
            fout2Cfg.set("preferences", "violence_level", "2")

        if system.isOptSet("fout2_subtitles"):
            fout2Cfg.set("preferences", "subtitles", system.config["fout2_subtitles"])
        else:
            fout2Cfg.set("preferences", "subtitles", "0")

        if system.isOptSet("fout2_language"):
            fout2Cfg.set("system", "language", system.config["fout2_language"])
        else:
            fout2Cfg.set("system", "language", "english")

        with open(fout2ConfigFile, "w") as configfile:
            fout2Cfg.write(configfile)

        ## INI Configuration
        fout2Ini = configparser.ConfigParser()
        fout2Ini.optionxform = str
        if os.path.exists(fout2IniFile):
            fout2Ini.read(fout2IniFile)

        # [MAIN]
        if not fout2Ini.has_section("MAIN"):
            fout2Ini.add_section("MAIN")

        # Note: This will increase the minimum resolution to from 640x480 to 1280x960.
        if gameResolution["width"] >= 1280 and gameResolution["height"] >= 960:
            fout2Ini.set("MAIN", "SCALE_2X", "1")
        else:
            fout2Ini.set("MAIN", "SCALE_2X", "0")
        fout2Ini.set("MAIN", "SCR_WIDTH", format(gameResolution["width"]))
        fout2Ini.set("MAIN", "SCR_HEIGHT", format(gameResolution["height"]))

        # fullscreen
        fout2Ini.set("MAIN", "WINDOWED", "0")

        # fix path
        fout2Ini.set("MAIN", "f2_res_patches", "data/")

        with open(fout2IniFile, "w") as configfile:
            fout2Ini.write(configfile)

        # IMPORTANT: Move dir before executing
        os.chdir(fout2RomDir)

        ## Setup the command
        commandArray = ["fallout2-ce"]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
