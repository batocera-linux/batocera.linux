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
playConfigDir = os.path.dirname(playConfigFile)
playInputFile = playConfig + '/Play Data Files/inputprofiles/default.xml'

class PlayGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        # Create config folder
        if not path.isdir(playConfig):
            os.makedirs(playConfig)
        # Create save folder
        if not path.isdir(playSaves):
            os.makedirs(playSaves)
        # Create save folder
        if not path.isdir(playConfigDir):
            os.makedirs(playConfigDir)
        
        ## Work with the config.xml file
        # Check if the file exists
        if not os.path.exists(playConfigFile):
            root = ET.Element('Config')
            # Create the Preference element & set the arcade directory
            arcade_element = ET.SubElement(root, 'Preference')
            arcade_element.attrib['Name'] = 'ps2.arcaderoms.directory'
            arcade_element.attrib['Type'] = 'path'
            arcade_element.attrib['Value'] = '/userdata/roms/namco2x6'
            # set the confirmation exit to false
            exit_element = ET.SubElement(root, 'Preference')
            exit_element.attrib['Name'] = 'ui.showexitconfirmation'
            exit_element.attrib['Type'] = 'boolean'
            exit_element.attrib['Value'] = 'false'
            # dont pause
            pause_element = ET.SubElement(root, 'Preference')
            pause_element.attrib['Name'] = 'ui.pausewhenfocuslost'
            pause_element.attrib['Type'] = 'boolean'
            pause_element.attrib['Value'] = 'false'
            # no cpu usage
            cpu_element = ET.SubElement(root, 'Preference')
            cpu_element.attrib['Name'] = 'ui.showeecpuusage'
            cpu_element.attrib['Type'] = 'boolean'
            cpu_element.attrib['Value'] = 'false'
            # Create the tree
            tree = ET.ElementTree(root)
            # write the xml
            tree.write(playConfigFile)
        else:
            tree = ET.parse(playConfigFile)
            root = tree.getroot()
            # set the arcaderoms directory
            arcade_element = root.find(".//Preference[@Name='ps2.arcaderoms.directory']")
            arcade_element.attrib['Value'] = '/userdata/roms/namco2x6'
            # set the confirmation exit to false
            exit_element = root.find(".//Preference[@Name='ui.showexitconfirmation']")
            exit_element.attrib['Value'] = 'false'
            # don't pause
            pause_element = root.find(".//Preference[@Name='ui.pausewhenfocuslost']")
            pause_element.attrib['Value'] = 'false'
            # cpu
            cpu_element = root.find(".//Preference[@Name='ui.showeecpuusage']")
            cpu_element.attrib['Value'] = 'false'
            # write the xml
            tree.write(playConfigFile)
        
        ## Controller config
        if not os.path.exists(playInputFile):
            os.makedirs(os.path.dirname(playInputFile))
        # Create xml each launch
        

        commandArray = ["/usr/bin/Play"]
        
        if rom != "config":
            # if zip, it's usually an arcade game
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
