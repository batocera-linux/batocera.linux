#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from utils.logger import get_logger
from os import path
from os import environ
import configparser
from xml.dom import minidom
import codecs
import shutil
import utils.bezels as bezelsUtil
import subprocess
from xml.dom import minidom
from PIL import Image, ImageOps

eslog = get_logger(__name__)

class MameGenerator(Generator):

    def supportsInternalBezels(self):
        return True

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

        # Define systems that will use the MESS executable instead of MAME
        messSystems = [ "lcdgames", "gameandwatch", "cdi", "advision", "tvgames", "megaduck", "crvision", "gamate", "pv1000", "gamecom" , "fm7", "xegs", "gamepock", "aarch", "atom", "apfm1000", "bbc", "camplynx", "adam", "arcadia", "supracan", "gmaster", "astrocde", "ti99", "tutor", "coco", "socrates" ]
        # If it needs a system name defined, use it here. Add a blank string if it does not (ie non-arcade, non-system ROMs)
        messSysName = [ "", "", "cdimono1", "advision", "", "megaduck", "crvision", "gamate", "pv1000", "gamecom", "fm7", "xegs", "gamepock", "aa310", "atom", "apfm1000", "bbcb", "lynx48k", "adam", "arcadia", "supracan", "gmaster", "astrocde", "ti99_4a", "tutor", "coco", "socrates" ]
        # For systems with a MAME system name, the type of ROM that needs to be passed on the command line (cart, tape, cdrm, etc)
        # If there are multiple ROM types (ie a computer w/disk & tape), select the default or primary type here.
        messRomType = [ "", "", "cdrm", "cart", "", "cart", "cart", "cart", "cart", "cart1", "flop1", "cart", "cart", "flop", "cass", "cart", "flop1", "cass", "cass1", "cart", "cart", "cart", "cart", "cart", "cart", "cart", "cart" ]
        messAutoRun = [ "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 'mload""\\n', "", "", "", "", "", "", "", "", "" ]
        
        # Identify the current system, select MAME or MESS as needed.
        try:
            messMode = messSystems.index(system.name)
        except ValueError:
            messMode = -1
        if messMode == -1:
            commandArray =  [ "/usr/bin/mame/mame" ]
        else:
            commandArray =  [ "/usr/bin/mame/mess" ]
        
        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        commandArray += [ "-skip_gameinfo" ]
        if messMode == -1:
            commandArray += [ "-rompath",      romDirname ]
        else:
            commandArray += [ "-rompath",      romDirname + ";/userdata/bios/;/userdata/roms/mame/" ]

        # MAME various paths we can probably do better
        commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
        commandArray += [ "-fontpath",     "/usr/bin/mame/" ]               # Fonts can be left on ROM filesystem
        commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
        commandArray += [ "-pluginspath", "/usr/bin/mame/plugins/" ]
        commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path or cheat.7z file ?
        commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
        commandArray += [ "-artpath",       "/userdata/decorations/;/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/mame/artwork/" ] # first for systems ; second for overlays

        # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
        commandArray += [ "-nvram_directory" ,    "/userdata/saves/mame/nvram/" ]
        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        cfgPath = "/userdata/system/configs/mame/"
        if system.isOptSet("pergamecfg") and system.getOptBoolean("pergamecfg"):
            if not messMode == -1:
                if not messSysName[messMode] == "":
                    if not os.path.exists("/userdata/system/configs/mame/" + messSysName[messMode] + "/"):
                        os.makedirs("/userdata/system/configs/mame/" + messSysName[messMode] + "/")
                    cfgPath = "/userdata/system/configs/mame/" + messSysName[messMode] + "/" + romBasename + "/"
                    if not os.path.exists(cfgPath):
                        os.makedirs(cfgPath)
        commandArray += [ "-cfg_directory"   ,    cfgPath ]
        commandArray += [ "-input_directory" ,    "/userdata/saves/mame/input/" ]
        commandArray += [ "-state_directory" ,    "/userdata/saves/mame/state/" ]
        commandArray += [ "-snapshot_directory" , "/userdata/screenshots/" ]
        commandArray += [ "-diff_directory" ,     "/userdata/saves/mame/diff/" ]
        commandArray += [ "-comment_directory",   "/userdata/saves/mame/comments/" ]

        # TODO These paths are not handled yet
        # TODO -homepath            path to base folder for plugin data (read/write)
        # TODO -ctrlrpath           path to controller definitions
        # TODO -inipath             path to ini files
        # TODO -crosshairpath       path to crosshair files
        # TODO -pluginspath         path to plugin files
        # TODO -swpath              path to loose software

        # BGFX video engine : https://docs.mamedev.org/advanced/bgfx.html
        if system.isOptSet("video") and system.config["video"] == "bgfx":
            commandArray += [ "-video", "bgfx" ]

            # BGFX backend
            if system.isOptSet("bgfxbackend") and system.config['bgfxbackend'] != 'automatic':
                commandArray += [ "-bgfx_backend", system.config['bgfxbackend'] ]
            else:
                commandArray += [ "-bgfx_backend", "auto" ]

            # BGFX shaders effects
            if system.isOptSet("bgfxshaders") and system.config['bgfxshaders'] != 'default':
                commandArray += [ "-bgfx_screen_chains", system.config['bgfxshaders'] ]
            else:
                commandArray += [ "-bgfx_screen_chains", "default" ]

        # Other video modes
        elif system.isOptSet("video") and system.config["video"] == "accel":
            commandArray += ["-video", "accel" ]
        else:
            commandArray += [ "-video", "opengl" ]

        # CRT / SwitchRes support
        if system.isOptSet("switchres") and system.getOptBoolean("switchres"):
            commandArray += [ "-modeline_generation" ]
            commandArray += [ "-changeres" ]
        else:
            commandArray += [ "-nomodeline_generation" ]
            commandArray += [ "-nochangeres" ]
            commandArray += [ "-noswitchres" ]

        # Rotation / TATE options
        if system.isOptSet("rotation") and system.config["rotation"] == "autoror":
            commandArray += [ "-autoror" ]
        if system.isOptSet("rotation") and system.config["rotation"] == "autorol":
            commandArray += [ "-autorol" ]
        
        # UI enable - for computer systems, the default sends all keys to the emulated system.
        # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
        # Hotkey + D-Pad Up will toggle this when in use (scroll lock key)
        if not (system.isOptSet("enableui") and not system.getOptBoolean("enableui")):
            commandArray += [ "-ui_active" ]
        
        # Finally we pass game name
        # MESS will use the full filename and pass the system & rom type parameters if needed.
        if messMode == -1:
            commandArray += [ romBasename ]
        else:
            if messSysName[messMode] == "":
                commandArray += [ romBasename ]
            else:
                # Alternate system for machines that have different configs (ie computers with different hardware)
                if system.isOptSet("altmodel"):
                    commandArray += [ system.config["altmodel"] ]
                else:
                    commandArray += [ messSysName[messMode] ]
                # Autostart computer games where applicable
                # Generic boot if only one type is available
                if messAutoRun[messMode] != "":
                    commandArray += [ "-autoboot_delay", "2", "-autoboot_command", messAutoRun[messMode] ]
                # bbc has different boots for floppy & cassette, no special boot for carts
                if system.name == "bbc":
                    if system.isOptSet("altromtype"):
                        if system.config["altromtype"] == "cass":
                            commandArray += [ '-autoboot_delay', '2', '-autoboot_command', '*tape\\nchain""\\n' ]
                        elif left(system.config["altromtype"], 4) == "flop":
                            commandArray += [ '-autoboot_delay',  '3',  '-autoboot_command', '*cat\\n*exec !boot\\n' ]
                    else:
                        commandArray += [ '-autoboot_delay',  '3',  '-autoboot_command', '*cat\\n*exec !boot\\n' ]
                # fm7 boots floppies, needs cassette loading
                if system.name == "fm7" and system.isOptSet("altromtype") and system.config["altromtype"] == "cass":
                    commandArray += [ '-autoboot_delay', '5', '-autoboot_command', 'LOADM”“,,R\\n' ]
                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                if system.isOptSet("altromtype"):
                    commandArray += [ "-" + system.config["altromtype"] ]
                else:
                    commandArray += [ "-" + messRomType[messMode] ]
                # Use the full filename for MESS ROMs
                commandArray += [ rom ]
        
        
        # config file
        config = minidom.Document()
        configFile = cfgPath + "default.cfg"
        if os.path.exists(configFile):
            try:
                config = minidom.parse(configFile)
            except:
                pass # reinit the file
        
        # Alternate D-Pad Mode
        if system.isOptSet("altdpad"):
            dpadMode = system.config["altdpad"]
        else:
            dpadMode = 0

        # Controls for games with 5-6 buttons
        if system.isOptSet("altlayout"):
            buttonLayout = system.config["altlayout"] # Option was manually selected
        else:
            romName = os.path.splitext(romBasename)[0]
            if romName in [ "ts2", "ts2ja", "ts2j", "ts2ua", "ts2u", "kikaioh", "dstlka", "dstlk", "dstlkh", "dstlkur1", "dstlku", "hsf2a", "hsf2j1", "hsf2j", 
                "hsf2", "jojojr2", "jojojr1", "jojoj", "jojobanr1", "jojobajr1", "jojoban", "jojobaj", "jojobaner1", "jojobar1", "jojobane", "jojoba", "jojonr2", 
                "jojoar2", "jojonr1", "jojoar1", "jojon", "jojoa", "jojor2", "jojor1", "jojo", "jojour2", "jojour1", "jojou", "msha", "mshbr1", "mshb", "msh", "mshh", 
                "mshjr1", "mshj", "mshu", "mshvsfa1", "mshvsfa", "mshvsfb1", "mshvsfb", "mshvsf", "mshvsfh", "mshvsfj2", "mshvsfj1", "mshvsfj", "mshvsfu1", "mshvsfu", 
                "mvscar1", "mvsca", "mvscb", "mvscr1", "mvsc", "mvsch", "mvscjr1", "mvscj", "mvscjsing", "mvscur1", "mvscu", "nwarra", "nwarrb", "nwarr", "nwarrh", 
                "nwarru", "plsmaswda", "plsmaswd", "redearthr1", "redearth", "ringdesta", "ringdestb", "ringdest", "ringdesth", "rvschoola", "rvschool", "rvschoolu", 
                "jgakuen1", "jgakuen", "stargld2", "stargladj", "starglad", "sfa2", "sfa2ur1", "sfa2u", "sfa3b", "sfa3", "sfa3hr1", "sfa3h", "sfa3us", "sfa3ur1", 
                "sfa3u", "sfar3", "sfar2", "sfar1", "sfa", "sfau", "sfexa", "sfex", "sfexj", "sfexu", "sfexpj1", "sfexpj", "sfexpu1", "sfexp", "sfex2a", "sfex2", 
                "sfex2h", "sfex2j", "sfex2u1", "sfex2u", "sfex2pa", "sfex2p", "sfex2ph", "sfex2pj", "sfex2pu", "sf2ja", "sf2jc", "sf2jf", "sf2jh", "sf2j", "sf2j17", 
                "sf2jl", "sf2ua", "sf2ub", "sf2ue", "sf2uc", "sf2ud", "sf2uf", "sf2ug", "sf2uh", "sf2ui", "sf2uk", "sf2um", "sf2em", "sf2en", "sf2ea", "sf2eb", "sf2ee", 
                "sf2ed", "sf2ef", "sf2", "sf2hfj", "sf2ceja", "sf2cejb", "sf2cejc", "sf2cet", "sf2ceua", "sf2ceub", "sf2ceuc", "sf2ceea", "sf2ce", "sf2hfu", "sf2hf", 
                "sfiii2n", "sfiii2j", "sfiii2", "sfiii3r1", "sfiii3", "sfiii3nr1", "sfiii3jr1", "sfiii3n", "sfiii3j", "sfiii3ur1", "sfiii3u", "sfiiin", "sfiiina", 
                "sfiiia", "sfiii", "sfiiih", "sfiiij", "sfiiiu", "sfzar1", "sfza", "sfzbr1", "sfzb", "sfzhr1", "sfzh", "sfzjr2", "sfzjr1", "sfzj", "sfz2a", "sfz2br1", 
                "sfz2b", "sfz2h", "sfz2jr1", "sfz2j", "sfz2n", "sfz2alr1", "sfz2al", "sfz2alb", "sfz2alh", "sfz2alj", "sfz3ar1", "sfz3a", "sfz3jr2", "sfz3jr1", "sfz3j", 
                "smbombr1", "smbomb", "ssf2ta", "ssf2th", "ssf2tur1", "ssf2tu", "ssf2t", "ssf2xjr1r", "ssf2xjr1", "ssf2xj", "ssf2ar1", "ssf2a", "ssf2h", "ssf2jr2", 
                "ssf2jr1", "ssf2j", "ssf2u", "ssf2r1", "ssf2", "ssf2tba", "ssf2tbh", "ssf2tbj1", "ssf2tbj", "ssf2tbu", "ssf2tbr1", "ssf2tb", "techromna", "techromn", 
                "techromnu", "vhunt2r1", "vhunt2", "vhuntjr2", "vhuntjr1s", "vhuntjr1", "vhuntj", "vsav2", "vsava", "vsavb", "vsav", "vsavh", "vsavj", "vsavu", "vampjr1", 
                "vampja", "vampj", "warzardr1", "warzard", "xmvsfar3", "xmvsfar2", "xmvsfar1", "xmvsfa", "xmvsfb", "xmvsfr1", "xmvsf", "xmvsfh", "xmvsfjr3", "xmvsfjr2", 
                "xmvsfjr1", "xmvsfj", "xmvsfur2", "xmvsfur1", "xmvsfu", "xmcotaar2", "xmcotaar1", "xmcotaa", "xmcotab", "xmcotar1", "xmcota", "xmcotahr1", "xmcotah", 
                "xmcotajr", "xmcotaj3", "xmcotaj2", "xmcotaj1", "xmcotaj", "xmcotau" ]:
                buttonLayout = 1 # Capcom 6 button
            elif romName in [ "mknifty666", "mknifty", "mkprot4", "mkprot8", "mkprot9", "mkrep", "mkla1", "mkla2", "mkla3", "mkla4", "mkr4", "mk", "mkyturboe",
                "mkyturbo", "mktturbo", "mkyawdim", "mkyawdim2", "mkyawdim3", "mkyawdim4", "mk3p40", "mk3r10", "mk3r20", "mk3", "mk4b", "mk4a", "mk4", "mk2r11", "mk2r14",
                "mk2r20", "mk2r21", "mk2r30", "mk2r31e", "mk2", "mk2r32e", "mk2r42", "mk2r91", "mk2chal", "umk3r10", "umk3r11", "umk3" ]:
                buttonLayout = 2 # Mortal Kombat 5/6 button
            elif romName in [ "kinst", "kinst2", "kinst2uk" ]:
                buttonLayout = 3 # Killer Inistinct 6 button
            else:
                buttonLayout = 0 # Default layout if it's not a recognized game
        
        if messMode == -1:
            MameGenerator.generatePadsConfig(config, playersControllers, "", dpadMode, cfgPath, buttonLayout)
        else:
            MameGenerator.generatePadsConfig(config, playersControllers, messSysName[messMode], dpadMode, cfgPath, buttonLayout)

        # save the config file
        #mameXml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        mameXml = codecs.open(configFile, "w", "utf-8")
        dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        mameXml.write(dom_string)

        # bezels
        if 'bezel' not in system.config or system.config['bezel'] == '':
            bezel = None
        else:
            bezel = system.config['bezel']
        if system.isOptSet('forceNoBezel') and system.getOptBoolean('forceNoBezel'):
            bezel = None
        try:
            MameGenerator.writeBezelConfig(bezel, system, rom)
        except:
            MameGenerator.writeBezelConfig(None, system, rom)

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
    def generatePadsConfig(config, playersControllers, sysName, dpadMode, cfgPath, altButtons):
        # Common controls
        mappings = {
            "JOYSTICK_UP":    "joystick1up",
            "JOYSTICK_DOWN":  "joystick1down",
            "JOYSTICK_LEFT":  "joystick1left",
            "JOYSTICK_RIGHT": "joystick1right",
            "JOYSTICKLEFT_UP":    "joystick1up",
            "JOYSTICKLEFT_DOWN":  "joystick1down",
            "JOYSTICKLEFT_LEFT":  "joystick1left",
            "JOYSTICKLEFT_RIGHT": "joystick1right",
            "JOYSTICKRIGHT_UP": "joystick2up",
            "JOYSTICKRIGHT_DOWN": "joystick2down",
            "JOYSTICKRIGHT_LEFT": "joystick2left",
            "JOYSTICKRIGHT_RIGHT": "joystick2right",
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
        # Buttons that change based on game/setting
        if altButtons == 1: # Capcom 6-button Mapping (Based on Street Fighter II for SNES)
            mappings.update({"BUTTON1": "y"})
            mappings.update({"BUTTON2": "x"})
            mappings.update({"BUTTON3": "pageup"})
            mappings.update({"BUTTON4": "b"})
            mappings.update({"BUTTON5": "a"})
            mappings.update({"BUTTON6": "pagedown"})
        elif altButtons == 2: # MK 6-button Mapping (Based on Mortal Kombat 3 for SNES)
            mappings.update({"BUTTON1": "y"})
            mappings.update({"BUTTON2": "pageup"})
            mappings.update({"BUTTON3": "x"})
            mappings.update({"BUTTON4": "b"})
            mappings.update({"BUTTON5": "a"})
            mappings.update({"BUTTON6": "pagedown"})
        elif altButtons == 3: # KI 6-button Mapping (Based on Killer Instinct for SNES)
            mappings.update({"BUTTON1": "pageup"})
            mappings.update({"BUTTON2": "y"})
            mappings.update({"BUTTON3": "x"})
            mappings.update({"BUTTON4": "pagedown"})
            mappings.update({"BUTTON5": "b"})
            mappings.update({"BUTTON6": "a"})
        
        xml_mameconfig = MameGenerator.getRoot(config, "mameconfig")
        xml_system     = MameGenerator.getSection(config, xml_mameconfig, "system")
        xml_system.setAttribute("name", "default")

        MameGenerator.removeSection(config, xml_system, "input")
        xml_input = config.createElement("input")
        xml_system.appendChild(xml_input)
        
        # Open or create alternate config file for systems with special controllers/settings
        # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
        if sysName in ("cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb"):
            config_alt = minidom.Document()
            configFile_alt = cfgPath + sysName + ".cfg"
            if os.path.exists(configFile_alt) and cfgPath == "/userdata/system/configs/mame/":
                writeConfig = True
                try:
                    config_alt = minidom.parse(configFile_alt)
                except:
                    pass # reinit the file
            elif not os.path.exists(configFile_alt):
                writeConfig = True
            else:
                writeConfig = False
                try:
                    config_alt = minidom.parse(configFile_alt)
                except:
                    pass # reinit the file
            xml_mameconfig_alt = MameGenerator.getRoot(config_alt, "mameconfig")
            xml_system_alt = MameGenerator.getSection(config_alt, xml_mameconfig_alt, "system")
            xml_system_alt.setAttribute("name", sysName)
            
            MameGenerator.removeSection(config_alt, xml_system_alt, "input")
            xml_input_alt = config_alt.createElement("input")
            xml_system_alt.appendChild(xml_input_alt)
        
        nplayer = 1
        maxplayers = len(playersControllers)
        for playercontroller, pad in sorted(playersControllers.items()):
            mappings_use = mappings
            if "joystick1up" not in pad.inputs:
                mappings_use["JOYSTICK_UP"] = "up"
                mappings_use["JOYSTICK_DOWN"] = "down"
                mappings_use["JOYSTICK_LEFT"] = "left"
                mappings_use["JOYSTICK_RIGHT"] = "right"
                
            for mapping in mappings_use:
                if mappings_use[mapping] in pad.inputs:
                    xml_input.appendChild(MameGenerator.generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[mappings_use[mapping]], False, dpadMode))
                else:
                    rmapping = MameGenerator.reverseMapping(mappings_use[mapping])
                    if rmapping in pad.inputs:
                        xml_input.appendChild(MameGenerator.generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[rmapping], True, dpadMode))
                
            # Special case for CD-i - doesn't use default controls, map special controller
            # Keep orginal mapping functions for menus etc, create system-specific config file dor CD-i.
            if nplayer == 1 and sysName == "cdimono1":
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON1", int(pad.inputs["b"].id) + 1, "1", "0"))
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON2", int(pad.inputs["y"].id) + 1, "2", "0"))
                if dpadMode == 0:
                    xml_input_alt.appendChild(MameGenerator.generateIncDecPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "1023", "0", "10"))
                    xml_input_alt.appendChild(MameGenerator.generateIncDecPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "1023", "0", "10"))
                elif dpadMode == 1:
                    xml_input_alt.appendChild(MameGenerator.generateIncDecPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "1023", "0", "10"))
                    xml_input_alt.appendChild(MameGenerator.generateIncDecPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "1023", "0", "10"))
                else:
                    xml_input_alt.appendChild(MameGenerator.generateIncDecPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "1023", "0", "10"))
                    xml_input_alt.appendChild(MameGenerator.generateIncDecPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "1023", "0", "10"))
                
                #Hide LCD display
                MameGenerator.removeSection(config_alt, xml_system_alt, "video")
                xml_video_alt = config_alt.createElement("video")                
                xml_system_alt.appendChild(xml_video_alt)
                
                xml_screencfg_alt = config_alt.createElement("target")
                xml_screencfg_alt.setAttribute("index", "0")
                xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
                xml_video_alt.appendChild(xml_screencfg_alt)
                
            # Special case for APFM1000 - uses numpad controllers
            if nplayer <= 2 and sysName == "apfm1000":
                if nplayer == 1:
                    # Based on Colecovision button mapping, changed slightly since Enter = Fire
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", int(pad.inputs["a"].id) + 1, "32", "32"))        # Clear
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["b"].id) + 1, "32", "32"))        # Enter/Fire
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", int(pad.inputs["x"].id) + 1, "16", "16"))        # 1
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["y"].id) + 1, "16", "16"))        # 2
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", int(pad.inputs["pagedown"].id) + 1, "16", "16")) # 3
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", int(pad.inputs["pageup"].id) + 1, "64", "64"))   # 4
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["r2"].id) + 1, "64", "64"))       # 5
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", int(pad.inputs["l2"].id) + 1, "64", "64"))       # 6
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", int(pad.inputs["r3"].id) + 1, "128", "128"))     # 7
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["l3"].id) + 1, "128", "128"))     # 8
                    xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':joy.2', "OTHER", "5", "128", "128"))                                                  # 9
                    xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':joy.0', "OTHER", "1", "32", "32"))                                                    # 0
                elif nplayer == 2:
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["a"].id) + 1, "2", "2"))        # Clear
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["b"].id) + 1, "2", "2"))        # Enter/Fire
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["x"].id) + 1, "1", "1"))        # 1
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["y"].id) + 1, "1", "1"))        # 2
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["pagedown"].id) + 1, "1", "1")) # 3
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["pageup"].id) + 1, "4", "4"))   # 4
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["r2"].id) + 1, "4", "4"))       # 5
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["l2"].id) + 1, "4", "4"))       # 6
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["r3"].id) + 1, "8", "8"))       # 7
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["l3"].id) + 1, "8", "8"))       # 8
                    xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':joy.2', "TYPE_OTHER(243,1)", "6", "8", "8"))                                                    # 9
                    xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':joy.0', "TYPE_OTHER(243,1)", "2", "2", "2"))                                                    # 0
            # Special case for Astrocade - numpad on console
            if nplayer == 1 and sysName == "astrocde":
                # Based on Colecovision button mapping, keypad is on the console
                # A auto maps to Fire, using B for 0, Select for 9, Start for = (which is the "enter" key)
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["b"].id) + 1, "32", "0"))        # 0
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "16", "0"))        # 1
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["y"].id) + 1, "16", "0"))        # 2
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "16", "0")) # 3
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "8", "0"))    # 4
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "8", "0"))        # 5
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "8", "0"))        # 6
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "4", "0"))        # 7
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "4", "0"))        # 8
                xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':KEYPAD1', "KEYPAD", "6", "4", "0"))                                                     # 9
                xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':KEYPAD0', "KEYPAD", "1", "32", "0"))                                                    # = (Start)
            
            # Special case for Adam - numpad
            if nplayer == 1 and sysName == "adam":
                # Based on Colecovision button mapping - not enough buttons to map 0 & 9
                # Fire 1 & 2 map to A & B
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "2", "2"))          # 1
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["a"].id) + 1, "4", "4"))          # 2
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "8", "8"))   # 3
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "16", "16"))   # 4
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "32", "32"))       # 5
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "64", "64"))       # 6
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "128", "128"))     # 7
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "512", "512"))     # 8
                # xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "128", "128"))     9
                # xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", , "1", ""))                                      0                
                xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':joy1:hand:KEYPAD', "KEYPAD", "1", "1024", "0"))                                                   # #
                xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':joy1:hand:KEYPAD', "KEYPAD", "5", "2048", "0"))                                                   # *
            
            # Special case for Arcadia
            if nplayer <= 2 and sysName == "arcadia":
                if nplayer == 1:
                    # Based on Colecovision button mapping - not enough buttons to map clear, enter
                    # No separate fire button, Start + Select on console (automapped), Option button also on console.
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["a"].id) + 1, "8", "0"))        # 1
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["b"].id) + 1, "8", "0"))        # 2
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "8", "0"))        # 3
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["y"].id) + 1, "4", "0"))        # 4
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "4", "0")) # 5
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "4", "0"))   # 6
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "2", "0"))       # 7
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "2", "0"))       # 8
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "2", "0"))       # 9
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "1", "0"))       # 0
                    # xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Clear
                    # xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Enter
                elif nplayer == 2:
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["a"].id) + 1, "8", "0"))        # 1
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["b"].id) + 1, "8", "0"))        # 2
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "8", "0"))        # 3
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["y"].id) + 1, "4", "0"))        # 4
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "4", "0")) # 5
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "4", "0"))   # 6
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "2", "0"))       # 7
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "2", "0"))       # 8
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "2", "0"))       # 9
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "1", "0"))       # 0
                    # xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Clear
                    # xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Enter
            
            # Special case for Gamecom - buttons don't map normally
            if nplayer == 1 and sysName == "gamecom":
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':IN0', nplayer, pad.index, "P1_BUTTON1", int(pad.inputs["y"].id) + 1, "128", "128")) # A
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':IN1', nplayer, pad.index, "P1_BUTTON2", int(pad.inputs["x"].id) + 1, "1", "1"))     # B
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':IN1', nplayer, pad.index, "P1_BUTTON3", int(pad.inputs["b"].id) + 1, "2", "2"))     # C
                xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':IN2', nplayer, pad.index, "P1_BUTTON4", int(pad.inputs["a"].id) + 1, "2", "2"))     # D
                xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':IN0', "OTHER", "5", "16", "16"))                                                    # Menu
                xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':IN0', "OTHER", "1", "32", "32"))                                                    # Pause
            
            # Special case for Tomy Tutor - directions don't map normally
            # Also maps arrow keys to directional input & enter to North button to get through the initial menu without a keyboard
            if nplayer <= 2 and sysName == "tutor":
                if nplayer == 1:
                    if dpadMode == 0:
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "16", "0"))     # Down
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "32", "0"))     # Left
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "64", "0"))           # Up
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "128", "0")) # Right
                    elif dpadMode == 1:
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "16", "0"))     # Down
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "32", "0"))     # Left
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "128", "0")) # Right
                    else:                        
                        xml_input_dChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "32", "0"))     # Left
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "128", "0")) # Right
                    xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':LINE6', pad.index, "KEYBOARD", "ENTER", int(pad.inputs["a"].id) + 1, "16", "0"))      # Enter Key
                    xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':LINE7', pad.index, "KEYBOARD", "DOWN", int(pad.inputs["pagedown"].id) + 1, "4", "0")) # Down Arrow
                elif nplayer == 2:
                    if dpadMode == 0:
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "16", "0"))     # Down
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "32", "0"))     # Left
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "64", "0"))           # Up
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "128", "0")) # Right
                    elif dpadMode == 1:
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "16", "0"))     # Down
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "32", "0"))     # Left
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "128", "0")) # Right
                    else:
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "16", "0"))     # Down
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "32", "0"))     # Left
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(MameGenerator.generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "128", "0")) # Right
            
            # Special case for crvision - maps the 4 corner buttons + 2nd from upper right since MAME considers that button 2.
            if nplayer <= 2 and sysName == "crvision":
                if nplayer == 1:
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA1.7', nplayer, pad.index, "P1_BUTTON1", int(pad.inputs["y"].id) + 1, "128", "128"))  # P1 Button 1 (Shift)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA0.7', nplayer, pad.index, "P1_BUTTON2", int(pad.inputs["x"].id) + 1, "128", "128"))  # P1 Button 2 (Control)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA0.2', nplayer, pad.index, "KEYBOARD", int(pad.inputs["pagedown"].id) + 1, "8", "8")) # P1 Upper Right (1)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA1.1', nplayer, pad.index, "KEYBOARD", int(pad.inputs["b"].id) + 1, "4", "4"))        # P1 Lower Left (B)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA1.4', nplayer, pad.index, "KEYBOARD", int(pad.inputs["a"].id) + 1, "64", "64"))      # P1 Lower Right (6)
                    xml_input_alt.appendChild(MameGenerator.generateKeycodePortElement(config_alt, ':NMI', "P1_START", "1", "1", "0"))                                                      # Reset/Start
                elif nplayer == 2:
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA3.7', nplayer, pad.index, "P2_BUTTON1", int(pad.inputs["y"].id) + 1, "128", "128"))  # P2 Button 1 (-/=)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA2.7', nplayer, pad.index, "P2_BUTTON2", int(pad.inputs["x"].id) + 1, "128", "128"))  # P2 Button 2 (Right)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA2.2', nplayer, pad.index, "KEYBOARD", int(pad.inputs["pagedown"].id) + 1, "8", "8")) # P2 Upper Right (Space)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA3.1', nplayer, pad.index, "KEYBOARD", int(pad.inputs["b"].id) + 1, "4", "4"))        # P2 Lower Left (7)
                    xml_input_alt.appendChild(MameGenerator.generateSpecialPortElement(config_alt, ':PA3.1', nplayer, pad.index, "KEYBOARD", int(pad.inputs["a"].id) + 1, "64", "64"))      # P2 Lower Right (N)
            
            # BBC Micro - joystick not emulated/supported for most games, map some to gamepad
            if nplayer == 1 and sysName == "bbcb":
                xml_kbenable_alt = config_alt.createElement("keyboard")
                xml_kbenable_alt.setAttribute("tag", ":")
                xml_kbenable_alt.setAttribute("enabled", "1")
                xml_input_alt.appendChild(xml_kbenable_alt)
                xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':COL8', pad.index, "KEYBOARD", "QUOTE", int(pad.inputs["y"].id) + 1, "64", "64"))        # *
                xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':COL8', pad.index, "KEYBOARD", "SLASH", int(pad.inputs["x"].id) + 1, "16", "16"))        # ?
                xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':COL1', pad.index, "KEYBOARD", "Z", int(pad.inputs["b"].id) + 1, "64", "64"))            # Z
                xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':COL2', pad.index, "KEYBOARD", "X", int(pad.inputs["a"].id) + 1, "16", "16"))            # X
                xml_input_alt.appendChild(MameGenerator.generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "ENTER", int(pad.inputs["pagedown"].id) + 1, "16", "16")) # Enter
                if dpadMode == 0:
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "4", "4"))       # Down
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "2", "2"))       # Left
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "8", "8"))           # Up
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "128", "128")) # Right
                elif dpadMode == 1:
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "4", "4"))       # Down
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "2", "2"))       # Left
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "8", "8"))           # Up
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "128", "128")) # Right
                else:
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "4", "4"))       # Down
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "2", "2"))       # Left
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "8", "8"))           # Up
                    xml_input_alt.appendChild(MameGenerator.generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "128", "128")) # Right
            
            nplayer = nplayer + 1
            
        # Write alt config (if used, custom config is turned off or file doesn't exist yet)
        if sysName in ("cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb") and writeConfig:
            mameXml_alt = codecs.open(configFile_alt, "w", "utf-8")
            dom_string_alt = os.linesep.join([s for s in config_alt.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            mameXml_alt.write(dom_string_alt)

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
    def generatePortElement(config, nplayer, padindex, mapping, key, input, reversed, dpadMode):
        # Generic input
        xml_port = config.createElement("port")
        xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode(MameGenerator.input2definition(key, input, padindex + 1, reversed, dpadMode))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def generateSpecialPortElement(config, tag, nplayer, padindex, mapping, key, mask, default):
        # Special button input (ie mouse button to gamepad)
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", tag)
        xml_port.setAttribute("type", mapping)
        xml_port.setAttribute("mask", mask)
        xml_port.setAttribute("defvalue", default)
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode("JOYCODE_{}_BUTTON{}".format(padindex + 1, key))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def generateKeycodePortElement(config, tag, mapping, key, mask, default):
        # Map a keyboard key instead of a button (for start/select due to auto pad2key)
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", tag)
        xml_port.setAttribute("type", mapping)
        xml_port.setAttribute("mask", mask)
        xml_port.setAttribute("defvalue", default)
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode("KEYCODE_{}".format(key))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def generateComboPortElement(config, tag, padindex, mapping, key, button, mask, default):
        # Maps a keycode + button - for important keyboard keys when available
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", tag)
        xml_port.setAttribute("type", mapping)
        xml_port.setAttribute("mask", mask)
        xml_port.setAttribute("defvalue", default)
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode("KEYCODE_{} OR JOYCODE_{}_BUTTON{}".format(key, padindex + 1, button))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def generateComboDirPortElement(config, tag, padindex, mapping, key, buttontext, mask, default):
        # Maps a keyboard key + directional input - for keyboard arrow keys
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", tag)
        xml_port.setAttribute("type", mapping)
        xml_port.setAttribute("mask", mask)
        xml_port.setAttribute("defvalue", default)
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode("KEYCODE_{} OR ".format(key) + buttontext.format(padindex + 1, padindex + 1, padindex + 1))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def generateDirectionPortElement(config, tag, nplayer, padindex, mapping, key, mask, default):
        # Special direction mapping for emulated controllers
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", tag)
        xml_port.setAttribute("type", mapping)
        xml_port.setAttribute("mask", mask)
        xml_port.setAttribute("defvalue", default)
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode(key.format(padindex + 1, padindex + 1, padindex + 1))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def generateIncDecPortElement(config, tag, nplayer, padindex, mapping, inckey, deckey, mask, default, delta):
        # Mapping analog to digital (mouse, etc)
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", tag)
        xml_port.setAttribute("type", mapping)
        xml_port.setAttribute("mask", mask)
        xml_port.setAttribute("defvalue", default)
        xml_port.setAttribute("keydelta", delta)
        xml_newseq_inc = config.createElement("newseq")
        xml_newseq_inc.setAttribute("type", "increment")
        xml_port.appendChild(xml_newseq_inc)
        incvalue = config.createTextNode(inckey.format(padindex + 1, padindex + 1, padindex + 1))
        xml_newseq_inc.appendChild(incvalue)
        xml_newseq_dec = config.createElement("newseq")
        xml_port.appendChild(xml_newseq_dec)
        xml_newseq_dec.setAttribute("type", "decrement")
        decvalue = config.createTextNode(deckey.format(padindex + 1, padindex + 1, padindex + 1))
        xml_newseq_dec.appendChild(decvalue)
        return xml_port

    @staticmethod
    def input2definition(key, input, joycode, reversed, dpadMode):
        if input.type == "button":
            return "JOYCODE_{}_BUTTON{}".format(joycode, int(input.id)+1)
        elif input.type == "hat":
            if input.value == "1":
                return "JOYCODE_{}_HAT1UP".format(joycode)
            elif input.value == "2":
                return "JOYCODE_{}_HAT1RIGHT".format(joycode)
            elif input.value == "4":
                return "JOYCODE_{}_HAT1DOWN".format(joycode)
            elif input.value == "8":
                return "JOYCODE_{}_HAT1LEFT".format(joycode)
        elif input.type == "axis":
            if key == "joystick1up" or key == "up":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP".format(joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13".format(joycode, joycode, joycode)
            if key == "joystick1down" or key == "down":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN".format(joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14".format(joycode, joycode, joycode)
            if key == "joystick1left" or key == "left":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT".format(joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15".format(joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11".format(joycode, joycode, joycode)
            if key == "joystick1right" or key == "right":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT".format(joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16".format(joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12".format(joycode, joycode, joycode)
            if key == "joystick2up":
                return "JOYCODE_{}_RYAXIS_NEG_SWITCH OR JOYCODE_{}_BUTTON4".format(joycode, joycode)
            if key == "joystick2down":
                return "JOYCODE_{}_RYAXIS_POS_SWITCH OR JOYCODE_{}_BUTTON1".format(joycode, joycode)
            if key == "joystick2left":
                return "JOYCODE_{}_RXAXIS_NEG_SWITCH OR JOYCODE_{}_BUTTON3".format(joycode, joycode)
            if key == "joystick2right":
                return "JOYCODE_{}_RXAXIS_POS_SWITCH OR JOYCODE_{}_BUTTON2".format(joycode, joycode)
        eslog.warning("unable to find input2definition for {} / {}".format(input.type, key))
        return "unknown"

    @staticmethod
    def writeBezelConfig(bezel, system, rom):
        romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension

        tmpZipDir = "/var/run/mame_artwork/" + romBase # ok, no need to zip, a folder is taken too
        # clean, in case no bezel is set, and in case we want to recreate it
        if os.path.exists(tmpZipDir):
            shutil.rmtree(tmpZipDir)

        if bezel is None:
            return

        # let's generate the zip file
        os.makedirs(tmpZipDir)

        # bezels infos
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name)
        if bz_infos is None:
            return

        # copy the png inside
        os.symlink(bz_infos["png"], tmpZipDir + "/default.png")

        img_width, img_height = bezelsUtil.fast_image_size(bz_infos["png"])
        _, _, rotate = MameGenerator.getMameMachineSize(romBase, tmpZipDir)

        # assumes that all bezels are setup for 4:3H or 3:4V aspects
        if rotate == 270 or rotate == 90:
            bz_width = int(img_height * (3 / 4))
        else:
            bz_width = int(img_height * (4 / 3))
        bz_height = img_height
        bz_x = int((img_width - bz_width) / 2)
        bz_y = 0

        if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
            if system.config['bezel.tattoo'] == 'system':
                try:
                    tattoo_file = '/usr/share/batocera/controller-overlays/'+system.name+'.png'
                    if not os.path.exists(tattoo_file):
                        tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
                    tattoo = Image.open(tattoo_file)
                except Exception as e:
                    eslog.error("Error opening controller overlay: {}".format(tattoo_file))
            elif system.config['bezel.tattoo'] == 'custom' and os.path.exists(system.config['bezel.tattoo_file']):
                try:
                    tattoo_file = system.config['bezel.tattoo_file']
                    tattoo = Image.open(tattoo_file)
                except:
                    eslog.error("Error opening custom file: {}".format('tattoo_file'))
            else:
                try:
                    tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
                    tattoo = Image.open(tattoo_file)
                except:
                    eslog.error("Error opening custom file: {}".format('tattoo_file'))
            output_png_file = "/tmp/bezel_tattooed.png"
            back = Image.open(tmpZipDir + "/default.png")
            tattoo = tattoo.convert("RGBA")
            back = back.convert("RGBA")
            tw,th = bezelsUtil.fast_image_size(tattoo_file)
            tatwidth = int(240/1920 * img_width) # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
            pcent = float(tatwidth / tw)
            tatheight = int(float(th) * pcent)
            tattoo = tattoo.resize((tatwidth,tatheight), Image.ANTIALIAS)
            alpha = back.split()[-1]
            alphatat = tattoo.split()[-1]
            if system.isOptSet('bezel.tattoo_corner'):
                corner = system.config['bezel.tattoo_corner']
            else:
                corner = 'NW'
            if (corner.upper() == 'NE'):
                back.paste(tattoo, (img_width-tatwidth,20), alphatat) # 20 pixels vertical margins (on 1080p)
            elif (corner.upper() == 'SE'):
                back.paste(tattoo, (img_width-tatwidth,img_height-tatheight-20), alphatat)
            elif (corner.upper() == 'SW'):
                back.paste(tattoo, (0,img_height-tatheight-20), alphatat)
            else: # default = NW
                back.paste(tattoo, (0,20), alphatat)
            imgnew = Image.new("RGBA", (img_width,img_height), (0,0,0,255))
            imgnew.paste(back, (0,0,img_width,img_height))
            imgnew.save(output_png_file, mode="RGBA", format="PNG")

            try:
                os.remove(tmpZipDir + "/default.png")
            except:
                pass
            os.symlink(output_png_file, tmpZipDir + "/default.png")

        f = open(tmpZipDir + "/default.lay", 'w')
        f.write("<mamelayout version=\"2\">")
        f.write("<element name=\"bezel\"><image file=\"default.png\" /></element>")
        f.write("<view name=\"bezel\">")
        f.write("<screen index=\"0\"><bounds x=\"" + str(bz_x) + "\" y=\"" + str(bz_y) + "\" width=\"" + str(bz_width) + "\" height=\"" + str(bz_height) + "\" /></screen>")
        f.write("<bezel element=\"bezel\"><bounds x=\"0\" y=\"0\" width=\"" + str(img_width) + "\" height=\"" + str(img_height) + "\" /></bezel>")
        f.write("</view>")
        f.write("</mamelayout>")
        f.close()

    @staticmethod
    def getMameMachineSize(machine, tmpdir):
        proc = subprocess.Popen(["/usr/bin/mame/mame", "-listxml", machine], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        exitcode = proc.returncode

        if exitcode != 0:
            raise Exception("mame -listxml " + machine + " failed")

        infofile = tmpdir + "/infos.xml"
        f = open(infofile, "w")
        f.write(out.decode())
        f.close()

        infos = minidom.parse(infofile)
        display = infos.getElementsByTagName('display')

        for element in display:
            iwidth  = element.getAttribute("width")
            iheight = element.getAttribute("height")
            irotate = element.getAttribute("rotate")
            return int(iwidth), int(iheight), int(irotate)

        raise Exception("display element not found")
