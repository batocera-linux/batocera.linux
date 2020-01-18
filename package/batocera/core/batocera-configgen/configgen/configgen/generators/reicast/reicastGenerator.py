#!/usr/bin/env python
import Command
#~ import reicastControllers
import batoceraFiles
from generators.Generator import Generator
import reicastControllers
import shutil
import os.path
import ConfigParser
from shutil import copyfile
from os.path import dirname
from os.path import isdir
from os.path import isfile

class ReicastGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Write emu.cfg to map joysticks, init with the default emu.cfg
        Config = ConfigParser.ConfigParser()
        Config.optionxform = str
        if os.path.exists(batoceraFiles.reicastConfig):
            try:
                Config.read(batoceraFiles.reicastConfig)
            except:
                pass # give up the file
        
        if not Config.has_section("input"):
            Config.add_section("input")
        # For each pad detected
        for index in range(len(playersControllers), 4):
            Config.set("input", 'evdev_device_id_' + str(index+1), -1)
            Config.set("input", 'evdev_mapping_' + str(index+1), "")

        for index in playersControllers:
            controller = playersControllers[index]
        
            # Get the event number
            eventNum = controller.dev.replace('/dev/input/event', '')
            
            # Write its mapping file
            controllerConfigFile = reicastControllers.generateControllerConfig(controller)
            
            # set the evdev_device_id_X
            Config.set("input", 'evdev_device_id_' + controller.player, eventNum)
            
            # Set the evdev_mapping_X
            Config.set("input", 'evdev_mapping_' + controller.player, controllerConfigFile)
        
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

        # custom : allow the user to configure directly emu.cfg via batocera.conf via lines like : dreamcast.reicast.section.option=value
        for user_config in system.config:
            if user_config[:8] == "reicast.":
                section_option = user_config[8:]
                section_option_splitter = section_option.find(".")
                custom_section = section_option[:section_option_splitter]
                custom_option = section_option[section_option_splitter+1:]
                if not Config.has_section(custom_section):
                    Config.add_section(custom_section)
                Config.set(custom_section, custom_option, system.config[user_config])

        ### update the configuration file
        if not os.path.exists(os.path.dirname(batoceraFiles.reicastConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.reicastConfig))
        with open(batoceraFiles.reicastConfig, 'w+') as cfgfile:
            Config.write(cfgfile)        
            cfgfile.close()
            
        # internal config
        # vmuA1
        if not isfile(batoceraFiles.reicastVMUA1):
            if not isdir(dirname(batoceraFiles.reicastVMUA1)):
                os.mkdir(dirname(batoceraFiles.reicastVMUA1))
            copyfile(batoceraFiles.reicastVMUBlank, batoceraFiles.reicastVMUA1)
        # vmuA2
        if not isfile(batoceraFiles.reicastVMUA2):
            if not isdir(dirname(batoceraFiles.reicastVMUA2)):
                os.mkdir(dirname(batoceraFiles.reicastVMUA2))
            copyfile(batoceraFiles.reicastVMUBlank, batoceraFiles.reicastVMUA2)

        # the command to run  
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append(rom)
        # Here is the trick to make reicast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME. The latter is better
        # VMU will be in $XDG_DATA_HOME because it needs rw access -> /userdata/saves/dreamcast
        # BIOS will be in $XDG_DATA_DIRS
        # controller cfg files are set with an absolute path, so no worry
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.reicastSaves, "XDG_DATA_DIRS":batoceraFiles.reicastBios})
