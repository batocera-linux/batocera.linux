#!/usr/bin/env python

from generators.Generator import Generator
import Command
import controllersConfig

class OdcommanderGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["od-commander"]

        # pad number
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.append("joynum={}".format(pad.index))
            nplayer += 1

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })
