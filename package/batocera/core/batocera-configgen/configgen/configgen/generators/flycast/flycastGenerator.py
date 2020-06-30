#!/usr/bin/env python
import Command
#~ import flycastControllers
import batoceraFiles
from generators.Generator import Generator
import flycastControllers
import shutil
import os.path
import ConfigParser
import subprocess
from shutil import copyfile
from os.path import dirname
from os.path import isdir
from os.path import isfile

class FlycastGenerator(Generator):

    # Main entry of the module
    # Configure flycast and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Write emu.cfg to map joysticks, init with the default emu.cfg
        Config = ConfigParser.ConfigParser()
        Config.optionxform = str
        if os.path.exists(batoceraFiles.flycastConfig):
            try:
                Config.read(batoceraFiles.flycastConfig)
            except:
                pass # give up the file
        
        if not Config.has_section("input"):
            Config.add_section("input")

        # Clear setting for pads NOT detected
        for index in range(len(playersControllers), 5):
            Config.set("input", 'device' + str(index), "10")
            Config.set("input", 'device' + str(index) + ".1", "10")
            Config.set("input", 'device' + str(index) + ".2", "10")

	# Setup detected pads
        for index in playersControllers:
            controller = playersControllers[index]
        
            # Write its mapping file
            controllerConfigFile = flycastControllers.generateControllerConfig(controller)
            
            # Set the device events
            Config.set("input", 'maple_' + controller.dev, int(controller.player) - 1)
            # setup the device types
            Config.set("input", 'device' + controller.player, "0")
            Config.set("input", 'device' + controller.player + ".1", "1")
            Config.set("input", 'device' + controller.player + ".2", "1")
        
        if not Config.has_section("players"):
            Config.add_section("players")
        # number of players
        Config.set("players", 'nb', len(playersControllers))

        if not Config.has_section("config"):
            Config.add_section("config")
        # wide screen mode
        if system.config["ratio"] == "16/9":
            Config.set("config", "rend.WideScreen", "1")
        # seems buggy + works only in 60hz on my side, so don't apply it automatically
        #elif system.config["ratio"] == "auto" and gameResolution["width"] / float(gameResolution["height"]) >= (16.0 / 9.0) - 0.1: # let a marge
        #    Config.set("config", "WideScreen", "1")
        else:
            Config.set("config", "rend.WideScreen", "0")

        # resolution
        if not Config.has_section("window"):
            Config.add_section("window")
        Config.set("window", "height", gameResolution["height"])
        Config.set("window", "width", gameResolution["width"])

        # custom : allow the user to configure directly emu.cfg via batocera.conf via lines like : dreamcast.flycast.section.option=value
        for user_config in system.config:
            if user_config[:8] == "flycast.":
                section_option = user_config[8:]
                section_option_splitter = section_option.find(".")
                custom_section = section_option[:section_option_splitter]
                custom_option = section_option[section_option_splitter+1:]
                if not Config.has_section(custom_section):
                    Config.add_section(custom_section)
                Config.set(custom_section, custom_option, system.config[user_config])

        ### update the configuration file
        if not os.path.exists(os.path.dirname(batoceraFiles.flycastConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.flycastConfig))
        with open(batoceraFiles.flycastConfig, 'w+') as cfgfile:
            Config.write(cfgfile)        
            cfgfile.close()
            
        # internal config
        # vmuA1
        if not isfile(batoceraFiles.flycastVMUA1):
            if not isdir(dirname(batoceraFiles.flycastVMUA1)):
                os.mkdir(dirname(batoceraFiles.flycastVMUA1))
            copyfile(batoceraFiles.flycastVMUBlank, batoceraFiles.flycastVMUA1)
        # vmuA2
        if not isfile(batoceraFiles.flycastVMUA2):
            if not isdir(dirname(batoceraFiles.flycastVMUA2)):
                os.mkdir(dirname(batoceraFiles.flycastVMUA2))
            copyfile(batoceraFiles.flycastVMUBlank, batoceraFiles.flycastVMUA2)

        # the command to run  
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append(rom)
        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME. The latter is better
        # VMU will be in $XDG_DATA_HOME because it needs rw access -> /userdata/saves/dreamcast
        # BIOS will be in $XDG_DATA_DIRS
        # controller cfg files are set with an absolute path, so no worry
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.flycastSaves, "XDG_DATA_DIRS":batoceraFiles.flycastBios})
