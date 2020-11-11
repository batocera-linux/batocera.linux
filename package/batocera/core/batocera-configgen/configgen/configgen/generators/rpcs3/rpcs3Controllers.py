import os
import batoceraFiles
from os import path
import codecs
from utils.logger import eslog

def generateControllerConfig(system, controllers, rom):
    generateConfigInputYml(controllers)
    generateInputConfigs(controllers)

def generateConfigInputYml(controllers):
    configFileName = "{}/{}".format(batoceraFiles.CONF, "rpcs3/config_input.yml")
    if not path.isdir(batoceraFiles.CONF + "/rpcs3"):
        os.makedirs(batoceraFiles.CONF + "/rpcs3")
    f = codecs.open(configFileName, "w", encoding="utf_8_sig")

    nplayer = 1
    for controller, pad in sorted(controllers.items()):
        if nplayer <= 7:
            f.write("Player {} Input:\n".format(nplayer))
            f.write("  Handler: Evdev\n")
            f.write("  Device: {}\n".format(pad.realName))
            f.write("  Profile: pad{}\n".format(nplayer))
        nplayer += 1
    for i in range(nplayer, 8):
        f.write("Player {} Input:\n".format(i))
        f.write("  Handler: \"Null\"\n")
        f.write("  Device: \"Null\"\n")
        f.write("  Profile: Default Profile\n")
    f.close()

def generateInputConfigs(controllers):
    if not path.isdir(batoceraFiles.CONF + "/rpcs3/InputConfigs/Evdev"):
        os.makedirs(batoceraFiles.CONF + "/rpcs3/InputConfigs/Evdev")
    nplayer = 1
    for controller, pad in sorted(controllers.items()):
        if nplayer <= 7:
            configFileName = "{}/{}/pad{}.yml".format(batoceraFiles.CONF, "rpcs3/InputConfigs/Evdev", nplayer)
            f = codecs.open(configFileName, "w", encoding="utf_8_sig")
            for inputIdx in pad.inputs:
                input = pad.inputs[inputIdx]
                key = rpcs3_mappingKey(input.name)
                if key is not None:
                    f.write("{}: {}\n".format(key, rpcs3_mappingValue(input.name, input.type, input.code, int(input.value))))
                else:
                    eslog.log("no rpcs3 mapping found for {}".format(input.name))

                # write the reverse
                if input.name == "joystick1up" or input.name == "joystick1left" or input.name == "joystick2up" or input.name == "joystick2left":
                    reversedName = rpcs3_reverseMapping(input.name)
                    key = rpcs3_mappingKey(reversedName)
                    if key is not None:
                        f.write("{}: {}\n".format(key, rpcs3_mappingValue(reversedName, input.type, input.code, int(input.value)*-1)))
                    else:
                        eslog.log("no rpcs3 mapping found for {}".format(input.name))
                    
            rpcs3_otherKeys(f, controller)
            f.close()
        nplayer += 1

def rpcs3_reverseMapping(name):
    if name == "joystick1up":
        return "joystick1down"
    if name == "joystick1left":
        return "joystick1right"
    if name == "joystick2up":
        return "joystick2down"
    if name == "joystick2left":
        return "joystick2right"

def rpcs3_mappingKey(input):
    keys = {
        "start":          "Start",
        "select":         "Select",
        "hotkey":         "PS Button",
        "y":              "Square",
        "b":              "Cross",
        "a":              "Circle",
        "x":              "Triangle",
        "left":           "Left",
        "down":           "Down",
        "right":          "Right",
        "up":             "Up",
        "pageup":         "R1",
        "r2":             "R2",
        "r3":             "R3",
        "pagedown":       "L1",
        "l2":             "L2",
        "l3":             "L3",
        "joystick1left":  "Left Stick Left",
        "joystick1down":  "Left Stick Down",
        "joystick1right": "Left Stick Right",
        "joystick1up":    "Left Stick Up",
        "joystick2left":  "Right Stick Left",
        "joystick2down":  "Right Stick Down",
        "joystick2right": "Right Stick Right",
        "joystick2up":    "Right Stick Up"
    }
    if input in keys:
        return keys[input]
    return None

def rpcs3_mappingValue(name, type, code, value):
    if   type == "button":
        return code
    elif type == "hat":
        if value == 1:
            return -1017
        if value == 2:
            return 1016
        if value == 4:
            return 1017
        if value == 8:
            return -1016
        raise Exception("invalid hat value {}".format(value))
    elif type == "axis":
        res = int(code)+1000
        if value < 0:
            eslog.log("name = {} and value = {}".format(name, value))
            res = res * -1
        return res
    return None

def rpcs3_otherKeys(f, controller):
    f.write("Left Stick Multiplier: 100\n")
    f.write("Right Stick Multiplier: 100\n")
    f.write("Left Stick Deadzone: 30\n")
    f.write("Right Stick Deadzone: 30\n")
    f.write("Left Trigger Threshold: 0\n")
    f.write("Right Trigger Threshold: 0\n")
    f.write("Left Pad Squircling Factor: 5000\n")
    f.write("Right Pad Squircling Factor: 5000\n")
    f.write("Color Value R: 0\n")
    f.write("Color Value G: 0\n")
    f.write("Color Value B: 20\n")
    f.write("Blink LED when battery is below 20%: true\n")
    f.write("Use LED as a battery indicator: false\n")
    f.write("LED battery indicator brightness: 10\n")
    f.write("Enable Large Vibration Motor: true\n")
    f.write("Enable Small Vibration Motor: true\n")
    f.write("Switch Vibration Motors: false\n")
    f.write("Mouse Deadzone X Axis: 60\n")
    f.write("Mouse Deadzone Y Axis: 60\n")
    f.write("Mouse Acceleration X Axis: 200\n")
    f.write("Mouse Acceleration Y Axis: 250\n")
    f.write("Left Stick Lerp Factor: 100\n")
    f.write("Right Stick Lerp Factor: 100\n")
    f.write("Analog Button Lerp Factor: 100\n")
    f.write("Trigger Lerp Factor: 100\n")
    f.write("Device Class Type: 0\n")
    #f.write("Vendor ID: {}\n".format(controller.productId))
    #f.write("Product ID: {}\n".format(controller.vendorId))
