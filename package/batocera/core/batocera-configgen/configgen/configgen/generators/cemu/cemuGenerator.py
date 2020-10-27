#!/usr/bin/env python

from generators.Generator import Generator
import cemuControllers
import Command
import os
from os import path
import batoceraFiles
from xml.dom import minidom
import codecs

class CemuGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        if not path.isdir(batoceraFiles.BIOS + "/cemu"):
            os.mkdir(batoceraFiles.BIOS + "/cemu")
        if not path.isdir(batoceraFiles.CONF + "/cemu"):
            os.mkdir(batoceraFiles.CONF + "/cemu")

        for folder in ["shaderCache", "controllerProfiles", "gameProfiles", "graphicPacks"]:
            if not path.isdir(batoceraFiles.CONF + "/cemu/" + folder):
                os.mkdir(batoceraFiles.CONF + "/cemu/" + folder)

        if not path.isdir(batoceraFiles.SAVES + "/cemu"):
            os.mkdir(batoceraFiles.SAVES + "/cemu")

        CemuGenerator.CemuConfig(batoceraFiles.CONF + "/cemu/settings.xml")
        # TODO
        CemuGenerator.CemuConfig("/usr/cemu/settings.xml")
        
        
        
        sdlstring = cemuControllers.generateControllerConfig(system, playersControllers, rom)

        commandArray = ["wine64", "/usr/cemu/Cemu.exe", "-g", "z:" + rom, "-m", "z:" + batoceraFiles.SAVES + "/cemu", "-f"]
        return Command.Command(array=commandArray, env={"WINEPREFIX":batoceraFiles.SAVES + "/cemu", "vblank_mode":"0", "mesa_glthread":"true", "SDL_GAMECONTROLLERCONFIG":sdlstring})

    @staticmethod
    def CemuConfig(configFile):
        # config file
        config = minidom.Document()
        if os.path.exists(configFile):
            try:
                config = minidom.parse(configFile)
            except:
                pass # reinit the file

        # root
        xml_root = CemuGenerator.getRoot(config, "content")

        ###
        CemuGenerator.setSectionConfig(config, xml_root, "check_update", "false")
        # avoid the welcome window
        CemuGenerator.setSectionConfig(config, xml_root, "gp_download", "true")
        ###

        # save the config file
        xml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        xml = codecs.open(configFile, "w", "utf-8")
        dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        xml.write(dom_string)

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
