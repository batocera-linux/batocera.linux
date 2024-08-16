#!/usr/bin/env python

import batoceraFiles
import os
import pyudev
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
    API_WIIMOTE = "Wiimote"

    # from https://github.com/cemu-project/Cemu/blob/main/src/input/emulated/WPADController.h
    WIIMOTE_TYPE_CORE               = '0'
    WIIMOTE_TYPE_NUNCHUK            = '1'
    WIIMOTE_TYPE_CLASSIC            = '2'
    WIIMOTE_TYPE_MOTIONPLUS         = '5'
    WIIMOTE_TYPE_MOTIONPLUS_NUNCHUK = '6'
    WIIMOTE_TYPE_MOTIONPLUS_CLASSIC = '7'

    # from https://github.com/xwiimote/xwiimote/blob/master/lib/xwiimote.h
    WIIMOTE_NAME            = 'Nintendo Wii Remote'
    WIIMOTE_NAME_MOTIONPLUS = WIIMOTE_NAME + ' Motion Plus'
    WIIMOTE_NAME_NUNCHUK    = WIIMOTE_NAME + ' Nunchuk'
    WIIMOTE_NAME_CLASSIC    = WIIMOTE_NAME + ' Classic Controller'

    DEFAULT_DEADZONE       = '0.25'
    DEFAULT_RANGE          = '1'

    buttonMappingsSDL = {
        GAMEPAD: { # excludes show screen
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
            "24": "40",
            "25": "7"
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
        WIIMOTE: { # with MotionPlus & Nunchuk, excludes Home button
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
    }

    buttonMappingsWiimote = {
        WIIMOTE: {
            "1":  "11",
            "2":  "10",
            "3":  "9",
            "4":  "8",
            "5":  "17",
            "6":  "16",
            "7":  "4",
            "8":  "12",
            "9":  "3",
            "10": "2",
            "11": "0",
            "12": "1",
            "13": "39",
            "14": "45",
            "15": "44",
            "16": "38",
            "17": "15"
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

    def isWiimote(pad):
        return WIIMOTE_NAME == pad.realName

    def findWiimoteType(pad):
        context = pyudev.Context()
        device = pyudev.Devices.from_device_file(context, pad.dev)
        names = []
        for input_device in context.list_devices(parent=device.find_parent('hid')).match_subsystem('input'):
            if 'NAME' in input_device.properties:
                names += [input_device.properties['NAME'].strip('"')]
        if WIIMOTE_NAME_MOTIONPLUS in names:
            if WIIMOTE_NAME_NUNCHUK in names:
                return WIIMOTE_TYPE_MOTIONPLUS_NUNCHUK
            if WIIMOTE_NAME_CLASSIC in names:
                return WIIMOTE_TYPE_MOTIONPLUS_CLASSIC
            return WIIMOTE_TYPE_MOTIONPLUS
        else:
            if WIIMOTE_NAME_NUNCHUK in names:
                return WIIMOTE_TYPE_NUNCHUK
            if WIIMOTE_NAME_CLASSIC in names:
                return WIIMOTE_TYPE_CLASSIC
            return WIIMOTE_TYPE_CORE

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

        if isWiimote(pad):
            api = API_WIIMOTE
            deviceType = findWiimoteType(pad)
            addTextElement(root, 'device_type', deviceType)
        else:
            api = API_SDL

        # Create controller configuration
        controllerNode = ET.SubElement(root, 'controller')
        addTextElement(controllerNode, 'api', api)
        addTextElement(controllerNode, 'uuid', "{}_{}".format(guid_n[pad.index], pad.guid)) # controller guid
        addTextElement(controllerNode, 'display_name', pad.realName) # controller name
        addTextElement(controllerNode, 'rumble', getOption('cemu_rumble', '0')) # % chosen
        addAnalogControl(controllerNode, 'axis')
        addAnalogControl(controllerNode, 'rotation')
        addAnalogControl(controllerNode, 'trigger')

        # Apply the appropriate button mappings
        mappingsNode = ET.SubElement(controllerNode, "mappings")
        mapping = (buttonMappingsSDL,buttonMappingsWiimote)[isWiimote(pad)][type]
        for key, value in mapping.items():
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
