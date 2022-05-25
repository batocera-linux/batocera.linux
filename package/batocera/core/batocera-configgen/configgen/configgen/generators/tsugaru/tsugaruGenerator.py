#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
import configparser
import batoceraFiles

class TsugaruGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

	# Start emulator fullscreen
        commandArray = ["/usr/bin/Tsugaru_CUI", "/userdata/bios/fmtowns"]
        commandArray += ["-AUTOSCALE", "-HIGHRES", "-NOWAITBOOT"]
        commandArray += ["-GAMEPORT0", "KEY"]
        commandArray += ["-KEYBOARD", "DIRECT"]
        commandArray += ["-PAUSEKEY", "F10"]

        # CD Speed
        if system.isOptSet('cdrom_speed') and system.config['cdrom_speed'] != 'auto':
            commandArray += ["-CDSPEED", system.config["cdrom_speed"]]

        # CPU Emulation
        if system.isOptSet('386dx') and system.config['386dx'] == '1':
            commandArray += ["-PRETEND386DX"]

        extension = os.path.splitext(rom)[1][1:].lower()
        if extension in ['iso', 'cue', 'bin']:
            # Launch CD-ROM
            commandArray += ["-CD", rom]
        else:
            # Launch floppy
            commandArray += ["-FD0", rom]

        return Command.Command(array=commandArray)
