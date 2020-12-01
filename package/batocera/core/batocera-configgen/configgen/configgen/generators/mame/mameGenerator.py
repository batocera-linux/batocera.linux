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
        commandArray = [ batoceraFiles.batoceraBins[system.config['emulator']] ]
	commandArray += [ "-skip_gameinfo" ]
	commandArray += [ "-rompath",      "/userdata/roms/mame/" ]

	# MAME various paths we can probably do better
	commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
	commandArray += [ "-fontpath",     "/usr/bin/mame/" ]	            # Fonts can be left on ROM filesystem
	commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
	commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path or cheat.7z file ?
	commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
	commandArray += [ "-artpath",	   "/usr/bin/mame/artwork/" ]       # This should be on /userdata but we need to copy "base" files onto /userdata partition

	# MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
	commandArray += [ "-nvram_directory" ,    "/userdata/saves/mame/nvram/" ]
	commandArray += [ "-cfg_directory"   ,    "/userdata/saves/mame/cfg/" ]
	commandArray += [ "-input_directory" ,    "/userdata/saves/mame/input/" ]
	commandArray += [ "-state_directory" ,    "/userdata/saves/mame/state/" ]
	commandArray += [ "-snapshot_directory" , "/userdata/saves/mame/snap/" ]
	commandArray += [ "-diff_directory" ,     "/userdata/saves/mame/diff/" ]
	commandArray += ["-comment_directory",   "/userdata/saves/mame/comments/" ]

	# TODO These paths are not handled yet
	# TODO -homepath            path to base folder for plugin data (read/write)
	# TODO -ctrlrpath           path to controller definitions
	# TODO -inipath             path to ini files
	# TODO -crosshairpath       path to crosshair files
	# TODO -pluginspath         path to plugin files
	# TODO -swpath              path to loose software

	# BGFX video engine
	if system.isOptSet("video") and system.config["video"] == "bgfx":
		commandArray += [ "-video", "bgfx" ]

		# BGFX backend
		if system.isOptSet("bgfxbackend") and system.config["bgfxbackend"] == "opengl":
			commandArray += [ "-bgfx_backend", "opengl" ]
		if system.isOptSet("bgfxbackend") and system.config["bgfxbackend"] == "gles":
			commandArray += [ "-bgfx_backend", "gles" ]
		if system.isOptSet("bgfxbackend") and system.config["bgfxbackend"] == "vulkan":
			commandArray += [ "-bgfx_backend", "vulkan" ]

		# BGFX shaders effects
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "crt-geom":
			commandArray += [ "-bgfx_screen_chains", "crt-geom" ]
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "crt-geom-deluxe":
			commandArray += [ "-bgfx_screen_chains", "crt-geom-deluxe" ]
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "eagle":
			commandArray += [ "-bgfx_screen_chains", "eagle" ]
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hlsl":
			commandArray += [ "-bgfx_screen_chains", "hlsl" ]
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hq2x":
			commandArray += [ "-bgfx_screen_chains", "hq2x" ]
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hq3x":
			commandArray += [ "-bgfx_screen_chains", "hq3x" ]
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hq4x":
			commandArray += [ "-bgfx_screen_chains", "hq4x" ]

	# Other video modes
	if system.isOptSet("video") and system.config["video"] == "accel":
		commandArray += ["-video", "accel" ]
	if system.isOptSet("video") and system.config["video"] == "opengl":
		commandArray += [ "-video", "opengl" ]

	# Rotation / TATE options
	if system.isOptSet("rotation") and system.config["rotation"] == "autoror":
		commandArray += [ "-autoror" ]
	if system.isOptSet("rotation") and system.config["rotation"] == "autorol":
		commandArray += [ "-autorol" ]

	# Finally we pass game name
	commandArray += [ romBasename ]

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})
