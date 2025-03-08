from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ...batoceraPaths import mkdir_if_not_exists
from ...utils.configparser import CaseSensitiveRawConfigParser

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

    if system.config.get_bool('noborder'):
        aspect_mode = "0"
        border_mode = "3"
    else:
        aspect_mode = "2"
        border_mode = "0"
    viceConfig.set(systemCore, "SDLGLAspectMode",        aspect_mode)
    viceConfig.set(systemCore, "VICBorderMode",        border_mode)

    viceConfig.set(systemCore, "VICFullscreen",        "1")

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
