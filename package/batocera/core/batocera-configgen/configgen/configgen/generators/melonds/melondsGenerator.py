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

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        romBasename = path.basename(rom)
        
        # Verify the save path exists
        if not os.path.exists("/userdata/saves/melonds"):
            os.mkdir("/userdata/saves/melonds")
        # Verify the cheat path exist
        if not os.path.exists("/userdata/cheats/melonDS"):
            os.mkdir("/userdata/cheats/melonDS")      
        # Config path
        configdir = "{}/{}".format(batoceraFiles.CONF, "melonDS")
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        # Config file
        configFileName = "{}/{}".format(configdir, "melonDS.ini")              
        f = codecs.open(configFileName, "w", encoding="utf_8_sig")

        # [Set config defaults]
        f.write("WindowWidth={}\n".format(gameResolution["width"]))
        f.write("WindowHeight={}\n".format(gameResolution["height"]))
        f.write("WindowMax=1\n")
        # Hide mouse after 5 seconds
        f.write("MouseHide=1\n")
        f.write("MouseHideSeconds=5\n")
        # Set bios locations
        f.write("ExternalBIOSEnable=1\n")
        f.write("BIOS9Path=/userdata/bios/bios9.bin\n")
        f.write("BIOS7Path=/userdata/bios/bios7.bin\n")
        f.write("FirmwarePath=/userdata/bios/firmware.bin\n")
        f.write("DSiBIOS9Path=/userdata/bios/dsi_bios9.bin\n")
        f.write("DSiBIOS7Path=/userdata/bios/dsi_bios7.bin\n")
        f.write("DSiFirmwarePath=/userdata/bios/dsi_firmware.bin\n")
        f.write("DSiNANDPath=/userdata/bios/dsi_nand.bin\n")
        # Set save locations
        f.write("DLDIFolderPath=/userdata/saves/melonds\n")
        f.write("DSiSDFolderPath=/userdata/saves/melonds\n")
        f.write("MicWavPath=/userdata/saves/melonds\n")
        f.write("SaveFilePath=/userdata/saves/melonds\n")
        f.write("SavestatePath=/userdata/saves/melonds\n")
        # Cheater!
        f.write("CheatFilePath=/userdata/cheats/melonDS\n")
        # Roms
        f.write("LastROMFolder=/userdata/roms/nds\n")
        # Audio
        f.write("AudioInterp=1\n")
        f.write("AudioBitrate=2\n")
        f.write("AudioVolume=256\n")
        # For Software Rendering
        f.write("Threaded3D=1\n")

        # [User selected options]
        # MelonDS only has OpenGL or Software - use OpenGL if not selected
        if system.isOptSet("melonds_renderer"):
            f.write("3DRenderer={}\n".format(system.config["melonds_renderer"]))
        else:
            f.write("3DRenderer=1\n")
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
        # Cheater!
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
                val = input.id
                if val == "0":
                    if option == "Joy_Up":
                        val = 257
                    elif option == "Joy_Down":
                        val = 260
                    elif option == "Joy_Left":
                        val = 264
                    elif option == "Joy_Right":
                        val = 258
                eslog.debug(f"Name: {option} - Var: {val}")
                f.write(f"{option}={val}\n")
        # Always set ID to 0
        f.write("JoystickID=0\n")

        # Now write the ini file
        f.close()

        commandArray = ["/usr/bin/melonDS", "-f", rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, \
            "XDG_DATA_HOME":batoceraFiles.SAVES, "QT_QPA_PLATFORM":"xcb"})
