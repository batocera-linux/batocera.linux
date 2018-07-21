#!/usr/bin/env python
import Command
import recalboxFiles
import zipfile
import shutil
from generators.Generator import Generator
import fsuaeControllers
from os import path

class FsuaeGenerator(Generator):

    # from one file (x1.zip), get the list of all existing files with the same extension + last char (as number) suffix
    # for example, "/path/toto0.zip" becomes ["/path/toto0.zip", "/path/toto1.zip", "/path/toto2.zip"]
    def floppiesFromRom(self, rom):
        floppies = []

        # split path and extension
        filepath, fileext = path.splitext(rom)

        # if the last char is not a digit, only 1 file
        if not filepath[-1:].isdigit():
            floppies.append(rom)
            return floppies

        # path without the number
        fileprefix=filepath[:-1]

        # special case for 0 while numerotation can start at 1
        n = 0
        if path.isfile(fileprefix + str(n) + fileext):
            floppies.append(fileprefix + str(n) + fileext)

        # adding all other files
        n = 1
        while path.isfile(fileprefix + str(n) + fileext):
            floppies.append(fileprefix + str(n) + fileext)
            n += 1

        return floppies

    def filePrefix(self, rom):
        filename, fileext = path.splitext(path.basename(rom))
        if not filename[-1:].isdigit():
            return filename
        return filename[:-1]

    def generate(self, system, rom, playersControllers, gameResolution):
        fsuaeControllers.generateControllerConfig(system, playersControllers)

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "--fullscreen",
                                                                               "--amiga-model="     + system.config['core'],
                                                                               "--base_dir="        + recalboxFiles.fsuaeConfig,
                                                                               "--kickstarts_dir="  + recalboxFiles.fsuaeBios,
                                                                               "--save_states_dir=" + recalboxFiles.fsuaeSaves + "/" + system.config['core'] + "/" + self.filePrefix(rom),
                                                                               "--zoom=auto"
                       ]

        device_type = "floppy"
        if system.config['core'] in ["CD32", "CDTV"]:
            device_type = "cdrom"

        # extract zip here
        TEMP_DIR="/tmp/fsuae/" # with trailing slash!
        diskNames = []

        # read from zip
        if (rom.lower().endswith("zip")):
            zf = zipfile.ZipFile(rom, 'r')
            for name in zf.namelist():
                d = name.lower()
                if (d.endswith("ipf") or d.endswith("adf") or d.endswith("dms") or d.endswith("adz")):
                    diskNames.append(name)

            print("Amount of disks in zip " + str(len(diskNames)))

        # if 2+ files, we have a multidisk ZIP (0=no zip)
        if (len(diskNames) > 1):
            print("extracting...")
            shutil.rmtree(TEMP_DIR, ignore_errors=True) # cleanup
            zf.extractall(TEMP_DIR)

            n = 0
            for disk in diskNames:
                commandArray.append("--" + device_type + "_image_" + str(n) + "=" + TEMP_DIR + disk + "")
                if (n <= 1 and device_type == "floppy") or (n == 0 and device_type == "cdrom"):
                    commandArray.append("--" + device_type + "_drive_" + str(n) + "=" + TEMP_DIR + disk + "")
                n += 1

        else:
            n = 0
            for img in self.floppiesFromRom(rom):
                commandArray.append("--" + device_type + "_image_" + str(n) + "=" + img + "")
                if (n <= 1 and device_type == "floppy") or (n == 0 and device_type == "cdrom"):
                    commandArray.append("--" + device_type + "_drive_" + str(n) + "=" + img + "")
                n += 1

        # controllers
        n = 0
        for pad in playersControllers:
            if n <= 3:
                commandArray.append("--joystick_port_" + str(n) + "=" + playersControllers[pad].realName + "")
                n += 1

        if 'args' in system.config and system.config['args'] is not None:
             commandArray.extend(system.config['args'])
        return Command.Command(array=commandArray)
