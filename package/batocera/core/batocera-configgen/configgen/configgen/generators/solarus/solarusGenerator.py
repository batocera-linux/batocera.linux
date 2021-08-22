#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import batoceraFiles
import codecs
import os
import zipfile

class SolarusGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):

        # basis
        commandArray = ["solarus-run", "-fullscreen=yes", "-cursor-visible=no", "-lua-console=no"]

        # hotkey to exit
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                if "hotkey" in pad.inputs and "start" in pad.inputs:
                    commandArray.append("-quit-combo={}+{}".format(pad.inputs["hotkey"].id, pad.inputs["start"].id))
                    commandArray.append("-joypad-num={}".format(pad.index))
            nplayer += 1

        # player pad
        SolarusGenerator.padConfig(system, playersControllers)

        # rom
        commandArray.append(rom)

        return Command.Command(array=commandArray, env={
                'SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS': '0' })

    @staticmethod
    def padConfig(system, playersControllers):
        keymapping = {
            "action": "a",
            "attack": "b",
            "item1":  "y",
            "item2":  "x",
            "pause":  "start",
            "right":  "right",
            "up":     "up",
            "left":   "left",
            "down":   "down"
        }

        reverseAxis = {
            "up": "down",
            "left": "right"
        }

        if system.isOptSet('joystick'):
            if system.config['joystick'] == "joystick1":
                keymapping["up"]    = "joystick1up"
                keymapping["down"]  = "joystick1down"
                keymapping["left"]  = "joystick1left"
                keymapping["right"] = "joystick1right"
            elif system.config['joystick'] == "joystick2":
                keymapping["up"]    = "joystick2up"
                keymapping["down"]  = "joystick2down"
                keymapping["left"]  = "joystick2left"
                keymapping["right"] = "joystick2right"

        configdir = "{}/{}".format(batoceraFiles.CONF, "solarus")
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        configFileName = "{}/{}".format(configdir, "pads.ini")
        f = codecs.open(configFileName, "w", encoding="ascii")

        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                for key in keymapping:
                    if keymapping[key] in pad.inputs:
                        f.write("{}={}\n".format(key, SolarusGenerator.key2val(pad.inputs[keymapping[key]], False)))
                    if key in reverseAxis and pad.inputs[keymapping[key]].type == "axis":
                        f.write("{}={}\n".format(reverseAxis[key], SolarusGenerator.key2val(pad.inputs[keymapping[key]], True)))

            nplayer += 1

    @staticmethod
    def key2val(input, reverse):
        if input.type == "button":
            return "button {}".format(input.id)
        if input.type == "hat":
            if input.value == "1":
                return "hat 0 up"
            if input.value == "2":
                return "hat 0 right"
            if input.value == "4":
                return "hat 0 down"
            if input.value == "8":
                return "hat 0 left"
        if input.type == "axis":
            if (reverse and input.value == "-1") or (not reverse and input.value == "1"):
                return "axis {} +".format(str(input.id))
            else:
                return "axis {} -".format(str(input.id))
        return None
