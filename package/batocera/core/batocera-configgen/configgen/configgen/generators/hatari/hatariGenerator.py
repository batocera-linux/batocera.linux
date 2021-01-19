#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig


class HatariGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
	# Start emulator fullscreen
        commandArray = ["hatari", "--fullscreen"]

	# Machine can be st (default), ste, megaste, tt, falcon
	# st should use TOS 1.00 to TOS 1.04 (tos100 / tos102 / tos104)
	# ste should use TOS 1.06 at least (tos106 / tos162 / tos206)
	# megaste should use TOS 2.XX series (tos206)
	# tt should use tos 3.XX
	# falcon should use tos 4.XX
	commandArray += ["--machine", "st"]
	commandArray += [ "--tos", "/userdata/bios/tos.img"]

	# RAM (ST Ram) options (0 for 512k, 1 for 1MB)
	commandArray += ["--memsize", "0"]

	# Floppy (A) options
	commandArray += ["--disk-a", rom]

	# Floppy (B) options
	commandArray += ["--drive-b", "off"]

        return Command.Command(array=commandArray)
