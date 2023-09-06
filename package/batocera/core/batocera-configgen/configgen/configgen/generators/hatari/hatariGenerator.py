#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from utils.logger import get_logger
import os
import configparser
import batoceraFiles

eslog = get_logger(__name__)

class HatariGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        model_mapping = {
            "520st_auto":   { "machine": "st",      "tos": "auto" },
            "520st_100":    { "machine": "st",      "tos": "100"  },
            "520st_102":    { "machine": "st",      "tos": "102"  },
            "520st_104":    { "machine": "st",      "tos": "104"  },
            "1040ste_auto": { "machine": "ste",     "tos": "auto" },
            "1040ste_106":  { "machine": "ste",     "tos": "106"  },
            "1040ste_162":  { "machine": "ste",     "tos": "162"  },
            "megaste_auto": { "machine": "megaste", "tos": "auto" },
            "megaste_205":  { "machine": "megaste", "tos": "205"  },
            "megaste_206":  { "machine": "megaste", "tos": "206"  },
        }
        
        # Start emulator fullscreen
        commandArray = ["hatari", "--fullscreen"]
        
        # Machine can be st (default), ste, megaste, tt, falcon
        # st should use TOS 1.00 to TOS 1.04 (tos100 / tos102 / tos104)
        # ste should use TOS 1.06 at least (tos106 / tos162 / tos206)
        # megaste should use TOS 2.XX series (tos206)
        # tt should use tos 3.XX
        # falcon should use tos 4.XX
        
        machine = "st"
        tosversion = "auto"
        if system.isOptSet("model") and system.config["model"] in model_mapping:
            machine   = model_mapping[system.config["model"]]["machine"]
            tosversion = model_mapping[system.config["model"]]["tos"]
        toslang = "us"
        if system.isOptSet("language"):
            toslang = system.config["language"]

        commandArray += ["--machine", machine]
        biosdir = "/userdata/bios"
        tos = HatariGenerator.findBestTos(biosdir, machine, tosversion, toslang)
        commandArray += [ "--tos", f"{biosdir}/{tos}"]
        
        # RAM (ST Ram) options (0 for 512k, 1 for 1MB)
        memorysize = 0
        if system.isOptSet("ram"):
            memorysize = system.config["ram"]
        commandArray += ["--memsize", str(memorysize)]
        
        rom_extension = os.path.splitext(rom)[1].lower()
        if rom_extension == ".hd":
            if system.isOptSet("hatari_drive") and system.config["hatari_drive"] == "ASCI":
                commandArray += ["--asci", rom]
            else:
                commandArray += ["--ide-master", rom]
        elif rom_extension == ".gemdos":
            blank_file = "/userdata/system/configs/hatari/blank.st"
            if not os.path.exists(blank_file):
                with open(blank_file, 'w') as file:
                    pass
            commandArray += ["--harddrive", rom, blank_file]
        else:
            # Floppy (A) options
            commandArray += ["--disk-a", rom]
            # Floppy (B) options
            commandArray += ["--drive-b", "off"]
        
        # config file
        HatariGenerator.generateConfig(system, playersControllers)

        return Command.Command(array=commandArray)

    @staticmethod
    def generateConfig(system, playersControllers):
        config = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        config.optionxform = str

        padMapping = {
            1: "y",
            2: "b",
            3: "a"
        }

        configdir = "{}/{}".format(batoceraFiles.CONF, "hatari")
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        configFileName = "{}/{}".format(configdir, "hatari.cfg")
        if os.path.isfile(configFileName):
            config.read(configFileName)

        # pads
        # disable previous configuration
        for i in range(1, 6): # 1 to 5 included
            section = "Joystick" + str(i)
            if config.has_section(section):
                config.set(section, "nJoyId", "-1")
                config.set(section, "nJoystickMode", "0")

        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer <= 5:
                section = "Joystick" + str(nplayer)
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, "nJoyId", str(pad.index))
                config.set(section, "nJoystickMode", "1")

                if padMapping[1] in pad.inputs:
                    config.set(section, "nButton1", str(pad.inputs[padMapping[1]].id))
                else:
                    config.set(section, "nButton1", "0")
                if padMapping[2] in pad.inputs:
                    config.set(section, "nButton2", str(pad.inputs[padMapping[2]].id))
                else:
                    config.set(section, "nButton2", "1")
                if padMapping[3] in pad.inputs:
                    config.set(section, "nButton3", str(pad.inputs[padMapping[3]].id))
                else:
                    config.set(section, "nButton3", "2")
            nplayer += 1

        # Log
        if not config.has_section("Log"):
            config.add_section("Log")
        config.set("Log", "bConfirmQuit", "FALSE")

        # Screen
        if not config.has_section("Screen"):
            config.add_section("Screen")
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            config.set("Screen", "bShowStatusbar", "TRUE")
        else:
            config.set("Screen", "bShowStatusbar", "FALSE")

        with open(configFileName, 'w') as configfile:
            config.write(configfile)

    @staticmethod
    def findBestTos(biosdir, machine, tos_version, language):
        # all languages by preference, when value is "auto"
        all_languages = ["us", "uk", "de", "es", "fr", "it", "nl", "ru", "se", ""]

        # machine bioses by prefered orders, when value is "auto"
        all_machines_bios = {
            "st":      ["104", "102", "100"],
            "ste":     ["162", "106"],
            "megaste": ["206", "205"]
        }
        
        if machine in all_machines_bios:
            l_tos = []
            if tos_version != "auto":
                l_tos = [tos_version]
            l_tos.extend(all_machines_bios[machine])
            for v_tos_version in l_tos:
                l_lang = []
                if l_lang != "auto":
                    l_lang = [language]
                l_lang.extend(all_languages)
                for v_language in l_lang:
                    filename = f"tos{v_tos_version}{v_language}.img"
                    if os.path.exists(f"{biosdir}/{filename}"):
                        eslog.debug(f"tos filename: {filename}")
                        return filename
                    else:
                        eslog.warning(f"tos filename {filename} not found")

        raise Exception(f"no bios found for machine {machine}")
