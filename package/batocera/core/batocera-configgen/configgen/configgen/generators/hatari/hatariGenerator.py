from __future__ import annotations

import logging
import os

from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BIOS, CONFIGS, mkdir_if_not_exists
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

# libretro generator uses this, so it needs to be public
HATARI_CONFIG: Final = CONFIGS / "hatari"

class HatariGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "hatari",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        model_mapping = {
            "520st_auto":       { "machine": "st",      "tos": "auto" },
            "520st_100":        { "machine": "st",      "tos": "100"  },
            "520st_102":        { "machine": "st",      "tos": "102"  },
            "520st_104":        { "machine": "st",      "tos": "104"  },
            "520st_etos256":    { "machine": "st",      "tos": "etos256"  },
            "1040ste_auto":     { "machine": "ste",     "tos": "auto" },
            "1040ste_106":      { "machine": "ste",     "tos": "106"  },
            "1040ste_162":      { "machine": "ste",     "tos": "162"  },
            "1040ste_etos256":  { "machine": "ste",     "tos": "etos256"  },
            "megaste_auto":     { "machine": "megaste", "tos": "auto" },
            "megaste_205":      { "machine": "megaste", "tos": "205"  },
            "megaste_206":      { "machine": "megaste", "tos": "206"  },
            "megaste_etos256":  { "machine": "megaste", "tos": "etos256"  },
            "tt_auto":          { "machine": "tt",      "tos": "auto" },
            "tt_306":           { "machine": "tt",      "tos": "306"  },
            "tt_etos512":       { "machine": "tt",      "tos": "etos512"  },
            "falcon_auto":      { "machine": "falcon",  "tos": "auto" },
            "falcon_400":       { "machine": "falcon",  "tos": "400"  },
            "falcon_402":       { "machine": "falcon",  "tos": "402"  },
            "falcon_404":       { "machine": "falcon",  "tos": "404"  },
            "falcon_etos512":   { "machine": "falcon",  "tos": "etos512"  },
        }

        # Start emulator fullscreen
        commandArray: list[str | Path] = ["hatari", "--fullscreen"]

        # Machine can be st (default), ste, megaste, tt, falcon
        # st should use TOS 1.00 to TOS 1.04 (tos100 / tos102 / tos104 / emutos192k)
        # ste should use TOS 1.06 at least (tos106 / tos162 / tos206 / emutos192K)
        # megaste should use TOS 2.XX series (tos206 / emutos256k)
        # tt should use tos 3.XX / emutos512k
        # falcon should use tos 4.XX / emutos512k

        machine = "st"
        tosversion = "auto"
        if system.isOptSet("model") and system.config["model"] in model_mapping:
            machine   = model_mapping[system.config["model"]]["machine"]
            tosversion = model_mapping[system.config["model"]]["tos"]
        toslang = "us"
        if system.isOptSet("language"):
            toslang = system.config["language"]

        commandArray += ["--machine", machine]
        tos = HatariGenerator.findBestTos(BIOS, machine, tosversion, toslang)
        commandArray += [ "--tos", BIOS / tos]

        # RAM (ST Ram) options (0 for 512k, 1 for 1MB)
        memorysize = 0
        if system.isOptSet("ram"):
            memorysize = system.config["ram"]
        commandArray += ["--memsize", str(memorysize)]

        rom_extension = rom_path.suffix.lower()
        if rom_extension == ".hd":
            if system.isOptSet("hatari_drive") and system.config["hatari_drive"] == "ACSI":
                commandArray += ["--acsi", rom_path]
            else:
                commandArray += ["--ide-master", rom_path]
        elif rom_extension == ".gemdos":
            blank_file = HATARI_CONFIG / "blank.st"
            if not blank_file.exists():
                with blank_file.open('w'):
                    pass
            commandArray += ["--harddrive", rom_path, blank_file]
        else:
            # Floppy (A) options
            commandArray += ["--disk-a", rom_path]
            # Floppy (B) options
            commandArray += ["--drive-b", "off"]

        # config file
        HatariGenerator.generateConfig(system, playersControllers)

        return Command.Command(array=commandArray)

    @staticmethod
    def generateConfig(system, playersControllers):
        config = CaseSensitiveConfigParser(interpolation=None)

        padMapping = {
            1: "y",
            2: "b",
            3: "a"
        }

        mkdir_if_not_exists(HATARI_CONFIG)
        configFileName = HATARI_CONFIG / "hatari.cfg"
        if configFileName.is_file():
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

        with configFileName.open('w') as configfile:
            config.write(configfile)

    @staticmethod
    def findBestTos(biosdir: Path, machine, tos_version, language) -> str:
        # all languages by preference, when value is "auto"
        all_languages = ["us", "uk", "de", "es", "fr", "it", "nl", "ru", "se", ""]

        # machine bioses by prefered orders, when value is "auto"
        all_machines_bios = {
            "st":      ["etos256", "104", "102", "100"],
            "ste":     ["etos256", "162", "106"],
            "megaste": ["etos256", "206", "205"],
            "tt":      ["etos512", "306"],
            "falcon":  ["etos512", "404", "402", "400"]
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
                    if "etos" in v_tos_version:
                        biosversion = v_tos_version
                    else:
                        biosversion = f"tos{v_tos_version}"
                    filename = f"{biosversion}{v_language}.img"
                    if os.path.exists(f"{biosdir}/{filename}"):
                        eslog.debug(f"tos filename: {filename}")
                        return filename
                    else:
                        eslog.warning(f"tos filename {filename} not found")

        raise Exception(f"no bios found for machine {machine}")
