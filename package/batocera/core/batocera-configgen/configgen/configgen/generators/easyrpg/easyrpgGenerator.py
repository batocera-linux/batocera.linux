#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
import codecs

class EasyRPGGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        commandArray = ["easyrpg-player"]

        # FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            commandArray.append("--show-fps")

        # Test Play (Debug Mode)
        if system.isOptSet('testplay') and system.getOptBoolean("testplay"):
            commandArray.append("--test-play")

        # Game Region (Encoding)
        if system.isOptSet('encoding') and system.config["encoding"] != 'autodetect':
            commandArray.extend(["--encoding", system.config["encoding"]])
        else:
            commandArray.extend(["--encoding", "auto"])

        # Save directory
        savePath = f"/userdata/saves/easyrpg/{os.path.basename(rom)}"
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        commandArray.extend(["--save-path", savePath])

        # Dir for logs and conf
        configdir = "/userdata/system/configs/easyrpg"
        if not os.path.exists(configdir):
            os.makedirs(configdir)

        commandArray.extend(["--project-path", rom])

        EasyRPGGenerator.padConfig(configdir, playersControllers)

        return Command.Command(array=commandArray)

    @staticmethod
    def padConfig(configdir, playersControllers):
        keymapping = {
            "button_up": None,
            "button_down": None,
            "button_left": None,
            "button_right": None,
            "button_action": "a",
            "button_cancel": "b",
            "button_shift": "pageup",
            "button_n0": None,
            "button_n1": None,
            "button_n2": None,
            "button_n3": None,
            "button_n4": None,
            "button_n5": None,
            "button_n6": None,
            "button_n7": None,
            "button_n8": None,
            "button_n9": None,
            "button_plus": None,
            "button_minus": None,
            "button_multiply": None,
            "button_divide": None,
            "button_period": None,
            "button_debug_menu": None,
            "button_debug_through": None
        }

        configFileName = "{}/{}".format(configdir, "config.ini")
        f = codecs.open(configFileName, "w", encoding="ascii")
        f.write("[Joypad]\n");
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                f.write("number={}\n" .format(pad.index))
                for key in keymapping:
                    button = -1
                    if keymapping[key] is not None:
                        if pad.inputs[keymapping[key]].type == "button":
                            button = pad.inputs[keymapping[key]].id
                    f.write(f"{key}={button}\n")
            nplayer += 1
