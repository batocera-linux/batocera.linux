#!/usr/bin/env python

import Command
import recalboxFiles
from generators.Generator import Generator
import shutil
import os
from settings.unixSettings import UnixSettings
import ConfigParser

class CitraGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        CitraGenerator.writeCITRAConfig(recalboxFiles.citraConfig, system, playersControllers)

        commandArray = [recalboxFiles.recalboxBins[system.config['emulator']], "-f", rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":recalboxFiles.CONF, "XDG_DATA_HOME":recalboxFiles.SAVES, "XDG_CACHE_HOME":recalboxFiles.CACHE})

    @staticmethod
    def writeCITRAConfig(citraConfigFile, system, playersControllers):
        # pads
        citraButtons = {
            "button_a":      "a",
            "button_b":      "b",
            "button_x":      "x",
            "button_y":      "y",
            "button_up":     "up",
            "button_down":   "down",
            "button_left":   "left",
            "button_right":  "right",
            "button_l":      "pageup",
            "button_r":      "pagedown",
            "button_start":  "start",
            "button_select": "select",
            "button_zl":     "l2",
            "button_zr":     "r2",
            "button_home":   "hotkey"
        }

        citraAxis = {
            "circle_pad":    "joystick1",
            "c_stick":       "joystick2"
        }

        # ini file
        citraConfig = ConfigParser.RawConfigParser()
        if os.path.exists(citraConfigFile):
            citraConfig.read(citraConfigFile)

        # layout section
        if not citraConfig.has_section("Layout"):
            citraConfig.add_section("Layout")
        citraConfig.set("Layout", "custom_layout", "1")

        # controls section
        if not citraConfig.has_section("Controls"):
            citraConfig.add_section("Controls")

        for index in playersControllers :
            controller = playersControllers[index]
            # we only care about player 1
            if controller.player != "1":
                continue
            for x in citraButtons:
                citraConfig.set("Controls", x, CitraGenerator.setButton(citraButtons[x], controller.guid, controller.inputs))
            for x in citraAxis:
                citraConfig.set("Controls", x, CitraGenerator.setAxis(citraAxis[x], controller.guid, controller.inputs))
            break

        ### update the configuration file
        if not os.path.exists(os.path.dirname(citraConfigFile)):
            os.makedirs(os.path.dirname(citraConfigFile))
        with open(citraConfigFile, 'w') as configfile:
            citraConfig.write(configfile)

    @staticmethod
    def setButton(key, padGuid, padInputs):
        # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("engine:sdl,guid:{},button:{}").format(padGuid, input.id)
            elif input.type == "hat":
                return ("engine:sdl,guid:{},hat:{},direction:{}").format(padGuid, input.id, CitraGenerator.hatdirectionvalue(input.value))
            elif input.type == "axis":
                # untested, need to configure an axis as button / triggers buttons to be tested too
                return ("engine:sdl,guid:{},axis:{},direction:{},threshold:{}").format(padGuid, input.id, "+", 0.5)

    @staticmethod
    def setAxis(key, padGuid, padInputs):
        inputx = -1
        inputy = -1

        if key == "joystick1":
            inputx = padInputs["joystick1left"]
        elif key == "joystick2":
            inputx = padInputs["joystick2left"]

        if key == "joystick1":
            inputy = padInputs["joystick1up"]
        elif key == "joystick2":
            inputy = padInputs["joystick2up"]

        return ("engine:sdl,guid:{},axis_x:{},axis_y:{}").format(padGuid, inputx.id, inputy.id)

    @staticmethod
    def hatdirectionvalue(value):
        if int(value) == 1:
            return "up"
        if int(value) == 4:
            return "down"
        if int(value) == 2:
            return "right"
        if int(value) == 8:
            return "left"
        return "unknown"
