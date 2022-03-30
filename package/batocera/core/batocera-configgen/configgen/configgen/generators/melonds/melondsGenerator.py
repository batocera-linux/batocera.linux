#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import controllersConfig
import batoceraFiles
import codecs
from utils.logger import get_logger

eslog = get_logger(__name__)

class MelonDSGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        romBasename = path.basename(rom)
        
        # Verify the save path exists
        if not os.path.exists("/userdata/saves/melonds"):
            os.mkdir("/userdata/saves/melonds")
        # Verify the cheat path exist
        if not os.path.exists("/userdata/cheats/cht/melonDS"):
            os.mkdir("/userdata/cheats/cht/melonDS")      
        # Config path
        configdir = "{}/{}".format(batoceraFiles.CONF, "melonDS")
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        # Config file
        configFileName = "{}/{}".format(configdir, "melonDS.ini")              
        f = codecs.open(configFileName, "w", encoding="utf_8_sig")

        # Set config defaults
        f.write("WindowWidth={}\n".format(gameResolution["width"]))
        f.write("WindowHeight={}\n".format(gameResolution["height"]))
        f.write("WindowMax=1\n")
        # MelonDS only has OpenGL or Software - always go for OpenGL (1)
        f.write("3DRenderer=1\n")
        # Hide mouse after 5 seconds
        f.write("MouseHide=1\n")
        f.write("MouseHideSeconds=5\n")

        # User selected options
        if system.isOptSet("melonds_framerate"):
            f.write("LimitFPS={}\n".format(system.config["melonds_framerate"]))
        else:
            f.write("LimitFPS=1\n")
        if system.isOptSet("melonds_resolution"):
            f.write("GL_ScaleFactor={}\n".format(system.config["melonds_resolution"]))
        else:
            f.write("GL_ScaleFactor=1\n")
        if system.isOptSet("melonds_polygons"):
            f.write("GL_BetterPolygons={}\n".format(system.config["melonds_polygons"]))
        else:
            f.write("GL_BetterPolygons=0\n")
        if system.isOptSet("melonds_rotation"):
            f.write("ScreenRotation={}\n".format(system.config["melonds_rotation"]))
        else:
            f.write("ScreenRotation=0\n")
        if system.isOptSet("melonds_screenswap"):
            f.write("ScreenSwap={}\n".format(system.config["melonds_screenswap"]))
        else:
            f.write("ScreenSwap=0\n")
        if system.isOptSet("melonds_layout"):
            f.write("ScreenLayout={}\n".format(system.config["melonds_layout"]))
        else:
            f.write("ScreenLayout=0\n")       
        if system.isOptSet("melonds_screensizing"):
            f.write("ScreenSizing={}\n".format(system.config["melonds_screensizing"]))
        else:
            f.write("ScreenSizing=0\n")  
        if system.isOptSet("melonds_scaling"):
            f.write("IntegerScaling={}\n".format(system.config["melonds_scaling"]))
        else:
            f.write("IntegerScaling=0\n")  
        if system.isOptSet("melonds_cheats"):
            f.write("EnableCheats={}\n".format(system.config["melonds_cheats"]))
        else:
            f.write("EnableCheats=0\n")  
        if system.isOptSet("melonds_osd"):
            f.write("ShowOSD={}\n".format(system.config["melonds_osd"]))
        else:
            f.write("ShowOSD=1\n")
        if system.isOptSet("melonds_console"):
            f.write("ConsoleType={}\n".format(system.config["melonds_console"]))
        else:
            f.write("ConsoleType=0\n")
        
        # Map controllers
        melonDSMapping = {
        "a":        "Joy_A",
        "b":        "Joy_B",
        "select":   "Joy_Select",
        "start":    "Joy_Start",
        "right":    "Joy_Right",
        "left":     "Joy_Left",
        "up":       "Joy_Up",
        "down":     "Joy_Down",
        "pagedown": "Joy_R",
        "pageup":   "Joy_L",
        "x":        "Joy_X",
        "y":        "Joy_Y"
        }

        val = -1
        for controller, pad in sorted(playersControllers.items()):
            # Only use Player 1 controls
            if pad.player != "1":
                continue
            for index in pad.inputs:
                input = pad.inputs[index]
                if input.name not in melonDSMapping:
                    continue
                option = melonDSMapping[input.name]
                # Workaround - SDL numbers?
                if option == "Joy_Up":
                    val = 257
                elif option == "Joy_Down":
                    val = 260
                elif option == "Joy_Left":
                    val = 264
                elif option == "Joy_Right":
                    val = 258
                else:
                    val = input.id
                eslog.debug("Name: {} - Var: {}".format(option, val))
                f.write("{}={}\n".format(option, val))
        # Always set ID to 0
        f.write("JoystickID=0\n")

        # Now right the ini file
        f.close()

        commandArray = ["/usr/bin/melonDS", rom]
        return Command.Command(array=commandArray)
