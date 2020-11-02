#!/usr/bin/env python

import subprocess
import json
import re
import os
from utils.logger import eslog
import evdev

class Evmapy():
    # evmapy is a process that map pads to keyboards (for pygame for example)
    __started = False

    @staticmethod
    def start(system, emulator, core, rom, playersControllers):
	if Evmapy.__prepare(system, emulator, core, rom, playersControllers):
            Evmapy.__started = True
	    subprocess.call(["batocera-evmapy", "start"])

    @staticmethod
    def stop():
        if Evmapy.__started:
            Evmapy.__started = False
	    subprocess.call(["batocera-evmapy", "stop"])

    @staticmethod
    def __prepare(system, emulator, core, rom, playersControllers):
        # consider files here in this order to get a configuration
        for keysfile in [
                "{}.keys" .format (rom),
                "{}/padto.keys" .format (rom), # case when the rom is a directory
                #"/userdata/system/configs/evmapy/{}.{}.{}.keys" .format (system, emulator, core),
                #"/userdata/system/configs/evmapy/{}.{}.keys" .format (system, emulator),
                "/userdata/system/configs/evmapy/{}.keys" .format (system),
                #"/usr/share/evmapy/{}.{}.{}.keys" .format (system, emulator, core),
                #"/usr/share/evmapy/{}.{}.keys" .format (system, emulator),
                "/usr/share/evmapy/{}.keys" .format (system)
        ]:
            if os.path.exists(keysfile) and not (os.path.isdir(rom) and keysfile == "{}.keys" .format (rom)): # "{}.keys" .format (rom) is forbidden for directories, it must be inside
                eslog.log("evmapy on {}".format(keysfile))
                subprocess.call(["batocera-evmapy", "clear"])
    
                padActionConfig = json.load(open(keysfile))
    
                # configure each player
                nplayer = 1
                for playercontroller, pad in sorted(playersControllers.items()):
                    if "actions_player"+str(nplayer) in padActionConfig:
                        configfile = "/var/run/evmapy/{}.json" .format (re.sub(r'[^\w]', '.', pad.realName))
                        eslog.log("config file for keysfile is {} (from {})" .format (configfile, keysfile))
    
                        # create mapping
                        padConfig = {}
                        padConfig["axes"] = []
                        padConfig["buttons"] = []
                        padConfig["grab"] = False
    
                        # define buttons / axes
                        known_buttons_names = {}
                        known_buttons_codes = {}
                        known_buttons_alias = {}
                        for index in pad.inputs:
                            input = pad.inputs[index]
                            if input.type == "button":
                                # don't add 2 times the same button (ie select as hotkey)
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
                                axisId = 0
                                axisName = ""
                                if input.name == "joystick1up" or input.name == "joystick1left":
                                    axisId = 0
                                elif input.name == "joystick2up" or input.name == "joystick2left":
                                    axisId = 1
                                if input.name == "joystick1up" or input.name == "joystick2up":
                                    axisName = "Y"
                                elif input.name == "joystick1left" or input.name == "joystick2left":
                                    axisName = "X"
                                axisMin, axisMax = Evmapy.__getPadMinMaxAxis(pad.dev, int(input.code))
                                known_buttons_names["ABS" + str(axisId) + axisName + ":min"] = True
                                known_buttons_names["ABS" + str(axisId) + axisName + ":max"] = True
                                known_buttons_names["ABS" + str(axisId) + axisName + ":val"] = True
                                padConfig["axes"].append({
                                    "name": "ABS" + str(axisId) + axisName,
                                    "code": int(input.code),
                                    "min": axisMin,
                                    "max": axisMax
                                })

                        # only add actions for which buttons are defined (otherwise, evmapy doesn't like it)
                        padActionsDefined = padActionConfig["actions_player"+str(nplayer)]
                        padActionsFiltered = []
                        for action in padActionsDefined:
                            if "trigger" in action:
                                trigger = Evmapy.__trigger_mapper(action["trigger"], known_buttons_alias, known_buttons_names)
                                if "mode" not in action:
                                    mode = Evmapy.__trigger_mapper_mode(action["trigger"])
                                    if mode != None:
                                        action["mode"] = mode
                                action["trigger"] = trigger
                                if isinstance(trigger, list):
                                    allfound = True
                                    for x in trigger:
                                        if x not in known_buttons_names:
                                            allfound = False
                                    if allfound:
                                        padActionsFiltered.append(action)
                                else:
                                    if trigger in known_buttons_names:
                                        padActionsFiltered.append(action)
                                padConfig["actions"] = padActionsFiltered
    
                        # save config file
                        with open(configfile, "w") as fd:
                            fd.write(json.dumps(padConfig, indent=4))
    
                    nplayer += 1
                return True
        # otherwise, preparation did nothing
        return False
    
    # remap evmapy trigger (aka up become HAT0Y:max)
    @staticmethod
    def __trigger_mapper(trigger, known_buttons_alias, known_buttons_names):
        if isinstance(trigger, list):
            new_trigger = []
            for x in trigger:
                new_trigger.append(Evmapy.__trigger_mapper_string(x, known_buttons_alias, known_buttons_names))
            return new_trigger
        return Evmapy.__trigger_mapper_string(trigger, known_buttons_alias, known_buttons_names)

    @staticmethod
    def __trigger_mapper_string(trigger, known_buttons_alias, known_buttons_names):
        # maybe this function is more complex if a pad has several hat. never see them.
        mapping = {
            "left": "HAT0X:min",
            "right": "HAT0X:max",
            "down": "HAT0Y:max",
            "up": "HAT0Y:min",
            "joystick1right": "ABS0X:max",
            "joystick1left": "ABS0X:min",
            "joystick1down": "ABS0Y:max",
            "joystick1up": "ABS0Y:min",
            "joystick2right": "ABS1X:max",
            "joystick2left": "ABS1X:min",
            "joystick2down": "ABS1Y:max",
            "joystick2up": "ABS1Y:min",
            "joystick1x": ["ABS1X:val", "ABS1X:min", "ABS1X:max"],
            "joystick1y": ["ABS1Y:val", "ABS1Y:min", "ABS1Y:max"],
            "joystick2x": ["ABS2X:val", "ABS2X:min", "ABS2X:max"],
            "joystick2y": ["ABS2Y:val", "ABS2Y:min", "ABS2Y:max"]
        }
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
    def __getPadMinMaxAxis(devicePath, axisCode):
        device = evdev.InputDevice(devicePath)
        capabilities = device.capabilities(False)

        for event_type in capabilities:
            if event_type == 3: # "EV_ABS"
                for abs_code, val in capabilities[event_type]:
                    if abs_code == axisCode:
                        valrange = (val.max - val.min)/2 # for each side
                        valmin   = val.min + valrange/2
                        valmax   = val.max - valrange/2
                        return valmin, valmax
        return 0,0 # not found
