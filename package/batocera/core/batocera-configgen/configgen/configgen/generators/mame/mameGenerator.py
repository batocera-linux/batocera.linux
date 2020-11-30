#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from utils.logger import eslog
from os import path
from os import environ
import ConfigParser

class MameGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        romBasename = path.basename(rom)

	# Right now, hack to get into the proper MAME distro directory
	os.chdir("/usr/bin/mame")

	# MAME options quick explanation
	# -skip_gameinfo to skip info screen
	# -rompath for the ROMs path
	# -video bgfx for shaders (can be soft accel opengl bgfx)
	# -autoror / -autorol is TATE mode for vertical games (should be a core option)
	# -bgfx_screen_chains specifies the shader can be crt-geom crt-geom-deluxe hlsl
	# A lot more options can be configured, just run mame -showusage and have a look
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
			"-skip_gameinfo",
			"-rompath",   "/userdata/roms/mame/",
			"-bgfx_path", "/usr/bin/mame/bgfx/",
# TODO -homepath            path to base folder for plugin data (read/write)
# TODO -samplepath          path to audio sample sets
# TODO -artpath             path to artwork files
# TODO -ctrlrpath           path to controller definitions
# TODO -inipath             path to ini files
# TODO -fontpath            path to font files
# TODO -cheatpath           path to cheat files
# TODO -crosshairpath       path to crosshair files
# TODO -pluginspath         path to plugin files
# TODO -languagepath        path to UI translation files
# TODO -swpath              path to loose software
			"-nvram_directory" ,    "/userdata/saves/mame/nvram/",
			"-cfg_directory"   ,    "/userdata/saves/mame/cfg/",
			"-input_directory" ,    "/userdata/saves/mame/input/",
			"-state_directory" ,    "/userdata/saves/mame/state/",
			"-snapshot_directory" , "/userdata/saves/mame/snap",
			"-diff_directory" ,     "/userdata/saves/mame/diff",
			"-comment_directory",   "/userdata/saves/mame/comments",

			"-video", "bgfx",
			"-bgfx_screen_chains",  "crt-geom-deluxe",
			"-autoror",
			romBasename]

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})
