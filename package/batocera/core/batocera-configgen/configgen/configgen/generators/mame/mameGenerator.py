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
from xml.dom import minidom
import codecs

class MameGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

	# Extract "<romfile.zip>"
        romBasename = path.basename(rom)
        romDirname  = path.dirname(rom)

	# Generate userdata folders if needed
        if not os.path.exists("/userdata/system/configs/mame/"):
	    os.makedirs("/userdata/system/configs/mame/")
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
	if not os.path.exists("/userdata/saves/mame/diff/"):
	    os.makedirs("/userdata/saves/mame/diff/")
	if not os.path.exists("/userdata/saves/mame/comments/"):
	    os.makedirs("/userdata/saves/mame/comments/")

	# MAME options used here are explained as it's not always straightforward
	# A lot more options can be configured, just run mame -showusage and have a look
        commandArray = [ batoceraFiles.batoceraBins[system.config['emulator']] ]
	commandArray += [ "-skip_gameinfo" ]
	commandArray += [ "-rompath",      romDirname ]

	# MAME various paths we can probably do better
	commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
	commandArray += [ "-fontpath",     "/usr/bin/mame/" ]	            # Fonts can be left on ROM filesystem
	commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
	commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path or cheat.7z file ?
	commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
	commandArray += [ "-artpath",	   "/usr/bin/mame/artwork/" ]       # This should be on /userdata but we need to copy "base" files onto /userdata partition

	# MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
	commandArray += [ "-nvram_directory" ,    "/userdata/saves/mame/nvram/" ]
	commandArray += [ "-cfg_directory"   ,    "/userdata/system/configs/mame/" ]
	commandArray += [ "-input_directory" ,    "/userdata/saves/mame/input/" ]
	commandArray += [ "-state_directory" ,    "/userdata/saves/mame/state/" ]
	commandArray += [ "-snapshot_directory" , "/userdata/screenshots/" ]
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
		elif system.isOptSet("bgfxbackend") and system.config["bgfxbackend"] == "gles":
			commandArray += [ "-bgfx_backend", "gles" ]
		elif system.isOptSet("bgfxbackend") and system.config["bgfxbackend"] == "vulkan":
			commandArray += [ "-bgfx_backend", "vulkan" ]
        else
            commandArray += [ "-bgfx_backend", "auto" ]

		# BGFX shaders effects
		if system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "crt-geom":
			commandArray += [ "-bgfx_screen_chains", "crt-geom" ]
		elif system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "crt-geom-deluxe":
			commandArray += [ "-bgfx_screen_chains", "crt-geom-deluxe" ]
		elif system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "eagle":
			commandArray += [ "-bgfx_screen_chains", "eagle" ]
		elif system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hlsl":
			commandArray += [ "-bgfx_screen_chains", "hlsl" ]
		elif system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hq2x":
			commandArray += [ "-bgfx_screen_chains", "hq2x" ]
		elif system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hq3x":
			commandArray += [ "-bgfx_screen_chains", "hq3x" ]
		elif system.isOptSet("bgfxshaders") and system.config["bgfxshaders"] == "hq4x":
			commandArray += [ "-bgfx_screen_chains", "hq4x" ]
        else
            commandArray += [ "-bgfx_screen_chains", "" ]

	# Other video modes
	elif system.isOptSet("video") and system.config["video"] == "accel":
		commandArray += ["-video", "accel" ]
	else # if system.isOptSet("video") and system.config["video"] == "opengl":
		commandArray += [ "-video", "opengl" ]

	# CRT / SwitchRes support
	if system.isOptSet("switchres") and system.config["switchres"] == "true":
		commandArray += [ "-modeline_generation" ]
		commandArray += [ "-changeres" ]
	else:
		commandArray += [ "-nomodeline_generation" ]
		commandArray += [ "-nochangeres" ]

	# Rotation / TATE options
	if system.isOptSet("rotation") and system.config["rotation"] == "autoror":
		commandArray += [ "-autoror" ]
	elif system.isOptSet("rotation") and system.config["rotation"] == "autorol":
		commandArray += [ "-autorol" ]
    else
        commandArray += [ "" ]

	# Finally we pass game name
	commandArray += [ romBasename ]

        # Config file
        config = minidom.Document()
        configFile = "/userdata/system/configs/mame/default.cfg"
        if os.path.exists(configFile):
            try:
                config = minidom.parse(configFile)
            except:
                pass # reinit the file

        MameGenerator.generatePadsConfig(config, playersControllers)

        # Save the config file
        #mameXml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        mameXml = codecs.open(configFile, "w", "utf-8")
        dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        mameXml.write(dom_string)

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})

    @staticmethod
    def getRoot(config, name):
        xml_section = config.getElementsByTagName(name)

        if len(xml_section) == 0:
            xml_section = config.createElement(name)
            config.appendChild(xml_section)
        else:
            xml_section = xml_section[0]

        return xml_section

    @staticmethod
    def getSection(config, xml_root, name):
        xml_section = xml_root.getElementsByTagName(name)

        if len(xml_section) == 0:
            xml_section = config.createElement(name)
            xml_root.appendChild(xml_section)
        else:
            xml_section = xml_section[0]

        return xml_section

    @staticmethod
    def removeSection(config, xml_root, name):
        xml_section = xml_root.getElementsByTagName(name)

        for i in range(0, len(xml_section)):
            old = xml_root.removeChild(xml_section[i])
            old.unlink()

    @staticmethod
    def generatePadsConfig(config, playersControllers):
        mappings = {
            "JOYSTICK_UP":    "joystick1up",
            "JOYSTICK_DOWN":  "joystick1down",
            "JOYSTICK_LEFT":  "joystick1left",
            "JOYSTICK_RIGHT": "joystick1right",
            "JOYSTICKLEFT_UP":    "joystick2up",
            "JOYSTICKLEFT_DOWN":  "joystick2down",
            "JOYSTICKLEFT_LEFT":  "joystick2left",
            "JOYSTICKLEFT_RIGHT": "joystick2right",
            "BUTTON1": "b",
            "BUTTON2": "y",
            "BUTTON3": "a",
            "BUTTON4": "x",
            "BUTTON5": "pageup",
            "BUTTON6": "pagedown",
            "BUTTON7": "l2",
            "BUTTON8": "r2",
            "BUTTON9": "l3",
            "BUTTON10": "r3"
            #"BUTTON11": "",
            #"BUTTON12": "",
            #"BUTTON13": "",
            #"BUTTON14": "",
            #"BUTTON15": ""
        }

        xml_mameconfig = MameGenerator.getRoot(config, "mameconfig")
        xml_system     = MameGenerator.getSection(config, xml_mameconfig, "system")
        xml_system.setAttribute("name", "default")

        MameGenerator.removeSection(config, xml_system, "input")
        xml_input = config.createElement("input")
        xml_system.appendChild(xml_input)

        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            for mapping in mappings:
                if mappings[mapping] in pad.inputs:
                    xml_input.appendChild(MameGenerator.generatePortElement(config, nplayer, pad.index, mapping, mappings[mapping], pad.inputs[mappings[mapping]], False))
                else:
                    rmapping = MameGenerator.reverseMapping(mappings[mapping])
                    if rmapping in pad.inputs:
                        xml_input.appendChild(MameGenerator.generatePortElement(config, nplayer, pad.index, mapping, mappings[mapping], pad.inputs[rmapping], True))
            nplayer = nplayer + 1

    @staticmethod
    def reverseMapping(key):
        if key == "joystick1down":
            return "joystick1up"
        if key == "joystick1right":
            return "joystick1left"
        if key == "joystick2down":
            return "joystick2up"
        if key == "joystick2right":
            return "joystick2left"
        return None

    @staticmethod
    def generatePortElement(config, nplayer, padindex, mapping, key, input, reversed):
        xml_port = config.createElement("port")
        xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode("JOYCODE_{}_{}".format(padindex+1, MameGenerator.input2definition(key, input, reversed)))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def input2definition(key, input, reversed):
        if input.type == "button":
            return "BUTTON{}".format(int(input.id)+1)
        elif input.type == "hat":
            if input.value == "1":
                return "HAT1UP"
            elif input.value == "2":
                return "HAT1RIGHT"
            elif input.value == "4":
                return "HAT1DOWN"
            elif input.value == "8":
                return "HAT1LEFT"
        elif input.type == "axis":
            if key == "joystick1up":
                return "YAXIS_UP_SWITCH"
            if key == "joystick1down":
                return "YAXIS_DOWN_SWITCH"
            if key == "joystick1left":
                return "YAXIS_LEFT_SWITCH"
            if key == "joystick1right":
                return "YAXIS_RIGHT_SWITCH"
            if key == "joystick2up":
                return "RYAXIS_NEG_SWITCH"
            if key == "joystick2down":
                return "RYAXIS_POS_SWITCH"
            if key == "joystick2left":
                return "RXAXIS_NEG_SWITCH"
            if key == "joystick2right":
                return "RXAXIS_POS_SWITCH"
        return "unknown"
