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
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-skip_gameinfo", "-rompath", "/userdata/roms/mame/", "-video",  "bgfx", "-autoror", "-bgfx_screen_chains",  "crt-geom-deluxe", "-bgfx_path", "/usr/bin/mame/bgfx/", romBasename]

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})
