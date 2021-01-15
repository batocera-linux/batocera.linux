#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os


class SupermodelGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        commandArray = ["supermodel", "-fullscreen"]
        
        # legacy3d
        if system.isOptSet("engine3D")  and system.config["engine3D"] == "legacy3d":
            commandArray.append("-legacy3d")
        else:
            commandArray.append("-new3d")
        
        # fps
        if system.isOptSet("wideScreen") and system.getOptBoolean("wideScreen"):
            commandArray.append("-wide-screen")
            commandArray.append("-wide-bg")

        # quad rendering
        if system.isOptSet("quadRendering") and system.getOptBoolean("quadRendering"):
            commandArray.append("-quad-rendering")

        # resolution
        resx = str(gameResolution["width"])
        resy = str(gameResolution["height"])
        res = "-res={},{}".format(resx, resy)
        commandArray.append(res)

        commandArray.extend(["-log-output=/userdata/system/logs", rom])
        
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
                })
                