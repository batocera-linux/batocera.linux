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
	# os.chdir("/usr/bin/mame")

	# Generate userdata folders if needed
	if not os.path.exists("/userdata/saves/mame/"):
	    os.makedirs("/userdata/saves/mame/")
	if not os.path.exists("/userdata/saves/mame/nvram/"):
	    os.makedirs("/userdata/saves/mame/nvram")
	if not os.path.exists("/userdata/saves/mame/cfg/"):
	    os.makedirs("/userdata/saves/mame/cfg/")
	if not os.path.exists("/userdata/saves/mame/input/"):
	    os.makedirs("/userdata/saves/mame/input/")
	if not os.path.exists("/userdata/saves/mame/state/"):
	    os.makedirs("/userdata/saves/mame/state/")
	if not os.path.exists("/userdata/saves/mame/snap/"):
	    os.makedirs("/userdata/saves/mame/snap/")
	if not os.path.exists("/userdata/saves/mame/diff/"):
	    os.makedirs("/userdata/saves/mame/diff/")
	if not os.path.exists("/userdata/saves/mame/comments/"):
	    os.makedirs("/userdata/saves/mame/comments/")

	# MAME options quick explanation
	# -skip_gameinfo to skip info screen
	# -rompath for the ROMs path
	# -video bgfx for shaders (can be soft accel opengl bgfx)
	# -autoror / -autorol is TATE mode for vertical games (should be a core option)
	# -bgfx_screen_chains specifies the shader can be crt-geom crt-geom-deluxe hlsl eagle hq2x hq3x hq4x
	# A lot more options can be configured, just run mame -showusage and have a look
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
			"-skip_gameinfo",
			"-rompath",      "/userdata/roms/mame/",
			"-bgfx_path",    "/usr/bin/mame/bgfx/",
			"-fontpath",     "/usr/bin/mame/",
			"-languagepath", "/usr/bin/mame/language/",
			"-cheatpath",    "/userdata/cheats/mame/",
			"-samplepath",   "/userdata/bios/mame/samples/",
			"-artpath",	 "/usr/bin/mame/artwork/", # This should be on /userdata but we need to copy "base" files onto /userdata partition

			"-nvram_directory" ,    "/userdata/saves/mame/nvram/",
			"-cfg_directory"   ,    "/userdata/saves/mame/cfg/",
			"-input_directory" ,    "/userdata/saves/mame/input/",
			"-state_directory" ,    "/userdata/saves/mame/state/",
			"-snapshot_directory" , "/userdata/saves/mame/snap/",
			"-diff_directory" ,     "/userdata/saves/mame/diff/",
			"-comment_directory",   "/userdata/saves/mame/comments/",

# TODO -homepath            path to base folder for plugin data (read/write)
# TODO -ctrlrpath           path to controller definitions
# TODO -inipath             path to ini files
# TODO -crosshairpath       path to crosshair files
# TODO -pluginspath         path to plugin files
# TODO -swpath              path to loose software

			"-video", "bgfx",
			"-bgfx_screen_chains",  "crt-geom-deluxe",
			"-autoror",
			romBasename]

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})
