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

eslog = get_logger(__name__)

class MameGenerator(Generator):

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

        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        commandArray =  [ "/usr/bin/mame/mame" ]
        commandArray += [ "-skip_gameinfo" ]
        commandArray += [ "-rompath",      romDirname ]

        # MAME various paths we can probably do better
        commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
        commandArray += [ "-fontpath",     "/usr/bin/mame/" ]               # Fonts can be left on ROM filesystem
        commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
        commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path or cheat.7z file ?
        commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
        commandArray += [ "-artpath",       "/userdata/decorations/;/var/run/mame_artwork/;/usr/bin/mame/artwork/" ] # first for systems ; second for overlays

        # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
        commandArray += [ "-nvram_directory" ,    "/userdata/saves/mame/nvram/" ]
        commandArray += [ "-cfg_directory"   ,    "/userdata/system/configs/mame/" ]
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

        # Finally we pass game name
        commandArray += [ romBasename ]

        # config file
        config = minidom.Document()
        configFile = "/userdata/system/configs/mame/default.cfg"
        if os.path.exists(configFile):
            try:
                config = minidom.parse(configFile)
            except:
                pass # reinit the file

        MameGenerator.generatePadsConfig(config, playersControllers)

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
            MameGenerator.writeBezelConfig(bezel, system.name, rom)
        except:
            MameGenerator.writeBezelConfig(None, system.name, rom)

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
    def generatePadsConfig(config, playersControllers):
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

        xml_mameconfig = MameGenerator.getRoot(config, "mameconfig")
        xml_system     = MameGenerator.getSection(config, xml_mameconfig, "system")
        xml_system.setAttribute("name", "default")

        MameGenerator.removeSection(config, xml_system, "input")
        xml_input = config.createElement("input")
        xml_system.appendChild(xml_input)

        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            mappings_use = mappings
            if "joystick1up" not in pad.inputs:
                mappings_use["JOYSTICK_UP"] = "up"
                mappings_use["JOYSTICK_DOWN"] = "down"
                mappings_use["JOYSTICK_LEFT"] = "left"
                mappings_use["JOYSTICK_RIGHT"] = "right"

            for mapping in mappings_use:
                if mappings_use[mapping] in pad.inputs:
                    xml_input.appendChild(MameGenerator.generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[mappings_use[mapping]], False))
                else:
                    rmapping = MameGenerator.reverseMapping(mappings_use[mapping])
                    if rmapping in pad.inputs:
                        xml_input.appendChild(MameGenerator.generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[rmapping], True))
            nplayer = nplayer + 1

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
    def generatePortElement(config, nplayer, padindex, mapping, key, input, reversed):
        xml_port = config.createElement("port")
        xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode(MameGenerator.input2definition(key, input, padindex + 1, reversed))
        xml_newseq.appendChild(value)
        return xml_port

    @staticmethod
    def input2definition(key, input, joycode, reversed):
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
                return "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP".format(joycode, joycode)
            if key == "joystick1down" or key == "down":
                return "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN".format(joycode, joycode)
            if key == "joystick1left" or key == "left":
                return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT".format(joycode, joycode)
            if key == "joystick1right" or key == "right":
                return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT".format(joycode, joycode)
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
    def writeBezelConfig(bezel, systemName, rom):
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
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, systemName)
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
