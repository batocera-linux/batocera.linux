#!/usr/bin/env python

import batoceraFiles
import os
from os import path
import codecs
from Emulator import Emulator
import configparser
import json
import xml.etree.cElementTree as ET
import xml.dom.minidom

cemuConfig  = batoceraFiles.CONF + '/cemu'

# Create the controller configuration file
# First controller will ALWAYS be a Gamepad
# Additional controllers will either be a Pro Controller or Wiimote

def generateControllerConfig(system, playersControllers):
    # -= Wii U controller types =-

    # Wii U GamePad Controller (excludes show screen)
    wiiUGamePadButtons = {
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
    }
    # Wii U Pro Controller (no mapping 11)
    wiiUProButtons = {
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
    }
    # Wii U Classic Controller (no mapping 11)
    wiiUClassicButtons = {
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
    }
    # Wiimote, enable MotionPlus & Nunchuck (no home button)
    wiiMoteButtons = {
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

    # Make controller directory if it doesn't exist
    if not path.isdir(cemuConfig + "/controllerProfiles"):
        os.mkdir(cemuConfig + "/controllerProfiles")

    # Purge old controller files
    for counter in range(0,8):
        configFileName = "{}/{}".format(cemuConfig + "/controllerProfiles/", "controller" + str(counter) +".xml")
        if os.path.isfile(configFileName):
            os.remove(configFileName)

    ## CONTROLLER: Create the config xml files
    nplayer = 0
    m_encoding = 'UTF-8'

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
        guid_index = guid_n[pad.index]

        root = ET.Element("emulated_controller")
        doc = ET.SubElement(root, "type")
        # Controller combination type
        wiimote = 0
        mappings = wiiUProButtons # default
        if system.isOptSet('cemu_controller_combination') and system.config["cemu_controller_combination"] != '0':
            if system.config["cemu_controller_combination"] == '1':
                if (nplayer == 0):
                    doc.text = "Wii U GamePad"
                    mappings = wiiUGamePadButtons
                    addIndex = 0
                else:
                    doc.text = "Wiimote"
                    mappings = wiiMoteButtons
                    wiimote = 1
            elif system.config["cemu_controller_combination"] == '2':
                doc.text = "Wii U Pro Controller"
                mappings = wiiUProButtons
                addIndex = 1
            else:
                doc.text = "Wiimote"
                mappings = wiiMoteButtons
                wiimote = 1
            if system.config["cemu_controller_combination"] == '4':
                doc.text = "Wii U Classic Controller"
                mappings = wiiUClassicButtons
                addIndex = 1
        else:
            if (nplayer == 0):
                doc.text = "Wii U GamePad"
                mappings = wiiUGamePadButtons
                addIndex = 0
            else:
                doc.text = "Wii U Pro Controller"
                mappings = wiiUProButtons
                addIndex = 1

        doc = ET.SubElement(root, "controller")
        ctrl = ET.SubElement(doc, "api")
        ctrl.text = "SDLController" # use SDL
        ctrl = ET.SubElement(doc, "uuid")
        ctrl.text = "{}_{}".format(guid_index, pad.guid) # SDL guid
        ctrl = ET.SubElement(doc, "display_name")
        ctrl.text = pad.realName # controller name
        # Rumble
        if system.isOptSet("cemu_rumble"):
            ctrl = ET.SubElement(doc, "rumble")
            ctrl.text = system.config["cemu_rumble"] # % chosen
        else:
            ctrl = ET.SubElement(doc, "rumble")
            ctrl.text = "0" # none
        # axis
        ctrl = ET.SubElement(doc, "axis")
        axis = ET.SubElement(ctrl, "deadzone")
        axis.text = "0.25"
        axis = ET.SubElement(ctrl, "range")
        axis.text = "1"
        # rotation
        ctrl = ET.SubElement(doc, "rotation")
        rotation = ET.SubElement(ctrl, "deadzone")
        rotation.text = "0.25"
        rotation = ET.SubElement(ctrl, "range")
        rotation.text = "1"
        # trigger
        ctrl = ET.SubElement(doc, "trigger")
        trigger = ET.SubElement(ctrl, "deadzone")
        trigger.text = "0.25"
        trigger = ET.SubElement(ctrl, "range")
        trigger.text = "1"
        # apply the appropriate mappings
        ctrl = ET.SubElement(doc, "mappings")
        for mapping in mappings:
            ctrlmapping = ET.SubElement(ctrl, "entry")
            mp = ET.SubElement(ctrlmapping, "mapping")
            mp.text = mapping
            btn = ET.SubElement(ctrlmapping, "button")
            btn.text = mappings[mapping]

        # now format the xml file so it's all pirdy...
        dom = xml.dom.minidom.parseString(ET.tostring(root))
        xml_string = dom.toprettyxml()
        part1, part2 = xml_string.split('?>')

        configFileName = "{}/{}".format(cemuConfig + "/controllerProfiles/", "controller" + str(nplayer) + ".xml")

        # Save Cemu controller profiles
        with open(configFileName, 'w') as xfile:
            xfile.write(part1 + 'encoding=\"{}\"?>\n'.format(m_encoding) + part2)
            xfile.close()
        
        nplayer+=1
