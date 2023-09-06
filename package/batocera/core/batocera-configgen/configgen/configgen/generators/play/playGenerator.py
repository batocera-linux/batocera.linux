#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import os
from os import path
import xml.etree.ElementTree as ET

playConfig = batoceraFiles.CONF + '/play'
playSaves = batoceraFiles.SAVES + '/play'
playHome = batoceraFiles.CONF
playConfigFile = playConfig + '/Play Data Files/config.xml'
playInputFile = playConfig + '/Play Data Files/inputprofiles/default.xml'

class PlayGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        # Create config folder
        if not path.isdir(playConfig):
            os.makedirs(playConfig)
        # Create save folder
        if not path.isdir(playSaves):
            os.makedirs(playSaves)
        
        ## Work with the config.xml file
        root = ET.Element('Config')
        
        # Dictionary of preferences and defaults
        preferences = {
            'ps2.arcaderoms.directory': {
                'Type': 'path',
                'Value': '/userdata/roms/namco2x6'
            },
            'ui.showexitconfirmation': {
                'Type': 'boolean',
                'Value': 'false'
            },
            'ui.pausewhenfocuslost': {
                'Type': 'boolean',
                'Value': 'false'
            },
            'ui.showeecpuusage': {
                'Type': 'boolean',
                'Value': 'false'
            },
            'ps2.limitframerate': {
                'Type': 'boolean',
                'Value': 'true'
            },
            'renderer.widescreen': {
                'Type': 'boolean',
                'Value': 'false'
            },
            'system.language': {
                'Type': 'integer',
                'Value': '1'
            },
            'video.gshandler': {
                'Type': 'integer',
                'Value': '0'
            },
            'renderer.opengl.resfactor': {
                'Type': 'integer',
                'Value': '1'
            },
            'renderer.presentationmode': {
                'Type': 'integer',
                'Value': '1'
            },
            'renderer.opengl.forcebilineartextures': {
                'Type': 'boolean',
                'Value': 'false'
            }                          
        }

        # Check if the file exists
        if os.path.exists(playConfigFile):
            tree = ET.parse(playConfigFile)
            root = tree.getroot()
        # Add or update preferences
        for pref_name, pref_attrs in preferences.items():
            pref_element = root.find(f".//Preference[@Name='{pref_name}']")
            if pref_element is None:
                # Preference doesn't exist, create a new element
                pref_element = ET.SubElement(root, 'Preference')
                pref_element.attrib['Name'] = pref_name
            # Set or update attribute values
            for attr_name, attr_value in pref_attrs.items():
                pref_element.attrib[attr_name] = attr_value
                # User options
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
                 
        # Create the tree and write to the file
        tree = ET.ElementTree(root)
        
        # Handle the case when the file doesn't exist
        if not os.path.exists(playConfigFile):
            # Create the directory if it doesn't exist
            directory = os.path.dirname(playConfigFile)
            os.makedirs(directory, exist_ok=True)
            # Write the XML to the file
            tree.write(playConfigFile)
        else:
            # File exists, write the XML to the existing file
            with open(playConfigFile, "wb") as file:
                tree.write(file)
        
        commandArray = ["/usr/bin/Play"]
        
        if rom != "config":
            # if zip, it's a namco arcade game
            if (rom.lower().endswith("zip")):
                # strip path & extension
                rom = os.path.basename(rom)
                rom = os.path.splitext(rom)[0]
                commandArray.extend(["--arcade", rom])
            else:
                commandArray.extend(["--disc", rom])
        
        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":playConfig,
                "XDG_DATA_HOME":playConfig,
                "XDG_CACHE_HOME":batoceraFiles.CACHE,
                "QT_QPA_PLATFORM":"xcb",
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if 'play_widescreen' in config and config['play_widescreen'] == "true":
            return 16/9
        elif 'play_mode' in config and config['play_mode'] == "0":
            return 16/9
        else:
            return 4/3
