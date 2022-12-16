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
import controllersConfig

eslog = get_logger(__name__)

# Create the controller configuration file
def generateControllerConfig(system, playersControllers, rom, guns):

    generateHotkeys(playersControllers)
    if system.name == "wii":
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
            generateControllerConfig_guns("WiimoteNew.ini", "Wiimote", guns, system, rom)
            generateControllerConfig_gamecube(system, playersControllers, rom)           # You can use the gamecube pads on the wii together with wiimotes
        elif (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == False):
            # Generate if hardcoded
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(system, playersControllers, rom)           # You can use the gamecube pads on the wii together with wiimotes
        elif (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True):
            # Generate if hardcoded
            generateControllerConfig_emulatedwiimotes(system, playersControllers, rom)
            removeControllerConfig_gamecube()                                           # Because pads will already be used as emulated wiimotes
        elif (".cc." in rom or ".side." in rom or ".is." in rom or ".it." in rom or ".in." in rom or ".ti." in rom or ".ts." in rom or ".tn." in rom or ".ni." in rom or ".ns." in rom or ".nt." in rom) or system.isOptSet("sideWiimote"):
            # Generate if auto and name extensions are present
            generateControllerConfig_emulatedwiimotes(system, playersControllers, rom)
            removeControllerConfig_gamecube()                                           # Because pads will already be used as emulated wiimotes
        else:
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(system, playersControllers, rom)           # You can use the gamecube pads on the wii together with wiimotes
    elif system.name == "gamecube":
        generateControllerConfig_gamecube(system, playersControllers, rom)               # Pass ROM name to allow for per ROM configuration
    else:
        raise ValueError("Invalid system name : '" + system.name + "'")

def generateControllerConfig_emulatedwiimotes(system, playersControllers, rom):
    wiiMapping = {
        'x':            'Buttons/2',    'b':             'Buttons/A',
        'y':            'Buttons/1',    'a':             'Buttons/B',
        'pageup':       'Buttons/-',    'pagedown':      'Buttons/+',
        'select':       'Buttons/Home',
        'up': 'D-Pad/Up', 'down': 'D-Pad/Down', 'left': 'D-Pad/Left', 'right': 'D-Pad/Right',
        'joystick1up':  'IR/Up',        'joystick1left': 'IR/Left',
        'joystick2up':  'Tilt/Forward', 'joystick2left': 'Tilt/Left',
        'hotkey':       'Buttons/Hotkey'
    }
    wiiReverseAxes = {
        'IR/Up':        'IR/Down',
        'IR/Left':      'IR/Right',
        'Swing/Up':     'Swing/Down',
        'Swing/Left':   'Swing/Right',
        'Tilt/Left':    'Tilt/Right',
        'Tilt/Forward': 'Tilt/Backward',
        'Nunchuk/Stick/Up':         'Nunchuk/Stick/Down',
        'Nunchuk/Stick/Left':       'Nunchuk/Stick/Right',
        'Classic/Right Stick/Up':   'Classic/Right Stick/Down',
        'Classic/Right Stick/Left': 'Classic/Right Stick/Right',
        'Classic/Left Stick/Up':    'Classic/Left Stick/Down',
        'Classic/Left Stick/Left':  'Classic/Left Stick/Right'
    }

    extraOptions = {}
    extraOptions["Source"] = "1"

    # Side wiimote
    # l2 for shaking actions
    if (".side." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] != 'disabled' and system.config['controller_mode'] != 'cc'):
        extraOptions["Options/Sideways Wiimote"] = "1"
        wiiMapping['x']  = 'Buttons/B'
        wiiMapping['y']  = 'Buttons/A'
        wiiMapping['a']  = 'Buttons/2'
        wiiMapping['b']  = 'Buttons/1'
        wiiMapping['l2'] = 'Shake/X'
        wiiMapping['l2'] = 'Shake/Y'
        wiiMapping['l2'] = 'Shake/Z'

    # i: infrared, s: swing, t: tilt, n: nunchuk
    # 12 possible combinations : is si / it ti / in ni / st ts / sn ns / tn nt

    # i
    if (".is." in rom or ".it." in rom or ".in." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] != 'disabled' and system.config['controller_mode'] != 'in' and system.config['controller_mode'] != 'cc'):
        wiiMapping['joystick1up']   = 'IR/Up'
        wiiMapping['joystick1left'] = 'IR/Left'
    if (".si." in rom or ".ti." in rom or ".ni." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'in' and system.config['controller_mode'] != 'cc'):
        wiiMapping['joystick2up']   = 'IR/Up'
        wiiMapping['joystick2left'] = 'IR/Left'

    # s
    if ".si." in rom or ".st." in rom or ".sn." in rom:
        wiiMapping['joystick1up']   = 'Swing/Up'
        wiiMapping['joystick1left'] = 'Swing/Left'
    if (".is." in rom or ".ts." in rom or ".ns." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'is'):
        wiiMapping['joystick2up']   = 'Swing/Up'
        wiiMapping['joystick2left'] = 'Swing/Left'

    # t
    if ".ti." in rom or ".ts." in rom or ".tn." in rom:
        wiiMapping['joystick1up']   = 'Tilt/Forward'
        wiiMapping['joystick1left'] = 'Tilt/Left'
    if (".it." in rom or ".st." in rom or ".nt." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'it'):
        wiiMapping['joystick2up']   = 'Tilt/Forward'
        wiiMapping['joystick2left'] = 'Tilt/Left'

    # n
    if (".ni." in rom or ".ns." in rom or ".nt." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'in'):
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

    # cc : Classic Controller Settings
    if (".cc." in rom) or (system.isOptSet("controller_mode") and system.config['controller_mode'] == 'cc'):
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

    # This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"       # Define ROM configuration name
    if os.path.isfile(configname):  # File exists
        import ast
        with open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                wiiMapping.update(res)
                line = cconfig.readline()

    eslog.debug(f"Extra Options: {extraOptions}")
    eslog.debug(f"Wii Mappings: {wiiMapping}")

    generateControllerConfig_any(system, playersControllers, "WiimoteNew.ini", "Wiimote", wiiMapping, wiiReverseAxes, None, extraOptions)

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

    generateControllerConfig_any(system, playersControllers, "GCPadNew.ini", "GCPad", gamecubeMapping, gamecubeReverseAxes, gamecubeReplacements)

def removeControllerConfig_gamecube():
    configFileName = "{}/{}".format(batoceraFiles.dolphinConfig, "GCPadNew.ini")
    if os.path.isfile(configFileName):
        os.remove(configFileName)

def generateControllerConfig_realwiimotes(filename, anyDefKey):
    configFileName = f"{batoceraFiles.dolphinConfig}/{filename}"
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")
    nplayer = 1
    while nplayer <= 4:
        f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
        f.write("Source = 2\n")
        nplayer += 1
    f.write
    f.close()

def generateControllerConfig_guns(filename, anyDefKey, guns, system, rom):
    configFileName = f"{batoceraFiles.dolphinConfig}/{filename}"
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")

    # In case of two pads having the same name, dolphin wants a number to handle this
    double_pads = dict()

    gunsmetadata = {}
    if len(guns) > 0:
        gunsmetadata = controllersConfig.getGameGunsMetaData(system.name, rom)

    nplayer = 1
    while nplayer <= 4:
        if len(guns) >= nplayer:
            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write("Source = 1\n")

            gundevname = guns[nplayer-1]["name"]

            # Handle x pads having the same name
            nsamepad = 0
            if gundevname.strip() in double_pads:
                nsamepad = double_pads[gundevname.strip()]
            else:
                nsamepad = 0
                double_pads[gundevname.strip()] = nsamepad+1

            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write("Device = evdev/" + str(nsamepad).strip() + "/" + gundevname.strip() + "\n")

            buttons = guns[nplayer-1]["buttons"]
            eslog.debug(f"Gun : {buttons}")
            # buttons are orgnanized here as the reverse of the wii2gun mapping rules
            # so that the wiimote has the correct mapping
            # then, depending on missing buttons, we add the + which is important

            # fire
            if "right" in buttons:
                f.write("Buttons/A = `BTN_RIGHT`\n")
            if "left" in buttons:
                f.write("Buttons/B = `BTN_LEFT`\n")

            # extra buttons
            mappings = {
                "Home": "4",
                "-": "1",
                "1": "2",
                "2": "3",
                "+": "middle"
            }

            mapping_words = {
                "middle": "BTN_MIDDLE"
            }

            # for a button for + because it is an important button
            if mappings["+"] not in buttons:
                for key in mappings:
                    if mappings[key] in buttons:
                        mappings["+"] = mappings[key]
                        mappings[key] = None
                        break

            for mapping in mappings:
                if mappings[mapping] in buttons:
                    if mappings[mapping] in mapping_words:
                        f.write("Buttons/" + mapping + " = `" + mapping_words[mappings[mapping]] + "`\n")
                    else:
                        f.write("Buttons/" + mapping + " = `" + mappings[mapping] + "`\n")

            # directions
            if "5" in buttons:
                f.write("D-Pad/Up = `5`\n")
            if "6" in buttons:
                f.write("D-Pad/Down = `6`\n")
            if "7" in buttons:
                f.write("D-Pad/Left = `7`\n")
            if "8" in buttons:
                f.write("D-Pad/Right = `8`\n")

            if "ir_up" not in gunsmetadata:
                f.write("IR/Up = `Axis 1-`\n")
            if "ir_down" not in gunsmetadata:
                f.write("IR/Down = `Axis 1+`\n")
            if "ir_left" not in gunsmetadata:
                f.write("IR/Left = `Axis 0-`\n")
            if "ir_right" not in gunsmetadata:
                f.write("IR/Right = `Axis 0+`\n")

            # specific games configurations
            specifics = {
                "vertical_offset": "IR/Vertical Offset",
                "yaw":             "IR/Total Yaw",
                "pitch":           "IR/Total Pitch",
                "ir_up":           "IR/Up",
                "ir_down":         "IR/Down",
                "ir_left":         "IR/Left",
                "ir_right":        "IR/Right",
            }
            for spe in specifics:
                if spe in gunsmetadata:
                    f.write("{} = {}\n".format(specifics[spe], gunsmetadata[spe]))
        nplayer += 1
    f.write
    f.close()

def generateHotkeys(playersControllers):
    configFileName = "{}/{}".format(batoceraFiles.dolphinConfig, "Hotkeys.ini")
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
            f.write("Device = evdev/0/" + pad.realName.strip() + "\n")

            # Search the hotkey button
            hotkey = None
            if "hotkey" not in pad.inputs:
                return
            hotkey = pad.inputs["hotkey"]
            if hotkey.type != "button":
                return

            for x in pad.inputs:
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
    configFileName = f"{batoceraFiles.dolphinConfig}/{filename}"
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
        f.write("Device = evdev/" + str(nsamepad).strip() + "/" + pad.realName.strip() + "\n")

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
        # DualShock Motion control
        if system.isOptSet("dsmotion") and system.getOptBoolean("dsmotion") == True:
            f.write("IMUGyroscope/Pitch Up = `Gyro X-`\n")
            f.write("IMUGyroscope/Pitch Down = `Gyro X+`\n")
            f.write("IMUGyroscope/Roll Left = `Gyro Z-`\n")
            f.write("IMUGyroscope/Roll Right = `Gyro Z+`\n")
            f.write("IMUGyroscope/Yaw Left = `Gyro Y-`\n")
            f.write("IMUGyroscope/Yaw Right = `Gyro Y+`\n")
            f.write("IMUIR/Recenter = `Button 10`\n")
            f.write("IMUAccelerometer/Left = `Accel X-`\n")
            f.write("IMUAccelerometer/Right = `Accel X+`\n")
            f.write("IMUAccelerometer/Forward = `Accel Z-`\n")
            f.write("IMUAccelerometer/Backward = `Accel Z+`\n")
            f.write("IMUAccelerometer/Up = `Accel Y-`\n")
            f.write("IMUAccelerometer/Down = `Accel Y+`\n")
        # Mouse to emulate Wiimote
        if system.isOptSet("mouseir") and system.getOptBoolean("mouseir") == True:
            f.write("IR/Up = `Cursor Y-`\n")
            f.write("IR/Down = `Cursor Y+`\n")
            f.write("IR/Left = `Cursor X-`\n")
            f.write("IR/Right = `Cursor X+`\n")
        # Rumble option
        if system.isOptSet("rumble") and system.getOptBoolean("rumble") == True:
            f.write("Rumble/Motor = Weak\n")

def generateControllerConfig_any_from_profiles(f, pad):
    for profileFile in glob.glob("/userdata/system/configs/dolphin-emu/Profiles/GCPad/*.ini"):
        try:
            eslog.debug(f"Looking profile : {profileFile}")
            profileConfig = configparser.ConfigParser(interpolation=None)
            # To prevent ConfigParser from converting to lower case
            profileConfig.optionxform = str
            profileConfig.read(profileFile)
            profileDevice = profileConfig.get("Profile","Device")
            eslog.debug(f"Profile device : {profileDevice}")

            deviceVals = re.match("^([^/]*)/[0-9]*/(.*)$", profileDevice)
            if deviceVals is not None:
                if deviceVals.group(1) == "evdev" and deviceVals.group(2).strip() == pad.realName.strip():
                    eslog.debug("Eligible profile device found")
                    for key, val in profileConfig.items("Profile"):
                        if key != "Device":
                            f.write(f"{key} = {val}\n")
                    return True
        except:
            eslog.error(f"profile {profileFile} : FAILED")

    return False

def write_key(f, keyname, input_type, input_id, input_value, input_global_id, reverse, hotkey_id):
    f.write(keyname + " = ")
    if hotkey_id is not None:
        f.write("`Button " + str(hotkey_id) + "` & ")
    f.write("`")
    if input_type == "button":
        f.write("Button " + str(input_id))
    elif input_type == "hat":
        if input_value == "1" or input_value == "4":        # up or down
            f.write("Axis " + str(int(input_global_id)+1))
        else:
            f.write("Axis " + str(input_global_id))
        if input_value == "1" or input_value == "8":        # up or left
            f.write("-")
        else:
            f.write("+")
    elif input_type == "axis":
        if (reverse and input_value == "-1") or (not reverse and input_value == "1"):
            f.write("Axis " + str(input_id) + "+")
        else:
            f.write("Axis " + str(input_id) + "-")
    f.write("`\n")
