#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
import os
import configparser
import io
import re
from shutil import copyfile

class SupermodelGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        commandArray = ["supermodel", "-fullscreen", "-channels=2"]
        
        # legacy3d
        if system.isOptSet("engine3D") and system.config["engine3D"] == "new3d":
            commandArray.append("-new3d")
        else:
             commandArray.extend(["-multi-texture", "-legacy-scsp", "-legacy3d"])
        
        # widescreen
        if system.isOptSet("wideScreen") and system.getOptBoolean("wideScreen"):
            commandArray.append("-wide-screen")
            commandArray.append("-wide-bg")

        # quad rendering
        if system.isOptSet("quadRendering") and system.getOptBoolean("quadRendering"):
            commandArray.append("-quad-rendering")

        # crosshairs
        if system.isOptSet("crosshairs"):
            commandArray.append("-crosshairs={}".format(system.config["crosshairs"]))

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

        # resolution
        commandArray.append("-res={},{}".format(gameResolution["width"], gameResolution["height"]))

        # logs
        commandArray.extend(["-log-output=/userdata/system/logs/Supermodel.log", rom])

        # copy nvram files
        copy_nvram_files()

        # config
        configPadsIni(playersControllers, drivingGame)

        return Command.Command(array=commandArray, env={"SDL_VIDEODRIVER":"x11"})

def copy_nvram_files():
    sourceDir = "/usr/share/supermodel/NVRAM"
    targetDir = "/userdata/saves/supermodel/NVRAM"
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    # create nv files which are in source and not in target
    for file in os.listdir(sourceDir):
        extension = os.path.splitext(file)[1][1:]
        if extension == "nv":
            if not os.path.exists(targetDir + "/" + file):
                copyfile(sourceDir + "/" + file, targetDir + "/" + file)

def configPadsIni(playersControllers, altControl):
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
