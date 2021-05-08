#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
import codecs
import logging

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
        "easyrpg_action":   {"key": "button_action"   ,"default" : "a"},
        "easyrpg_cancel":   {"key": "button_cancel"   ,"default" : "b"},
        "easyrpg_shift":    {"key": "button_shift"    ,"default" : "pageup"},
        "easyrpg_n0":       {"key": "button_n0"       ,"default" : None},
        "easyrpg_n1":       {"key": "button_n1"       ,"default" : None},
        "easyrpg_n2":       {"key": "button_n2"       ,"default" : None},
        "easyrpg_n3":       {"key": "button_n3"       ,"default" : None},
        "easyrpg_n4":       {"key": "button_n4"       ,"default" : None},
        "easyrpg_n5":       {"key": "button_n5"       ,"default" : None},
        "easyrpg_n6":       {"key": "button_n6"       ,"default" : None},
        "easyrpg_n7":       {"key": "button_n7"       ,"default" : None},
        "easyrpg_n8":       {"key": "button_n8"       ,"default" : None},
        "easyrpg_n9":       {"key": "button_n9"       ,"default" : None},
        "easyrpg_plus":     {"key": "button_plus"     ,"default" : None},
        "easyrpg_minus":    {"key": "button_minus"    ,"default" : None},
        "easyrpg_multiply": {"key": "button_multiply" ,"default" : None},
        "easyrpg_divide":   {"key": "button_divide"   ,"default" : None},
        "easyrpg_period":   {"key": "button_period"   ,"default" : None}
        }
        # Loop every keys to assign 
        esbuttontable = {} 
        for entry in mappings:
            esbutton = "es"+str(mappings[entry]["key"]) 
            if system.isOptSet(entry):
                entryvalue = system.config[entry]
                esbuttontable[esbutton] = entryvalue
            else:
                entrydefault = mappings[entry]["default"]
                esbuttontable[esbutton] = entrydefault
        # Configuring Pads
        EasyRPGGenerator.padConfig(configdir, playersControllers, esbuttontable)
        # Launching EasyRPG
        return Command.Command(array=commandArray)

    @staticmethod
    def padConfig(configdir, playersControllers, esbuttontable):
        keymapping = {
            "button_up":                 None,
            "button_down":               None,
            "button_left":               None,
            "button_right":              None,
            "button_action":             esbuttontable['esbutton_action'],
            "button_cancel":             esbuttontable['esbutton_cancel'],
            "button_shift":              esbuttontable['esbutton_shift'],
            "button_n0":                 esbuttontable['esbutton_n0'],
            "button_n1":                 esbuttontable['esbutton_n1'],
            "button_n2":                 esbuttontable['esbutton_n2'],
            "button_n3":                 esbuttontable['esbutton_n3'],
            "button_n4":                 esbuttontable['esbutton_n4'],
            "button_n5":                 esbuttontable['esbutton_n5'],
            "button_n6":                 esbuttontable['esbutton_n6'],
            "button_n7":                 esbuttontable['esbutton_n7'],
            "button_n8":                 esbuttontable['esbutton_n8'],
            "button_n9":                 esbuttontable['esbutton_n9'],
            "button_plus":               esbuttontable['esbutton_plus'],
            "button_minus":              esbuttontable['esbutton_minus'],
            "button_multiply":           esbuttontable['esbutton_multiply'],
            "button_divide":             esbuttontable['esbutton_divide'],
            "button_period":             esbuttontable['esbutton_period'],
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
