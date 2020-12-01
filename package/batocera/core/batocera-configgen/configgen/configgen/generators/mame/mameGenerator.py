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

	# Extract "<romfile.zip>"
        romBasename = path.basename(rom)

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

	# MAME options used here are explained as it's not always straightforward
	# A lot more options can be configured, just run mame -showusage and have a look
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],

			# -skip_gameinfo to skip info screen
			"-skip_gameinfo",
			# -rompath for the ROMs path
			"-rompath",      "/userdata/roms/mame/",

			# MAME various paths we can probably do better
			"-bgfx_path",    "/usr/bin/mame/bgfx/",          # Core bgfx files can be left on ROM filesystem
			"-fontpath",     "/usr/bin/mame/",	         # Fonts can be left on ROM filesystem
			"-languagepath", "/usr/bin/mame/language/",      # Translations can be left on ROM filesystem
			"-cheatpath",    "/userdata/cheats/mame/",       # Should this point to path or cheat.7z file ?
			"-samplepath",   "/userdata/bios/mame/samples/", # Current batocera storage location for MAME samples
			"-artpath",	 "/usr/bin/mame/artwork/",       # This should be on /userdata but we need to copy "base" files onto /userdata partition

			# MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
			"-nvram_directory" ,    "/userdata/saves/mame/nvram/",
			"-cfg_directory"   ,    "/userdata/saves/mame/cfg/",
			"-input_directory" ,    "/userdata/saves/mame/input/",
			"-state_directory" ,    "/userdata/saves/mame/state/",
			"-snapshot_directory" , "/userdata/saves/mame/snap/",
			"-diff_directory" ,     "/userdata/saves/mame/diff/",
			"-comment_directory",   "/userdata/saves/mame/comments/",
			]

			# TODO These paths are not handled yet
			# TODO -homepath            path to base folder for plugin data (read/write)
			# TODO -ctrlrpath           path to controller definitions
			# TODO -inipath             path to ini files
			# TODO -crosshairpath       path to crosshair files
			# TODO -pluginspath         path to plugin files
			# TODO -swpath              path to loose software

			# Rendering options
			# Video can be : soft (slow, useless), accel (SDL2), opengl, or bgfx (shaders/effects)
			# SHOULD BE A CORE OPTION EXPOSED IN ES

	# If BGFX is selected
	commandArray += [
			"-video", "bgfx",
			# -bgfx_screen_chains specifies the shader can be crt-geom crt-geom-deluxe hlsl eagle hq2x hq3x hq4x
			# SHOULD BE A CORE OPTION EXPOSED IN ES
			"-bgfx_screen_chains",  "crt-geom-deluxe",
			# -bgfx_backend can be opengl gles vulkan
			# SHOULD BE A CORE OPTION EXPOSED IN ES
			"-bgfx_backend", "auto",
			]

	# If accel is selected
	#commandArray += [
	#		"-video", "accel",
	#		]

	# If opengl is selected
	#commandArray += [
	#		"-video", "opengl",
	#		]

	# Rotation / TATE options : autoror (CW 90), autorol (CCW 90) depending on system configuration
	commandArray += [ "-autoror" ] # "-autorol"

	# Finally we pass game name
	commandArray += [ romBasename ]

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})
