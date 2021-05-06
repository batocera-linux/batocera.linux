#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
import codecs

class EasyRPGGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
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
        savePath = "/userdata/saves/easyrpg/{}".format(os.path.basename(rom))
        if not os.path.exists(savePath):
            os.makedirs(savePath)
        commandArray.extend(["--save-path", savePath])

        # Dir for logs and conf
        configdir = "/userdata/system/configs/easyrpg"
        if not os.path.exists(configdir):
            os.makedirs(configdir)

        commandArray.extend(["--project-path", rom])

        # GETTING ES Forced Pad 
        esbtshift = system.config["easyrpg_shift"] if system.isOptSet('easyrpg_shift') and system.config["easyrpg_shift"] != 'pageup' else 'pageup' #By default it's PageUp
        
        esbt0 = system.config["easyrpg_n0"] if system.isOptSet('easyrpg_n0') and system.config["easyrpg_n0"] != None else None
        esbt1 = system.config["easyrpg_n1"] if system.isOptSet('easyrpg_n1') and system.config["easyrpg_n1"] != None else None
        esbt2 = system.config["easyrpg_n2"] if system.isOptSet('easyrpg_n2') and system.config["easyrpg_n2"] != None else None
        esbt3 = system.config["easyrpg_n3"] if system.isOptSet('easyrpg_n3') and system.config["easyrpg_n3"] != None else None
        esbt4 = system.config["easyrpg_n4"] if system.isOptSet('easyrpg_n4') and system.config["easyrpg_n4"] != None else None
        esbt5 = system.config["easyrpg_n5"] if system.isOptSet('easyrpg_n5') and system.config["easyrpg_n5"] != None else None
        esbt6 = system.config["easyrpg_n6"] if system.isOptSet('easyrpg_n6') and system.config["easyrpg_n6"] != None else None
        esbt7 = system.config["easyrpg_n7"] if system.isOptSet('easyrpg_n7') and system.config["easyrpg_n7"] != None else None
        esbt8 = system.config["easyrpg_n8"] if system.isOptSet('easyrpg_n8') and system.config["easyrpg_n8"] != None else None
        esbt9 = system.config["easyrpg_n9"] if system.isOptSet('easyrpg_n9') and system.config["easyrpg_n9"] != None else None
        
        esbtplus = system.config["easyrpg_plus"] if system.isOptSet('easyrpg_plus') and system.config["easyrpg_plus"] != None else None
        esbtminus = system.config["easyrpg_minus"] if system.isOptSet('easyrpg_minus') and system.config["easyrpg_minus"] != None else None
        esbtmulti = system.config["easyrpg_multiply"] if system.isOptSet('easyrpg_multiply') and system.config["easyrpg_multiply"] != None else None
        esbtdiv = system.config["easyrpg_divide"] if system.isOptSet('easyrpg_divide') and system.config["easyrpg_divide"] != None else None
        esbtperiod = system.config["easyrpg_period"] if system.isOptSet('easyrpg_period') and system.config["easyrpg_period"] != None else None
        
        EasyRPGGenerator.padConfig(configdir, playersControllers, esbtshift, esbt0, esbt1, esbt2, esbt3, esbt4, esbt5, esbt6, esbt7, esbt8, esbt9, esbtplus, esbtminus, esbtmulti, esbtdiv, esbtperiod)
        
        return Command.Command(array=commandArray)

    @staticmethod
    def padConfig(configdir, playersControllers, esbtshift, esbt0, esbt1, esbt2, esbt3, esbt4, esbt5, esbt6, esbt7, esbt8, esbt9, esbtplus, esbtminus, esbtmulti, esbtdiv, esbtperiod):
        keymapping = {
            "button_up":                 None,
            "button_down":               None,
            "button_left":               None,
            "button_right":              None,
            "button_action":             "a",
            "button_cancel":             "b",
            "button_shift":              esbtshift, #default at pageup
            "button_n0":                 esbt0,
            "button_n1":                 esbt1,
            "button_n2":                 esbt2,
            "button_n3":                 esbt3,
            "button_n4":                 esbt4,
            "button_n5":                 esbt5,
            "button_n6":                 esbt6,
            "button_n7":                 esbt7,
            "button_n8":                 esbt8,
            "button_n9":                 esbt9,
            "button_plus":               esbtplus,
            "button_minus":              esbtminus,
            "button_multiply":           esbtmulti,
            "button_divide":             esbtdiv,
            "button_period":             esbtperiod,
            "button_debug_menu":         None,
            "button_debug_through":      None
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
                    f.write("{}={}\n".format(key, button))
            nplayer += 1
