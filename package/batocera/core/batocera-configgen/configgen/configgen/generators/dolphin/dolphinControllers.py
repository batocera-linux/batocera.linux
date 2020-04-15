#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
import codecs
from Emulator import Emulator
from utils.logger import eslog

# Create the controller configuration file
def generateControllerConfig(system, playersControllers, rom):
    generateHotkeys(playersControllers)
    if system.name == "wii":
        if system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True:
            generateControllerConfig_emulatedwiimotes(playersControllers, rom)
            removeControllerConfig_gamecube() # because pads will already be used as emulated wiimotes
        else:
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(playersControllers,rom) # you can use the gamecube pads on the wii together with wiimotes
    elif system.name == "gamecube":
        generateControllerConfig_gamecube(playersControllers,rom) #pass ROM name to allow for per ROM configuration
    else:
        raise ValueError("Invalid system name : '" + system.name + "'")

def generateControllerConfig_emulatedwiimotes(playersControllers, rom):
    wiiMapping = {
        'x':      'Buttons/2',  'b':        'Buttons/A',
        'y':      'Buttons/1',  'a':        'Buttons/B',
        'pageup': 'Buttons/-',  'pagedown': 'Buttons/+',
        'select':    'Buttons/Home',
        'up': 'D-Pad/Up', 'down': 'D-Pad/Down', 'left': 'D-Pad/Left', 'right': 'D-Pad/Right',
        'joystick1up': 'IR/Up',    'joystick1left': 'IR/Left',
        'joystick2up': 'Tilt/Forward', 'joystick2left': 'Tilt/Left'
    }
    wiiReverseAxes = {
        'D-Pad/Up':   'D-Pad/Down',
        'D-Pad/Left': 'D-Pad/Right',
        'IR/Up':      'IR/Down',
        'IR/Left':    'IR/Right',
        'Swing/Up':   'Swing/Down',
        'Swing/Left': 'Swing/Right',
        'Tilt/Left':  'Tilt/Right',
        'Tilt/Forward': 'Tilt/Backward',
        'Nunchuk/Stick/Up' :  'Nunchuk/Stick/Down',
        'Nunchuk/Stick/Left': 'Nunchuk/Stick/Right',
        'Classic/Right Stick/Up' : 'Classic/Right Stick/Down',
        'Classic/Right Stick/Left' : 'Classic/Right Stick/Right',
        'Classic/Left Stick/Up' : 'Classic/Left Stick/Down',
        'Classic/Left Stick/Left' : 'Classic/Left Stick/Right'
    }

    extraOptions = {}
    extraOptions["Source"] = "1"

    # side wiimote
    # l2 for shaking actions
    if ".side." in rom:
        extraOptions["Options/Sideways Wiimote"] = "1"
        wiiMapping['x']   = 'Buttons/B'
        wiiMapping['y'] = 'Buttons/A'
        wiiMapping['a']   = 'Buttons/2'
        wiiMapping['b'] = 'Buttons/1'
        wiiMapping['l2'] = 'Shake/X'
        wiiMapping['l2'] = 'Shake/Y'
        wiiMapping['l2'] = 'Shake/Z'


    # i: infrared, s: swing, t: tilt, n: nunchuk
    # 12 possible combinations : is si / it ti / in ni / st ts / sn ns / tn nt

    # i
    if ".is." in rom or ".it." in rom or ".in." in rom:
        wiiMapping['joystick1up']   = 'IR/Up'
        wiiMapping['joystick1left'] = 'IR/Left'
    if ".si." in rom or ".ti." in rom or ".ni." in rom:
        wiiMapping['joystick2up']   = 'IR/Up'
        wiiMapping['joystick2left'] = 'IR/Left'

    # s
    if ".si." in rom or ".st." in rom or ".sn." in rom:
        wiiMapping['joystick1up']   = 'Swing/Up'
        wiiMapping['joystick1left'] = 'Swing/Left'
    if ".is." in rom or ".ts." in rom or ".ns." in rom:
        wiiMapping['joystick2up']   = 'Swing/Up'
        wiiMapping['joystick2left'] = 'Swing/Left'

    # t
    if ".ti." in rom or ".ts." in rom or ".tn." in rom:
        wiiMapping['joystick1up']   = 'Tilt/Forward'
        wiiMapping['joystick1left'] = 'Tilt/Left'
    if ".it." in rom or ".st." in rom or ".nt." in rom:
        wiiMapping['joystick2up']   = 'Tilt/Forward'
        wiiMapping['joystick2left'] = 'Tilt/Left'

    # n
    if ".ni." in rom or ".ns." in rom or ".nt." in rom:
        extraOptions['Extension']   = 'Nunchuk'
        wiiMapping['l2'] = 'Nunchuk/Buttons/C'
        wiiMapping['r2'] = 'Nunchuk/Buttons/Z'
        wiiMapping['joystick1up']   = 'Nunchuk/Stick/Up'
        wiiMapping['joystick1left'] = 'Nunchuk/Stick/Left'
    if ".in." in rom or ".sn." in rom or ".tn." in rom:
        extraOptions['Extension']   = 'Nunchuk'
        wiiMapping['l2'] = 'Nunchuk/Buttons/C'
        wiiMapping['r2'] = 'Nunchuk/Buttons/Z'
        wiiMapping['joystick2up']   = 'Nunchuk/Stick/Up'
        wiiMapping['joystick2left'] = 'Nunchuk/Stick/Left'

    if ".cc." in rom:  #Classic Controller Settings
        extraOptions['Extension']   = 'Classic'
        wiiMapping['x'] = 'Classic/Buttons/X'
        wiiMapping['y'] = 'Classic/Buttons/Y'
        wiiMapping['b'] = 'Classic/Buttons/B'
        wiiMapping['a'] = 'Classic/Buttons/A'
        wiiMapping['select'] = 'Classic/Buttons/-'
        wiiMapping['start'] = 'Classic/Buttons/+'
        wiiMapping['pageup'] = 'Classic/Triggers/L'
        wiiMapping['pagedown'] = 'Classic/Triggers/R'
        wiiMapping['l2'] = 'Classic/Buttons/ZL'
        wiiMapping['r2'] = 'Classic/Buttons/ZR'
        wiiMapping['up'] = 'Classic/D-Pad/Up'
        wiiMapping['down'] = 'Classic/D-Pad/Down'
        wiiMapping['left'] = 'Classic/D-Pad/Left'
        wiiMapping['right'] = 'Classic/D-Pad/Right'
        wiiMapping['joystick1up'] = 'Classic/Left Stick/Up'
        wiiMapping['joystick1left'] = 'Classic/Left Stick/Left'
        wiiMapping['joystick2up'] = 'Classic/Right Stick/Up'
        wiiMapping['joystick2left'] = 'Classic/Right Stick/Left'

    #This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"  #Define ROM configuration name
    if os.path.isfile(configname): #file exists
        import ast
        with open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                wiiMapping.update(res)
                line = cconfig.readline()


    eslog.log("Extra Options: {}".format(extraOptions))
    eslog.log("Wii Mappings: {}".format(wiiMapping))

    generateControllerConfig_any(playersControllers, "WiimoteNew.ini", "Wiimote", wiiMapping, wiiReverseAxes, None, extraOptions)

def generateControllerConfig_gamecube(playersControllers,rom):
    gamecubeMapping = {
        'y':      'Buttons/X',  'b':        'Buttons/A',
        'x':      'Buttons/Y',  'a':        'Buttons/B',
        'r2':     'Buttons/Z',  'start':    'Buttons/Start',
        'pageup': 'Triggers/L', 'pagedown': 'Triggers/R',
        'up': 'D-Pad/Up', 'down': 'D-Pad/Down', 'left': 'D-Pad/Left', 'right': 'D-Pad/Right',
        'joystick1up': 'Main Stick/Up', 'joystick1left': 'Main Stick/Left',
        'joystick2up': 'C-Stick/Up',    'joystick2left': 'C-Stick/Left'
    }
    gamecubeReverseAxes = {
        'D-Pad/Up':        'D-Pad/Down',
        'D-Pad/Left':      'D-Pad/Right',
        'Main Stick/Up':   'Main Stick/Down',
        'Main Stick/Left': 'Main Stick/Right',
        'C-Stick/Up':      'C-Stick/Down',
        'C-Stick/Left':    'C-Stick/Right'
    }
    # if joystick1up is missing on the pad, use up instead
    gamecubeReplacements = {
        'joystick1up': 'up',
        'joystick1left': 'left',
        'joystick1down': 'down',
        'joystick1right': 'right'
    }

    #This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"  #Define ROM configuration name
    if os.path.isfile(configname): #file exists
        import ast
        with open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                gamecubeMapping.update(res)
                line = cconfig.readline()


    generateControllerConfig_any(playersControllers, "GCPadNew.ini", "GCPad", gamecubeMapping, gamecubeReverseAxes, gamecubeReplacements)

def removeControllerConfig_gamecube():
    configFileName = "{}/{}".format(batoceraFiles.dolphinConfig, "GCPadNew.ini")
    if os.path.isfile(configFileName):
        os.remove(configFileName)

def generateControllerConfig_realwiimotes(filename, anyDefKey):
    configFileName = "{}/{}".format(batoceraFiles.dolphinConfig, filename)
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")
    nplayer = 1
    while nplayer <= 4:
        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Source = 2\n")
        nplayer += 1
    f.write
    f.close()

def generateHotkeys(playersControllers):
    configFileName = "{}/{}".format(batoceraFiles.dolphinConfig, "Hotkeys.ini")
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")

    hotkeysMapping = {
        'a':  'Keys/Reset',                      'b': 'Keys/Toggle Pause',
        'x':  'Keys/Load from selected slot',    'y': 'Keys/Save to selected slot',
        'r2': None,                          'start': 'Keys/Exit',
        'pageup': 'Keys/Take Screenshot', 'pagedown': 'Keys/Toggle 3D Side-by-side',
        'up': 'Keys/Select State Slot 1', 'down': 'Keys/Select State Slot 2', 'left': None, 'right': None,
        'joystick1up': None, 'joystick1left': None,
        'joystick2up': None,    'joystick2left': None
    }

    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if nplayer == 1:
            f.write("[Hotkeys1]" + "\n")
            f.write("Device = evdev/0/" + pad.realName.strip() + "\n")

            # search the hotkey button
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

                # write the configuration for this key
                if keyname is not None:
                    write_key(f, keyname, input.type, input.id, input.value, pad.nbaxes, False, hotkey.id)
                #else:
                #    f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")

        nplayer += 1

    f.write
    f.close()

def generateControllerConfig_any(playersControllers, filename, anyDefKey, anyMapping, anyReverseAxes, anyReplacements, extraOptions = {}):
    configFileName = "{}/{}".format(batoceraFiles.dolphinConfig, filename)
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")
    nplayer = 1
    nsamepad = 0

    # in case of two pads having the same name, dolphin wants a number to handle this
    double_pads = dict()

    for playercontroller, pad in sorted(playersControllers.items()):
        # handle x pads having the same name
        if pad.configName in double_pads:
            nsamepad = double_pads[pad.configName]
        else:
            nsamepad = 0
        double_pads[pad.configName] = nsamepad+1

        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Device = evdev/" + str(nsamepad).strip() + "/" + pad.realName.strip() + "\n")
        for opt in extraOptions:
            f.write(opt + " = " + extraOptions[opt] + "\n")

        # recompute the mapping according to available buttons on the pads and the available replacements
        currentMapping = anyMapping
        # apply replacements
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
            #else:
            #    f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")

            # write the configuration for this key
            if keyname is not None:
                write_key(f, keyname, input.type, input.id, input.value, pad.nbaxes, False, None)
            # write the 2nd part
            if input.name in { "joystick1up", "joystick1left", "joystick2up", "joystick2left"} and keyname is not None:
                write_key(f, anyReverseAxes[keyname], input.type, input.id, input.value, pad.nbaxes, True, None)

        nplayer += 1
    f.write
    f.close()

def write_key(f, keyname, input_type, input_id, input_value, input_global_id, reverse, hotkey_id):
    f.write(keyname + " = ")
    if hotkey_id is not None:
        f.write("`Button " + str(hotkey_id) + "` & ")
    f.write("`")
    if input_type == "button":
        f.write("Button " + str(input_id))
    elif input_type == "hat":
        if input_value == "1" or input_value == "4": # up or down
            f.write("Axis " + str(int(input_global_id)+1))
        else:
            f.write("Axis " + str(input_global_id))
        if input_value == "1" or input_value == "8": # up or left
            f.write("-")
        else:
            f.write("+")
    elif input_type == "axis":
        if (reverse and input_value == "-1") or (not reverse and input_value == "1"):
            f.write("Axis " + str(input_id) + "+")
        else:
            f.write("Axis " + str(input_id) + "-")
    f.write("`\n")
