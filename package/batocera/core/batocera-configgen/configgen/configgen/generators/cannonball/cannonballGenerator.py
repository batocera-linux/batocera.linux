from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class CannonballGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "cannonball",
            "keys": {"exit": ["KEY_LEFTALT", "KEY_F4"]}
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        configDir = CONFIGS / "cannonball"
        mkdir_if_not_exists(configDir)

        configFile = configDir / "config.xml"

        # Create data section
        data = ET.Element("data")
        ET.SubElement(data, "rompath").text = str(ROMS / "cannonball") + "/"
        ET.SubElement(data, "respath").text = str(configDir) + "/"
        ET.SubElement(data, "savepath").text = str(SAVES / "cannonball") + "/"
        ET.SubElement(data, "crc32").text = "0"

        # Create video section
        video = ET.Element("video")
        ET.SubElement(video, "mode").text = "1"  # fullscreen
        window = ET.SubElement(video, "window")
        ET.SubElement(window, "scale").text = "2" # scale
        ET.SubElement(video, "fps_counter").text = "1" if (system.isOptSet("showFPS") and system.getOptBoolean("showFPS")) else "0"
        ET.SubElement(video, "widescreen").text = "1" if (system.isOptSet("ratio") and system.config["ratio"] == "1") else "0"
        ET.SubElement(video, "hires").text = "1" if (system.isOptSet("highResolution") and system.config["highResolution"] == "1") else "0"
        ET.SubElement(video, "vsync").text = "1"  # default vsync to 1
        ET.SubElement(video, "scanlines").text = "0"
        ET.SubElement(video, "fps").text = "2" # 60 fps

        # OutRun shipped with a corrupt PCM sample ROM. This uses the repaired ROM 'opr-10188.71f'
        sound = ET.Element("sound")
        ET.SubElement(sound, "enable").text = "1"
        ET.SubElement(sound, "fix_samples").text = "0"  # run without it

        # Create controls section - disable, use controller defaults
        controls = ET.Element("controls")
        #from .cannonballControllers import generateControllerConfig
        #generateControllerConfig(controls, playersControllers)

        # Function to convert XML to pretty-printed
        def prettify(element: ET.Element) -> bytes:
            ET.indent(element, space='    ')
            return ET.tostring(element, encoding='unicode').encode('utf-8')

        # Save the config file with multiple sections
        with configFile.open("wb") as cannonballXml:
            cannonballXml.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            cannonballXml.write(prettify(data))
            cannonballXml.write(b"\n")
            cannonballXml.write(prettify(video))
            cannonballXml.write(b"\n")
            cannonballXml.write(prettify(sound))
            cannonballXml.write(b"\n")
            cannonballXml.write(prettify(controls))

        write_sdl_controller_db(playersControllers, configDir / "gamecontrollerdb.txt")

        commandArray = ["/usr/bin/cannonball", "-cfgfile", configFile]

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_HOME": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )
