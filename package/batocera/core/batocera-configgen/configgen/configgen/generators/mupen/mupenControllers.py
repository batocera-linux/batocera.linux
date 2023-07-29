#!/usr/bin/env python

import os
import configparser
from controllersConfig import Input
from xml.dom import minidom

import batoceraFiles

# Must read :
# http://mupen64plus.org/wiki/index.php?title=Mupen64Plus_Plugin_Parameters

# Mupen doesn't like to have 2 buttons mapped for N64 pad entry. That's why r2 is commented for now. 1 axis and 1 button is ok
mupenHatToAxis        = {'1': 'Up',   '2': 'Right', '4': 'Down', '8': 'Left'}
mupenHatToReverseAxis = {'1': 'Down', '2': 'Left',  '4': 'Up',   '8': 'Right'}
mupenDoubleAxis = {0:'X Axis', 1:'Y Axis'}

def getMupenMapping(use_n64_inputs):
    # load system values and override by user values in case some user values are missing
    map = dict()
    for file in [batoceraFiles.mupenMappingSystem, batoceraFiles.mupenMappingUser]:
        if os.path.exists(file):
            dom = minidom.parse(file)
            list_name = 'n64InputList' if use_n64_inputs else 'defaultInputList'
            for inputs in dom.getElementsByTagName(list_name):
                for input in inputs.childNodes:
                    if input.attributes:
                        if input.attributes['name']:
                            if input.attributes['value']:
                                map[input.attributes['name'].value] = input.attributes['value'].value
    return map

def setControllersConfig(iniConfig, controllers, system):
    nplayer = 1
    for playercontroller, pad in sorted(controllers.items()):
        # Dynamic controller bindings
        config = defineControllerKeys(nplayer, pad, system)
        fillIniPlayer(nplayer, iniConfig, pad, config)
        nplayer += 1

    # remove section with no player
    for x in range(nplayer, 4):
        section = "Input-SDL-Control"+str(x)
        if iniConfig.has_section(section):
            cleanPlayer(nplayer, iniConfig)
         
def getPeakandDeadzoneValues(start_value, config_value, system, default_multiplier):
    number = int(start_value.split(',')[0])
    if config_value in system.config:
        percentage = float(system.config[config_value]) / 100
        result = int(round(number * percentage))
    else:
        result = int(round(number * default_multiplier))
    return f"{result},{result}"
         
def defineControllerKeys(nplayer, controller, system):
        if f"mupen64-controller{nplayer}" in system.config and system.config[f"mupen64-controller{nplayer}"] != "retropad":
            mupenmapping = getMupenMapping(True)
        else:    
            mupenmapping = getMupenMapping(False)

        # config holds the final pad configuration in the mupen style
        # ex: config['DPad U'] = "button(1)"
        config = dict()

        # determine joystick deadzone and peak       
        config['AnalogPeak'] = getPeakandDeadzoneValues(mupenmapping['AnalogPeak'], f"mupen64-sensitivity{nplayer}", system, 1)
        config['AnalogDeadzone'] = getPeakandDeadzoneValues(mupenmapping['AnalogPeak'], f"mupen64-deadzone{nplayer}", system, 0.05)
        
        # z is important, in case l2 is not available for this pad, use l1
        # assume that l2 is for "Z Trig" in the mapping
        if 'l2' not in controller.inputs:
            mupenmapping['pageup'] = mupenmapping['l2']

        # if joystick1up is not available, use up/left while these keys are more used
        if 'joystick1up' not in controller.inputs:
            mupenmapping['up']    = mupenmapping['joystick1up']
            mupenmapping['down']  = mupenmapping['joystick1down']
            mupenmapping['left']  = mupenmapping['joystick1left']
            mupenmapping['right'] = mupenmapping['joystick1right']

        # the input.xml adds 2 directions per joystick, ES handles just 1
        fakeSticks = { 'joystick2up' : 'joystick2down', 'joystick2left' : 'joystick2right'}
        # Cheat on the controller
        for realStick, fakeStick in fakeSticks.items():
                if realStick in controller.inputs:
                    if controller.inputs[realStick].type == "axis":
                        print(fakeStick + "-> " + realStick)
                        inputVar =  Input(fakeStick
                                        , controller.inputs[realStick].type
                                        , controller.inputs[realStick].id
                                        , str(-int(controller.inputs[realStick].value))
                                        , controller.inputs[realStick].code)
                        controller.inputs[fakeStick] = inputVar

        for inputIdx in controller.inputs:
                input = controller.inputs[inputIdx]
                if input.name in mupenmapping and mupenmapping[input.name] != "":
                        value=setControllerLine(mupenmapping, input, mupenmapping[input.name], controller.inputs)
                        # Handle multiple inputs for a single N64 Pad input
                        if value != "":
                            if mupenmapping[input.name] not in config :
                                config[mupenmapping[input.name]] = value
                            else:
                                config[mupenmapping[input.name]] += " " + value
        return config

def setControllerLine(mupenmapping, input, mupenSettingName, allinputs):
        value = ''
        inputType = input.type
        if inputType == 'button':
            if mupenSettingName in ["X Axis", "Y Axis"]: # special case for these 2 axis...
                # hum, a button is mapped on an axis, find the reverse button
                if input.name == "up":
                    if "down" in allinputs:
                        reverseInput = allinputs["down"]
                        value = f"button({input.id}, {reverseInput.id})"
                    else:
                        value = f"button({input.id})"
                elif input.name == "left":
                    if "right" in allinputs:
                        reverseInput = allinputs["right"]
                        value = f"button({input.id}, {reverseInput.id})"
                    else:
                        value = f"button({input.id})"
                else:
                    return "" # skip down and right
            else:
                # normal button
                value = f"button({input.id})"
        elif inputType == 'hat':
                if mupenSettingName in ["X Axis", "Y Axis"]: # special case for these 2 axis...
                    if input.value == "1" or input.value == "8": # only for the lower value to avoid duplicate
                        value = f"hat({input.id} {mupenHatToAxis[input.value]} {mupenHatToReverseAxis[input.value]})"
                else:
                    value = f"hat({input.id} {mupenHatToAxis[input.value]})"
        elif inputType == 'axis':
                # Generic case for joystick1up and joystick1left
                if mupenSettingName in mupenDoubleAxis.values():
                        # X axis : value = -1 for left, +1 for right
                        # Y axis : value = -1 for up, +1 for down
                        # we configure only left and down to not configure 2 times each axis
                        if input.name in [ "left", "up", "joystick1left", "joystick1up", "joystick2left", "joystick2up" ]:
                            if input.value == "-1":
                                value = f"axis({input.id}-,{input.id}+)"
                            else:
                                value = f"axis({input.id}+,{input.id}-)"
                else:
                        if input.value == "1":
                                value = f"axis({input.id}+)"
                        else:
                                value = f"axis({input.id}-)"
        return value

def fillIniPlayer(nplayer, iniConfig, controller, config):
        section = "Input-SDL-Control"+str(nplayer)

        # set static config
        if not iniConfig.has_section(section):
            iniConfig.add_section(section)
        iniConfig.set(section, 'Version', '2')
        iniConfig.set(section, 'mode', '0')
        iniConfig.set(section, 'device', str(controller.index))
        # TODO: python 3 remove hack to overcome ConfigParser limitation with utf8 in python 2.7
        name_encode = controller.realName.encode("ascii", "ignore")
        iniConfig.set(section, 'name', str(name_encode))
        iniConfig.set(section, 'plugged', "True")
        iniConfig.set(section, 'plugin', '2')
        iniConfig.set(section, 'AnalogDeadzone', str(config['AnalogDeadzone']))
        iniConfig.set(section, 'AnalogPeak', str(config['AnalogPeak']))
        iniConfig.set(section, 'mouse', "False")

        # set dynamic config - clear all keys then fill
        iniConfig.set(section, "Mempak switch", "")
        iniConfig.set(section, "Rumblepak switch", "")
        iniConfig.set(section, "C Button R", "")
        iniConfig.set(section, "A Button", "")
        iniConfig.set(section, "C Button U", "")
        iniConfig.set(section, "B Button", "")
        iniConfig.set(section, "Start", "")
        iniConfig.set(section, "L Trig", "")
        iniConfig.set(section, "R Trig", "")
        iniConfig.set(section, "Z Trig", "")
        iniConfig.set(section, "DPad U", "")
        iniConfig.set(section, "DPad D", "")
        iniConfig.set(section, "DPad R", "")
        iniConfig.set(section, "DPad L", "")
        iniConfig.set(section, "Y Axis", "")
        iniConfig.set(section, "Y Axis", "")
        iniConfig.set(section, "X Axis", "")
        iniConfig.set(section, "X Axis", "")
        iniConfig.set(section, "C Button U", "")
        iniConfig.set(section, "C Button D", "")
        iniConfig.set(section, "C Button L", "")
        iniConfig.set(section, "C Button R", "")
        for inputName in sorted(config):
                iniConfig.set(section, inputName, config[inputName])

def cleanPlayer(nplayer, iniConfig):
        section = "Input-SDL-Control"+str(nplayer)

        # set static config
        if not iniConfig.has_section(section):
            iniConfig.add_section(section)
        iniConfig.set(section, 'Version', '2')
        iniConfig.set(section, 'plugged', "False")

