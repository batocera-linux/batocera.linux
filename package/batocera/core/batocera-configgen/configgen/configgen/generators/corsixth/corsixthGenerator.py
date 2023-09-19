#!/usr/bin/env python
import Command
from generators.Generator import Generator
import controllersConfig
import os
import batoceraFiles
import subprocess

corsixthConfigPath = batoceraFiles.CONF + "/corsixth"
corsixthConfigFile = corsixthConfigPath + "/config.txt"
corsixthSavesPath = "/userdata/saves/corsixth"
corsixthDataPath = "/userdata/roms/corsixth"
corsixthFontPath = "/usr/share/fonts/dejavu/DejaVuSans.ttf"
corsixthScreenshotsPath = "/userdata/screenshots"

from utils.logger import get_logger
eslog = get_logger(__name__)

class CorsixTHGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        # Create corsixth config directory if needed
        if not os.path.exists(corsixthConfigPath):
            os.makedirs(corsixthConfigPath)

        # Create corsixth savesg directory if needed
        if not os.path.exists(corsixthSavesPath):
            os.makedirs(corsixthSavesPath)

        # Check game data is installed
        try:
            os.chdir("/userdata/roms/corsixth/ANIMS/")
            os.chdir("/userdata/roms/corsixth/DATA/")
            os.chdir("/userdata/roms/corsixth/INTRO/")
            os.chdir("/userdata/roms/corsixth/LEVELS/")
            os.chdir("/userdata/roms/corsixth/QDATA/")
        except:
            eslog.error("ERROR: Game assets not installed. You can get them from the game Theme Hospital.")

        # If config file already exists, delete it
        if os.path.exists(corsixthConfigFile):
            os.unlink(corsixthConfigFile)

        # Create the config file and fill it with basic data
        source_config_file = open(corsixthConfigFile, "w")
        source_config_file.write("check_for_updates = false\n")
        source_config_file.write("theme_hospital_install = [[" + corsixthDataPath +"]]\n")
        source_config_file.write("unicode_font = [[" + corsixthFontPath + "]]\n")
        source_config_file.write("savegames = [[" + corsixthSavesPath + "]]\n")
        source_config_file.write("screenshots = [[" + corsixthScreenshotsPath +"]]\n")

        # Values coming from ES configuration : Resolution
        source_config_file.write("fullscreen = true\n")
        source_config_file.write("width = " + str(gameResolution["width"]) +"\n")
        source_config_file.write("height = " + str(gameResolution["height"]) + "\n")

        # Values coming from ES configuration : New Graphics
        if system.isOptSet('cth_new_graphics'):
          source_config_file.write("use_new_graphics = "+ system.config['cth_new_graphics'] +"\n")
        else:
          source_config_file.write("use_new_graphics = true\n")

        # Values coming from ES configuration : Sandbox Mode
        if system.isOptSet('cth_free_build_mode'):
          source_config_file.write("free_build_mode = "+ system.config['cth_free_build_mode'] +"\n")
        else:
          source_config_file.write("free_build_mode = false\n")

        # Values coming from ES configuration : Intro Movie
        if system.isOptSet('cth_play_intro'):
          source_config_file.write("play_intro = "+ system.config['cth_play_intro'] +"\n")
        else:
          source_config_file.write("play_intro = true\n")

        # Now auto-set the language from batocera ES locale
        # 1. Grab batocera system language
        language = 'en_US'
        corsixthLanguage = 'en'
        try:
            language = subprocess.check_output("batocera-settings-get system.language", shell=True, text=True).strip()
        except subprocess.CalledProcessError:
            language = 'en_US'
        # 2. Map it
        # English = en
        if language == 'en_US' or language == 'en_GB':
            corsixthLanguage = 'en'
        # French = fr
        elif language == 'fr_FR' or language == 'oc_FR':
            corsixthLanguage = 'fr'
        # German = de
        elif language == 'de_DE':
            corsixthLanguage = 'de'
        # Spanish = es
        elif language == 'es_ES' or language == 'es_MX':
            corsixthLanguage = 'es'
        # Italian = it
        elif language == 'it_IT':
            corsixthLanguage = 'it'
        # Dutch = nl
        elif language == 'nl_NL':
            corsixthLanguage = 'nl'
        # Russian = ru
        elif language == 'ru_RU':
            corsixthLanguage = 'ru'
        # Swedish = sv
        elif language == 'sv_SE':
            corsixthLanguage = 'sv'
        # Czech = cs
        elif language == 'cs_CZ':
            corsixthLanguage = 'cs'
        # Finnish = fi
        elif language == 'fi_FI':
            corsixthLanguage = 'fi'
        # Polish = pl
        elif language == 'pl_PL':
            corsixthLanguage = 'pl'
        # Hungarian = hu
        elif language == 'hu_HU':
            corsixthLanguage = 'hu'
        # Portuguese = pt
        elif language == 'pt_PT':
            corsixthLanguage = 'pt'
        # Brazilian Portuguese = br
        elif language == 'pt_BR':
            corsixthLanguage = 'br'
        # Chinese (simplified) = zhs
        elif language == 'zh_CN':
            corsixthLanguage = 'zhs'
        # Chinese (traditional) = zht
        elif language == 'zh_TW':
            corsixthLanguage = 'zht'
        # Korean = ko
        elif language == 'ko_KR':
            corsixthLanguage = 'ko'
        # Norwegian = nb
        elif language == 'nb_NO' or language == 'nn_NO':
            corsixthLanguage = 'nb'
        # Danish = da
        # TODO
        # 3. Write it
        source_config_file.write("language = [[" + corsixthLanguage +"]]\n")

        # Check custom music is installed
        try:
            os.chdir(corsixthDataPath +"/MP3")
            source_config_file.write("audio_music = [[" + corsixthDataPath + "/MP3" +"]]\n")
        except:
            eslog.warning("NOTICE: Audio & Music system loaded, but found no external background tracks. Missing MP3 folder")
            source_config_file.write("audio_music = nil\n")

        # Close config file as we are done
        source_config_file.close()

        # Launch engine with config file path
        commandArray = ["corsix-th", "--config-file=" + corsixthConfigFile]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
