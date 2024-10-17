from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ..Generator import Generator
from . import fsuaeControllers
from .fsuaePaths import FSUAE_BIOS_DIR, FSUAE_CONFIG_DIR, FSUAE_SAVES

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

class FsuaeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "fsuae",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    # from one file (x1.zip), get the list of all existing files with the same extension + last char (as number) suffix
    # for example, "/path/toto0.zip" becomes ["/path/toto0.zip", "/path/toto1.zip", "/path/toto2.zip"]
    def floppiesFromRom(self, rom: Path):
        floppies: list[Path] = []

        # if the last char is not a digit, only 1 file
        if not rom.stem[-1:].isdigit():
            floppies.append(rom)
            return floppies

        # path without the number
        fileprefix=rom.stem[:-1]

        # special case for 0 while numerotation can start at 1
        zero_file = rom.with_name(f'{fileprefix}0{rom.suffix}')
        if zero_file.is_file():
            floppies.append(zero_file)

        # adding all other files
        n = 1
        while (floppy := rom.with_name(f'{fileprefix}{n}{rom.suffix}')).is_file():
            floppies.append(floppy)
            n += 1

        return floppies

    def filePrefix(self, rom: Path):
        if not rom.stem[-1:].isdigit():
            return rom.stem
        return rom.stem[:-1]

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        fsuaeControllers.generateControllerConfig(system, playersControllers)

        commandArray = ['/usr/bin/fs-uae', "--fullscreen",
                                           "--amiga-model="     + system.config['core'],
                                           f"--base_dir={FSUAE_CONFIG_DIR!s}",
                                           f"--kickstarts_dir={FSUAE_BIOS_DIR!s}",
                                           f"--save_states_dir={FSUAE_SAVES / system.config['core'] / self.filePrefix(rom_path)}",
                                           "--zoom=auto"
                       ]

        device_type = "floppy"
        if system.config['core'] in ["CD32", "CDTV"]:
            device_type = "cdrom"

        # extract zip here
        TEMP_DIR = Path("/tmp/fsuae")
        diskNames: list[str] = []

        # read from zip
        if (rom.lower().endswith("zip")):
            zf = zipfile.ZipFile(rom, 'r')
            for name in zf.namelist():
                d = name.lower()
                if (d.endswith("ipf") or d.endswith("adf") or d.endswith("dms") or d.endswith("adz")):
                    diskNames.append(name)

            eslog.debug("Amount of disks in zip " + str(len(diskNames)))

        # if 2+ files, we have a multidisk ZIP (0=no zip)
        if (len(diskNames) > 1):
            eslog.debug("extracting...")
            shutil.rmtree(TEMP_DIR, ignore_errors=True) # cleanup
            zf.extractall(TEMP_DIR)

            n = 0
            for disk in diskNames:
                commandArray.append(f"--{device_type}_image_{n}={TEMP_DIR / disk}")
                if (n <= 1 and device_type == "floppy") or (n == 0 and device_type == "cdrom"):
                    commandArray.append(f"--{device_type}_drive_{n}={TEMP_DIR / disk}")
                n += 1

        else:
            n = 0
            for img in self.floppiesFromRom(rom_path):
                commandArray.append(f"--{device_type}_image_{n}={img}")
                if (n <= 1 and device_type == "floppy") or (n == 0 and device_type == "cdrom"):
                    commandArray.append(f"--{device_type}_drive_{n}={img}")
                n += 1

        # controllers
        n = 0
        for playercontroller, pad in sorted(playersControllers.items()):
            if n <= 3:
                commandArray.append("--joystick_port_" + str(n) + "=" + pad.real_name + "")
                n += 1

        return Command.Command(array=commandArray)
