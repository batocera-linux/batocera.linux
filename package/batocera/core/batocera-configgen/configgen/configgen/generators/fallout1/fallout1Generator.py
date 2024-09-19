import configparser
import os
import shutil

from ... import Command
from ... import controllersConfig
from ... import batoceraFiles
from ..Generator import Generator

fout1ConfigDir = batoceraFiles.CONF + "/fallout1"
fout1ConfigFile = fout1ConfigDir + "/fallout.cfg"
fout1IniFile = fout1ConfigDir + "/f1_res.ini"
fout1RomDir = "/userdata/roms/fallout1-ce"
fout1SrcConfig = fout1RomDir + "/fallout.cfg"
fout1SrcIni = fout1RomDir + "/f1_res.ini"
fout1ExeFile = fout1RomDir + "/fallout1-ce"
fout1SourceFile = '/usr/bin/fallout1-ce'

class Fallout1Generator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Check if the directories exist, if not create them
        if not os.path.exists(fout1ConfigDir):
            os.makedirs(fout1ConfigDir)

        # Copy latest binary to the rom directory
        if not os.path.exists(fout1ExeFile):
            shutil.copy(fout1SourceFile, fout1ExeFile)
        else:
            source_version = os.path.getmtime(fout1SourceFile)
            destination_version = os.path.getmtime(fout1ExeFile)
            if source_version > destination_version:
                shutil.copy(fout1SourceFile, fout1ExeFile)

        # Copy cfg file to the config directory
        if not os.path.exists(fout1ConfigFile):
            if os.path.exists(fout1SrcConfig):
                shutil.copy(fout1SrcConfig , fout1ConfigFile)

        # Now copy the ini file to the config directory
        if not os.path.exists(fout1IniFile):
            if os.path.exists(fout1SrcIni):
                shutil.copy(fout1SrcIni , fout1IniFile)

        ## Configure

        ## CFG Configuration
        fout1Cfg = configparser.ConfigParser()
        fout1Cfg.optionxform = str
        if os.path.exists(fout1ConfigFile):
            fout1Cfg.read(fout1ConfigFile)

        if not fout1Cfg.has_section("debug"):
            fout1Cfg.add_section("debug")
        if not fout1Cfg.has_section("preferences"):
            fout1Cfg.add_section("preferences")
        if not fout1Cfg.has_section("sound"):
            fout1Cfg.add_section("sound")
        if not fout1Cfg.has_section("system"):
            fout1Cfg.add_section("system")

        # fix linux path issues
        fout1Cfg.set("sound", "music_path1", "DATA/SOUND/MUSIC/")
        fout1Cfg.set("sound", "music_path2", "DATA/SOUND/MUSIC/")

        fout1Cfg.set("system", "critter_dat", "CRITTER.DAT")
        fout1Cfg.set("system", "critter_patches", "DATA")
        fout1Cfg.set("system", "master_dat", "MASTER.DAT")
        fout1Cfg.set("system", "master_patches", "DATA")

        if system.isOptSet("fout1_game_difficulty"):
            fout1Cfg.set("preferences", "game_difficulty", system.config["fout1_game_difficulty"])
        else:
            fout1Cfg.set("preferences", "game_difficulty", "1")

        if system.isOptSet("fout1_combat_difficulty"):
            fout1Cfg.set("preferences", "combat_difficulty", system.config["fout1_combat_difficulty"])
        else:
            fout1Cfg.set("preferences", "combat_difficulty", "1")

        if system.isOptSet("fout1_violence_level"):
            fout1Cfg.set("preferences", "violence_level", system.config["fout1_violence_level"])
        else:
            fout1Cfg.set("preferences", "violence_level", "2")

        if system.isOptSet("fout1_subtitles"):
            fout1Cfg.set("preferences", "subtitles", system.config["fout1_subtitles"])
        else:
            fout1Cfg.set("preferences", "subtitles", "0")

        if system.isOptSet("fout1_language"):
            fout1Cfg.set("system", "language", system.config["fout1_language"])
        else:
            fout1Cfg.set("system", "language", "english")

        with open(fout1ConfigFile, "w") as configfile:
            fout1Cfg.write(configfile)

        ## INI Configuration
        fout1Ini = configparser.ConfigParser()
        fout1Ini.optionxform = str
        if os.path.exists(fout1IniFile):
            fout1Ini.read(fout1IniFile)

        # [MAIN]
        if not fout1Ini.has_section("MAIN"):
            fout1Ini.add_section("MAIN")

        # Note: This will increase the minimum resolution to from 640x480 to 1280x960.
        if gameResolution["width"] >= 1280 and gameResolution["height"] >= 960:
            fout1Ini.set("MAIN", "SCALE_2X", "1")
        else:
            fout1Ini.set("MAIN", "SCALE_2X", "0")
        fout1Ini.set("MAIN", "SCR_WIDTH", format(gameResolution["width"]))
        fout1Ini.set("MAIN", "SCR_HEIGHT", format(gameResolution["height"]))

        # fullscreen
        fout1Ini.set("MAIN", "WINDOWED", "0")

        with open(fout1IniFile, "w") as configfile:
            fout1Ini.write(configfile)

        # IMPORTANT: Move dir before executing
        os.chdir(fout1RomDir)

        ## Setup the command
        commandArray = ["fallout1-ce"]

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
