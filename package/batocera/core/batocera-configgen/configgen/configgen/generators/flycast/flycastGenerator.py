#!/usr/bin/env python
import Command
#~ import flycastControllers
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
import configparser
import controllersConfig
from shutil import copyfile
from os.path import dirname
from os.path import isdir
from os.path import isfile
from . import flycastControllers

class FlycastGenerator(Generator):

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Write emu.cfg to map joysticks, init with the default emu.cfg
        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str
        if os.path.exists(batoceraFiles.flycastConfig):
            try:
                Config.read(batoceraFiles.flycastConfig)
            except:
                pass # give up the file
        
        if not Config.has_section("input"):
            Config.add_section("input")
        # For each pad detected
        for index in range(len(playersControllers), 4):
            Config.set("input", 'evdev_device_id_' + str(index+1), "-1")
            Config.set("input", 'evdev_mapping_' + str(index+1), "")

        for index in playersControllers:
            controller = playersControllers[index]
        
            # Get the event number
            eventNum = controller.dev.replace('/dev/input/event', '')
            
            # Write its mapping file
            controllerConfigFile = flycastControllers.generateControllerConfig(controller)
            # write the arcade file variant (atomiswave & naomi)
            flycastControllers.generateArcadeControllerConfig(controller)
            
            # set the evdev_device_id_X
            Config.set("input", 'evdev_device_id_' + controller.player, eventNum)
            
            # Set the evdev_mapping_X
            Config.set("input", 'evdev_mapping_' + controller.player, controllerConfigFile)
        
        if not Config.has_section("players"):
            Config.add_section("players")
        # number of players
        Config.set("players", 'nb', str(len(playersControllers)))

        if not Config.has_section("config"):
            Config.add_section("config")
        if not Config.has_section("window"):
            Config.add_section("window")
        # ensure we are always fullscreen
        Config.set("window", "fullscreen", "yes")
        # set video resolution
        Config.set("window", "width", str(gameResolution["width"]))
        Config.set("window", "height", str(gameResolution["height"]))
        # set render resolution - default 480 (Native)
        if system.isOptSet("flycast_render_resolution"):
            Config.set("config", "rend.Resolution", str(system.config["flycast_render_resolution"]))
        else:
            Config.set("config", "rend.Resolution", "480")
        # wide screen mode - default off
        if system.isOptSet("flycast_ratio"):
            Config.set("config", "rend.WideScreen", str(system.config["flycast_ratio"]))
        else:
            Config.set("config", "rend.WideScreen", "no")
        # rotate option - default off
        if system.isOptSet("flycast_rotate"):
            Config.set("config", "rend.Rotate90", str(system.config["flycast_rotate"]))
        else:
            Config.set("config", "rend.Rotate90", "no")
        # renderer - default: OpenGL
        if system.isOptSet("flycast_renderer"):
            Config.set("config", "pvr.rend", str(system.config["flycast_renderer"]))
        else:
            Config.set("config", "pvr.rend", "0")
        
        # dreamcast specifics
        # language
        if system.isOptSet("flycast_language"):
            Config.set("config", "Dreamcast.Language", str(system.config["flycast_language"]))
        else:
            Config.set("config", "Dreamcast.Language", "1")
        # region
        if system.isOptSet("flycast_region"):
            Config.set("config", "Dreamcast.Region", str(system.config["flycast_language"]))
        else:
            Config.set("config", "Dreamcast.Region", "1")
        # save / load states
        if system.isOptSet("flycast_loadstate"):
            Config.set("config", "Dreamcast.AutoLoadState", str(system.config["flycast_loadstate"]))
        else:
            Config.set("config", "Dreamcast.AutoLoadState", "no")
        if system.isOptSet("flycast_savestate"):
            Config.set("config", "Dreamcast.AutoSaveState", str(system.config["flycast_savestate"]))
        else:
            Config.set("config", "Dreamcast.AutoSaveState", "no")
        # windows CE
        if system.isOptSet("flycast_winCE"):
            Config.set("config", "Dreamcast.ForceWindowsCE", str(system.config["flycast_winCE"]))
        else:
            Config.set("config", "Dreamcast.ForceWindowsCE", "no")

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
                os.mkdir(batoceraFiles.flycastSaves)
                os.mkdir(dirname(batoceraFiles.flycastVMUA1))
            copyfile(batoceraFiles.flycastVMUBlank, batoceraFiles.flycastVMUA1)
        # vmuA2
        if not isfile(batoceraFiles.flycastVMUA2):
            if not isdir(dirname(batoceraFiles.flycastVMUA2)):
                os.mkdir(batoceraFiles.flycastSaves)
                os.mkdir(dirname(batoceraFiles.flycastVMUA2))
            copyfile(batoceraFiles.flycastVMUBlank, batoceraFiles.flycastVMUA2)
        
        # flycast vulkan workaround - manually point to vulkan icd's in preferred order.
        # pi4
        broadcom_icd = "/usr/share/vulkan/icd.d/broadcom_icd.cortex-a72.json"
        if os.path.exists(broadcom_icd):
            gpu_icd = broadcom_icd
        # x86_64
        else:
            gpu_icd = "/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/radeon_icd.x86_64.json:/usr/share/vulkan/icd.d/intel_icd.x86_64.json"

        # the command to run  
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append(rom)
        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME. The latter is better
        # VMU will be in $XDG_DATA_HOME because it needs rw access -> /userdata/saves/dreamcast
        # BIOS will be in $XDG_DATA_DIRS
        # controller cfg files are set with an absolute path, so no worry
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF,
            "XDG_DATA_HOME":batoceraFiles.flycastSaves,
            "XDG_DATA_DIRS":batoceraFiles.flycastBios,
            "FLYCAST_BIOS_PATH":batoceraFiles.flycastBios,
            "VK_ICD_FILENAMES":gpu_icd,
            })
