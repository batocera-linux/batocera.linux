#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
import codecs
from Emulator import Emulator
from utils.logger import get_logger
import glob
import configparser
import re

eslog = get_logger(__name__)

# Create the controller configuration file
def generateControllerConfig(system, playersControllers, rom):

    generateHotkeys(playersControllers)
    generateControllerConfig_gamecube(system, playersControllers,rom)               # Pass ROM name to allow for per ROM configuration

def generateControllerConfig_gamecube(system, playersControllers,rom):
    gamecubeMapping = {
        'y':            'Buttons/B',     'b':             'Buttons/A',
        'x':            'Buttons/Y',     'a':             'Buttons/X',
        'pagedown':     'Buttons/Z',     'start':         'Buttons/Start',
        'l2':           'Triggers/L',    'r2':            'Triggers/R',
        'up': 'D-Pad/Up', 'down': 'D-Pad/Down', 'left': 'D-Pad/Left', 'right': 'D-Pad/Right',
        'joystick1up':  'Main Stick/Up', 'joystick1left': 'Main Stick/Left',
        'joystick2up':  'C-Stick/Up',    'joystick2left': 'C-Stick/Left',
        'hotkey':       'Buttons/Hotkey'
    }
    gamecubeReverseAxes = {
        'Main Stick/Up':   'Main Stick/Down',
        'Main Stick/Left': 'Main Stick/Right',
        'C-Stick/Up':      'C-Stick/Down',
        'C-Stick/Left':    'C-Stick/Right'
    }
    # If joystick1up is missing on the pad, use up instead, and if l2/r2 is missing, use l1/r1
    gamecubeReplacements = {
        'joystick1up':    'up',
        'joystick1left':  'left',
        'joystick1down':  'down',
        'joystick1right': 'right',
        'l2':             'pageup',
        'r2':             'pagedown'
    }

    # This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"       # Define ROM configuration name
    if os.path.isfile(configname):  # File exists
        import ast
        with open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                gamecubeMapping.update(res)
                line = cconfig.readline()

    generateControllerConfig_any(system, playersControllers, "Config/GCPadNew.ini", "GCPad", gamecubeMapping, gamecubeReverseAxes, gamecubeReplacements)

def removeControllerConfig_gamecube():
    configFileName = "{}/{}".format(batoceraFiles.dolphinTriforceConfig, "Config/GCPadNew.ini")
    if os.path.isfile(configFileName):
        os.remove(configFileName)

def generateHotkeys(playersControllers):
    configFileName = "{}/{}".format(batoceraFiles.dolphinTriforceConfig, "Config/Hotkeys.ini")
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")

    hotkeysMapping = {
        'a':           'Keys/Reset',                    'b': 'Keys/Toggle Pause',
        'x':           'Keys/Load from selected slot',  'y': 'Keys/Save to selected slot',
        'r2':          None,                            'start': 'Keys/Exit',
        'pageup': 'Keys/Take Screenshot', 'pagedown': 'Keys/Toggle 3D Side-by-side',
        'up': 'Keys/Select State Slot 1', 'down': 'Keys/Select State Slot 2', 'left': None, 'right': None,
        'joystick1up': None,    'joystick1left': None,
        'joystick2up': None,    'joystick2left': None
    }

    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer == 1:
            f.write("[Hotkeys1]" + "\n")
            f.write("Device = SDL/0/" + pad.realName.strip() + "\n")

            # Search the hotkey button
            hotkey = None
            if "hotkey" not in pad.inputs:
                return
            hotkey = pad.inputs["hotkey"]
            if hotkey.type != "button":
                return

            for x in pad.inputs:
                print
                input = pad.inputs[x]

                keyname = None
                if input.name in hotkeysMapping:
                    keyname = hotkeysMapping[input.name]

                # Write the configuration for this key
                if keyname is not None:
                    write_key(f, keyname, input.type, input.id, input.value, pad.nbaxes, False, hotkey.id)
                    
                #else:
                #    f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")

        nplayer += 1

    f.write
    f.close()

def generateControllerConfig_any(system, playersControllers, filename, anyDefKey, anyMapping, anyReverseAxes, anyReplacements, extraOptions = {}):
    configFileName = "{}/{}".format(batoceraFiles.dolphinTriforceConfig, filename)
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")
    nplayer = 1
    nsamepad = 0

    # In case of two pads having the same name, dolphin wants a number to handle this
    double_pads = dict()

    for playercontroller, pad in sorted(playersControllers.items()):
        # Handle x pads having the same name
        if pad.realName.strip() in double_pads:
            nsamepad = double_pads[pad.realName.strip()]
        else:
            nsamepad = 0
        double_pads[pad.realName.strip()] = nsamepad+1

        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Device = SDL/" + str(nsamepad).strip() + "/" + pad.realName.strip() + "\n")

        if system.isOptSet("use_pad_profiles") and system.getOptBoolean("use_pad_profiles") == True:
            if not generateControllerConfig_any_from_profiles(f, pad):
                generateControllerConfig_any_auto(f, pad, anyMapping, anyReverseAxes, anyReplacements, extraOptions, system)
        else:
            generateControllerConfig_any_auto(f, pad, anyMapping, anyReverseAxes, anyReplacements, extraOptions, system)

        nplayer += 1
    f.write
    f.close()

def generateControllerConfig_any_auto(f, pad, anyMapping, anyReverseAxes, anyReplacements, extraOptions, system):
    for opt in extraOptions:
        f.write(opt + " = " + extraOptions[opt] + "\n")
    
    # Recompute the mapping according to available buttons on the pads and the available replacements
    currentMapping = anyMapping
    # Apply replacements
    if anyReplacements is not None:
        for x in anyReplacements:
            if x not in pad.inputs and x in currentMapping:
                currentMapping[anyReplacements[x]] = currentMapping[x]
                if x == "joystick1up":
                    currentMapping[anyReplacements["joystick1down"]] = anyReverseAxes[currentMapping["joystick1up"]]
                if x == "joystick1left":
                    currentMapping[anyReplacements["joystick1right"]] = anyReverseAxes[currentMapping["joystick1left"]]
                if x == "joystick2up":
                    currentMapping[anyReplacements["joystick2down"]] = anyReverseAxes[currentMapping["joystick2up"]]
                if x == "joystick2left":
                    currentMapping[anyReplacements["joystick2right"]] = anyReverseAxes[currentMapping["joystick2left"]]
    
    for x in pad.inputs:
        input = pad.inputs[x]
    
        keyname = None
        if input.name in currentMapping:
            keyname = currentMapping[input.name]
    
        # Write the configuration for this key
        if keyname is not None:
            write_key(f, keyname, input.type, input.id, input.value, pad.nbaxes, False, None)
            if 'Triggers' in keyname and input.type == 'axis':
                write_key(f, keyname + '-Analog', input.type, input.id, input.value, pad.nbaxes, False, None)
        # Write the 2nd part
        if input.name in { "joystick1up", "joystick1left", "joystick2up", "joystick2left"} and keyname is not None:
            write_key(f, anyReverseAxes[keyname], input.type, input.id, input.value, pad.nbaxes, True, None)
        # Rumble option
        if system.isOptSet("rumble") and system.getOptBoolean("rumble") == True:
            f.write("Rumble/Motor = Weak\n")

def generateControllerConfig_any_from_profiles(f, pad):
    for profileFile in glob.glob("/userdata/system/configs/dolphin-triforce/Config/Profiles/GCPad/*.ini"):
        try:
            eslog.debug("Looking profile : {}".format(profileFile))
            profileConfig = configparser.ConfigParser(interpolation=None)
            # To prevent ConfigParser from converting to lower case
            profileConfig.optionxform = str
            profileConfig.read(profileFile)
            profileDevice = profileConfig.get("Profile","Device")
            eslog.debug("Profile device : {}".format(profileDevice))

            deviceVals = re.match("^([^/]*)/[0-9]*/(.*)$", profileDevice)
            if deviceVals is not None:
                if deviceVals.group(1) == "SDL" and deviceVals.group(2).strip() == pad.realName.strip():
                    eslog.debug("Eligible profile device found")
                    for key, val in profileConfig.items("Profile"):
                        if key != "Device":
                            f.write("{} = {}\n".format(key, val))
                    return True
        except:
            eslog.error("profile {} : FAILED".format(profileFile))

    return False

def write_key(f, keyname, input_type, input_id, input_value, input_global_id, reverse, hotkey_id):
    f.write(keyname + " = ")
    if hotkey_id is not None:
        f.write("`Button " + str(hotkey_id) + "` & ")
    f.write("`")
    if input_type == "button":
        f.write("Button " + str(input_id))
    elif input_type == "hat":
        if input_value == "1":        # up
            f.write("Hat 0 N")
        elif input_value == "4": # down
            f.write("Hat 0 S")
        elif input_value == "8": # left
            f.write("Hat 0 W")
    elif input_type == "axis":
        if (reverse and input_value == "-1") or (not reverse and input_value == "1"):
            f.write("Axis " + str(input_id) + "+")
        else:
            f.write("Axis " + str(input_id) + "-")
    f.write("`\n")
