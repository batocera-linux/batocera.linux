#!/usr/bin/env python

import subprocess
import json
import re
import os
import evdev
import controllersConfig as controllers

from utils.logger import get_logger
eslog = get_logger(__name__)

class Evmapy():
    # evmapy is a process that map pads to keyboards (for pygame for example)
    __started = False

    @staticmethod
    def start(system, emulator, core, rom, playersControllers, guns):
        if Evmapy.__prepare(system, emulator, core, rom, playersControllers, guns):
            Evmapy.__started = True
            subprocess.call(["batocera-evmapy", "start"])

    @staticmethod
    def stop():
        if Evmapy.__started:
            Evmapy.__started = False
            subprocess.call(["batocera-evmapy", "stop"])

    @staticmethod
    def __buildMergedEvmappy(system, emulator, core, rom, playersControllers, guns):
        # consider files here in this order to get a configuration
        filesToMerge = []
        for keysfile in [
                "{}.keys" .format (rom),
                "{}/padto.keys" .format (rom), # case when the rom is a directory
                #"/userdata/system/configs/evmapy/{}.{}.{}.keys" .format (system, emulator, core),
                #"/userdata/system/configs/evmapy/{}.{}.keys" .format (system, emulator),
                "/userdata/system/configs/evmapy/{}.keys" .format (system),
                "/userdata/system/configs/evmapy/{}.keys" .format (emulator),
                "/userdata/system/configs/evmapy/any.keys",
                #"/usr/share/evmapy/{}.{}.{}.keys" .format (system, emulator, core),
                "/usr/share/evmapy/{}.{}.keys" .format (system, emulator),
                "/usr/share/evmapy/{}.keys" .format (system),
                "/usr/share/evmapy/{}.keys" .format (emulator),
                "/usr/share/evmapy/any.keys",
        ]:
            if os.path.exists(keysfile) and not (os.path.isdir(rom) and keysfile == "{}.keys" .format (rom)): # "{}.keys" .format (rom) is forbidden for directories, it must be inside
                eslog.debug(f"evmapy file to merge : {keysfile}")
                filesToMerge.append(keysfile)

        if len(filesToMerge) == 0:
            return None
        if len(filesToMerge) == 1:
            return filesToMerge[0]

        mergedFile = "/var/run/evmapy_merged.keys"

        mergedValues = {}
        for file in filesToMerge:
            values = json.load(open(file))
            for action in values:
                if action in mergedValues:
                    mergedValues[action].extend(values[action])
                else:
                    mergedValues[action] = values[action]
        with open(mergedFile, "w") as fd:
            fd.write(json.dumps(mergedValues, indent=2))
        
        return mergedFile
            
    @staticmethod
    def __prepare(system, emulator, core, rom, playersControllers, guns):
        keysfile = Evmapy.__buildMergedEvmappy(system, emulator, core, rom, playersControllers, guns)
        if keysfile is not None:
            eslog.debug(f"evmapy on {keysfile}")
            subprocess.call(["batocera-evmapy", "clear"])
    
            padActionConfig = json.load(open(keysfile))

            # configure guns
            ngun = 1
            for gun in guns:
                if "actions_gun"+str(ngun) in padActionConfig:
                    configfile = "/var/run/evmapy/{}.json" .format (os.path.basename(guns[gun]["node"]))
                    eslog.debug("config file for keysfile is {} (from {}) - gun" .format (configfile, keysfile))
                    padConfig = {}
                    padConfig["buttons"] = []
                    padConfig["axes"] = []
                    padConfig["actions"] = []
                    for button in guns[gun]["buttons"]:
                        padConfig["buttons"].append({
                            "name": button,
                            "code": controllers.mouseButtonToCode(button)
                        })
                    padConfig["grab"] = False

                    for action in padActionConfig["actions_gun"+str(ngun)]:
                        if "trigger" in action and "type" in action and "target" in action:
                            guntrigger = Evmapy.__getGunTrigger(action["trigger"], guns[gun])
                            if guntrigger:
                                newaction = action
                                if "description" in newaction:
                                    del newaction["description"]
                                newaction["trigger"] = guntrigger
                                padConfig["actions"].append(newaction)
                    with open(configfile, "w") as fd:
                        fd.write(json.dumps(padConfig, indent=2))
                ngun = ngun+1

            # configure each player
            nplayer = 1
            for playercontroller, pad in sorted(playersControllers.items()):
                if "actions_player"+str(nplayer) in padActionConfig:
                    configfile = "/var/run/evmapy/{}.json" .format (os.path.basename(pad.dev))
                    eslog.debug("config file for keysfile is {} (from {})" .format (configfile, keysfile))
    
                    # create mapping
                    padConfig = {}
                    padConfig["axes"] = []
                    padConfig["buttons"] = []
                    padConfig["grab"] = False
                    absbasex_positive = True
                    absbasey_positive = True
    
                    # define buttons / axes
                    known_buttons_names = {}
                    known_buttons_codes = {}
                    known_buttons_alias = {}
                    known_axes_codes = {}
                    for index in pad.inputs:
                        input = pad.inputs[index]
                        if input.type == "button":
                            # don't add 2 times the same button (ie select as hotkey)
                            if input.code is not None:
                                if input.code not in known_buttons_codes:
                                    known_buttons_names[input.name] = True
                                    known_buttons_codes[input.code] = input.name # keep the master name for aliases
                                    padConfig["buttons"].append({
                                        "name": input.name,
                                        "code": int(input.code)
                                    })
                                else:
                                    known_buttons_alias[input.name] = known_buttons_codes[input.code]
                        elif input.type == "hat":
                            if int(input.value) in [1, 2]: # don't duplicate values
                                if int(input.value) == 1:
                                    name = "X"
                                    isYAsInt = 0
                                else:
                                    name = "Y"
                                    isYAsInt =  1 
                                known_buttons_names["HAT" + input.id + name + ":min"] = True
                                known_buttons_names["HAT" + input.id + name + ":max"] = True
                                padConfig["axes"].append({
                                    "name": "HAT" + input.id + name,
                                    "code": int(input.id) + 16 + isYAsInt, # 16 = HAT0X in linux/input.h
                                    "min": -1,
                                    "max": 1
                                })
                        elif input.type == "axis":
                            if input.code not in known_axes_codes: # avoid duplicated value for axis (bad pad configuration that make evmappy to stop)
                                known_axes_codes[input.code] = True
                                axisId = None
                                axisName = None
                                if input.name == "joystick1up" or input.name == "joystick1left":
                                    axisId = "0"
                                elif input.name == "joystick2up" or input.name == "joystick2left":
                                    axisId = "1"
                                if input.name == "joystick1up" or input.name == "joystick2up":
                                    axisName = "Y"
                                elif input.name == "joystick1left" or input.name == "joystick2left":
                                    axisName = "X"
                                elif input.name == "up" or input.name == "down":
                                    axisId   = "BASE"
                                    axisName = "Y"
                                    if input.name == "up":
                                        absbasey_positive =  int(input.value) >= 0
                                    else:
                                        axisId = None # don't duplicate, configuration should be done for up
                                elif input.name == "left" or input.name == "right":
                                    axisId   = "BASE"
                                    axisName = "X"
                                    if input.name == "left":
                                        absbasex_positive = int(input.value) < 0
                                    else:
                                        axisId = None # don't duplicate, configuration should be done for left
                                else:
                                    axisId   = "_OTHERS_"
                                    axisName = input.name

                                if ((axisId in ["0", "1", "BASE"] and axisName in ["X", "Y"]) or axisId == "_OTHERS_") and input.code is not None:
                                    axisMin, axisMax = Evmapy.__getPadMinMaxAxis(pad.dev, int(input.code))
                                    known_buttons_names["ABS" + axisId + axisName + ":min"] = True
                                    known_buttons_names["ABS" + axisId + axisName + ":max"] = True
                                    known_buttons_names["ABS" + axisId + axisName + ":val"] = True

                                    padConfig["axes"].append({
                                        "name": "ABS" + axisId + axisName,
                                        "code": int(input.code),
                                        "min": axisMin,
                                        "max": axisMax
                                    })

                    # only add actions for which buttons are defined (otherwise, evmapy doesn't like it)
                    padActionsPreDefined = padActionConfig["actions_player"+str(nplayer)]
                    padActionsFiltered = []

                    # handle mouse events : only joystick1 or joystick2 defined for 2 events
                    padActionsDefined = []
                    for action in padActionsPreDefined:
                        if "type" in action and action["type"] == "mouse" and "target" not in action and "trigger" in action:
                            if action["trigger"] == "joystick1":
                                newaction = action.copy()
                                newaction["trigger"] = "joystick1x"
                                newaction["target"] = 'X'
                                padActionsDefined.append(newaction)
                                newaction = action.copy()
                                newaction["trigger"] = "joystick1y"
                                newaction["target"] = 'Y'
                                padActionsDefined.append(newaction)
                            elif action["trigger"] == "joystick2":
                                newaction = action.copy()
                                newaction["trigger"] = "joystick2x"
                                newaction["target"] = 'X'
                                padActionsDefined.append(newaction)
                                newaction = action.copy()
                                newaction["trigger"] = "joystick2y"
                                newaction["target"] = 'Y'
                                padActionsDefined.append(newaction)
                        else:
                            padActionsDefined.append(action)

                    # define actions
                    for action in padActionsDefined:
                        if "trigger" in action:
                            trigger = Evmapy.__trigger_mapper(action["trigger"], known_buttons_alias, known_buttons_names, absbasex_positive, absbasey_positive)
                            if "mode" not in action:
                                mode = Evmapy.__trigger_mapper_mode(action["trigger"])
                                if mode != None:
                                    action["mode"] = mode
                            action["trigger"] = trigger
                            if isinstance(trigger, list):
                                allfound = True
                                for x in trigger:
                                    if x not in known_buttons_names and ("ABS_OTHERS_" + x + ":max") not in known_buttons_names :
                                        allfound = False
                                if allfound:
                                    # rewrite axis buttons
                                    x = 0
                                    for val in trigger:
                                        if "ABS_OTHERS_" + val + ":max" in known_buttons_names:
                                            action["trigger"][x] = "ABS_OTHERS_" + val + ":max"
                                        x = x+1
                                    padActionsFiltered.append(action)
                            else:
                                if trigger in known_buttons_names:
                                    padActionsFiltered.append(action)
                                if "ABS_OTHERS_" + trigger + ":max" in known_buttons_names:
                                    action["trigger"] = "ABS_OTHERS_" + action["trigger"] + ":max"
                                    padActionsFiltered.append(action)
                            padConfig["actions"] = padActionsFiltered

                    # remove comments
                    for action in padConfig["actions"]:
                        if "description" in action:
                            del action["description"]

                    # use full axis for mouse and 50% for keys
                    axis_for_mouse = {}
                    for action in padConfig["actions"]:
                        if "type" in action and action["type"] == "mouse":
                            if isinstance(action["trigger"], list):
                                for x in action["trigger"]:
                                    axis_for_mouse[x] = True
                            else:
                                axis_for_mouse[action["trigger"]] = True

                    for axis in padConfig["axes"]:
                        if axis["name"]+":val" not in axis_for_mouse and axis["name"]+":min" not in axis_for_mouse and axis["name"]+":max" not in axis_for_mouse:
                            min, max = Evmapy.__getPadMinMaxAxisForKeys(axis["min"], axis["max"])
                            axis["min"] = min
                            axis["max"] = max

                    # save config file
                    with open(configfile, "w") as fd:
                        fd.write(json.dumps(padConfig, indent=2))
    
                nplayer += 1
            return True
        # otherwise, preparation did nothing
        eslog.debug("no evmapy config file found for system={}, emulator={}".format(system, emulator))
        return False
    
    # remap evmapy trigger (aka up become HAT0Y:max)
    @staticmethod
    def __trigger_mapper(trigger, known_buttons_alias, known_buttons_names, absbasex_positive, absbasey_positive):
        if isinstance(trigger, list):
            new_trigger = []
            for x in trigger:
                new_trigger.append(Evmapy.__trigger_mapper_string(x, known_buttons_alias, known_buttons_names, absbasex_positive, absbasey_positive))
            return new_trigger
        return Evmapy.__trigger_mapper_string(trigger, known_buttons_alias, known_buttons_names, absbasex_positive, absbasey_positive)

    @staticmethod
    def __trigger_mapper_string(trigger, known_buttons_alias, known_buttons_names, absbasex_positive, absbasey_positive):
        # maybe this function is more complex if a pad has several hat. never see them.
        mapping = {
            "joystick1right": "ABS0X:max",
            "joystick1left": "ABS0X:min",
            "joystick1down": "ABS0Y:max",
            "joystick1up": "ABS0Y:min",
            "joystick2right": "ABS1X:max",
            "joystick2left": "ABS1X:min",
            "joystick2down": "ABS1Y:max",
            "joystick2up": "ABS1Y:min",
            "joystick1x": ["ABS0X:val", "ABS0X:min", "ABS0X:max"],
            "joystick1y": ["ABS0Y:val", "ABS0Y:min", "ABS0Y:max"],
            "joystick2x": ["ABS1X:val", "ABS1X:min", "ABS1X:max"],
            "joystick2y": ["ABS1Y:val", "ABS1Y:min", "ABS1Y:max"]
        }

        if "HAT0X:min" in known_buttons_names:
            mapping["left"]  = "HAT0X:min"
            mapping["right"] = "HAT0X:max"
            mapping["down"]  = "HAT0Y:max"
            mapping["up"]    = "HAT0Y:min"

        if "ABSBASEX:min" in known_buttons_names:
            if absbasex_positive:
                mapping["left"]  = "ABSBASEX:min"
                mapping["right"] = "ABSBASEX:max"
            else:
                mapping["left"]  = "ABSBASEX:max"
                mapping["right"] = "ABSBASEX:min"

        if "ABSBASEX:min" in known_buttons_names:
            if absbasey_positive:
                mapping["down"]  = "ABSBASEY:max"
                mapping["up"]    = "ABSBASEY:min"
            else:
                mapping["down"]  = "ABSBASEY:min"
                mapping["up"]    = "ABSBASEY:max"

        if trigger in known_buttons_alias:
            return known_buttons_alias[trigger]
        if trigger in mapping:
            if isinstance(mapping[trigger], list):
                all_found = True
                for x in mapping[trigger]:
                    if x not in known_buttons_names:
                        all_found = False
                if all_found:
                    return mapping[trigger]
            elif mapping[trigger] in known_buttons_names:
                return mapping[trigger]
        return trigger # no tranformation

    @staticmethod
    def __trigger_mapper_mode(trigger):
        if isinstance(trigger, list):
            new_trigger = []
            for x in trigger:
                mode = Evmapy.__trigger_mapper_mode_string(x)
                if mode != None:
                    return mode
            return None
        return Evmapy.__trigger_mapper_mode_string(trigger)

    @staticmethod
    def __trigger_mapper_mode_string(trigger):
        if trigger in [ "joystick1x", "joystick1y", "joystick2x", "joystick2y"]:
            return "any"
        return None

    @staticmethod
    def __getGunTrigger(trigger, gun):
        if isinstance(trigger, list):
            for button in trigger:
                if button not in gun["buttons"]:
                    return None
            return trigger
        else:
            if trigger not in gun["buttons"]:
                return None
            return trigger

    @staticmethod
    def __getPadMinMaxAxis(devicePath, axisCode):
        device = evdev.InputDevice(devicePath)
        capabilities = device.capabilities(False)

        for event_type in capabilities:
            if event_type == 3: # "EV_ABS"
                for abs_code, val in capabilities[event_type]:
                    if abs_code == axisCode:
                        return val.min, val.max
        return 0,0 # not found

    @staticmethod
    def __getPadMinMaxAxisForKeys(min, max):
        valrange = (max - min)/2 # for each side
        valmin   = min + valrange/2
        valmax   = max - valrange/2
        return valmin, valmax
