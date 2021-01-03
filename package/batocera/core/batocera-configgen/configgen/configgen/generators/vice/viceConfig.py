#!/usr/bin/env python

import batoceraFiles
import os
from Emulator import Emulator
import ConfigParser

def setViceConfig(viceConfigFile, system):
    
    # Path
    viceController = viceConfigFile + "/sdl-joymap.vjm"
    viceConfigRC   = viceConfigFile + "/sdl-vicerc"

    if not os.path.exists(os.path.dirname(viceConfigRC)):
            os.makedirs(os.path.dirname(viceConfigRC))

    # config file
    viceConfig = ConfigParser.RawConfigParser()
    viceConfig.optionxform=str
    
    if os.path.exists(viceConfigRC):
        viceConfig.read(viceConfigRC)

    if(system.config['core'] == 'x64'):
        systemCore = "C64"    
    elif(system.config['core'] == 'x64dtv'):
        systemCore = "C64DTV"    
    elif(system.config['core'] == 'xplus4'):
        systemCore = "PLUS4"    
    elif(system.config['core'] == 'xscpu64'):
        systemCore = "SCPU64"    
    elif(system.config['core'] == 'xvic'):
       systemCore = "VIC20"    
    elif(system.config['core'] == 'xpet'):
       systemCore = "PET"    
    else:
        systemCore = "C128"

    if not viceConfig.has_section(systemCore):
        viceConfig.add_section(systemCore)

    viceConfig.set(systemCore, "SaveResourcesOnExit",    "1")
    viceConfig.set(systemCore, "SoundDeviceName",        "alsa")

    viceConfig.set(systemCore, "SDLGLAspectMode",        "0")
    viceConfig.set(systemCore, "VICIIFullscreen",        "1")
    viceConfig.set(systemCore, "VICIISDLFullscreenMode", "0")
    viceConfig.set(systemCore, "VICIIBorderMode",        "3")
    viceConfig.set(systemCore, "WarpMode",               "0")
    
    viceConfig.set(systemCore, "JoyDevice1",             "4")
    viceConfig.set(systemCore, "JoyDevice2",             "4")
    viceConfig.set(systemCore, "JoyMapFile",  viceController)

    # custom : allow the user to configure directly sdl-vicerc via batocera.conf via lines like : vice.section.option=value
    for user_config in system.config:
        if user_config[:5] == "vice.":
            section_option = user_config[5:]
            section_option_splitter = section_option.find(".")
            custom_section = section_option[:section_option_splitter]
            custom_option = section_option[section_option_splitter+1:]
            if not viceConfig.has_section(custom_section):
                viceConfig.add_section(custom_section)
            viceConfig.set(custom_section, custom_option, system.config[user_config])

    # update the configuration file
    with open(viceConfigRC, 'w') as configfile:
        viceConfig.write(EqualsSpaceRemover(configfile))

class EqualsSpaceRemover:
    output_file = None
    def __init__( self, new_output_file ):
        self.output_file = new_output_file

    def write( self, what ):
        self.output_file.write( what.replace( " = ", "=", 1 ) )
