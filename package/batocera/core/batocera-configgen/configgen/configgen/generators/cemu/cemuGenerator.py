#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
from os import path
from os import environ
import batoceraFiles
from xml.dom import minidom
import codecs
import controllersConfig
import shutil
import filecmp
from . import cemuControllers

cemuConfig  = batoceraFiles.CONF + '/cemu'
cemuHomedir = 'Z:\\userdata\\roms\\wiiu'
cemuMLC = 'C:\\cemu'
cemuDatadir = '/usr/cemu'
cemuSaves   = batoceraFiles.SAVES + '/cemu'

class CemuGenerator(Generator):

    def hasInternalMangoHUDCall(self):
        return True

    def generate(self, system, rom, playersControllers, gameResolution):

        # in case of squashfs, the root directory is passed
        rpxrom = rom
        if os.path.isdir(rom + "/code"):
            rpxInDir = os.listdir(rom + "/code")
            for file in rpxInDir:
                basename, extension = os.path.splitext(file)
                if extension == ".rpx":
                    rpxrom = rom + "/code/" + basename + extension

        game_dir = cemuConfig + "/gameProfiles"
        resources_dir = cemuConfig + "/resources"
        cemu_exe = cemuConfig + "/Cemu.exe"
        cemu_hook = cemuConfig + "/cemuhook.ini"
        keystone_dll = cemuConfig + "/keystone.dll"
        cemuhook_dll = cemuConfig + "/cemuhook.dll"
        if not path.isdir(batoceraFiles.BIOS + "/cemu"):
            os.mkdir(batoceraFiles.BIOS + "/cemu")
        if not path.isdir(cemuConfig):
            os.mkdir(cemuConfig)
        if not os.path.exists(game_dir):
            shutil.copytree(cemuDatadir + "/gameProfiles", game_dir)
        if not os.path.exists(resources_dir):
            shutil.copytree(cemuDatadir + "/resources", resources_dir)

        for folder in ["controllerProfiles", "graphicPacks"]:
            if not path.isdir(cemuConfig + "/" + folder):
                os.mkdir(cemuConfig + "/" + folder)

        # Create save folder
        if not path.isdir(batoceraFiles.SAVES + "/cemu"):
            os.mkdir(batoceraFiles.SAVES + "/cemu")

        # Check & Create mlc folders
        if not path.isdir(batoceraFiles.SAVES + "/cemu/drive_c/cemu"):
            os.makedirs(batoceraFiles.SAVES + "/cemu/drive_c/cemu/sys")
            os.makedirs(batoceraFiles.SAVES + "/cemu/drive_c/cemu/usr")

        CemuGenerator.CemuConfig(cemuConfig + "/settings.xml", system)
        # Copy the file from where cemu reads it
        shutil.copyfile(batoceraFiles.BIOS + "/cemu/keys.txt", cemuConfig + "/keys.txt")
        if not os.path.exists(cemu_exe) or not filecmp.cmp(cemuDatadir + "/Cemu.exe", cemu_exe):
            shutil.copyfile(cemuDatadir + "/Cemu.exe", cemu_exe)
        # Copy cemuhook for secure upgrade
        if not os.path.exists(cemu_hook) or not filecmp.cmp(cemuDatadir + "/cemuhook.ini", cemu_hook):
            shutil.copyfile(cemuDatadir + "/cemuhook.ini", cemu_hook)
        if not os.path.exists(keystone_dll) or not filecmp.cmp(cemuDatadir + "/keystone.dll", keystone_dll):
            shutil.copyfile(cemuDatadir + "/keystone.dll", keystone_dll)
        if not os.path.exists(cemuhook_dll) or not filecmp.cmp(cemuDatadir + "/cemuhook.dll", cemuhook_dll):
            shutil.copyfile(cemuDatadir + "/cemuhook.dll", cemuhook_dll)

        cemuControllers.generateControllerConfig(system, playersControllers)

        if rom == "config":
            commandArray = ["/usr/wine/lutris/bin/wine64", "/userdata/system/configs/cemu/Cemu.exe"]
        else:
            commandArray = ["/usr/wine/lutris/bin/wine64", "/userdata/system/configs/cemu/Cemu.exe", "-g", "z:" + rpxrom, "-f"]
            if system.isOptSet('hud') and system.config["hud"] != "":
               commandArray.insert(0, "mangohud")

        return Command.Command(
            array=commandArray,
            env={
                "WINEPREFIX": batoceraFiles.SAVES + "/cemu",
                "vblank_mode": "0",
                "mesa_glthread": "true",
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "WINEDLLOVERRIDES": "mscoree=;mshtml=;cemuhook.dll=n,b",
                "__GL_THREADED_OPTIMIZATIONS": "1"
            })

    @staticmethod
    def CemuConfig(configFile, system):
        # Config file
        config = minidom.Document()
        if os.path.exists(configFile):
            try:
                config = minidom.parse(configFile)
            except:
                pass # reinit the file

        ## [ROOT]
        xml_root = CemuGenerator.getRoot(config, "content")

        # Default mlc path
        CemuGenerator.setSectionConfig(config, xml_root, "mlc_path", cemuMLC)

        # Remove auto updates
        CemuGenerator.setSectionConfig(config, xml_root, "check_update", "false")
        # Avoid the welcome window
        CemuGenerator.setSectionConfig(config, xml_root, "gp_download", "true")
        # Other options
        CemuGenerator.setSectionConfig(config, xml_root, "logflag", "0")
        CemuGenerator.setSectionConfig(config, xml_root, "advanced_ppc_logging", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "use_discord_presence", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "fullscreen_menubar", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "cpu_mode", "1")
        CemuGenerator.setSectionConfig(config, xml_root, "vk_warning", "false")
        CemuGenerator.setSectionConfig(config, xml_root, "fullscreen", "true")

        # Language
        CemuGenerator.setSectionConfig(config, xml_root, "console_language", str(getCemuLangFromEnvironment()))

        ## [WINDOW POSITION]
        CemuGenerator.setSectionConfig(config, xml_root, "window_position", "")
        window_position = CemuGenerator.getRoot(config, "window_position")

        # Default window position
        CemuGenerator.setSectionConfig(config, window_position, "x", "-4")
        # Default games path
        CemuGenerator.setSectionConfig(config, window_position, "y", "-23")

        ## [WINDOW POSITION]
        CemuGenerator.setSectionConfig(config, xml_root, "window_size", "")
        window_size = CemuGenerator.getRoot(config, "window_size")

        # Default window size
        CemuGenerator.setSectionConfig(config, window_size, "x", "1")
        # Default games path
        CemuGenerator.setSectionConfig(config, window_size, "y", "1")

        ## [GAME PATH]
        CemuGenerator.setSectionConfig(config, xml_root, "GamePaths", "")
        game_root = CemuGenerator.getRoot(config, "GamePaths")

        # Default games path
        CemuGenerator.setSectionConfig(config, game_root, "Entry", cemuHomedir)

        ## [AUDIO]
        CemuGenerator.setSectionConfig(config, xml_root, "Audio", "")
        audio_root = CemuGenerator.getRoot(config, "Audio")

        # Turn audio ONLY on TV
        CemuGenerator.setSectionConfig(config, audio_root, "TVDevice", "default")
        CemuGenerator.setSectionConfig(config, audio_root, "TVVolume", "90")


        ## [GRAPHIC]
        CemuGenerator.setSectionConfig(config, xml_root, "Graphic", "")
        graphic_root = CemuGenerator.getRoot(config, "Graphic")

        # Graphical backend
        if system.isOptSet("gfxbackend"):
            if system.config["gfxbackend"] == "Vulkan":
                CemuGenerator.setSectionConfig(config, graphic_root, "api", "1") # Vulkan
            else:
                CemuGenerator.setSectionConfig(config, graphic_root, "api", "0") # OpenGL
        else:
            CemuGenerator.setSectionConfig(config, graphic_root, "api", "1")     # Vulkan

        # Async VULKAN Shader compilation
        if system.isOptSet("async") and system.config["async"] == "0":
            CemuGenerator.setSectionConfig(config, graphic_root, "AsyncCompile", "false") 
        else:
            CemuGenerator.setSectionConfig(config, graphic_root, "AsyncCompile", "true")

        ## [GRAPHIC]
        CemuGenerator.setSectionConfig(config, graphic_root, "Overlay", "")
        overlay_root = CemuGenerator.getRoot(config, "Overlay")

        # Display FPS / CPU / GPU / RAM
        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
            CemuGenerator.setSectionConfig(config, overlay_root, "Position", "1")
            CemuGenerator.setSectionConfig(config, overlay_root, "FPS",       "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "CPUUsage",  "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "RAMUsage",  "true")
            CemuGenerator.setSectionConfig(config, overlay_root, "VRAMUsage", "true")
        else:
            CemuGenerator.setSectionConfig(config, overlay_root, "Position", "0")
            CemuGenerator.setSectionConfig(config, overlay_root, "FPS",       "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "CPUUsage",  "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "RAMUsage",  "false")
            CemuGenerator.setSectionConfig(config, overlay_root, "VRAMUsage", "false")

        # Save the config file
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


# Lauguage auto setting
def getCemuLangFromEnvironment():
    if 'LANG' in environ:
        lang = environ['LANG'][:5]
    else:
        lang = "en_US"

    availableLanguages = { "ja_JP": 0, "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "zh_CN": 6, "ko_KR": 7, "hu_HU": 8, "pt_PT": 9, "ru_RU": 10, "zh_TW": 11 }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
