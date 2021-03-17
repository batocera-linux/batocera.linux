#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from utils.logger import eslog
import os
import configparser
import batoceraFiles

class TsugaruGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

	# Start emulator fullscreen
        commandArray = ["/usr/bin/Tsugaru_CUI", "/userdata/bios/fmtowns"]

	# Floppy (A) options
        commandArray += ["-FD0", rom]

        return Command.Command(array=commandArray)
