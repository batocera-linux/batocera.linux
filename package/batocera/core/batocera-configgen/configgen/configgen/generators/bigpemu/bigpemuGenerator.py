#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import sys
import json
import utils.videoMode as videoMode
import controllersConfig
import math
from utils.logger import get_logger

eslog = get_logger(__name__)

bigPemuConfig = "/userdata/system/.bigpemu_userdata/BigPEmuConfig.bigpcfg"

# BigPEmu controller sequence, P1 only requires keyboard inputs
# default standard bindings
P1_BINDINGS_SEQUENCE = {
    "C": {"button": "y", "keyboard": "4"},
    "B": {"button": "b", "keyboard": "22"},
    "A": {"button": "a", "keyboard": "7"},
    "Pause": {"button": "select", "keyboard": "20"},
    "Option": {"button": "start", "keyboard": "26"},    
    "Pad-Up": {"button": "up", "keyboard": "82"},
    "Pad-Down": {"button": "down", "keyboard": "81"},
    "Pad-Left": {"button": "left", "keyboard": "80"},
    "Pad-Right": {"button": "right", "keyboard": "79"},
    "Numpad-0": {"buttons": ["r3", "l2"], "keyboard": "39"},
    "Numpad-1": {"buttons": ["y", "l2"], "keyboard": "30"},
    "Numpad-2": {"buttons": ["x", "l2"], "keyboard": "31"},
    "Numpad-3": {"buttons": ["a", "l2"], "keyboard": "32"},
    "Numpad-4": {"button": "pageup", "keyboard": "33"},
    "Numpad-5": {"button": "x", "keyboard": "34"},
    "Numpad-6": {"button": "pagedown", "keyboard": "35"},
    "Numpad-7": {"buttons": ["pageup", "l2"], "keyboard": "36"},
    "Numpad-8": {"buttons": ["b", "l2"], "keyboard": "37"},
    "Numpad-9": {"buttons": ["pagedown", "l2"], "keyboard": "38"},
    "Asterick": {"button": "l3", "keyboard": "18"},
    "Pound": {"button": "r3", "keyboard": "19"},
    "Analog-0-left": {"button": "joystick1left"},
    #"Analog-0-right": {"button": "joystick1right"},
    "Analog-0-up": {"button": "joystick1up"},
    #"Analog-0-down": {"button": "joystick1down"},
    "Analog-1-left": {"button": "joystick2left"},
    #"Analog-1-right": {"button": "joystick2right"},
    "Analog-1-up": {"button": "joystick2up"},
    #"Analog-1-down": {"button": "joystick2down"},
    "Extra-Up": {"blank": None},
    "Extra-Down": {"blank": None},
    "Extra-Left": {"blank": None},
    "Extra-Right": {"blank": None},
    "Extra-A": {"blank": None},
    "Extra-B": {"blank": None},
    "Extra-C": {"blank": None},
    "Extra-D": {"blank": None},
    "Menu": {"buttons": ["start", "r2"], "keyboard": "41"},
    "Fast Forward": {"buttons": ["x", "r2"], "keyboard": "59"},
    "Rewind": {"blank": None},
    "Save State": {"blank": None},
    "Load State": {"blank": None},
    "Screenshot": {"blank": None},
    "Overlay": {"buttons": ["l3", "r2"]},
    "Chat": {"keyboard": "23"},
    "Blank1": {"blank": None},
    "Blank2": {"blank": None},
    "Blank3": {"blank": None},
    "Blank4": {"blank": None},
    "Blank5": {"blank": None}
}

# BigPEmu controller sequence, P2+ 
# default standard bindings
P2_BINDINGS_SEQUENCE = {
    "C": {"button": "y"},
    "B": {"button": "b"},
    "A": {"button": "a"},
    "Pause": {"button": "select"},
    "Option": {"button": "start"},    
    "Pad-Up": {"button": "up"},
    "Pad-Down": {"button": "down"},
    "Pad-Left": {"button": "left"},
    "Pad-Right": {"button": "right"},
    "Numpad-0": {"buttons": ["r3", "l2"]},
    "Numpad-1": {"buttons": ["y", "l2"]},
    "Numpad-2": {"buttons": ["x", "l2"]},
    "Numpad-3": {"buttons": ["a", "l2"]},
    "Numpad-4": {"button": "pageup"},
    "Numpad-5": {"button": "x"},
    "Numpad-6": {"button": "pagedown"},
    "Numpad-7": {"buttons": ["pageup", "l2"]},
    "Numpad-8": {"buttons": ["b", "l2"]},
    "Numpad-9": {"buttons": ["pagedown", "l2"]},
    "Asterick": {"button": "l3"},
    "Pound": {"button": "r3"},
    "Analog-0-left": {"button": "joystick1left"},
    #"Analog-0-right": {"button": "joystick1right"},
    "Analog-0-up": {"button": "joystick1up"},
    #"Analog-0-down": {"button": "joystick1down"},
    "Analog-1-left": {"button": "joystick2left"},
    #"Analog-1-right": {"button": "joystick2right"},
    "Analog-1-up": {"button": "joystick2up"},
    #"Analog-1-down": {"button": "joystick2down"},
    "Extra-Up": {"blank": None},
    "Extra-Down": {"blank": None},
    "Extra-Left": {"blank": None},
    "Extra-Right": {"blank": None},
    "Extra-A": {"blank": None},
    "Extra-B": {"blank": None},
    "Extra-C": {"blank": None},
    "Extra-D": {"blank": None}
}

def generate_keyb_button_bindings(device_id, keyb_id, button_id, button_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": True,
                "B_ID": int(keyb_id),
                "B_AH": 0.0
            },
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_button_bindings(device_id, button_id, button_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_keyb_combo_bindings(device_id, keyb_id, button_id, button_value, analog_id, analog_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": True,
                "B_ID": int(keyb_id),
                "B_AH": 0.0
            },
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id,
                "M_KB": False,
                "M_ID": int(analog_id),
                "M_AH": float(analog_value),
                "M_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_combo_bindings(device_id, button_id, button_value, analog_id, analog_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id,
                "M_KB": False,
                "M_ID": int(analog_id),
                "M_AH": float(analog_value),
                "M_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_blank_bindings():
    bindings = []
    binding = {
        "Triggers": []
    }
    bindings.append(binding)
    return bindings

def generate_keyb_bindings(keyb_id):
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": True,
                "B_ID": int(keyb_id),
                "B_AH": 0.0
            }
        ]
    }
    bindings.append(binding)
    return bindings

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        directory = os.path.dirname(bigPemuConfig)
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Delete the config file to update controllers
        # As it doesn't like to be updated
        # ¯\_(ツ)_/¯
        if os.path.exists(bigPemuConfig):
            os.remove(bigPemuConfig)
        
        # Create the config file as it doesn't exist
        if not os.path.exists(bigPemuConfig):
            with open(bigPemuConfig, "w") as file:
                json.dump({}, file)
        
        # Load or initialize the configuration
        with open(bigPemuConfig, "r") as file:
            try:
                config = json.load(file)
            except json.decoder.JSONDecodeError:
                config = {}
        
        # Ensure the necessary structure in the config
        if "BigPEmuConfig" not in config:
            config["BigPEmuConfig"] = {}
        if "Video" not in config["BigPEmuConfig"]:
            config["BigPEmuConfig"]["Video"] = {}
        
        # Adjust basic settings
        config["BigPEmuConfig"]["Video"]["DisplayMode"] = 2
        config["BigPEmuConfig"]["Video"]["ScreenScaling"] = 5
        config["BigPEmuConfig"]["Video"]["DisplayWidth"] = gameResolution["width"]
        config["BigPEmuConfig"]["Video"]["DisplayHeight"] = gameResolution["height"]
        config["BigPEmuConfig"]["Video"]["DisplayFrequency"] = int(round(float(videoMode.getRefreshRate())))
        
        # User selections
        if system.isOptSet("bigpemu_vsync"):
            config["BigPEmuConfig"]["Video"]["VSync"] = system.config["bigpemu_vsync"]
        else:
            config["BigPEmuConfig"]["Video"]["VSync"] = 1
        if system.isOptSet("bigpemu_ratio"):
            config["BigPEmuConfig"]["Video"]["ScreenAspect"] = int(system.config["bigpemu_ratio"])
        else:
            config["BigPEmuConfig"]["Video"]["ScreenAspect"] = 2
        config["BigPEmuConfig"]["Video"]["LockAspect"] = 1
               
        # Controller config
        if "Input" not in config["BigPEmuConfig"]:
            config["BigPEmuConfig"]["Input"] = {}
        
        # initial settings
        config["BigPEmuConfig"]["Input"]["DeviceCount"] = len(playersControllers)
        config["BigPEmuConfig"]["Input"]["AnalDeadMice"] = 0.25
        config["BigPEmuConfig"]["Input"]["AnalToDigi"] = 0.25
        config["BigPEmuConfig"]["Input"]["AnalExpo"] = 0.0
        config["BigPEmuConfig"]["Input"]["ConflictingPad"] = 0
        config["BigPEmuConfig"]["Input"]["XboxAnus"] = 0
        config["BigPEmuConfig"]["Input"]["OLAnchor"] = 3
        config["BigPEmuConfig"]["Input"]["OLScale"] = 0.75
        config["BigPEmuConfig"]["Input"]["MouseInput"] = 0
        config["BigPEmuConfig"]["Input"]["MouseSens"] = 1.0
        config["BigPEmuConfig"]["Input"]["MouseThresh"] = 0.5

        # per controller settings (standard controller only currently)
        nplayer = 0
        for controller, pad in sorted(playersControllers.items()):
            if nplayer <= 7:
                if "Device{}".format(nplayer) not in config["BigPEmuConfig"]["Input"]:
                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)] = {}
                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["DeviceType"] = 0 # standard controller
                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["InvertAnally"] = 0
                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["RotaryScale"] = 0.5
                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["HeadTrackerScale"] = 8.0
                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["HeadTrackerSpring"] = 0
                    if "Bindings" not in config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]:
                        config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["Bindings"] = []
                    
                    # Loop through BINDINGS_SEQUENCE to maintain the specific order of bindings
                    if nplayer == 0:
                        BINDINGS_SEQUENCE = P1_BINDINGS_SEQUENCE
                    else:
                        BINDINGS_SEQUENCE = P2_BINDINGS_SEQUENCE
                    
                    for binding_key, binding_info in BINDINGS_SEQUENCE.items():
                        #eslog.debug(f"Binding sequence input: {binding_key}")
                        if "button" in binding_info:
                            if "keyboard" in binding_info:
                                generate_func = generate_keyb_button_bindings
                            else:
                                generate_func = generate_button_bindings
                        elif "buttons" in binding_info:
                            if "keyboard" in binding_info:
                                generate_func = generate_keyb_combo_bindings
                            else:
                                generate_func = generate_combo_bindings
                        else:
                            if "keyboard" in binding_info:
                                generate_func = generate_keyb_bindings
                            else:
                                generate_func = generate_blank_bindings

                        if "blank" not in binding_info and generate_func != generate_keyb_bindings:
                            for x in pad.inputs:
                                input = pad.inputs[x]
                                # workaround values for SDL2
                                if input.type == "button":
                                    input.value = 0
                                if input.type == "hat":
                                    input.id = 134
                                if input.name == "joystick1left":
                                    input.id = 128
                                if input.name == "joystick1up":
                                    input.id = 129
                                if input.name == "joystick2left":
                                    input.id = 131
                                if input.name == "joystick2up":
                                    input.id = 132
                                
                                # Generate the bindings if input name matches the button in sequence
                                if input.name == binding_info.get("button") or input.name in binding_info.get("buttons", []):
                                    # Handle combo bindings
                                    if "buttons" in binding_info:
                                        button_combos = binding_info["buttons"]
                                        button_bindings = []
                                        for button_name in button_combos:
                                            for y in pad.inputs:
                                                button_input = pad.inputs[y]
                                                # workaround values here too
                                                if button_input.type == "button":
                                                    button_input.value = 0
                                                if button_input.name == "l2":
                                                    button_input.id = 130
                                                if button_input.name == "r2":
                                                    button_input.id = 133
                                                if button_input.name == button_name:
                                                    button_bindings.extend([button_input.id, button_input.value])
                                        if len(button_bindings) == len(button_combos) * 2:
                                            if "keyboard" in binding_info:
                                                bindings = generate_func(pad.guid, binding_info["keyboard"], *button_bindings)
                                            else:
                                                bindings = generate_func(pad.guid, *button_bindings)
                                    # Handle single button bindings
                                    elif "button" in binding_info:
                                        if input.name.startswith("joystick1") or input.name.startswith("joystick2"):
                                            # For joysticks, generate two bindings with positive and then negative values
                                            if "keyboard" in binding_info:
                                                bindings = generate_func(pad.guid, binding_info["keyboard"], input.id, input.value)
                                                bindings.extend(generate_func(pad.guid, binding_info["keyboard"], input.id, -float(input.value)))
                                            else:
                                                bindings = generate_func(pad.guid, input.id, input.value)
                                                bindings.extend(generate_func(pad.guid, input.id, -float(input.value)))
                                        else:
                                            if "keyboard" in binding_info:
                                                bindings = generate_func(pad.guid, binding_info["keyboard"], input.id, input.value)
                                            else:
                                                bindings = generate_func(pad.guid, input.id, input.value)
                                    config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["Bindings"].extend(bindings)
                                    break
                        else:
                            if generate_func == generate_keyb_bindings:
                                bindings = generate_func(binding_info["keyboard"])
                                config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["Bindings"].extend(bindings)
                            else:
                                bindings = generate_func()
                                config["BigPEmuConfig"]["Input"]["Device{}".format(nplayer)]["Bindings"].extend(bindings)
            
            # Onto the next controller as necessary
            nplayer += 1
        
        # Close off input
        config["BigPEmuConfig"]["Input"]["InputVer"] = 2
        config["BigPEmuConfig"]["Input"]["InputPluginVer"] = 666
        
        with open(bigPemuConfig, "w") as file:
            json.dump(config, file, indent=4)
        
        # Run the emulator
        commandArray = ["/usr/bigpemu/bigpemu", rom]

        environment = {
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
        }
        
        return Command.Command(array=commandArray, env=environment)

    def getInGameRatio(self, config, gameResolution, rom):
        if "bigpemu_ratio" in config:
            if config['bigpemu_ratio'] == "8":
                return 16/9
            else:
                return 4/3
        else:
            return 4/3
