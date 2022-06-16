#!/usr/bin/env python

from generators.Generator import Generator
import Command
import controllersConfig
import batoceraFiles
import os
import shutil
import configparser

class GZDoomGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        commandArray = ["gzdoom", "-iwad", rom]

        # [ini file] - create /userdata/system/configs/gzdoom/gzdoom.ini
        gzdoomConfigPath = batoceraFiles.CONF + "/gzdoom"
        gzdoomConfigFile = gzdoomConfigPath + "/gzdoom.ini"
        gzdoomSavePath = batoceraFiles.savesDir + "/gzdoom"    

        Config = configparser.ConfigParser(interpolation=None)
        Config.optionxform = str
        if os.path.exists(gzdoomConfigFile):
            try:
                with io.open(gzdoomConfigFile, 'r', encoding='utf_8_sig') as configFileName:
                    Config.readfp(configFileName)
            except:
                pass
        
        # General settings
        if not Config.has_section("GlobalSettings"):
            Config.add_section("GlobalSettings")
        # ensure we do not use joystick - axis problems!
        # we use pad2key for the controller
        Config.set("GlobalSettings", "use_joystick", "false")

        # [set GPU]
        # Vulkan / OpenGL or OpenGLES etc
        #vid_rendermode=4 -< default

        # [set Display]

        # [joystick config]
        if not Config.has_section("Doom.Bindings"):
            Config.add_section("Doom.Bindings")
        # add bindings... ?

        if not os.path.exists(gzdoomConfigPath):
            os.makedirs(gzdoomConfigPath)
            os.makedirs(gzdoomConfigPath + "/soundfonts")
            os.makedirs(gzdoomConfigPath + "/fm_banks")

        cfgfile = open(gzdoomConfigFile,'w+')
        Config.write(cfgfile)
        cfgfile.close()

        # [other commandline options]
        # config file
        commandArray.append("-config")
        commandArray.append(gzdoomConfigFile)
        # save path
        if not os.path.exists(gzdoomSavePath):
            os.makedirs(gzdoomSavePath)
        commandArray.append("-savedir")
        commandArray.append(gzdoomSavePath)       

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })
