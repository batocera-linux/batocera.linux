#!/usr/bin/env python
# -*- coding: utf-8 -*-

import recalboxFiles

# Create the controller configuration file
def generateControllerConfig(system, playersControllers, rom):
    generateHotkeys(playersControllers)
    if system.name == "wii":
        if 'emulatedwiimotes' in system.config and system.config['emulatedwiimotes'] == '1':
            generateControllerConfig_emulatedwiimotes(playersControllers, rom)
        else:
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
    elif system.name == "gamecube":
        generateControllerConfig_gamecube(playersControllers)
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
        'Nunchuk/Stick/Left': 'Nunchuk/Stick/Right'
    }

    extraOptions = {}
    extraOptions["Source"] = "1"

    # side wiimote
    if ".side." in rom:
      extraOptions["Options/Sideways Wiimote"] = "1,000000"

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

    generateControllerConfig_any(playersControllers, "WiimoteNew.ini", "Wiimote", wiiMapping, wiiReverseAxes, extraOptions)

def generateControllerConfig_gamecube(playersControllers):
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
    generateControllerConfig_any(playersControllers, "GCPadNew.ini", "GCPad", gamecubeMapping, gamecubeReverseAxes)

def generateControllerConfig_realwiimotes(filename, anyDefKey):
    configFileName = "{}/{}".format(recalboxFiles.dolphinConfig, filename)
    f = open(configFileName, "w")
    nplayer = 1
    while nplayer <= 4:
        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Source = 2\n")
        nplayer += 1
    f.write
    f.close()

def generateHotkeys(playersControllers):
    configFileName = "{}/{}".format(recalboxFiles.dolphinConfig, "Hotkeys.ini")
    f = open(configFileName, "w")

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
    for playercontroller in playersControllers:
        if nplayer == 1:
            pad = playersControllers[playercontroller]
            f.write("[Hotkeys1]" + "\n")
            f.write("Device = evdev/0/" + pad.realName + "\n")

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

def generateControllerConfig_any(playersControllers, filename, anyDefKey, anyMapping, anyReverseAxes, extraOptions = {}):
    configFileName = "{}/{}".format(recalboxFiles.dolphinConfig, filename)
    f = open(configFileName, "w")
    nplayer = 1
    nsamepad = 0

    # in case of two pads having the same name, dolphin wants a number to handle this
    double_pads = dict()

    for playercontroller in playersControllers:
        # handle x pads having the same name
        pad = playersControllers[playercontroller]
        if pad.configName in double_pads:
            nsamepad = double_pads[pad.configName]
        else:
            nsamepad = 0
        double_pads[pad.configName] = nsamepad+1

        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Device = evdev/" + str(nsamepad) + "/" + pad.realName + "\n")
        for opt in extraOptions:
            f.write(opt + " = " + extraOptions[opt] + "\n")
        for x in pad.inputs:
            input = pad.inputs[x]

            keyname = None
            if input.name in anyMapping:
                keyname = anyMapping[input.name]
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
