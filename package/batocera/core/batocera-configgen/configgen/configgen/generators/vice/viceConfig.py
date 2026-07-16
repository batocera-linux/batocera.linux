from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveRawConfigParser

from ...batoceraPaths import mkdir_if_not_exists

if TYPE_CHECKING:
    from collections.abc import Mapping
    from io import TextIOWrapper
    from pathlib import Path

    from ...Emulator import Emulator
    from ...gun import Guns


_SYSTEM_CORE_MAP: Final = {
    'x64': 'C64',
    'x64dtv': 'C64DTV',
    'xplus4': 'PLUS4',
    'xscpu64': 'SCPU64',
    'xvic': 'VIC20',
    'xpet': 'PET',
}

# Map each core to its emulated video chip(s) as documented in the manual
_CORE_CHIP_MAP: Final = {
    'C64':    ['VICII'],
    'C64DTV': ['VICII'],
    'PLUS4':  ['TED'],
    'SCPU64': ['VICII'],
    'VIC20':  ['VIC'],
    'PET':    ['Crtc'],
    'C128':   ['VICII', 'VDC'],
}

def setViceConfig(vice_config_dir: Path, system: Emulator, metadata: Mapping[str, str], guns: Guns, rom: Path) -> None:

    # Path
    viceController = vice_config_dir / "sdl-joymap.vjm"
    viceConfigRC   = vice_config_dir / "sdl-vicerc"

    mkdir_if_not_exists(viceConfigRC.parent)

    # config file
    viceConfig = CaseSensitiveRawConfigParser(interpolation=None)

    if viceConfigRC.exists():
        viceConfig.read(viceConfigRC)

    systemCore = _SYSTEM_CORE_MAP.get(system.config.core, 'C128')

    if not viceConfig.has_section(systemCore):
        viceConfig.add_section(systemCore)

    viceConfig.set(systemCore, "SaveResourcesOnExit",    "0")
    viceConfig.set(systemCore, "SoundDeviceName",        "alsa")

    # Determine border and aspect values
    if system.config.get_bool('noborder'):
        aspect_mode = "0"
        border_mode = "3"
    else:
        aspect_mode = "2"
        border_mode = "0"

    # Dynamically apply settings to the correct video chip(s)
    chips = _CORE_CHIP_MAP.get(systemCore, ['VICII'])
    for chip in chips:
        # Fullscreen configurations
        viceConfig.set(systemCore, f"{chip}Fullscreen", "1")
        viceConfig.set(systemCore, f"{chip}FullscreenMode", "0")  # 0 = Use desktop resolution

        # Aspect Ratio Mode
        viceConfig.set(systemCore, f"{chip}AspectMode", aspect_mode)

        # Border display mode (Only VIC-II, VIC-I, and TED chips support borders)
        if chip in ['VICII', 'VIC', 'TED']:
            viceConfig.set(systemCore, f"{chip}BorderMode", border_mode)

    if system.config.use_guns and guns:
        if metadata.get("gun_type") == "stack_light_rifle":
            joyport1 = "15"
        else:
            joyport1 = "14"
    else:
        joyport1 = "1"
    viceConfig.set(systemCore, "JoyPort1Device",             joyport1)

    viceConfig.set(systemCore, "JoyDevice1",             "4")
    if systemCore != "VIC20":
        viceConfig.set(systemCore, "JoyDevice2",             "4")
    viceConfig.set(systemCore, "JoyMapFile",  str(viceController))

    # custom : allow the user to configure directly sdl-vicerc via batocera.conf via lines like : vice.section.option=value
    for section_option, user_config_value in system.config.items(starts_with='vice.'):
        custom_section, _, custom_option = section_option.partition(".")
        if not viceConfig.has_section(custom_section):
            viceConfig.add_section(custom_section)
        viceConfig.set(custom_section, custom_option, user_config_value)

    # update the configuration file
    with viceConfigRC.open('w') as configfile:
        viceConfig.write(EqualsSpaceRemover(configfile))

class EqualsSpaceRemover:
    def __init__(self, new_output_file: TextIOWrapper):
        self.output_file = new_output_file

    def write(self, what: str):
        self.output_file.write( what.replace( " = ", "=", 1 ) )
