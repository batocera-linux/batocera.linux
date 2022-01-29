#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os
import batoceraFiles
import filecmp
import codecs

redream_file = "/usr/bin/redream"
redreamConfig = batoceraFiles.CONF + "/redream"

class RedreamGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        redream_exec = redreamConfig + "/redream"

        if not os.path.exists(redreamConfig):
            os.makedirs(redreamConfig)

        if not os.path.exists(redream_exec) or not filecmp.cmp(redream_file, redream_exec):
            copyfile(redream_file, redream_exec)
            os.chmod(redream_exec, 0o0775)
        
        configFileName = redreamConfig + "/redream.cfg"
        f = codecs.open(configFileName, "w")
        # set the roms path
        f.write("gamedir=/userdata/roms/dreamcast\n")
        # force fullscreen
        f.write("mode=exclusive fullscreen\n")
        f.write("fullmode=exclusive fullscreen\n")
        # todo change controller config for exit

        # change settings as per users options
        # video
        f.write("fullwidth={}".format(gameResolution["width"]))
        f.write("fullheight={}".format(gameResolution["height"]))
        if system.isOptSet("redreamResolution"):
            f.write("res={}".format(system.config["redreamResolution"]) + "\n")
        else:
            f.write("res=2\n")
        if system.isOptSet("redreamRatio"):
            f.write("aspect={}".format(system.config["redreamRatio"]) + "\n")
        else:
            f.write("aspect=4:3\n")
        if system.isOptSet("redreamFrameSkip"):
            f.write("frameskip={}".format(system.config["redreamFrameSkip"]) + "\n")
        else:
            f.write("frameskip=0\n")
        if system.isOptSet("redreamVsync"):
            f.write("vysnc={}".format(system.config["redreamVsync"]) + "\n")
        else:
            f.write("vsync=0\n")
        if system.isOptSet("redreamPolygon"):
            f.write("autosort={}".format(system.config["redreamPolygon"]) + "\n")
        else:
            f.write("autosort=0\n")
        # system
        if system.isOptSet("redreamRegion"):
            f.write("region={}".format(system.config["redreamRegion"]) + "\n")
        else:
            f.write("region=usa\n")
        if system.isOptSet("redreamLanguage"):
            f.write("language={}".format(system.config["redreamLanguage"]) + "\n")
        else:
            f.write("language=english\n")
        if system.isOptSet("redreamBroadcast"):
            f.write("broadcast={}".format(system.config["redreamBroadcast"]) + "\n")
        else:
            f.write("broadcast=ntsc\n")
        if system.isOptSet("redreamCable"):
            f.write("cable={}".format(system.config["redreamCable"]) + "\n")
        else:
            f.write("cable=vga\n")
        
        f.write
        f.close()

        commandArray = [redream_exec, rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
