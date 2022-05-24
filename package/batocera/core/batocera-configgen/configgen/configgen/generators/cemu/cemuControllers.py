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

#  -=Cemu XInput mappings=-

# A =                Button 13
# B =                Button 12
# X =                Button 15
# Y =                Button 14
# Left Shoulder =    Button 8
# Right Shoulder =   Button 9
# Left Trigger =     Button 42
# Right Trigger =    Button 43
# + / Start =        Button 4
# - / Select =       Button 5

# Left Axis Click =  Button 6
# Left Axis Up =     Button 39
# Left Axis Down =   Button 45
# Left Axis Left =   Button 44
# Left Axis Right =  Button 38

# Rigth Axis Click = Button 7
# Rigth Axis Up =    Button 41
# Rigth Axis Down =  Button 47 
# Rigth Axis Left =  Button 46
# Rigth Axis Right = Button 40

# D-Pad Up =         Button 0
# D-Pad Down =       Button 1
# D-Pad Left =       Button 2
# D-pad Right =      Button 3

# First controller will ALWAYS BE A Gamepad
# Additional controllers will either be a Pro Controller or Wiimote

def generateControllerConfig(system, playersControllers):
    # -= Wii U controller types =-

    # xml mapping number: cemu expected XInput button number

    # Wii U GamePad Controller (excludes blow mic & show screen)
    wiiUGamePadButtons = {
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
            "11": "0",
            "12": "1",
            "13": "2",
            "14": "3",
            "15": "6",
            "16": "7",
            "17": "39",
            "18": "45",
            "19": "44",
            "20": "38",
            "21": "41",
            "22": "47",
            "23": "46",
            "24": "40"
    }
    # Wii U Pro Controller (no mapping 11)
    wiiUProButtons = {
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
            "16": "6",
            "17": "7",
            "18": "39",
            "19": "45",
            "20": "44",
            "21": "38",
            "22": "41",
            "23": "47",
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
            "1":  "13",
            "2":  "43",
            "3":  "15",
            "4":  "12",
            "5":  "42",
            "6":  "8",
            "7":  "4",
            "8":  "5",
            "9":  "0",
            "10": "1",
            "11": "2",
            "12": "3",
            "13": "39",            
            "14": "45",
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
    for playercontroller, pad in sorted(playersControllers.items()):
        root = ET.Element("emulated_controller")
        doc = ET.SubElement(root, "type")      
        # Controller combination type
        wiimote = 0
        mappings = wiiUProButtons # default
        if system.isOptSet('controller_combination') and system.config["controller_combination"] != '0':
            if system.config["controller_combination"] == '1':
                if (nplayer == 0):
                    doc.text = "Wii U GamePad"
                    mappings = wiiUGamePadButtons
                    addIndex = 0
                else:
                    doc.text = "Wiimote"
                    mappings = wiiMoteButtons
                    wiimote = 1
            elif system.config["controller_combination"] == '2':
                doc.text = "Wii U Pro Controller"
                mappings = wiiUProButtons
                addIndex = 1
            else:
                doc.text = "Wiimote"
                mappings = wiiMoteButtons
                wiimote = 1
            if system.config["controller_combination"] == '4':
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
        ctrl.text = "XInput" # use XInput for now 
        ctrl = ET.SubElement(doc, "uuid") #uuid is the XInput controller number
        ctrl.text = str(nplayer)
        ctrl = ET.SubElement(doc, "display_name")
        ctrl.text = "Controller {}".format((nplayer)+1) # use controller number for display name
        # Rumble
        if system.isOptSet("rumble"):
            ctrl = ET.SubElement(doc, "rumble")
            ctrl.text = system.config["rumble"] # % chosen
        else:
            ctrl = ET.SubElement(doc, "rumble")
            ctrl.text = "0" # none
        # axis
        ctrl = ET.SubElement(doc, "axis")
        axis = ET.SubElement(ctrl, "deadzone")
        axis.text = "0.15" # XInput is 0.15 by default
        axis = ET.SubElement(ctrl, "range")
        axis.text = "1"
        # rotation
        ctrl = ET.SubElement(doc, "rotation")
        rotation = ET.SubElement(ctrl, "deadzone")
        rotation.text = "0.15"
        rotation = ET.SubElement(ctrl, "range")
        rotation.text = "1"
        # trigger
        ctrl = ET.SubElement(doc, "trigger")
        trigger = ET.SubElement(ctrl, "deadzone")
        trigger.text = "0.15"
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
