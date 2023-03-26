#!/usr/bin/env python

import batoceraFiles
import os
import xml.etree.cElementTree as ET
from os import path

profilesDir = path.join(batoceraFiles.CONF, 'cemu', 'controllerProfiles')

# Create the controller configuration file
# First controller will ALWAYS be a Gamepad
# Additional controllers will either be a Pro Controller or Wiimote

def generateControllerConfig(system, playersControllers):

    # -= Wii U controller types =-
    GAMEPAD = "Wii U GamePad"
    PRO     = "Wii U Pro Controller"
    CLASSIC = "Wii U Classic Controller"
    WIIMOTE = "Wiimote"

    API_SDL = "SDLController"
    API_DSU = "DSUController"

    DEFAULT_CONTROLLER_API = API_SDL
    DEFAULT_IP             = 'localhost'
    DEFAULT_PORT           = '26760'
    DEFAULT_DEADZONE       = '0.25'
    DEFAULT_RANGE          = '1'

    apiButtonMappings = {
        API_SDL: {
            GAMEPAD: { # excludes blow mic & show screen
                    "1":  "1",
                    "2":  "0",
                    "3":  "3",
                    "4":  "2",
                    "5":  "9",
                    "6":  "10",
                    "7":  "42",
                    "8":  "43",
                    "9":  "6",
                    "10": "4",
                    "11": "11",
                    "12": "12",
                    "13": "13",
                    "14": "14",
                    "15": "7",
                    "16": "8",
                    "17": "45",
                    "18": "39",
                    "19": "44",
                    "20": "38",
                    "21": "47",
                    "22": "41",
                    "23": "46",
                    "24": "40"
            },
            PRO: {
                    "1":  "1",
                    "2":  "0",
                    "3":  "3",
                    "4":  "2",
                    "5":  "9",
                    "6":  "10",
                    "7":  "42",
                    "8":  "43",
                    "9":  "6",
                    "10": "4",
                    # 11 is excluded
                    "12": "11",
                    "13": "12",
                    "14": "13",
                    "15": "14",
                    "16": "7",
                    "17": "8",
                    "18": "45",
                    "19": "39",
                    "20": "44",
                    "21": "38",
                    "22": "47",
                    "23": "41",
                    "24": "46",
                    "25": "40"
            },
            CLASSIC: {
                    "1":  "13",
                    "2":  "12",
                    "3":  "15",
                    "4":  "14",
                    "5":  "8",
                    "6":  "9",
                    "7":  "42",
                    "8":  "43",
                    "9":  "4",
                    "10": "5",
                    # 11 is excluded
                    "12": "0",
                    "13": "1",
                    "14": "2",
                    "15": "3",
                    "16": "39",
                    "17": "45",
                    "18": "44",
                    "19": "38",
                    "20": "41",
                    "21": "47",
                    "22": "46",
                    "23": "40"
            },
            WIIMOTE: { # with MotionPlus & Nunchuck, excludes Home button
                    "1":  "0",
                    "2":  "43",
                    "3":  "2",
                    "4":  "1",
                    "5":  "42",
                    "6":  "9",
                    "7":  "6",
                    "8":  "4",
                    "9":  "11",
                    "10": "12",
                    "11": "13",
                    "12": "14",
                    "13": "45",
                    "14": "39",
                    "15": "44",
                    "16": "38"
            }
        },
        API_DSU: {
            GAMEPAD: { # excludes blow mic & show screen
                    "1":  "13",
                    "2":  "14",
                    "3":  "12",
                    "4":  "15",
                    "5":  "10",
                    "6":  "11",
                    "7":  "8",
                    "8":  "9",
                    "9":  "3",
                    "10": "0",
                    "11": "4",
                    "12": "6",
                    "13": "7",
                    "14": "5",
                    "15": "1",
                    "16": "2",
                    "17": "39",
                    "18": "45",
                    "19": "44",
                    "20": "38",
                    "21": "41",
                    "22": "47",
                    "23": "46",
                    "24": "40"
            },
            PRO: {
                    "1":  "13",
                    "2":  "14",
                    "3":  "12",
                    "4":  "15",
                    "5":  "10",
                    "6":  "11",
                    "7":  "8",
                    "8":  "9",
                    "9":  "3",
                    "10": "0",
                    # 11 is excluded
                    "12": "4",
                    "13": "6",
                    "14": "7",
                    "15": "5",
                    "16": "1",
                    "17": "2",
                    "18": "39",
                    "19": "45",
                    "20": "44",
                    "21": "38",
                    "22": "41",
                    "23": "47",
                    "24": "46",
                    "25": "40"
            },
            CLASSIC: {
                    "1":  "13",
                    "2":  "14",
                    "3":  "12",
                    "4":  "15",
                    "5":  "10",
                    "6":  "11",
                    "7":  "8",
                    "8":  "9",
                    "9":  "3",
                    "10": "0",
                    # 11 is excluded
                    "12": "4",
                    "13": "6",
                    "14": "7",
                    "15": "5",
                    "16": "39",
                    "17": "45",
                    "18": "44",
                    "19": "38",
                    "20": "41",
                    "21": "47",
                    "22": "46",
                    "23": "40"
            },
            WIIMOTE: { # with MotionPlus & Nunchuck, excludes Home button
                    "1":  "13",
                    "2":  "14",
                    "3":  "15",
                    "4":  "12",
                    "5":  "8",
                    "6":  "10",
                    "7":  "3",
                    "8":  "0",
                    "9":  "4",
                    "10": "6",
                    "11": "7",
                    "12": "5",
                    "13": "39",
                    "14": "45",
                    "15": "44",
                    "16": "38"
            }
        }
    }

    def getOption(option, defaultValue):
        if (system.isOptSet(option)):
            return system.config[option]
        else:
            return defaultValue

    def addTextElement(parent, name, value):
        element = ET.SubElement(parent, name)
        element.text = value

    def addAnalogControl(parent, name):
        element = ET.SubElement(parent, name)
        addTextElement(element, "deadzone", DEFAULT_DEADZONE)
        addTextElement(element, "range", DEFAULT_RANGE)

    def getConfigFileName(controller):
        return path.join(profilesDir, "controller{}.xml".format(controller))


    # Make controller directory if it doesn't exist
    if not path.isdir(profilesDir):
        os.mkdir(profilesDir)

    # Purge old controller files
    for counter in range(0,8):
        configFileName = getConfigFileName(counter)
        if path.isfile(configFileName):
            os.remove(configFileName)

    ## CONTROLLER: Create the config xml files
    nplayer = 0

    # cemu assign pads by uuid then by index with the same uuid
    # so, if 2 pads have the same uuid, the index is not 0 but 1 for the 2nd one
    # sort pads by index
    pads_by_index = playersControllers
    dict(sorted(pads_by_index.items(), key=lambda kv: kv[1].index))
    guid_n = {}
    guid_count = {}
    for playercontroller, pad in pads_by_index.items():
        if pad.guid in guid_count:
            guid_count[pad.guid] += 1
        else:
            guid_count[pad.guid] = 0
        guid_n[pad.index] = guid_count[pad.guid]
    ###

    # Read the controller API from config, use default on invalid value
    controllerAPI = getOption('cemu_controller_api', DEFAULT_CONTROLLER_API)
    if not controllerAPI in apiButtonMappings:
        controllerAPI = DEFAULT_CONTROLLER_API

    for playercontroller, pad in sorted(playersControllers.items()):
        root = ET.Element("emulated_controller")

        # Set type from controller combination
        type = PRO # default
        if system.isOptSet('cemu_controller_combination') and system.config["cemu_controller_combination"] != '0':
            if system.config["cemu_controller_combination"] == '1':
                if (nplayer == 0):
                    type = GAMEPAD
                else:
                    type = WIIMOTE
            elif system.config["cemu_controller_combination"] == '2':
                type = PRO
            else:
                type = WIIMOTE
            if system.config["cemu_controller_combination"] == '4':
                type = CLASSIC
        else:
            if (nplayer == 0):
                type = GAMEPAD
            else:
                type = PRO
        addTextElement(root, "type", type)

        # Create controller configuration
        controllerNode = ET.SubElement(root, 'controller')
        addTextElement(controllerNode, 'api', controllerAPI)
        if (controllerAPI == API_DSU):
            addTextElement(controllerNode, 'motion', 'true')
            addTextElement(controllerNode, 'ip', getOption('cemuhook_server_ip', DEFAULT_IP))
            addTextElement(controllerNode, 'port', getOption('cemuhook_server_port', DEFAULT_PORT))
        addTextElement(controllerNode, 'uuid', "{}_{}".format(guid_n[pad.index], pad.guid)) # controller guid
        addTextElement(controllerNode, 'display_name', pad.realName) # controller name
        addTextElement(controllerNode, 'rumble', getOption('cemu_rumble', '0')) # % chosen
        addAnalogControl(controllerNode, 'axis')
        addAnalogControl(controllerNode, 'rotation')
        addAnalogControl(controllerNode, 'trigger')

        # Apply the appropriate button mappings
        mappingsNode = ET.SubElement(controllerNode, "mappings")
        for key, value in apiButtonMappings[controllerAPI][type].items():
            entryNode = ET.SubElement(mappingsNode, "entry")
            addTextElement(entryNode, "mapping", key)
            addTextElement(entryNode, "button", value)

        # Save to file
        with open(getConfigFileName(nplayer), 'wb') as handle:
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(handle, encoding='UTF-8', xml_declaration=True)
            handle.close()

        nplayer+=1
