#!/usr/bin/env python
import Command
from generators.Generator import Generator
import controllersConfig
import configparser
import os
import shutil
import batoceraFiles

forceConfigDir = batoceraFiles.CONF + "/theforceengine"
forceModsDir = forceConfigDir + "/Mods"
forcePatchFile = "v3.zip" # current patch version
forceModFile = forceModsDir + "/" + forcePatchFile
forceConfigFile = forceConfigDir + "/settings.ini"

class TheForceEngineGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        
        # Check if the directories exist, if not create them
        if not os.path.exists(forceConfigDir):
            os.makedirs(forceConfigDir)
        if not os.path.exists(forceModsDir):
            os.makedirs(forceModsDir)
        
        mod_name = None
        # use the patch file if available
        if os.path.exists(forceModFile):
            mod_name = forcePatchFile
        
        # Open the .tfe rom file for user mods
        with open(rom, 'r') as file:
            # Read the first line and store it as 'first_line'
            first_line = file.readline().strip()
            # use the first_line as mod if the file isn't empty
            if first_line:
                mod_name = first_line
                        
        ## Configure
        forceConfig = configparser.ConfigParser()
        forceConfig.optionxform=str
        if os.path.exists(forceConfigFile):
            forceConfig.read(forceConfigFile)
        
        # Windows
        if not forceConfig.has_section("Window"):
            forceConfig.add_section("Window")
        forceConfig.set("Window", "width", format(gameResolution["width"]))
        forceConfig.set("Window", "height", format(gameResolution["height"]))
        # always fullscreen
        forceConfig.set("Window", "fullscreen", "true")
        
        # Graphics
        if not forceConfig.has_section("Graphics"):
            forceConfig.add_section("Graphics")
        
        if system.isOptSet("force_render_res"):
            res_height = system.config["force_render_res"]
            res_width = int(res_height) * 4/3
            forceConfig.set("Graphics", "gameWidth", str(res_width))
            forceConfig.set("Graphics", "gameHeight", res_height)
        else:
            res_width = int(gameResolution["height"] * 4/3)
            forceConfig.set("Graphics", "gameWidth", str(res_width))
            forceConfig.set("Graphics", "gameHeight", format(gameResolution["height"]))
        
        if system.isOptSet("force_widescreen") and system.getOptBoolean("force_widescreen"):
            forceConfig.set("Graphics", "widescreen", "true")
        else:
            forceConfig.set("Graphics", "widescreen", "false")
        
        if system.isOptSet("force_vsync") and system.config["force_vsync"] == "0":
            forceConfig.set("Graphics", "vsync", "false")
        else:
            forceConfig.set("Graphics", "vsync", "true")
        
        if system.isOptSet("force_rate"):
            forceConfig.set("Graphics", "frameRateLimit", system.config["force_rate"])
        else:
            forceConfig.set("Graphics", "frameRateLimit", "60")
        
        if system.isOptSet("force_api") and system.config["force_api"] == "Software":
            forceConfig.set("Graphics", "renderer", "0")
        else:
            forceConfig.set("Graphics", "renderer", "1")
        
        if system.isOptSet("force_colour"):
            forceConfig.set("Graphics", "colorMode", system.config["force_colour"])
        else:
            forceConfig.set("Graphics", "colorMode", "0")

        if system.isOptSet("force_bilinear") and system.getOptBoolean("force_bilinear"):
            forceConfig.set("Graphics", "useBilinear", "true")
        else:
            forceConfig.set("Graphics", "useBilinear", "false")

        if system.isOptSet("force_mipmapping") and system.getOptBoolean("force_mipmapping"):
            forceConfig.set("Graphics", "useMipmapping", "true")
        else:
            forceConfig.set("Graphics", "useMipmapping", "false")
        
        if system.isOptSet("force_crosshair") and system.getOptBoolean("force_crosshair"):
            forceConfig.set("Graphics", "reticleEnable", "true")
        else:
            forceConfig.set("Graphics", "reticleEnable", "false")
        
        if system.isOptSet("force_postfx") and system.getOptBoolean("force_postfx"):
            forceConfig.set("Graphics", "bloomEnabled", "true")
        else:
            forceConfig.set("Graphics", "bloomEnabled", "false")
            
        # Hud
        if not forceConfig.has_section("Hud"):
            forceConfig.add_section("Hud")
        forceConfig.set("Hud", "hudScale", '"Proportional"')
        forceConfig.set("Hud", "hudPos", '"Edge"')
        forceConfig.set("Hud", "scale", "1.000")

        # Enhancements
        if not forceConfig.has_section("Enhancements"):
            forceConfig.add_section("Enhancements")
        if system.isOptSet("force_hd") and system.getOptBoolean("force_hd"):
            forceConfig.set("Enhancements", "hdTextures", "1")
            forceConfig.set("Enhancements", "hdSprites", "1")
            forceConfig.set("Enhancements", "hdHud", "1")
            # force true colour for HD textures
            forceConfig.set("Graphics", "colorMode", "2")
        else:
            forceConfig.set("Enhancements", "hdTextures", "0")
            forceConfig.set("Enhancements", "hdSprites", "0")
            forceConfig.set("Enhancements", "hdHud", "0")
        
        # Sound
        if not forceConfig.has_section("Sound"):
            forceConfig.add_section("Sound")
        
        if system.isOptSet("force_menu_sound") and system.getOptBoolean("force_menu_sound"):
            forceConfig.set("Sound", "disableSoundInMenus", "true")
        else:
            forceConfig.set("Sound", "disableSoundInMenus", "false")
        
        if system.isOptSet("force_digital_audio") and system.getOptBoolean("force_digital_audio"):
            forceConfig.set("Sound", "use16Channels", "true")
        else:
            forceConfig.set("Sound", "use16Channels", "false")
                
        # System
        if not forceConfig.has_section("System"):
            forceConfig.add_section("System")
                
        # A11y
        if not forceConfig.has_section("A11y"):
            forceConfig.add_section("A11y")
        
        # Game
        if not forceConfig.has_section("Game"):
            forceConfig.add_section("Game")
        # currently Dark Forces only - to do
        forceConfig.set("Game", "game", "Dark Forces")

        # Dark_Forces
        if not forceConfig.has_section("Dark_Forces"):
            forceConfig.add_section("Dark_Forces")
        # currently use this directory
        forceConfig.set("Dark_Forces", "sourcePath", '"/userdata/roms/theforceengine/Star Wars - Dark Forces/"')

        if system.isOptSet("force_fight_music") and system.getOptBoolean("force_fight_music"):
            forceConfig.set("Dark_Forces", "disableFightMusic", "true")
        else:
            forceConfig.set("Dark_Forces", "disableFightMusic", "false")
        
        if system.isOptSet("force_auto_aim") and system.config["force_auto_aim"] == "0":
            forceConfig.set("Dark_Forces", "enableAutoaim", "false")
        else:
            forceConfig.set("Dark_Forces", "enableAutoaim", "true")
        
        if system.isOptSet("force_secret_msg") and system.config["force_secret_msg"] == "0":
            forceConfig.set("Dark_Forces", "showSecretFoundMsg", "false")
        else:
            forceConfig.set("Dark_Forces", "showSecretFoundMsg", "true")
        
        if system.isOptSet("force_auto_run") and system.getOptBoolean("force_auto_run"):
            forceConfig.set("Dark_Forces", "autorun", "true")
        else:
            forceConfig.set("Dark_Forces", "autorun", "false")

        if system.isOptSet("force_boba") and system.getOptBoolean("force_boba"):
            forceConfig.set("Dark_Forces", "bobaFettFacePlayer", "true")
        else:
            forceConfig.set("Dark_Forces", "bobaFettFacePlayer", "false")
        
        if system.isOptSet("force_smooth_vues") and system.getOptBoolean("force_smooth_vues"):
            forceConfig.set("Dark_Forces", "smoothVUEs", "true")
        else:
            forceConfig.set("Dark_Forces", "smoothVUEs", "false")

        # Outlaws
        if not forceConfig.has_section("Outlaws"):
            forceConfig.add_section("Outlaws")
        forceConfig.set("Outlaws", "sourcePath", '""')

        # CVar
        if not forceConfig.has_section("CVar"):
            forceConfig.add_section("CVar")
        
        ## Update the configuration file
        if not os.path.exists(os.path.dirname(forceConfigFile)):
            os.makedirs(os.path.dirname(forceConfigFile))
        with open(forceConfigFile, 'w') as configfile:
            forceConfig.write(configfile)
        
        ## Setup the command
        commandArray = ["theforceengine"]
        
        ## Accomodate Mods, skip cutscenes etc
        if system.isOptSet("force_skip_cutscenes") and system.config["force_skip_cutscenes"] == "initial":
            commandArray.extend(["-c0"])
        elif system.isOptSet("force_skip_cutscenes") and system.getOptBoolean("force_skip_cutscenes") == "skip":
            commandArray.extend(["-c"])
        # Add mod zip file if necessary
        if mod_name is not None:
            commandArray.extend(["-u" + mod_name])
        
        # Run - only Dark Forces currently
        commandArray.extend(["-gDARK"])

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "TFE_DATA_HOME": forceConfigDir
            }
        )

    # Show mouse for menu actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        if ("force_widescreen" in config and config["force_widescreen"] == "1"):
            return 16/9
        return 4/3
