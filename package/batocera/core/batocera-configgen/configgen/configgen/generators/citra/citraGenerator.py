#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os
import configparser

class CitraGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        CitraGenerator.writeCITRAConfig(batoceraFiles.citraConfig, system, playersControllers)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], rom]
        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_DATA_HOME":batoceraFiles.citraSaves, "XDG_CACHE_HOME":batoceraFiles.CACHE, "QT_QPA_PLATFORM":"xcb"})

    @staticmethod
    def writeCITRAConfig(citraConfigFile, system, playersControllers):
        # Pads
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
        citraConfig = configparser.RawConfigParser(strict=False)
        if os.path.exists(citraConfigFile):
            citraConfig.read(citraConfigFile)

        ## [LAYOUT]
        if not citraConfig.has_section("Layout"):
            citraConfig.add_section("Layout")

        # Screen Layout
        citraConfig.set("Layout", "custom_layout", "0")
        if system.isOptSet('citra_screen_layout'):
            tab = system.config["citra_screen_layout"].split('-')
            citraConfig.set("Layout", "swap_screen",   tab[1])
            citraConfig.set("Layout", "layout_option", tab[0])
        else:
            citraConfig.set("Layout", "swap_screen",   "false")
            citraConfig.set("Layout", "layout_option", "4")


        ## [UI]
        if not citraConfig.has_section("UI"):
            citraConfig.add_section("UI")
        
        # Start Fullscreen
        citraConfig.set("UI", "fullscreen", "true")


        ## [CONTROLS]
        if not citraConfig.has_section("Controls"):
            citraConfig.add_section("Controls")

        # Options required to load the functions when the configuration file is created
        if not citraConfig.has_option("Controls", "profiles\\size"):
            citraConfig.set("Controls", "profile", 0)
            citraConfig.set("Controls", "profile\\default", "true")    
            citraConfig.set("Controls", "profiles\\1\\name", "default")
            citraConfig.set("Controls", "profiles\\1\\name\\default", "true")
            citraConfig.set("Controls", "profiles\\size", 1)

        for index in playersControllers :
            controller = playersControllers[index]
            # We only care about player 1
            if controller.player != "1":
                continue
            for x in citraButtons:
                citraConfig.set("Controls", "profiles\\1\\" + x, '"{}"'.format(CitraGenerator.setButton(citraButtons[x], controller.guid, controller.inputs)))
            for x in citraAxis:
                citraConfig.set("Controls", "profiles\\1\\" + x, '"{}"'.format(CitraGenerator.setAxis(citraAxis[x], controller.guid, controller.inputs)))
            break

        ## Update the configuration file
        if not os.path.exists(os.path.dirname(citraConfigFile)):
            os.makedirs(os.path.dirname(citraConfigFile))
        with open(citraConfigFile, 'w') as configfile:
            citraConfig.write(configfile)

    @staticmethod
    def setButton(key, padGuid, padInputs):
        # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("button:{},guid:{},engine:sdl").format(input.id, padGuid)
            elif input.type == "hat":
                return ("engine:sdl,guid:{},hat:{},direction:{}").format(padGuid, input.id, CitraGenerator.hatdirectionvalue(input.value))
            elif input.type == "axis":
                # Untested, need to configure an axis as button / triggers buttons to be tested too
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

        return ("axis_x:{},guid:{},axis_y:{},engine:sdl").format(inputx.id, padGuid, inputy.id)

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
