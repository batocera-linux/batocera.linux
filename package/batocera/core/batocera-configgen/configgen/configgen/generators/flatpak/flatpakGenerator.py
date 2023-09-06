#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os

class FlatpakGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        romId = None
        with open(rom) as f:
            romId = str.strip(f.read())

        # bad hack in a first time to get audio for user batocera
        os.system('chown -R root:audio /var/run/pulse')
        os.system('chmod -R g+rwX /var/run/pulse')

        # the directory monitor must exist and all the dirs must be owned by batocera
        commandArray = ["su", "-", "batocera", "-c",  "DISPLAY=:0.0 flatpak run -v " + romId]
        return Command.Command(array=commandArray)

    def getMouseMode(self, config):
        return True
