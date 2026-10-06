from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class Cannonball(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.config_dir / 'gamecontrollerdb.txt'

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'cannonball',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Data Section
        data = ET.Element('data')
        ET.SubElement(data, 'rompath').text = str(self.roms_dir) + '/'
        ET.SubElement(data, 'respath').text = str(self.config_dir) + '/'
        ET.SubElement(data, 'savepath').text = str(self.saves_dir) + '/'
        ET.SubElement(data, 'crc32').text = '0'

        # Video Section
        video = ET.Element('video')
        ET.SubElement(video, 'mode').text = '1'  # Fullscreen
        window = ET.SubElement(video, 'window')
        ET.SubElement(window, 'scale').text = '2'
        ET.SubElement(video, 'fps_counter').text = '1' if self.config.show_fps else '0'
        ET.SubElement(video, 'widescreen').text = self.config.get('ratio', '0')
        ET.SubElement(video, 'hires').text = self.config.get('highResolution', '0')
        ET.SubElement(video, 'vsync').text = self.config.get('vsync', '1')  # default vsync to 1
        ET.SubElement(video, 'scanlines').text = self.config.get('scanlines', '0')
        ET.SubElement(video, 'fps').text = self.config.get('fps', '2')  # 60 FPS default

        # Sound Section
        # OutRun shipped with a corrupt PCM sample ROM. This uses the repaired ROM 'opr-10188.71f'
        sound = ET.Element('sound')
        ET.SubElement(sound, 'enable').text = '1'
        ET.SubElement(sound, 'fix_samples').text = '0'  # run without it
        ET.SubElement(sound, 'advertise').text = '1'
        ET.SubElement(sound, 'preview').text = '1'

        # Engine Section
        engine = ET.Element('engine')
        ET.SubElement(engine, 'time').text = self.config.get('time_limit', '1')
        ET.SubElement(engine, 'traffic').text = self.config.get('traffic_level', '1')
        ET.SubElement(engine, 'freeplay').text = '0'
        ET.SubElement(engine, 'japanese_tracks').text = '0'
        ET.SubElement(engine, 'prototype').text = '0'
        ET.SubElement(engine, 'levelobjects').text = '1'
        ET.SubElement(engine, 'fix_bugs').text = self.config.get('fix_bugs', '1')
        ET.SubElement(engine, 'fix_timer').text = '0'
        ET.SubElement(engine, 'new_attract').text = '1'
        ET.SubElement(engine, 'offroad').text = self.config.get('cheats_offroad', '0')
        ET.SubElement(engine, 'grippy_tyres').text = self.config.get('cheats_grippy_tyres', '0')
        ET.SubElement(engine, 'bumper').text = '0'
        ET.SubElement(engine, 'turbo').text = self.config.get('cheats_turbo', '0')
        ET.SubElement(engine, 'car_color').text = self.config.get('car_colour', '0')

        # Controls Section
        controls = ET.Element('controls')
        ET.SubElement(controls, 'gear').text = self.config.get('gear_mode', '3')  # default, automatic

        # Function to convert XML to pretty-printed
        def prettify(element: ET.Element) -> bytes:
            ET.indent(element, space='    ')
            return ET.tostring(element, encoding='unicode').encode('utf-8')

        # Save the config file with multiple sections
        config_file = self.config_dir / 'config.xml'
        with config_file.open('wb') as cannonballXml:
            cannonballXml.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            cannonballXml.write(prettify(data))
            cannonballXml.write(b'\n')
            cannonballXml.write(prettify(video))
            cannonballXml.write(b'\n')
            cannonballXml.write(prettify(sound))
            cannonballXml.write(b'\n')
            cannonballXml.write(prettify(engine))
            cannonballXml.write(b'\n')
            cannonballXml.write(prettify(controls))

        return Command(
            ['/usr/bin/cannonball', '-cfgfile', config_file],
            env={
                'XDG_DATA_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
