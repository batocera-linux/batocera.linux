#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
import batoceraFiles
from xml.dom import minidom
import codecs
import cemuControllers
from shutil import copyfile

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
        # copy the file from where cemu reads it
        copyfile(batoceraFiles.CONF + "/cemu/settings.xml", "/usr/cemu/settings.xml")
        
        sdlstring = cemuControllers.generateControllerConfig(system, playersControllers, rom)
        
        commandArray = ["wine64", "/usr/cemu/Cemu.exe", "-g", "z:" + rom, "-m", "z:" + batoceraFiles.SAVES + "/cemu", "-f"]
        return Command.Command(array=commandArray, env={"WINEPREFIX":batoceraFiles.SAVES + "/cemu", "vblank_mode":"0", "mesa_glthread":"true", "SDL_GAMECONTROLLERCONFIG":sdlstring, "WINEDLLOVERRIDES":"mscoree=;mshtml=;dbghelp.dll=n,b", "__GL_THREADED_OPTIMIZATIONS":"1" })

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
        CemuGenerator.setSectionConfig(config, xml_root, "logflag", "0")
        CemuGenerator.setSectionConfig(config, xml_root, "advanced_ppc_logging", "false")
        
        CemuGenerator.setSectionConfig(config, xml_root, "use_discord_presence", "0")
        CemuGenerator.setSectionConfig(config, xml_root, "fullscreen_menubar", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "true", "true")
        CemuGenerator.setSectionConfig(config, xml_root, "fullscreen_menubar", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "cpu_mode", "1")
        
        ## Audio Settings - Turn audio on for TV
        CemuGenerator.setSectionConfig(config, xml_root, "Audio", "")
        audio_root = CemuGenerator.getRoot(config, "Audio")
        CemuGenerator.setSectionConfig(config, audio_root, "TVDevice", "default")
        CemuGenerator.setSectionConfig(config, audio_root, "TVVolume", "50")
        ##TVVolume
        #Graphic Settings
        
        CemuGenerator.setSectionConfig(config, xml_root, "Graphic", "")
        graphic_root = CemuGenerator.getRoot(config, "Graphic")
        
        graphic_root = CemuGenerator.getRoot(config, "Graphic")
        
        

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
