from __future__ import annotations

from typing import TYPE_CHECKING

from ...batoceraPaths import mkdir_if_not_exists
from ...utils.configparser import CaseSensitiveRawConfigParser

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from ...Emulator import Emulator
    from ...types import GunMapping


def setViceConfig(vice_config_dir: Path, system: Emulator, metadata: Mapping[str, str], guns: GunMapping, rom: str) -> None:

    # Path
    viceController = vice_config_dir / "sdl-joymap.vjm"
    viceConfigRC   = vice_config_dir / "sdl-vicerc"

    mkdir_if_not_exists(viceConfigRC.parent)

    # config file
    viceConfig = CaseSensitiveRawConfigParser(interpolation=None)

    if viceConfigRC.exists():
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

    viceConfig.set(systemCore, "SaveResourcesOnExit",    "0")
    viceConfig.set(systemCore, "SoundDeviceName",        "alsa")

    if system.isOptSet('noborder') and system.getOptBoolean('noborder') == True:
        viceConfig.set(systemCore, "SDLGLAspectMode",        "0")
        viceConfig.set(systemCore, "VICBorderMode",        "3")
    else:
        viceConfig.set(systemCore, "SDLGLAspectMode",        "2")
        viceConfig.set(systemCore, "VICBorderMode",        "0")
    viceConfig.set(systemCore, "VICFullscreen",        "1")
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
        if "gun_type" in metadata and metadata["gun_type"] == "stack_light_rifle":
            viceConfig.set(systemCore, "JoyPort1Device",             "15")
        else:
            viceConfig.set(systemCore, "JoyPort1Device",             "14")
    else:
        viceConfig.set(systemCore, "JoyPort1Device",             "1")
    viceConfig.set(systemCore, "JoyDevice1",             "4")
    if not systemCore == "VIC20":
        viceConfig.set(systemCore, "JoyDevice2",             "4")
    viceConfig.set(systemCore, "JoyMapFile",  str(viceController))

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
    with viceConfigRC.open('w') as configfile:
        viceConfig.write(EqualsSpaceRemover(configfile))

class EqualsSpaceRemover:
    output_file = None
    def __init__( self, new_output_file ):
        self.output_file = new_output_file

    def write( self, what ):
        self.output_file.write( what.replace( " = ", "=", 1 ) )
