#!/usr/bin/env python

import batoceraFiles
import os
from Emulator import Emulator
import ConfigParser

def setViceConfig(viceConfigFile, system):
    # config file
    viceConfig = ConfigParser.RawConfigParser()
    viceConfig.optionxform=str
    if os.path.exists(viceConfigFile):
        viceConfig.read(viceConfigFile)

    # Commodore 64
    if not viceConfig.has_section("C64"):
        viceConfig.add_section("C64")

    viceConfig.set("C64", "SaveResourcesOnExit",    "1")
    viceConfig.set("C64", "SDLGLAspectMode",        "0")
    viceConfig.set("C64", "VICIIFullscreen",        "1")
    viceConfig.set("C64", "VICIISDLFullscreenMode", "1")
    viceConfig.set("C64", "VICIIBorderMode",        "3")
    viceConfig.set("C64", "JoyDevice1",             "4")
    viceConfig.set("C64", "JoyDevice2",             "4")

    if not viceConfig.has_section("C64DTV"):
        viceConfig.add_section("C64DTV")

    viceConfig.set("C64DTV", "SaveResourcesOnExit",    "1")
    viceConfig.set("C64DTV", "SDLGLAspectMode",        "0")
    viceConfig.set("C64DTV", "VICIIFullscreen",        "1")
    viceConfig.set("C64DTV", "VICIISDLFullscreenMode", "1")
    viceConfig.set("C64DTV", "VICIIBorderMode",        "3")
    viceConfig.set("C64DTV", "JoyDevice1",             "4")
    viceConfig.set("C64DTV", "JoyDevice2",             "4")

    if not viceConfig.has_section("PLUS4"):
        viceConfig.add_section("PLUS4")

    viceConfig.set("PLUS4", "SaveResourcesOnExit",    "1")
    viceConfig.set("PLUS4", "SDLGLAspectMode",        "0")
    viceConfig.set("PLUS4", "VICIIFullscreen",        "1")
    viceConfig.set("PLUS4", "VICIISDLFullscreenMode", "1")
    viceConfig.set("PLUS4", "VICIIBorderMode",        "3")
    viceConfig.set("PLUS4", "JoyDevice1",             "4")
    viceConfig.set("PLUS4", "JoyDevice2",             "4")

    if not viceConfig.has_section("SCPU64"):
        viceConfig.add_section("SCPU64")

    viceConfig.set("SCPU64", "SaveResourcesOnExit",    "1")
    viceConfig.set("SCPU64", "SDLGLAspectMode",        "0")
    viceConfig.set("SCPU64", "VICIIFullscreen",        "1")
    viceConfig.set("SCPU64", "VICIISDLFullscreenMode", "1")
    viceConfig.set("SCPU64", "VICIIBorderMode",        "3")
    viceConfig.set("SCPU64", "JoyDevice1",             "4")
    viceConfig.set("SCPU64", "JoyDevice2",             "4")

    # Commodore 128
    if not viceConfig.has_section("C128"):
        viceConfig.add_section("C128")

    viceConfig.set("C128", "SaveResourcesOnExit",    "1")
    viceConfig.set("C128", "SDLGLAspectMode",        "0")
    viceConfig.set("C128", "VICIIFullscreen",        "1")
    viceConfig.set("C128", "VICIISDLFullscreenMode", "1")
    viceConfig.set("C128", "VICIIBorderMode",        "3")
    viceConfig.set("C128", "JoyDevice1",             "4")
    viceConfig.set("C128", "JoyDevice2",             "4")

    # Commodore VIC-20
    if not viceConfig.has_section("VIC20"):
        viceConfig.add_section("VIC20")

    viceConfig.set("VIC20", "SaveResourcesOnExit",    "1")
    viceConfig.set("VIC20", "SDLGLAspectMode",        "0")
    viceConfig.set("VIC20", "VICIIFullscreen",        "1")
    viceConfig.set("VIC20", "VICIISDLFullscreenMode", "1")
    viceConfig.set("VIC20", "VICIIBorderMode",        "3")
    viceConfig.set("VIC20", "JoyDevice1",             "4")
    viceConfig.set("VIC20", "JoyDevice2",             "4")

    # update the configuration file
    with open(viceConfigFile, 'w') as configfile:
        viceConfig.write(EqualsSpaceRemover(configfile))

class EqualsSpaceRemover:
    output_file = None
    def __init__( self, new_output_file ):
        self.output_file = new_output_file

    def write( self, what ):
        self.output_file.write( what.replace( " = ", "=", 1 ) )