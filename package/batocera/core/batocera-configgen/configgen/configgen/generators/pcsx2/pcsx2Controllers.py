#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from utils.logger import eslog

# Create the controller configuration file
def generateControllerConfig(system, playersControllers, rom):
    pcsx2Keys = {
        0: "l2",
        1: "r2",
        2: "pageup",
        3: "pagedown",
        4: "x",
        5: "a",
        6: "b",
        7: "y",
        8: "select",
        9: "l3",
        10: "r3",
        11: "start",
        12: "up",
        13: "right",
        14: "down",
        15: "left",
        16: "joystick1up",
        17: "joystick1right",
        18: "joystick1down",
        19: "joystick1left",
        20: "joystick2up",
        21: "joystick2right",
        22: "joystick2down",
        23: "joystick2left",
        24: "hotkey"
    }

    configDir      = "{}/{}".format(batoceraFiles.pcsx2ConfigDir, "inis")
    configFileName = "{}/{}".format(configDir, "OnePAD.ini")
    if not os.path.exists(configDir):
        os.makedirs(configDir)
    f = open(configFileName, "w")
    f.write("log = 0\n")
    f.write("options = 1919117645\n")
    f.write("mouse_sensibility = 500\n")
    f.write("joy_pad_map = 256\n")
    f.write("ff_intensity = 32767\n")

    nplayer = 0

    # players with a controller
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer < 2:
            f.write("[{}][name] = {}\n".format(nplayer, pad.realName))

            for x in pcsx2Keys:
                writeKey(f, nplayer, x, pcsx2Keys[x], pad.inputs)
            
        nplayer += 1

    # players without controller
    for i in range(nplayer, 2):
        f.write("[{}][name] = \n".format(i))
        for x in pcsx2Keys:
            f.write("[{}][{}] = 0x0\n".format(i, x))

    f.close()

def writeKey(f, nplayer, x, key, padInputs):
    configkey = key
    
    # reversed keys
    reversedAxis = False
    if key == "joystick1down":
        reversedAxis = True
        configkey = "joystick1up"
    elif key == "joystick1right":
        reversedAxis = True
        configkey = "joystick1left"
    elif key == "joystick2down":
        reversedAxis = True
        configkey = "joystick2up"
    elif key == "joystick2right":
        reversedAxis = True
        configkey = "joystick2left"
    eslog.log("Config Key: {}".format(configkey))
    eslog.log("reversedAxis: {}".format(reversedAxis))
    #define button 

    if configkey in padInputs:
        input = padInputs[configkey]
        #f.write("# key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")
        
        
        if input.type == "button":
            f.write("[{}][{}] = 0x{:02x}\n".format(nplayer, x, button_to_key(input.id)))
        elif input.type == "axis":
            eslog.log("input.value: {}".format(input.value))
            full_axis = 0
            if int(input.value) > 0:
                full_axis = 1
            eslog.log("full_axis: {}".format(full_axis))
            sign = 0
            if int(input.value) < 0:
                sign = 1
            if reversedAxis:
                if int(input.value) < 0:
                    sign = 0
                else:
                    sign = 1
            f.write("[{}][{}] = 0x{:02x}\n".format(nplayer, x, axis_to_key(full_axis, sign, input.id)))
        elif input.type == "hat":
            f.write("[{}][{}] = 0x{:02x}\n".format(nplayer, x, hat_to_key(input.value, input.id)))
    else:
        f.write("[{}][{}] = 0x0\n".format(nplayer, x))

def button_to_key(button_id):
    return (0x10000 | int(button_id))

def axis_to_key(full_axis, sign, axis_id):
    return (0x20000 | (full_axis << 9) | (sign << 8) | int(axis_id));

def hat_to_key(dir, axis_id):
    return (0x30000 | (int(dir) << 8) | int(axis_id))
