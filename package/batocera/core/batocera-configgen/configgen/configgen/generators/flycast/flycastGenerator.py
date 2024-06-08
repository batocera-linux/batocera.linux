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
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
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
        for index in playersControllers:
            controller = playersControllers[index]
            # Write the mapping files for Dreamcast
            if (system.name == "dreamcast"):
                flycastControllers.generateControllerConfig(controller, "dreamcast")
            else:
                # Write the Arcade variant (Atomiswave & Naomi/2)
                flycastControllers.generateControllerConfig(controller, "arcade")

            # Set the controller type per Port
            Config.set("input", 'device' + str(controller.player), "0") # Sega Controller
            Config.set("input", 'device' + str(controller.player) + '.1', "1") # Sega VMU
            # Set controller pack, gui option
            ctrlpackconfig = "flycast_ctrl{}_pack".format(controller.player)
            if system.isOptSet(ctrlpackconfig):
                Config.set("input", 'device' + str(controller.player) + '.2', str(system.config[ctrlpackconfig]))
            else:
                Config.set("input", 'device' + str(controller.player) + '.2', "1") # Sega VMU
            # Ensure controller(s) are on seperate Ports
            port = int(controller.player)-1
            Config.set("input", 'maple_sdl_joystick_' + str(port), str(port))

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
        if system.isOptSet("flycast_renderer") and system.config["flycast_renderer"] == "0":
            if system.isOptSet("flycast_sorting") and system.config["flycast_sorting"] == "3":
                # per pixel
                Config.set("config", "pvr.rend", "3")
            else:
                # per triangle
                Config.set("config", "pvr.rend", "0")
        elif system.isOptSet("flycast_renderer") and system.config["flycast_renderer"] == "4":
            if system.isOptSet("flycast_sorting") and system.config["flycast_sorting"] == "3":
                # per pixel
                Config.set("config", "pvr.rend", "5")
            else:
                # per triangle
                Config.set("config", "pvr.rend", "4")
        else:
            Config.set("config", "pvr.rend", "0")
            if system.isOptSet("flycast_sorting") and system.config["flycast_sorting"] == "3":
                # per pixel
                Config.set("config", "pvr.rend", "3")
        # anisotropic filtering
        if system.isOptSet("flycast_anisotropic"):
            Config.set("config", "rend.AnisotropicFiltering", str(system.config["flycast_anisotropic"]))
        else:
            Config.set("config", "rend.AnisotropicFiltering", "1")
        # transparent sorting
        # per strip
        if system.isOptSet("flycast_sorting") and system.config["flycast_sorting"] == "2":
            Config.set("config", "rend.PerStripSorting", "yes")
        else:
            Config.set("config", "rend.PerStripSorting", "no")

        # [Dreamcast specifics]
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
        # DSP
        if system.isOptSet("flycast_DSP"):
             Config.set("config", "aica.DSPEnabled", str(system.config["flycast_DSP"]))
        else:
            Config.set("config", "aica.DSPEnabled", "no")
        # Guns (WIP)
        # Guns crosshairs
        if system.isOptSet("flycast_lightgun1_crosshair"):
            Config.set("config", "rend.CrossHairColor1", + str(system.config["flycast_lightgun1_crosshair"]))
        else:
            Config.set("config", "rend.CrossHairColor1", "0")
        if system.isOptSet("flycast_lightgun2_crosshair"):
            Config.set("config", "rend.CrossHairColor2", + str(system.config["flycast_lightgun2_crosshair"]))
        else:
            Config.set("config", "rend.CrossHairColor2", "0")
        if system.isOptSet("flycast_lightgun3_crosshair"):
            Config.set("config", "rend.CrossHairColor3", + str(system.config["flycast_lightgun3_crosshair"]))
        else:
            Config.set("config", "rend.CrossHairColor3", "0")
        if system.isOptSet("flycast_lightgun4_crosshair"):
            Config.set("config", "rend.CrossHairColor4", + str(system.config["flycast_lightgun4_crosshair"]))
        else:
            Config.set("config", "rend.CrossHairColor4", "0")
        
        # Retroachievements
        if not Config.has_section("achievements"):
            Config.add_section("achievements")
        
        if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
            headers   = {"Content-type": "text/plain", "User-Agent": "Batocera.linux"}
            login_url = "https://retroachievements.org/"
            username  = system.config.get('retroachievements.username', "")
            password  = system.config.get('retroachievements.password', "")
            hardcore  = system.config.get('retroachievements.hardcore', "")
            token     = system.config.get('retroachievements.token', "")
            # apply config            
            Config.set("achievements", "Enabled", "yes")
            if hardcore == '1':
                Config.set("achievements", "HardcoreMode", "yes")
            else:
                Config.set("achievements", "HardcoreMode", "no")
            Config.set("achievements", "Token", token)
            Config.set("achievements", "UserName" , username)
        else:
            Config.set("achievements", "Enabled", "no")
        
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
        if not isdir(batoceraFiles.flycastSaves):
            os.mkdir(batoceraFiles.flycastSaves)
        if not isdir(batoceraFiles.flycastSaves + "/flycast"):
            os.mkdir(batoceraFiles.flycastSaves + "/flycast")
        # vmuA1
        if not isfile(batoceraFiles.flycastVMUA1):
            copyfile(batoceraFiles.flycastVMUBlank, batoceraFiles.flycastVMUA1)
        # vmuA2
        if not isfile(batoceraFiles.flycastVMUA2):
            copyfile(batoceraFiles.flycastVMUBlank, batoceraFiles.flycastVMUA2)

        # the command to run
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']]]
        commandArray.append(rom)
        # Here is the trick to make flycast find files :
        # emu.cfg is in $XDG_CONFIG_DIRS or $XDG_CONFIG_HOME.
        # VMU will be in $XDG_DATA_HOME / $FLYCAST_DATADIR because it needs rw access -> /userdata/saves/dreamcast
        # $FLYCAST_BIOS_PATH is where Flaycast should find the bios files
        # controller cfg files are set with an absolute path, so no worry
        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":batoceraFiles.CONF,
                "XDG_CONFIG_DIRS":batoceraFiles.CONF,
                "XDG_DATA_HOME":batoceraFiles.flycastSaves,
                "FLYCAST_DATADIR":batoceraFiles.flycastSaves,
                "FLYCAST_BIOS_PATH":batoceraFiles.flycastBios,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )
