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

        # Data Section
        data = ET.Element("data")
        ET.SubElement(data, "rompath").text = str(ROMS / "cannonball") + "/"
        ET.SubElement(data, "respath").text = str(configDir) + "/"
        ET.SubElement(data, "savepath").text = str(SAVES / "cannonball") + "/"
        ET.SubElement(data, "crc32").text = "0"

        # Video Section
        video = ET.Element("video")
        ET.SubElement(video, "mode").text = "1"  # Fullscreen
        window = ET.SubElement(video, "window")
        ET.SubElement(window, "scale").text = "2"
        ET.SubElement(video, "fps_counter").text = "1" if system.config.show_fps else "0"
        ET.SubElement(video, "widescreen").text = system.config.get("ratio", "0")
        ET.SubElement(video, "hires").text = system.config.get("highResolution", "0")
        ET.SubElement(video, "vsync").text = system.config.get("vsync", "1") # default vsync to 1
        ET.SubElement(video, "scanlines").text = system.config.get("scanlines", "0")
        ET.SubElement(video, "fps").text = system.config.get("fps", "2")  # 60 FPS default

        # Sound Section
        # OutRun shipped with a corrupt PCM sample ROM. This uses the repaired ROM 'opr-10188.71f'
        sound = ET.Element("sound")
        ET.SubElement(sound, "enable").text = "1"
        ET.SubElement(sound, "fix_samples").text = "0" # run without it
        ET.SubElement(sound, "advertise").text = "1"
        ET.SubElement(sound, "preview").text = "1"

        # Engine Section
        engine = ET.Element("engine")
        ET.SubElement(engine, "time").text = system.config.get("time_limit", "1")
        ET.SubElement(engine, "traffic").text = system.config.get("traffic_level", "1")
        ET.SubElement(engine, "freeplay").text = "0"
        ET.SubElement(engine, "japanese_tracks").text = "0"
        ET.SubElement(engine, "prototype").text = "0"
        ET.SubElement(engine, "levelobjects").text = "1"
        ET.SubElement(engine, "fix_bugs").text = system.config.get("fix_bugs", "1")
        ET.SubElement(engine, "fix_timer").text = "0"
        ET.SubElement(engine, "new_attract").text = "1"
        ET.SubElement(engine, "offroad").text = system.config.get("cheats_offroad", "0")
        ET.SubElement(engine, "grippy_tyres").text = system.config.get("cheats_grippy_tyres", "0")
        ET.SubElement(engine, "bumper").text = "0"
        ET.SubElement(engine, "turbo").text = system.config.get("cheats_turbo", "0")
        ET.SubElement(engine, "car_color").text = system.config.get("car_colour", "0")

        # Controls Section
        controls = ET.Element("controls")
        ET.SubElement(controls, "gear").text = system.config.get("gear_mode", "3") # default, automatic

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
            cannonballXml.write(prettify(engine))
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
