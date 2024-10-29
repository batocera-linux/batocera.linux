from __future__ import annotations

import re
from evdev import InputDevice
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

playConfig: Final = CONFIGS / 'play'
playSaves: Final = SAVES / 'play'
playConfigFile: Final = playConfig / 'Play Data Files' / 'config.xml'
playInputFile: Final = playConfig / 'Play Data Files' / 'inputprofiles' / 'default.xml'

class PlayGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "play",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Create necessary directories
        mkdir_if_not_exists(playConfig)
        mkdir_if_not_exists(playSaves)

        ## Work with the config.xml file
        root = ET.Element('Config')

        # Dictionary of preferences and defaults
        preferences = {
            'ps2.arcaderoms.directory': {'Type': 'path', 'Value': '/userdata/roms/namco2x6'},
            'ui.showexitconfirmation': {'Type': 'boolean', 'Value': 'false'},
            'ui.pausewhenfocuslost': {'Type': 'boolean', 'Value': 'false'},
            'ui.showeecpuusage': {'Type': 'boolean', 'Value': 'false'},
            'ps2.limitframerate': {'Type': 'boolean', 'Value': 'true'},
            'renderer.widescreen': {'Type': 'boolean', 'Value': 'false'},
            'system.language': {'Type': 'integer', 'Value': '1'},
            'video.gshandler': {'Type': 'integer', 'Value': '0'},
            'renderer.opengl.resfactor': {'Type': 'integer', 'Value': '1'},
            'renderer.presentationmode': {'Type': 'integer', 'Value': '1'},
            'renderer.opengl.forcebilineartextures': {'Type': 'boolean', 'Value': 'false'},
        }

        # Check if the configuration file exists
        if playConfigFile.exists():
            tree = ET.parse(playConfigFile)
            root = tree.getroot()

        # Add or update preferences
        for pref_name, pref_attrs in preferences.items():
            pref_element = root.find(f".//Preference[@Name='{pref_name}']")
            if pref_element is None:
                # Create a new preference element if it doesn't exist
                pref_element = ET.SubElement(root, 'Preference', Name=pref_name)

            # Update attribute values
            for attr_name, attr_value in pref_attrs.items():
                pref_element.attrib[attr_name] = attr_value
                # Check system options for overriding values
                if pref_name == 'ps2.limitframerate' and system.isOptSet('play_vsync'):
                    pref_element.attrib['Value'] = system.config['play_vsync']
                if pref_name == 'renderer.widescreen' and system.isOptSet('play_widescreen'):
                    pref_element.attrib['Value'] = system.config['play_widescreen']
                if pref_name == 'system.language' and system.isOptSet('play_language'):
                    pref_element.attrib['Value'] = system.config['play_language']
                if pref_name == 'video.gshandler' and system.isOptSet('play_api'):
                    pref_element.attrib['Value'] = system.config['play_api']
                if pref_name == 'renderer.opengl.resfactor' and system.isOptSet('play_scale'):
                    pref_element.attrib['Value'] = system.config['play_scale']
                if pref_name == 'renderer.presentationmode' and system.isOptSet('play_mode'):
                    pref_element.attrib['Value'] = system.config['play_mode']
                if pref_name == 'renderer.opengl.forcebilineartextures' and system.isOptSet('play_filter'):
                    pref_element.attrib['Value'] = system.config['play_filter']

        # Write the updated configuration back to the file
        tree = ET.ElementTree(root)
        playConfigFile.parent.mkdir(parents=True, exist_ok=True)
        tree.write(playConfigFile)

        ## Handle controller settings
        # Analog not functioning
        playMapping = {
            'a': 'circle',
            'b': 'cross',
            'x': 'triangle',
            'y': 'square',
            'start': 'start',
            'select': 'select',
            'pageup': 'l1',
            'pagedown': 'r1',
            'joystick1left': 'analog_left_x',
            'joystick1up': 'analog_left_y',
            'joystick2left': 'analog_right_x',
            'joystick2up': 'analog_right_y',
            'up': 'dpad_up',
            'down': 'dpad_down',
            'left': 'dpad_left',
            'right': 'dpad_right',
            'l2': 'l2',
            'r2': 'r2',
            'l3': 'l3',
            'r3': 'r3'
        }

        # Functions to convert the GUID
        def get_device_id(dev: InputDevice) -> str:
            uniq = dev.uniq  # Unique string (e.g., MAC) for the device
            
            if uniq and re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", uniq):
                return uniq.lower()  # Return the MAC address as-is, in lowercase
            
            # Fallback: use vendor, product, and version if uniq is not a valid MAC
            device = [0] * 6
            vendor = dev.info.vendor
            product = dev.info.product
            version = dev.info.version
            device[0] = vendor & 0xFF
            device[1] = (vendor >> 8) & 0xFF
            device[2] = product & 0xFF
            device[3] = (product >> 8) & 0xFF
            device[4] = version & 0xFF
            device[5] = (version >> 8) & 0xFF
            
            return ':'.join(f"{byte:x}" for byte in device)

        def create_input_preferences(input_config, pad_guid, key_id, key_type, provider_id, nplayer, joystick_name, binding_type, hat_value):
            """Helper function to create XML preferences for joystick inputs."""
            ET.SubElement(input_config,
                          "Preference",
                          Name=f"input.pad{nplayer}.{playMapping[joystick_name]}.bindingtarget1.deviceId",
                          Type="string",
                          Value=pad_guid)

            ET.SubElement(input_config,
                          "Preference",
                          Name=f"input.pad{nplayer}.{playMapping[joystick_name]}.bindingtarget1.keyId",
                          Type="integer",
                          Value=str(key_id))

            ET.SubElement(input_config,
                          "Preference",
                          Name=f"input.pad{nplayer}.{playMapping[joystick_name]}.bindingtarget1.keyType",
                          Type="integer",
                          Value=str(key_type))

            ET.SubElement(input_config,
                          "Preference",
                          Name=f"input.pad{nplayer}.{playMapping[joystick_name]}.bindingtarget1.providerId",
                          Type="integer",
                          Value=str(provider_id))

            ET.SubElement(input_config,
                          "Preference",
                          Name=f"input.pad{nplayer}.{playMapping[joystick_name]}.bindingtype",
                          Type="integer",
                          Value=str(binding_type))

            ET.SubElement(input_config,
                          "Preference",
                          Name=f"input.pad{nplayer}.{playMapping[joystick_name]}.povhatbinding.refvalue",
                          Type="integer",
                          Value=str(hat_value))

        input_config = ET.Element("Config")

        # Iterate over connected controllers with a limit of 2 players
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            controller = playersControllers[playercontroller]
            dev = InputDevice(pad.device_path)
            pad_guid = get_device_id(dev)
            provider_id = 1702257782
            
            if nplayer <= 2:
                # Write this per pad
                ET.SubElement(
                    input_config,
                    "Preference",
                    Name=f"input.pad{nplayer}.analog.sensitivity",
                    Type="float",
                    Value=str(1.000000)
                )
                
                # Handle joystick inputs
                for index in controller.inputs:
                    input = controller.inputs[index]
                    if input.name not in playMapping:
                        continue
                    
                    if input.type == 'axis':
                        key_type = 1
                        binding_type = 1
                        key_id = input.id
                        hat_value = -1
                        create_input_preferences(input_config, pad_guid, key_id, key_type, provider_id, nplayer, input.name, binding_type, hat_value)

                    elif input.type == 'hat':
                        key_type = 2
                        binding_type = 3
                        key_id = 17 if input.name in ['up', 'down'] else 16
                        hat_value = 4 if input.name in ['up', 'left'] else 0
                        if input.name in ['up', 'down', 'left', 'right']:
                            create_input_preferences(input_config, pad_guid, key_id, key_type, provider_id, nplayer, input.name, binding_type, hat_value)

                    elif input.type == 'button':
                        key_type = 0
                        binding_type = input.value
                        key_id = input.code
                        hat_value = -1
                        create_input_preferences(input_config, pad_guid, key_id, key_type, provider_id, nplayer, input.name, binding_type, hat_value)

                nplayer += 1
        
        # Save the controller settings to the specified input file
        input_tree = ET.ElementTree(input_config)
        ET.indent(input_tree, space="    ", level=0)
        playInputFile.parent.mkdir(parents=True, exist_ok=True)
        input_tree.write(playInputFile)

        ## Prepare the command to run the emulator
        commandArray = ["/usr/bin/Play", "--fullscreen"]

        if rom != "config":
            # if zip, it's a namco arcade game
            if rom.lower().endswith("zip"):
                # strip path & extension
                commandArray.extend(["--arcade", Path(rom).stem])
            else:
                commandArray.extend(["--disc", rom])

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME": playConfig,
                "XDG_DATA_HOME": playConfig,
                "XDG_CACHE_HOME": CACHE,
                "QT_QPA_PLATFORM": "xcb"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if 'play_widescreen' in config and config['play_widescreen'] == "true":
            return 16/9
        elif 'play_mode' in config and config['play_mode'] == "0":
            return 16/9
        else:
            return 4/3
