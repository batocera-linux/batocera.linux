#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import Command
import shutil
import os
from utils.logger import get_logger
from os import path
from os import environ
import configparser
from xml.dom import minidom
import codecs
import shutil
import utils.bezels as bezelsUtil
import subprocess
import csv
from xml.dom import minidom
from PIL import Image, ImageOps

eslog = get_logger(__name__)

def generatePadsConfig(cfgPath, playersControllers, sysName, altButtons, customCfg, specialController, decorations, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system):
    # config file
    config = minidom.Document()
    configFile = cfgPath + "default.cfg"
    if os.path.exists(configFile):
        try:
            config = minidom.parse(configFile)
        except:
            pass # reinit the file
    if os.path.exists(configFile) and customCfg:
        overwriteMAME = False
    else:
        overwriteMAME = True
    
    # Load standard controls from csv
    controlFile = '/usr/share/batocera/configgen/data/mame/mameControls.csv'
    openFile = open(controlFile, 'r')
    controlDict = {}
    with openFile:
        controlList = csv.reader(openFile)
        for row in controlList:
            if not row[0] in controlDict.keys():
                controlDict[row[0]] = {}
            controlDict[row[0]][row[1]] = row[2]

    # Common controls
    mappings = {}
    for controlDef in controlDict['default'].keys():
        mappings[controlDef] = controlDict['default'][controlDef]

    # Only use gun buttons if lightguns are enabled to prevent conflicts with mouse
    gunmappings = {}
    if useGuns:
        for controlDef in controlDict['gunbuttons'].keys():
            gunmappings[controlDef] = controlDict['gunbuttons'][controlDef]

    # Only define mouse buttons if mouse is enabled, to prevent unwanted inputs
    # For a standard mouse, left, right, scroll wheel should be mapped to action buttons, and if side buttons are available, they will be coin & start
    mousemappings = {}
    if useMouse:
        for controlDef in controlDict['mousebuttons'].keys():
            mousemappings[controlDef] = controlDict['mousebuttons'][controlDef]

    # Buttons that change based on game/setting
    if altButtons in controlDict:
        for controlDef in controlDict[altButtons].keys():
            mappings.update({controlDef: controlDict[altButtons][controlDef]})

    xml_mameconfig = getRoot(config, "mameconfig")
    xml_mameconfig.setAttribute("version", "10") # otherwise, config of pad won't work at first run (batocera v33)
    xml_system     = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    # crosshairs
    removeSection(config, xml_system, "crosshairs")
    xml_crosshairs = config.createElement("crosshairs")
    for p in range(0, 4):
        xml_crosshair = config.createElement("crosshair")
        xml_crosshair.setAttribute("player", str(p))
        if system.isOptSet("mame_crosshair") and system.config["mame_crosshair"] == "enabled":
            xml_crosshair.setAttribute("mode", "1")
        elif system.isOptSet("mame_crosshair") and system.config["mame_crosshair"] == "onmove":
            continue # keep no line
        else:
            xml_crosshair.setAttribute("mode", "0")
        xml_crosshairs.appendChild(xml_crosshair)
    xml_system.appendChild(xml_crosshairs)

    removeSection(config, xml_system, "input")
    xml_input = config.createElement("input")
    xml_system.appendChild(xml_input)

    messControlDict = {}
    if sysName in [ "bbcb", "bbcm", "bbcm512", "bbcmc" ]:
        if specialController == 'none':
            useControls = "bbc"
        else:
            useControls = f"bbc-{specialController}"
    elif sysName in [ "apple2p", "apple2e", "apple2ee" ]:
        if specialController == 'none':
            useControls = "apple2"
        else:
            useControls = f"apple2-{specialController}"
    else:
        useControls = sysName
    eslog.debug(f"Using {useControls} for controller config.")
    
    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    specialControlList = [ "cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb", "bbcm", "bbcm512", "bbcmc", "xegs", \
        "socrates", "vgmplay", "pdp1", "vc4000", "fmtmarty", "gp32", "apple2p", "apple2e", "apple2ee" ]
    if sysName in specialControlList:
        # Load mess controls from csv
        messControlFile = '/usr/share/batocera/configgen/data/mame/messControls.csv'
        openMessFile = open(messControlFile, 'r')
        with openMessFile:
            controlList = csv.reader(openMessFile, delimiter=';')
            for row in controlList:
                if not row[0] in messControlDict.keys():
                    messControlDict[row[0]] = {}
                messControlDict[row[0]][row[1]] = {}
                currentEntry = messControlDict[row[0]][row[1]]
                currentEntry['type'] = row[2]
                currentEntry['player'] = int(row[3])
                currentEntry['tag'] = row[4]
                currentEntry['key'] = row[5]
                if currentEntry['type'] in [ 'special', 'main' ]:
                    currentEntry['mapping'] = row[6]
                    currentEntry['useMapping'] = row[7]
                    currentEntry['reversed'] = row[8]
                    currentEntry['mask'] = row[9]
                    currentEntry['default'] = row[10]
                elif currentEntry['type'] == 'analog':
                    currentEntry['incMapping'] = row[6]
                    currentEntry['decMapping'] = row[7]
                    currentEntry['useMapping1'] = row[8]
                    currentEntry['useMapping2'] = row[9]
                    currentEntry['reversed'] = row[10]
                    currentEntry['mask'] = row[11]
                    currentEntry['default'] = row[12]
                    currentEntry['delta'] = row[13]
                    currentEntry['axis'] = row[14]
                if currentEntry['type'] == 'combo':
                    currentEntry['kbMapping'] = row[6]
                    currentEntry['mapping'] = row[7]
                    currentEntry['useMapping'] = row[8]
                    currentEntry['reversed'] = row[9]
                    currentEntry['mask'] = row[10]
                    currentEntry['default'] = row[11]
                if currentEntry['reversed'] == 'False':
                    currentEntry['reversed'] == False
                else:
                    currentEntry['reversed'] == True

        config_alt = minidom.Document()
        configFile_alt = cfgPath + sysName + ".cfg"
        if os.path.exists(configFile_alt) and cfgPath == "/userdata/system/configs/mame/" + sysName + "/":
            try:
                config_alt = minidom.parse(configFile_alt)
            except:
                pass # reinit the file
        elif os.path.exists(configFile_alt):
            try:
                config_alt = minidom.parse(configFile_alt)
            except:
                pass # reinit the file
        if cfgPath == "/userdata/system/configs/mame/" + sysName + "/":
            perGameCfg = False
        else:
            perGameCfg = True
        if os.path.exists(configFile_alt) and (customCfg or perGameCfg):
            overwriteSystem = False
        else:
            overwriteSystem = True

        xml_mameconfig_alt = getRoot(config_alt, "mameconfig")
        xml_mameconfig_alt.setAttribute("version", "10")
        xml_system_alt = getSection(config_alt, xml_mameconfig_alt, "system")
        xml_system_alt.setAttribute("name", sysName)
        
        removeSection(config_alt, xml_system_alt, "input")
        xml_input_alt = config_alt.createElement("input")
        xml_system_alt.appendChild(xml_input_alt)

        # Hide the LCD display on CD-i
        if useControls == "cdimono1":
            removeSection(config_alt, xml_system_alt, "video")
            xml_video_alt = config_alt.createElement("video")
            xml_system_alt.appendChild(xml_video_alt)

            xml_screencfg_alt = config_alt.createElement("target")
            xml_screencfg_alt.setAttribute("index", "0")
            if decorations == "none":
                xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
            else:
                xml_screencfg_alt.setAttribute("view", "Upright_Artwork")
            xml_video_alt.appendChild(xml_screencfg_alt)

        # If using BBC keyboard controls, enable keyboard to gamepad
        if useControls == 'bbc':
            xml_kbenable_alt = config_alt.createElement("keyboard")
            xml_kbenable_alt.setAttribute("tag", ":")
            xml_kbenable_alt.setAttribute("enabled", "1")
            xml_input_alt.appendChild(xml_kbenable_alt)
    
    # Fill in controls on cfg files
    nplayer = 1
    maxplayers = len(playersControllers)
    for playercontroller, pad in sorted(playersControllers.items()):
        mappings_use = mappings
        if hasStick(pad) == False:
            mappings_use["JOYSTICK_UP"] = "up"
            mappings_use["JOYSTICK_DOWN"] = "down"
            mappings_use["JOYSTICK_LEFT"] = "left"
            mappings_use["JOYSTICK_RIGHT"] = "right"

        # wheel mappings
        isWheel = False
        if useWheels:
            for w in wheels:
                if wheels[w]["joystick_index"] == pad.index:
                    isWheel = True
                    eslog.debug(f"player {nplayer} has a wheel")
            if isWheel:
                for x in mappings_use.copy():
                    if mappings_use[x] == "l2" or mappings_use[x] == "r2" or mappings_use[x] == "joystick1left":
                        del mappings_use[x]
                mappings_use["PEDAL".format(pad.index+1)] = "r2"
                mappings_use["PEDAL2".format(pad.index+1)] = "l2"
                mappings_use["PADDLE".format(pad.index+1)] = "joystick1left"

        addCommonPlayerPorts(config, xml_input, nplayer)

        ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
        pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
        pedalkey = None
        pedalcname = "controllers.pedals{}".format(nplayer)
        if pedalcname in system.config:
            pedalkey = system.config[pedalcname]
        else:
            if nplayer in pedalsKeys:
                pedalkey = pedalsKeys[nplayer]
        ###

        for mapping in mappings_use:
            if mappings_use[mapping] in pad.inputs:
                if mapping in [ 'START', 'COIN' ]:
                    xml_input.appendChild(generateSpecialPortElementPlayer(pad, config, 'standard', nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[mappings_use[mapping]], False, "", "", gunmappings, mousemappings, multiMouse, pedalkey))
                else:
                    xml_input.appendChild(generatePortElement(pad, config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[mappings_use[mapping]], False, altButtons, gunmappings, isWheel, mousemappings, multiMouse, pedalkey))
            else:
                rmapping = reverseMapping(mappings_use[mapping])
                if rmapping in pad.inputs:
                        xml_input.appendChild(generatePortElement(pad, config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[rmapping], True, altButtons, gunmappings, isWheel, mousemappings, multiMouse, pedalkey))

        #UI Mappings
        if nplayer == 1:
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_DOWN", "DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, "", ""))      # Down
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_LEFT", "LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, "", ""))    # Left
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_UP", "UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, "", ""))            # Up
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_RIGHT", "RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, "", "")) # Right
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_SELECT", "ENTER", 'b', pad.inputs['b'], False, "", ""))                                                     # Select

        if useControls in messControlDict.keys():
            for controlDef in messControlDict[useControls].keys():
                thisControl = messControlDict[useControls][controlDef]
                if nplayer == thisControl['player']:
                    if thisControl['type'] == 'special':
                        xml_input_alt.appendChild(generateSpecialPortElement(pad, config_alt, thisControl['tag'], nplayer, pad.index, thisControl['key'], thisControl['mapping'], \
                            pad.inputs[mappings_use[thisControl['useMapping']]], thisControl['reversed'], thisControl['mask'], thisControl['default'], pedalkey))
                    elif thisControl['type'] == 'main':
                        xml_input.appendChild(generateSpecialPortElement(pad, config_alt, thisControl['tag'], nplayer, pad.index, thisControl['key'], thisControl['mapping'], \
                            pad.inputs[mappings_use[thisControl['useMapping']]], thisControl['reversed'], thisControl['mask'], thisControl['default'], pedalkey))
                    elif thisControl['type'] == 'analog':
                        xml_input_alt.appendChild(generateAnalogPortElement(pad, config_alt, thisControl['tag'], nplayer, pad.index, thisControl['key'], mappings_use[thisControl['incMapping']], \
                            mappings_use[thisControl['decMapping']], pad.inputs[mappings_use[thisControl['useMapping1']]], pad.inputs[mappings_use[thisControl['useMapping2']]], thisControl['reversed'], \
                            thisControl['mask'], thisControl['default'], thisControl['delta'], thisControl['axis']))
                    elif thisControl['type'] == 'combo':
                        xml_input_alt.appendChild(generateComboPortElement(pad, config_alt, thisControl['tag'], pad.index, thisControl['key'], thisControl['kbMapping'], thisControl['mapping'], \
                            pad.inputs[mappings_use[thisControl['useMapping']]], thisControl['reversed'], thisControl['mask'], thisControl['default']))

        nplayer = nplayer + 1

    # in case there are more guns than pads, configure them
    if useGuns and len(guns) > len(playersControllers):
        for gunnum in range(len(playersControllers)+1, len(guns)+1):
            ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
            pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
            pedalkey = None
            pedalcname = "controllers.pedals{}".format(gunnum)
            if pedalcname in system.config:
                pedalkey = system.config[pedalcname]
            else:
                if gunnum in pedalsKeys:
                    pedalkey = pedalsKeys[gunnum]
            ###
            addCommonPlayerPorts(config, xml_input, gunnum)
            for mapping in gunmappings:
                xml_input.appendChild(generateGunPortElement(config, gunnum, mapping, gunmappings, pedalkey))

    # save the config file
    #mameXml = open(configFile, "w")
    # TODO: python 3 - workawround to encode files in utf-8
    if overwriteMAME:
        eslog.debug(f"Saving {configFile}")
        mameXml = codecs.open(configFile, "w", "utf-8")
        dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        mameXml.write(dom_string)

    # Write alt config (if used, custom config is turned off or file doesn't exist yet)
    if sysName in specialControlList and overwriteSystem:
        eslog.debug(f"Saving {configFile_alt}")
        mameXml_alt = codecs.open(configFile_alt, "w", "utf-8")
        dom_string_alt = os.linesep.join([s for s in config_alt.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
        mameXml_alt.write(dom_string_alt)

def reverseMapping(key):
    if key == "joystick1down":
        return "joystick1up"
    if key == "joystick1right":
        return "joystick1left"
    if key == "joystick2down":
        return "joystick2up"
    if key == "joystick2right":
        return "joystick2left"
    return None

def generatePortElement(pad, config, nplayer, padindex, mapping, key, input, reversed, altButtons, gunmappings, isWheel, mousemappings, multiMouse, pedalkey):
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = input2definition(pad, key, input, padindex + 1, reversed, altButtons, False, isWheel)
    if mapping in gunmappings:
        keyval = keyval + " OR GUNCODE_{}_{}".format(nplayer, gunmappings[mapping])
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += " OR KEYCODE_" + pedalkey.upper()
    if mapping in mousemappings:
        if multiMouse:
            keyval = keyval + " OR MOUSECODE_{}_{}".format(nplayer, mousemappings[mapping])
        else:
            keyval = keyval + " OR MOUSECODE_1_{}".format(mousemappings[mapping])
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port

def generateGunPortElement(config, nplayer, mapping, gunmappings, pedalkey):
    # Generic input
    xml_port = config.createElement("port")
    if mapping in ["START", "COIN"]:
        xml_port.setAttribute("type", mapping+str(nplayer))
    else:
        xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = None
    if mapping in gunmappings:
        keyval = "GUNCODE_{}_{}".format(nplayer, gunmappings[mapping])
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += " OR KEYCODE_" + pedalkey.upper()
    if keyval is None:
        return None
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElementPlayer(pad, config, tag, nplayer, padindex, mapping, key, input, reversed, mask, default, gunmappings, mousemappings, multiMouse, pedalkey):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping+str(nplayer))
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = input2definition(pad, key, input, padindex + 1, reversed, 0)
    if mapping in gunmappings:
        keyval = keyval + " OR GUNCODE_{}_{}".format(nplayer, gunmappings[mapping])
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += " OR KEYCODE_" + pedalkey.upper()
    if mapping in mousemappings:
        if multiMouse:
            keyval = keyval + " OR MOUSECODE_{}_{}".format(nplayer, mousemappings[mapping])
        else:
            keyval = keyval + " OR MOUSECODE_1_{}".format(mousemappings[mapping])
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElement(pad, config, tag, nplayer, padindex, mapping, key, input, reversed, mask, default, pedalkey):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(pad, key, input, padindex + 1, reversed, 0))
    xml_newseq.appendChild(value)
    return xml_port

def generateComboPortElement(pad, config, tag, padindex, mapping, kbkey, key, input, reversed, mask, default):
    # Maps a keycode + button - for important keyboard keys when available
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode("KEYCODE_{} OR ".format(kbkey) + input2definition(pad, key, input, padindex + 1, reversed, 0))
    xml_newseq.appendChild(value)
    return xml_port

def generateAnalogPortElement(pad, config, tag, nplayer, padindex, mapping, inckey, deckey, mappedinput, mappedinput2, reversed, mask, default, delta, axis = ''):
    # Mapping analog to digital (mouse, etc)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_port.setAttribute("keydelta", delta)
    xml_newseq_inc = config.createElement("newseq")
    xml_newseq_inc.setAttribute("type", "increment")
    xml_port.appendChild(xml_newseq_inc)
    incvalue = config.createTextNode(input2definition(pad, inckey, mappedinput, padindex + 1, reversed, 0, True))
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(input2definition(pad, deckey, mappedinput2, padindex + 1, reversed, 0, True))
    xml_newseq_dec.appendChild(decvalue)
    xml_newseq_std = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_std)
    xml_newseq_std.setAttribute("type", "standard")
    if axis == '':
        stdvalue = config.createTextNode("NONE")
    else:
        stdvalue = config.createTextNode("JOYCODE_{}_{}".format(padindex + 1, axis))
    xml_newseq_std.appendChild(stdvalue)
    return xml_port

def input2definition(pad, key, input, joycode, reversed, altButtons, ignoreAxis = False, isWheel = False):

    mameAxisMappingNames = {0: "XAXIS", 1: "YAXIS", 2: "ZAXIS", 3: "RXAXIS", 4: "RYAXIS", 5: "RZAXIS"}

    if isWheel:
        if key == "joystick1left" or key == "l2" or key == "r2":
            suffix = ""
            if key == "r2":
                suffix = "_NEG"
            if key == "l2":
                suffix = "_NEG"
            if int(input.id) in mameAxisMappingNames:
                idname = mameAxisMappingNames[int(input.id)]
                return f"JOYCODE_{joycode}_{idname}{suffix}"

    if input.type == "button":
        return f"JOYCODE_{joycode}_BUTTON{int(input.id)+1}"
    elif input.type == "hat":
        if input.value == "1":
            return f"JOYCODE_{joycode}_HAT1UP"
        elif input.value == "2":
            return f"JOYCODE_{joycode}_HAT1RIGHT"
        elif input.value == "4":
            return f"JOYCODE_{joycode}_HAT1DOWN"
        elif input.value == "8":
            return f"JOYCODE_{joycode}_HAT1LEFT"
    elif input.type == "axis":
        # Determine alternate button for D-Pad and right stick as buttons
        dpadInputs = {}
        for direction in ['up', 'down', 'left', 'right']:
            if pad.inputs[direction].type == 'button':
                dpadInputs[direction] = f'JOYCODE_{joycode}_BUTTON{int(pad.inputs[direction].id)+1}'
            elif pad.inputs[direction].type == 'hat':
                if pad.inputs[direction].value == "1":
                    dpadInputs[direction] = f'JOYCODE_{joycode}_HAT1UP'
                if pad.inputs[direction].value == "2":
                    dpadInputs[direction] = f'JOYCODE_{joycode}_HAT1RIGHT'
                if pad.inputs[direction].value == "4":
                    dpadInputs[direction] = f'JOYCODE_{joycode}_HAT1DOWN'
                if pad.inputs[direction].value == "8":
                    dpadInputs[direction] = f'JOYCODE_{joycode}_HAT1LEFT'
            else:
                dpadInputs[direction] = ''
        buttonDirections = {}
        # workarounds for issue #6892
        # Modified because right stick to buttons was not working after the workaround
        # Creates a blank, only modifies if the button exists in the pad.
        # Button assigment modified - blank "OR" gets removed by MAME if the button is undefined.
        for direction in ['a', 'b', 'x', 'y']:
            buttonDirections[direction] = ''
            if direction in pad.inputs.keys():
                if pad.inputs[direction].type == 'button':
                    buttonDirections[direction] = f'JOYCODE_{joycode}_BUTTON{int(pad.inputs[direction].id)+1}'

        if ignoreAxis and dpadInputs['up'] != '' and dpadInputs['down'] != '' \
            and dpadInputs['left'] != '' and dpadInputs['right'] != '':
            if key == "joystick1up" or key == "up":
                return dpadInputs['up']
            if key == "joystick1down" or key == "down":
                return dpadInputs['down']
            if key == "joystick1left" or key == "left":
                return dpadInputs['left']
            if key == "joystick1right" or key == "right":
                return dpadInputs['right']
        if altButtons == "qbert": # Q*Bert Joystick
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_YAXIS_UP_SWITCH JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH OR {dpadInputs['up']} {dpadInputs['right']}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_YAXIS_DOWN_SWITCH JOYCODE_{joycode}_XAXIS_LEFT_SWITCH OR {dpadInputs['down']} {dpadInputs['left']}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_XAXIS_LEFT_SWITCH JOYCODE_{joycode}_YAXIS_UP_SWITCH OR {dpadInputs['left']} {dpadInputs['up']}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH JOYCODE_{joycode}_YAXIS_DOWN_SWITCH OR {dpadInputs['right']} {dpadInputs['down']}"
        else:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_YAXIS_UP_SWITCH OR {dpadInputs['up']}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_YAXIS_DOWN_SWITCH OR {dpadInputs['down']}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_XAXIS_LEFT_SWITCH OR {dpadInputs['left']}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH OR {dpadInputs['right']}"
        # Fix for the workaround
        for direction in pad.inputs:
            if(key == "joystick2up"):
                return f"JOYCODE_{joycode}_RYAXIS_NEG_SWITCH OR {buttonDirections['x']}"
            if(key == "joystick2down"):
                return f"JOYCODE_{joycode}_RYAXIS_POS_SWITCH OR {buttonDirections['b']}"
            if(key == "joystick2left"):
                return f"JOYCODE_{joycode}_RXAXIS_NEG_SWITCH OR {buttonDirections['y']}"
            if(key == "joystick2right"):
                return f"JOYCODE_{joycode}_RXAXIS_POS_SWITCH OR {buttonDirections['a']}"
            if int(input.id) in mameAxisMappingNames:
                idname = mameAxisMappingNames[int(input.id)]
                return f"JOYCODE_{joycode}_{idname}_POS_SWITCH"

    return "unknown"

def hasStick(pad):
    if "joystick1up" in pad.inputs:
        return True
    else:
        return False

def getRoot(config, name):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def getSection(config, xml_root, name):
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def removeSection(config, xml_root, name):
    xml_section = xml_root.getElementsByTagName(name)

    for i in range(0, len(xml_section)):
        old = xml_root.removeChild(xml_section[i])
        old.unlink()

def addCommonPlayerPorts(config, xml_input, nplayer):
    # adstick for guns
    for axis in ["X", "Y"]:
        nanalog = 1 if axis == "X" else 2
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", ":mainpcb:ANALOG{}".format(nanalog))
        xml_port.setAttribute("type", "P{}_AD_STICK_{}".format(nplayer, axis))
        xml_port.setAttribute("mask", "255")
        xml_port.setAttribute("defvalue", "128")
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode("GUNCODE_{}_{}AXIS".format(nplayer, axis))
        xml_newseq.appendChild(value)
        xml_input.appendChild(xml_port)
