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

        # Retrieving ES Values 
        mappings = {
        "easyrpg_action":   {"key": "button_action"   ,"default" : "a"}
        "easyrpg_cancel":   {"key": "button_cancel"   ,"default" : "b"}
        "easyrpg_shift":    {"key": "button_shift"    ,"default" : "pageup"}
        "easyrpg_n0":       {"key": "button_n0"       ,"default" : None}
        "easyrpg_n1":       {"key": "button_n1"       ,"default" : None}
        "easyrpg_n2":       {"key": "button_n2"       ,"default" : None}
        "easyrpg_n3":       {"key": "button_n3"       ,"default" : None}
        "easyrpg_n4":       {"key": "button_n4"       ,"default" : None}
        "easyrpg_n5":       {"key": "button_n5"       ,"default" : None}
        "easyrpg_n6":       {"key": "button_n6"       ,"default" : None}
        "easyrpg_n7":       {"key": "button_n7"       ,"default" : None}
        "easyrpg_n8":       {"key": "button_n8"       ,"default" : None}
        "easyrpg_n9":       {"key": "button_n9"       ,"default" : None}
        "easyrpg_plus":     {"key": "button_plus"     ,"default" : None}
        "easyrpg_minus":    {"key": "button_minus"    ,"default" : None}
        "easyrpg_multiply": {"key": "button_multiply" ,"default" : None}
        "easyrpg_divide":   {"key": "button_divide"   ,"default" : None}
        "easyrpg_period":   {"key": "button_period"   ,"default" : None}
        }
        # Loop every keys to assign 
        
        for mapping in mappings:
        if system.isOptSet(mapping):
           esbt[mappings[mapping]["key"]] = system.config[mapping]
        else:
           esbt[mappings[mapping]["key"]] = mappings[mapping]["default"]

        # Configuring Pads
        EasyRPGGenerator.padConfig(configdir, playersControllers, esbtaction, esbtcancel,esbtshift, esbt0, esbt1, esbt2, esbt3, esbt4, esbt5, esbt6, esbt7, esbt8, esbt9, esbtplus, esbtminus, esbtmulti, esbtdiv, esbtperiod)
           
        
        # Launching EasyRPG
        return Command.Command(array=commandArray)

    @staticmethod
    def padConfig(configdir, playersControllers, esbtaction, esbtcancel, esbtshift, esbt0, esbt1, esbt2, esbt3, esbt4, esbt5, esbt6, esbt7, esbt8, esbt9, esbtplus, esbtminus, esbtmulti, esbtdiv, esbtperiod):
        keymapping = {
            "button_up":                 None,
            "button_down":               None,
            "button_left":               None,
            "button_right":              None,
            "button_action":             esbtaction,
            "button_cancel":             esbtcancel,
            "button_shift":              esbtshift,
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
