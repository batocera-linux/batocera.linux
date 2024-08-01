#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
import configparser
import io
import re
import shutil
from shutil import copyfile

class SupermodelGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["supermodel", "-fullscreen", "-channels=2"]
        
        # legacy3d
        if system.isOptSet("engine3D") and system.config["engine3D"] == "new3d":
            commandArray.append("-new3d")
        else:
             commandArray.extend(["-multi-texture", "-legacy-scsp", "-legacy3d"])
        
        # widescreen
        if system.isOptSet("m3_wideScreen") and system.getOptBoolean("m3_wideScreen"):
            commandArray.append("-wide-screen")
            commandArray.append("-wide-bg")
            system.config["bezel"] == "none"

        # quad rendering
        if system.isOptSet("quadRendering") and system.getOptBoolean("quadRendering"):
            commandArray.append("-quad-rendering")

        # crosshairs
        if system.isOptSet("crosshairs"):
            commandArray.append("-crosshairs={}".format(system.config["crosshairs"]))
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                if len(guns) == 1:
                    commandArray.append("-crosshairs={}".format("1"))
                else:
                    commandArray.append("-crosshairs={}".format("3"))

        # force feedback
        if system.isOptSet("forceFeedback") and system.getOptBoolean("forceFeedback"):
            commandArray.append("-force-feedback")

        # powerpc frequesncy
        if system.isOptSet("ppcFreq"):
            commandArray.append("-ppc-frequency={}".format(system.config["ppcFreq"]))

        #driving controls
        if system.isOptSet("pedalSwap") and system.getOptBoolean("pedalSwap"):
            drivingGame = 1
        else:
            drivingGame = 0
        
        #driving sensitivity
        if system.isOptSet("joystickSensitivity"):
            sensitivity = system.config["joystickSensitivity"]
        else:
            sensitivity = "100"

        # resolution
        commandArray.append("-res={},{}".format(gameResolution["width"], gameResolution["height"]))

        # logs
        commandArray.extend(["-log-output=/userdata/system/logs/Supermodel.log", rom])

        # copy nvram files
        copy_nvram_files()

        # copy gun asset files
        copy_asset_files()

        # copy xml
        copy_xml()

        # config
        configPadsIni(system, rom, playersControllers, guns, drivingGame, sensitivity)

        return Command.Command(array=commandArray, env={"SDL_VIDEODRIVER":"x11"})

def copy_nvram_files():
    sourceDir = "/usr/share/supermodel/NVRAM"
    targetDir = "/userdata/saves/supermodel/NVRAM"
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    # create nv files which are in source and have a newer modification time than in target
    for file in os.listdir(sourceDir):
        extension = os.path.splitext(file)[1][1:]
        if extension == "nv":
            sourceFile = os.path.join(sourceDir, file)
            targetFile = os.path.join(targetDir, file)
            if not os.path.exists(targetFile):
                # if the target file doesn't exist, just copy the source file
                copyfile(sourceFile, targetFile)
            else:
                # if the target file exists and has an older modification time than the source file, create a backup and copy the new file
                if os.path.getmtime(sourceFile) > os.path.getmtime(targetFile):
                    backupFile = targetFile + ".bak"
                    if os.path.exists(backupFile):
                        os.remove(backupFile)
                    os.rename(targetFile, backupFile)
                    copyfile(sourceFile, targetFile)

def copy_asset_files():
    sourceDir = "/usr/share/supermodel/Assets"
    targetDir = "/userdata/system/configs/supermodel/Assets"
    if not os.path.exists(sourceDir):
        return
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    # create asset files which are in source and have a newer modification time than in target
    for file in os.listdir(sourceDir):
        sourceFile = os.path.join(sourceDir, file)
        targetFile = os.path.join(targetDir, file)
        if not os.path.exists(targetFile) or os.path.getmtime(sourceFile) > os.path.getmtime(targetFile):
            copyfile(sourceFile, targetFile)

def copy_xml():
    source_path = '/usr/share/supermodel/Games.xml'
    dest_path = '/userdata/system/configs/supermodel/Games.xml'
    if not os.path.exists('/userdata/system/configs/supermodel'):
        os.makedirs('/userdata/system/configs/supermodel')
    if not os.path.exists(dest_path) or os.path.getmtime(source_path) > os.path.getmtime(dest_path):
        shutil.copy2(source_path, dest_path)

def configPadsIni(system, rom, playersControllers, guns, altControl, sensitivity):
    if bool(altControl):
        templateFile = "/usr/share/supermodel/Supermodel-Driving.ini.template"
        mapping = {
            "button1": "y",
            "button2": "b",
            "button3": "a",
            "button4": "x",
            "button5": "pageup",
            "button6": "pagedown",
            "button7": None,
            "button8": None,
            "button9": "start", # start
            "button10": "select", # coins
            "axisX": "joystick1left",
            "axisY": "joystick1up",
            "axisZ": "l2",
            "axisRX": "joystick2left",
            "axisRY": "joystick2up",
            "axisRZ": "r2",
            "left": "joystick1left",
            "right": "joystick1right",
            "up": "joystick1up",
            "down": "joystick1down"
        }
    else:
        templateFile = "/usr/share/supermodel/Supermodel.ini.template"
        mapping = {
            "button1": "y",
            "button2": "b",
            "button3": "a",
            "button4": "x",
            "button5": "pageup",
            "button6": "pagedown",
            "button7": "l2",
            "button8": "r2",
            "button9": "start", # start
            "button10": "select", # coins
            "axisX": "joystick1left",
            "axisY": "joystick1up",
            "axisZ": None,
            "axisRX": "joystick2left",
            "axisRY": "joystick2up",
            "axisRZ": None,
            "left": "joystick1left",
            "right": "joystick1right",
            "up": "joystick1up",
            "down": "joystick1down"
        }
    targetFile = "/userdata/system/configs/supermodel/Supermodel.ini"

    mapping_fallback = {
        "axisX": "left",
        "axisY": "up",
        "right": "right",
        "down": "down",
        "left": "left",
        "up": "up"
    }

    # template
    templateConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    templateConfig.optionxform = str
    with io.open(templateFile, 'r', encoding='utf_8_sig') as fp:
        templateConfig.readfp(fp)

    # target
    targetConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    targetConfig.optionxform = str

    for section in templateConfig.sections():
        targetConfig.add_section(section)
        for key, value in templateConfig.items(section):
            targetConfig.set(section, key, transformValue(value, playersControllers, mapping, mapping_fallback))

    # apply guns
    for section in targetConfig.sections():
        romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
        if section.strip() in [ "Global", romBase ]:
            # for an input sytem
            if section.strip() != "Global":
                targetConfig.set(section, "InputSystem", "to be defined")
            for key, value in targetConfig.items(section):
                if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
                    if key == "InputSystem":
                        targetConfig.set(section, key, "evdev")
                    elif key == "InputAnalogJoyX":
                        targetConfig.set(section, key, "MOUSE1_XAXIS_INV")
                    elif key == "InputAnalogJoyY":
                        targetConfig.set(section, key, "MOUSE1_YAXIS_INV")
                    elif key == "InputGunX" or key == "InputAnalogGunX":
                        targetConfig.set(section, key, "MOUSE1_XAXIS")
                    elif key == "InputGunY" or key == "InputAnalogGunY":
                        targetConfig.set(section, key, "MOUSE1_YAXIS")
                    elif key == "InputTrigger" or key == "InputAnalogTriggerLeft" or key == "InputAnalogJoyTrigger":
                        targetConfig.set(section, key, "MOUSE1_LEFT_BUTTON")
                    elif key == "InputOffscreen" or key == "InputAnalogTriggerRight":
                        targetConfig.set(section, key, "MOUSE1_RIGHT_BUTTON")
                    elif key == "InputStart1":
                        val = transformElement("JOY1_BUTTON9", playersControllers, mapping, mapping_fallback)
                        if val is not None:
                            val = "," + val
                        else:
                            val = ""
                        targetConfig.set(section, key, "MOUSE1_BUTTONX1" + val)
                    elif key == "InputCoin1":
                        val = transformElement("JOY1_BUTTON10", playersControllers, mapping, mapping_fallback)
                        if val is not None:
                            val = "," + val
                        else:
                            val = ""
                        targetConfig.set(section, key, "MOUSE1_BUTTONX2" + val)
                    elif key == "InputAnalogJoyEvent":
                        val = transformElement("JOY1_BUTTON2", playersControllers, mapping, mapping_fallback)
                        if val is not None:
                            val = "," + val
                        else:
                            val = ""
                        targetConfig.set(section, key, "KEY_S,MOUSE1_MIDDLE_BUTTON" + val)
                    elif len(guns) >= 2:
                        if key == "InputAnalogJoyX2":
                            targetConfig.set(section, key, "MOUSE2_XAXIS_INV")
                        elif key == "InputAnalogJoyY2":
                            targetConfig.set(section, key, "MOUSE2_YAXIS_INV")
                        elif key == "InputGunX2" or key == "InputAnalogGunX2":
                            targetConfig.set(section, key, "MOUSE2_XAXIS")
                        elif key == "InputGunY2" or key == "InputAnalogGunY2":
                            targetConfig.set(section, key, "MOUSE2_YAXIS")
                        elif key == "InputTrigger2" or key == "InputAnalogTriggerLeft2" or key == "InputAnalogJoyTrigger2":
                            targetConfig.set(section, key, "MOUSE2_LEFT_BUTTON")
                        elif key == "InputOffscreen2" or key == "InputAnalogTriggerRight2":
                            targetConfig.set(section, key, "MOUSE2_RIGHT_BUTTON")
                        elif key == "InputStart2":
                            val = transformElement("JOY2_BUTTON9", playersControllers, mapping, mapping_fallback)
                            if val is not None:
                                val += "," + val
                            else:
                                val = ""
                            targetConfig.set(section, key, "MOUSE2_BUTTONX1" + val)
                        elif key == "InputCoin1":
                            val = transformElement("JOY2_BUTTON10", playersControllers, mapping, mapping_fallback)
                            if val is not None:
                                val += "," + val
                            else:
                                val = ""
                            targetConfig.set(section, key,  "MOUSE2_BUTTONX2"+val)
                        elif key == "InputAnalogJoyEvent2":
                            val = transformElement("JOY2_BUTTON2", playersControllers, mapping, mapping_fallback)
                            if val is not None:
                                val += "," + val
                            else:
                                val = ""
                            targetConfig.set(section, key, "MOUSE2_MIDDLE_BUTTON" + val)
                else:
                    if key == "InputSystem":
                        targetConfig.set(section, key, "sdl")

    # Update InputJoy1XSaturation key with the given sensitivity value
    sensitivity = str(int(float(sensitivity)))
    for section in targetConfig.sections():
        if targetConfig.has_option(section, "InputJoy1XSaturation"):
            targetConfig.set(section, "InputJoy1XSaturation", sensitivity)

    # save the ini file
    if not os.path.exists(os.path.dirname(targetFile)):
        os.makedirs(os.path.dirname(targetFile))
    with open(targetFile, 'w') as configfile:
        targetConfig.write(configfile)

def transformValue(value, playersControllers, mapping, mapping_fallback):
    # remove comments
    cleanValue = value
    matches = re.search("^([^;]*[^ ])[ ]*;.*$", value)
    if matches:
        cleanValue = matches.group(1)

    if cleanValue[0] == '"' and cleanValue[-1] == '"':
        newvalue = ""
        for elt in cleanValue[1:-1].split(","):
            newelt = transformElement(elt, playersControllers, mapping, mapping_fallback)
            if newelt is not None:
                if newvalue != "":
                    newvalue = newvalue + ","
                newvalue = newvalue + newelt
        return '"' + newvalue + '"'
    else:
        # integers
        return cleanValue

def transformElement(elt, playersControllers, mapping, mapping_fallback):
    # Docs/README.txt
    # JOY1_LEFT  is the same as JOY1_XAXIS_NEG
    # JOY1_RIGHT is the same as JOY1_XAXIS_POS
    # JOY1_UP    is the same as JOY1_YAXIS_NEG
    # JOY1_DOWN  is the same as JOY1_YAXIS_POS

    matches = re.search("^JOY([12])_BUTTON([0-9]*)$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mapping["button" + matches.group(2)])
    matches = re.search("^JOY([12])_UP$", elt)
    if matches:
        # check joystick type if it's hat or axis 
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_up = "up"
        else:
            key_up = "axisY"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_up, mapping, mapping_fallback)
        print(mp)
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mp, -1)
    matches = re.search("^JOY([12])_DOWN$", elt)
    if matches:
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_down = "down"
        else:
            key_down = "axisY"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_down, mapping, mapping_fallback)
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mp, 1)
    matches = re.search("^JOY([12])_LEFT$", elt)
    if matches:
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_left = "left"
        else:
            key_left = "axisX"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_left, mapping, mapping_fallback)
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mp, -1)
    matches = re.search("^JOY([12])_RIGHT$", elt)
    if matches:
        joy_type = hatOrAxis(playersControllers, matches.group(1))
        if joy_type == "hat":
            key_right = "right"
        else:
            key_right = "axisX"
        mp = getMappingKeyIncludingFallback(playersControllers, matches.group(1), key_right, mapping, mapping_fallback)
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mp, 1)

    matches = re.search("^JOY([12])_(R?[XY])AXIS$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mapping["axis" + matches.group(2)])
    matches = re.search("^JOY([12])_(R?[XYZ])AXIS_NEG$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mapping["axis" + matches.group(2)], -1)
    matches = re.search("^JOY([12])_(R?[XYZ])AXIS_POS$", elt)
    if matches:
        return input2input(playersControllers, matches.group(1), joy2realjoyid(playersControllers, matches.group(1)), mapping["axis" + matches.group(2)], 1)
    if matches:
        return None
    return elt

def getMappingKeyIncludingFallback(playersControllers, padnum, key, mapping, mapping_fallback):
    if padnum in playersControllers:
        if key not in mapping or (key in mapping and mapping[key] not in playersControllers[padnum].inputs):
            if key in mapping_fallback and mapping_fallback[key] in playersControllers[padnum].inputs:
                return mapping_fallback[key]
    return mapping[key]

def joy2realjoyid(playersControllers, joy):
    if joy in playersControllers:
        return playersControllers[joy].index
    return None

def hatOrAxis(playersControllers, player):
    #default to axis
    type = "axis"
    if (player) in playersControllers:
        pad = playersControllers[(player)]
        for button in pad.inputs:
            input = pad.inputs[button]
            if input.type == "hat":
                type = "hat"
            elif input.type == "axis":
                type = "axis"
    return type

def input2input(playersControllers, player, joynum, button, axisside = None):
    if (player) in playersControllers:
        pad = playersControllers[(player)]
        if button in pad.inputs:
            input = pad.inputs[button]
            if input.type == "button":
                return f"JOY{joynum+1}_BUTTON{int(input.id)+1}"
            elif input.type == "hat":
                if input.value == "1":
                    return f"JOY{joynum+1}_UP,JOY{joynum+1}_POV1_UP"
                elif input.value == "2":
                    return f"JOY{joynum+1}_RIGHT,JOY{joynum+1}_POV1_RIGHT"
                elif input.value == "4":
                    return f"JOY{joynum+1}_DOWN,JOY{joynum+1}_POV1_DOWN"
                elif input.value == "8":
                    return f"JOY{joynum+1}_LEFT,JOY{joynum+1}_POV1_LEFT"
            elif input.type == "axis":
                sidestr = ""
                if axisside is not None:
                    if axisside == 1:
                        if input.value == 1:
                            sidestr = "_NEG"
                        else:
                            sidestr = "_POS"
                    else:
                        if input.value == 1:
                            sidestr = "_POS"
                        else:
                            sidestr = "_NEG"

                if button == "joystick1left" or button == "left":
                    return f"JOY{joynum+1}_XAXIS{sidestr}"
                elif button == "joystick1up" or button == "up":
                    return f"JOY{joynum+1}_YAXIS{sidestr}"
                elif button == "joystick2left":
                    return f"JOY{joynum+1}_RXAXIS{sidestr}"
                elif button == "joystick2up":
                    return f"JOY{joynum+1}_RYAXIS{sidestr}"
                elif button == "l2":
                    return f"JOY{joynum+1}_ZAXIS{sidestr}"
                elif button == "r2":
                    return f"JOY{joynum+1}_RZAXIS{sidestr}"

    return None
