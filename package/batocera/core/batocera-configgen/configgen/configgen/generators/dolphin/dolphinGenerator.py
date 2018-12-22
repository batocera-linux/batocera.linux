#!/usr/bin/env python
import Command
import recalboxFiles
from generators.Generator import Generator
import dolphinControllers
import dolphinSYSCONF
import shutil
import os.path
from os import environ
import ConfigParser
from settings.unixSettings import UnixSettings

# seem to be only for the gamecube. However, while this is not in a gamecube section
# it may be used for something else, so set it anyway

def getGameCubeLangFromEnvironment():
    lang = environ['LANG'][:5]
    availableLanguages = { "en_US": 0, "de_DE": 1, "fr_FR": 2, "es_ES": 3, "it_IT": 4, "nl_NL": 5 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]

class DolphinGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        dolphinControllers.generateControllerConfig(system, playersControllers, rom)

        dolphinSettings = UnixSettings(recalboxFiles.dolphinIni, separator=' ')

        #Draw or not FPS
	if system.config['showFPS'] == 'true':
            dolphinSettings.save("ShowLag", "True")
            dolphinSettings.save("ShowFrameCount", "True")
        else:
            dolphinSettings.save("ShowLag", "False")
            dolphinSettings.save("ShowFrameCount", "False")

        # don't ask about statistics
        dolphinSettings.save("PermissionAsked", "True")

        # don't confirm at stop
        dolphinSettings.save("ConfirmStop", "False")

        # language (for gamecube at least)
        dolphinSettings.save("SelectedLanguage", getGameCubeLangFromEnvironment())
        dolphinSettings.save("GameCubeLanguage", getGameCubeLangFromEnvironment())

        # update GFX
        dolphinGFXSettings = ConfigParser.ConfigParser()
        # To prevent ConfigParser from converting to lower case
        dolphinGFXSettings.optionxform = str
        dolphinGFXSettings.read(recalboxFiles.dolphinGfxIni)

        if not dolphinGFXSettings.has_section("Settings"):
            dolphinGFXSettings.add_section("Settings")
        dolphinGFXSettings.set("Settings", "AspectRatio", getGfxRatioFromConfig(system.config, gameResolution))
        cfgfile = open(recalboxFiles.dolphinGfxIni,'w+')
        dolphinGFXSettings.write(cfgfile)
        cfgfile.close()

        # update SYSCONF
        try:
            dolphinSYSCONF.update(system.config, recalboxFiles.dolphinSYSCONF, gameResolution)
        except Exception:
            pass # don't fail in case of SYSCONF update

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "-e", rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":recalboxFiles.CONF, "XDG_DATA_HOME":recalboxFiles.SAVES})

def getGfxRatioFromConfig(config, gameResolution):
    # 2: 4:3 ; 1: 16:9
    if "ratio" in config:
        if config["ratio"] == "4/3" or (config["ratio"] == "auto" and gameResolution["width"] / float(gameResolution["height"]) < (16.0 / 9.0) - 0.1): # let a marge):
            return 2
        else:
            return 1
    return 2
