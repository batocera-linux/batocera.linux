#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import os
from xml.dom import minidom
import codecs
import Command
from . import cannonballControllers

class CannonballGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        configFile = batoceraFiles.CONF + '/cannonball/config.xml'
        
        if not os.path.exists(os.path.dirname(configFile)):
            os.makedirs(os.path.dirname(configFile))

        # config file
        config = minidom.Document()
        if os.path.exists(configFile):
            try:
                config = minidom.parse(configFile)
            except:
                pass # reinit the file

        # root
        xml_root = CannonballGenerator.getRoot(config, "config")

        # video
        xml_video = CannonballGenerator.getSection(config, xml_root, "video")

        # fps
        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
            CannonballGenerator.setSectionConfig(config, xml_video, "fps_counter", "1")
        else:
            CannonballGenerator.setSectionConfig(config, xml_video, "fps_counter", "0")

        # ratio
        if system.isOptSet('ratio') and system.config["ratio"] == "16/9":
            CannonballGenerator.setSectionConfig(config, xml_video, "widescreen", "1")
        else:
            CannonballGenerator.setSectionConfig(config, xml_video, "widescreen", "0")

        # high resolution
        if system.isOptSet('highResolution') and system.config["highResolution"] == "1":
            CannonballGenerator.setSectionConfig(config, xml_video, "hires", "1")
        else:
            CannonballGenerator.setSectionConfig(config, xml_video, "hires", "0")

        # controllers
        cannonballControllers.generateControllerConfig(config, xml_root, playersControllers)

        # save the config file
        #cannonballXml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        cannonballXml = codecs.open(configFile, "w", "utf-8")
        dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        cannonballXml.write(dom_string)
        
        return Command.Command(array=["cannonball"])

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
    def setSectionConfig(config, xml_section, name, value):
        xml_elt = xml_section.getElementsByTagName(name)
        if len(xml_elt) == 0:
            xml_elt = config.createElement(name)
            xml_section.appendChild(xml_elt)
        else:
            xml_elt = xml_elt[0]

        if xml_elt.hasChildNodes():
            xml_elt.firstChild.data = value
        else:
            xml_elt.appendChild(config.createTextNode(value))
