from __future__ import annotations

import codecs
import csv
import logging
import os
from typing import TYPE_CHECKING
from xml.dom import minidom

from .mamePaths import MAME_CONFIG, MAME_DEFAULT_DATA

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from ...controller import Controller, Controllers
    from ...Emulator import Emulator
    from ...gun import Guns
    from ...input import Input
    from ...types import DeviceInfoMapping
    from .mameTypes import MameControlScheme

_logger = logging.getLogger(__name__)

def generatePadsConfig(cfgPath: Path, playersControllers: Controllers, sysName: str, altButtons: MameControlScheme, customCfg: bool, specialController: str, decorations: str | None, useGuns: bool, guns: Guns, useWheels: bool, wheels: DeviceInfoMapping, useMouse: bool, multiMouse: bool, system: Emulator) -> None:
    # config file
    config = minidom.Document()
    configFile = cfgPath / "default.cfg"
    if configFile.exists():
        try:
            config = minidom.parse(str(configFile))
        except Exception:
            pass # reinit the file
    if configFile.exists() and customCfg:
        overwriteMAME = False
    else:
        overwriteMAME = True

    # Load standard controls from csv
    controlFile = MAME_DEFAULT_DATA / 'mameControls.csv'
    openFile = controlFile.open('r')
    controlDict: dict[str, dict[str, str]] = {}
    with openFile:
        controlList = csv.reader(openFile)
        for row in controlList:
            if row[0] not in controlDict:
                controlDict[row[0]] = {}
            controlDict[row[0]][row[1]] = row[2]

    # Common controls
    mappings: dict[str, str] = {}
    for controlDef in controlDict['default']:
        mappings[controlDef] = controlDict['default'][controlDef]

    # Only use gun buttons if lightguns are enabled to prevent conflicts with mouse
    gunmappings: dict[str, str] = {}
    if useGuns:
        for controlDef in controlDict['gunbuttons']:
            gunmappings[controlDef] = controlDict['gunbuttons'][controlDef]

    # Only define mouse buttons if mouse is enabled, to prevent unwanted inputs
    # For a standard mouse, left, right, scroll wheel should be mapped to action buttons, and if side buttons are available, they will be coin & start
    mousemappings: dict[str, str] = {}
    if useMouse:
        for controlDef in controlDict['mousebuttons']:
            mousemappings[controlDef] = controlDict['mousebuttons'][controlDef]

    # Buttons that change based on game/setting
    if altButtons in controlDict:
        for controlDef in controlDict[altButtons]:
            mappings.update({controlDef: controlDict[altButtons][controlDef]})

    xml_mameconfig = getRoot(config, "mameconfig")
    xml_mameconfig.setAttribute("version", "10") # otherwise, config of pad won't work at first run (batocera v33)
    xml_system     = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    # crosshairs
    removeSection(config, xml_system, "crosshairs")
    xml_crosshairs = config.createElement("crosshairs")
    for p in range(4):
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
    _logger.debug("Using %s for controller config.", useControls)

    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    specialControlList = [ "cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb", "bbcm", "bbcm512", "bbcmc", "xegs", \
        "socrates", "vgmplay", "pdp1", "vc4000", "fmtmarty", "gp32", "apple2p", "apple2e", "apple2ee" ]
    if sysName in specialControlList:
        # Load mess controls from csv
        messControlFile = MAME_DEFAULT_DATA / 'messControls.csv'
        openMessFile = messControlFile.open('r')
        with openMessFile:
            controlList = csv.reader(openMessFile, delimiter=';')
            for row in controlList:
                if row[0] not in messControlDict:
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
                    currentEntry['reversed'] = False
                else:
                    currentEntry['reversed'] = True

        config_alt = minidom.Document()
        configFile_alt = cfgPath / f"{sysName}.cfg"
        if (configFile_alt.exists() and cfgPath == (MAME_CONFIG / sysName)) or configFile_alt.exists():
            try:
                config_alt = minidom.parse(str(configFile_alt))
            except Exception:
                pass # reinit the file
        if cfgPath == (MAME_CONFIG / sysName):
            perGameCfg = False
        else:
            perGameCfg = True
        if configFile_alt.exists() and (customCfg or perGameCfg):
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
    for nplayer, pad in enumerate(playersControllers, start=1):
        mappings_use = mappings
        if not hasStick(pad):
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
                    _logger.debug("player %s has a wheel", nplayer)
            if isWheel:
                for x in mappings_use.copy():
                    if mappings_use[x] == "l2" or mappings_use[x] == "r2" or mappings_use[x] == "joystick1left":
                        del mappings_use[x]
                mappings_use["PEDAL"] = "r2"
                mappings_use["PEDAL2"] = "l2"
                mappings_use["PADDLE"] = "joystick1left"

        addCommonPlayerPorts(config, xml_input, nplayer)

        ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
        pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
        pedalkey: str | None = None
        pedalcname = f"controllers.pedals{nplayer}"
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

        # UI Mappings - Clone P1 controls, change the type and append key codes
        if nplayer == 1:
            ports = xml_input.getElementsByTagName('port')
            for port in ports:
                match port.getAttribute('type'):
                    case 'P1_JOYSTICK_UP':
                        copyPort(port, xml_input, 'UI_UP', 'KEYCODE_UP')
                    case 'P1_JOYSTICK_DOWN':
                        copyPort(port, xml_input, 'UI_DOWN', 'KEYCODE_DOWN')
                    case 'P1_JOYSTICK_LEFT':
                        copyPort(port, xml_input, 'UI_LEFT', 'KEYCODE_LEFT')
                    case 'P1_JOYSTICK_RIGHT':
                        copyPort(port, xml_input, 'UI_RIGHT', 'KEYCODE_RIGHT')
                    case 'P1_BUTTON1':
                        copyPort(port, xml_input, 'UI_SELECT', 'KEYCODE_ENTER')

        if useControls in messControlDict:
            for controlDef in messControlDict[useControls]:
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

    # in case there are more guns than pads, configure them
    if useGuns and len(guns) > len(playersControllers):
        for gunnum in range(len(playersControllers)+1, len(guns)+1):
            ### find a keyboard key to simulate the action of the player (always like button 2) ; search in batocera.conf, else default config
            pedalsKeys = {1: "c", 2: "v", 3: "b", 4: "n"}
            pedalkey = None
            pedalcname = f"controllers.pedals{gunnum}"
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
        _logger.debug("Saving %s", configFile)
        with codecs.open(str(configFile), "w", "utf-8") as mameXml:
            dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            mameXml.write(dom_string)

    # Write alt config (if used, custom config is turned off or file doesn't exist yet)
    if sysName in specialControlList and overwriteSystem:
        _logger.debug("Saving %s", configFile_alt)
        with codecs.open(str(configFile_alt), "w", "utf-8") as mameXml_alt:
            dom_string_alt = os.linesep.join([s for s in config_alt.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            mameXml_alt.write(dom_string_alt)

def reverseMapping(key: str) -> str | None:
    if key == "joystick1down":
        return "joystick1up"
    if key == "joystick1right":
        return "joystick1left"
    if key == "joystick2down":
        return "joystick2up"
    if key == "joystick2right":
        return "joystick2left"
    return None

def generatePortElement(pad: Controller, config: minidom.Document, nplayer: int, padindex: int, mapping: str, key: str, input: Input, reversed: bool, altButtons: MameControlScheme, gunmappings: Mapping[str, str], isWheel: bool, mousemappings: Mapping[str, str], multiMouse: bool, pedalkey: str | None):
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = input2definition(pad, key, input, padindex + 1, reversed, altButtons, False, isWheel)
    if mapping in gunmappings:
        keyval = keyval + f" OR GUNCODE_{nplayer}_{gunmappings[mapping]}"
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += f" OR KEYCODE_{pedalkey.upper()}"
    if mapping in mousemappings:
        if multiMouse:
            keyval = keyval + f" OR MOUSECODE_{nplayer}_{mousemappings[mapping]}"
        else:
            keyval = keyval + f" OR MOUSECODE_1_{mousemappings[mapping]}"
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port

def generateGunPortElement(config: minidom.Document, nplayer: int, mapping: str, gunmappings: Mapping[str, str], pedalkey: str | None):
    # Generic input
    xml_port = config.createElement("port")
    if mapping in ["START", "COIN"]:
        xml_port.setAttribute("type", mapping+str(nplayer))
    else:
        xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = None
    if mapping in gunmappings:
        keyval = f"GUNCODE_{nplayer}_{gunmappings[mapping]}"
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += f" OR KEYCODE_{pedalkey.upper()}"
    if keyval is None:
        return None
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElementPlayer(pad: Controller, config: minidom.Document, tag: str, nplayer: int, padindex: int, mapping: str, key: str, input: Input, reversed: bool, mask: str, default: str, gunmappings: Mapping[str, str], mousemappings: Mapping[str, str], multiMouse: bool, pedalkey: str | None):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping+str(nplayer))
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    keyval = input2definition(pad, key, input, padindex + 1, reversed, None)
    if mapping == "COIN" and nplayer <= 4:
        keyval = keyval + f" OR KEYCODE_{nplayer}_{nplayer + 4}" # 5 for player 1, 6 for player 2, 7 for player 3 and 8 for player 4
    if mapping in gunmappings:
        keyval = keyval + f" OR GUNCODE_{nplayer}_{gunmappings[mapping]}"
        if gunmappings[mapping] == "BUTTON2" and pedalkey is not None:
            keyval += f" OR KEYCODE_{pedalkey.upper()}"
    if mapping in mousemappings:
        if multiMouse:
            keyval = keyval + f" OR MOUSECODE_{nplayer}_{mousemappings[mapping]}"
        else:
            keyval = keyval + f" OR MOUSECODE_1_{mousemappings[mapping]}"
    value = config.createTextNode(keyval)
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElement(pad: Controller, config: minidom.Document, tag: str, nplayer: int, padindex: int, mapping: str, key: str, input: Input, reversed: bool, mask: str, default: str, pedalkey: str | None):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(pad, key, input, padindex + 1, reversed, None))
    xml_newseq.appendChild(value)
    return xml_port

def generateComboPortElement(pad: Controller, config: minidom.Document, tag: str, padindex: int, mapping: str, kbkey: str, key: str, input: Input, reversed: bool, mask: str, default: str):
    # Maps a keycode + button - for important keyboard keys when available
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(f"KEYCODE_{kbkey} OR {input2definition(pad, key, input, padindex + 1, reversed, None)}")
    xml_newseq.appendChild(value)
    return xml_port

def generateAnalogPortElement(pad: Controller, config: minidom.Document, tag: str, nplayer: int, padindex: int, mapping: str, inckey: str, deckey: str, mappedinput: Input, mappedinput2: Input, reversed: bool, mask: str, default: str, delta: str, axis: str = ''):
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
    incvalue = config.createTextNode(input2definition(pad, inckey, mappedinput, padindex + 1, reversed, None, True))
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(input2definition(pad, deckey, mappedinput2, padindex + 1, reversed, None, True))
    xml_newseq_dec.appendChild(decvalue)
    xml_newseq_std = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_std)
    xml_newseq_std.setAttribute("type", "standard")
    if axis == '':
        stdvalue = config.createTextNode("NONE")
    else:
        stdvalue = config.createTextNode(f"JOYCODE_{padindex + 1}_{axis}")
    xml_newseq_std.appendChild(stdvalue)
    return xml_port

def input2definition(pad: Controller, key: str, input: Input, joycode: int, reversed: bool, altButtons: MameControlScheme | None, ignoreAxis: bool = False, isWheel: bool = False):

    mameAxisMappingNames = {0: "XAXIS", 1: "YAXIS", 2: "ZAXIS", 3: "RXAXIS", 4: "RYAXIS", 5: "RZAXIS"}

    if isWheel and (key == "joystick1left" or key == "l2" or key == "r2"):
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
    if input.type == "hat":
        if input.value == "1":
            return f"JOYCODE_{joycode}_HAT1UP"
        if input.value == "2":
            return f"JOYCODE_{joycode}_HAT1RIGHT"
        if input.value == "4":
            return f"JOYCODE_{joycode}_HAT1DOWN"
        if input.value == "8":
            return f"JOYCODE_{joycode}_HAT1LEFT"
    elif input.type == "axis":
        # Determine alternate button for D-Pad and right stick as buttons
        dpadInputs: dict[str, str] = {}
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
        buttonDirections: dict[str, str] = {}
        # workarounds for issue #6892
        # Modified because right stick to buttons was not working after the workaround
        # Creates a blank, only modifies if the button exists in the pad.
        # Button assigment modified - blank "OR" gets removed by MAME if the button is undefined.
        for direction in ['a', 'b', 'x', 'y']:
            buttonDirections[direction] = ''
            if direction in pad.inputs and pad.inputs[direction].type == 'button':
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
        for _ in pad.inputs:
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

def hasStick(pad: Controller) -> bool:
    return "joystick1up" in pad.inputs

def getRoot(config: minidom.Document, name: str):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def getSection(config: minidom.Document, xml_root: minidom.Element, name: str):
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def removeSection(config: minidom.Document, xml_root: minidom.Element, name: str):
    xml_section = xml_root.getElementsByTagName(name)

    for i in range(len(xml_section)):
        old = xml_root.removeChild(xml_section[i])
        old.unlink()

def addCommonPlayerPorts(config: minidom.Document, xml_input: minidom.Element, nplayer: int):
    # adstick for guns
    for axis in ["X", "Y"]:
        nanalog = 1 if axis == "X" else 2
        xml_port = config.createElement("port")
        xml_port.setAttribute("tag", f":mainpcb:ANALOG{nanalog}")
        xml_port.setAttribute("type", f"P{nplayer}_AD_STICK_{axis}")
        xml_port.setAttribute("mask", "255")
        xml_port.setAttribute("defvalue", "128")
        xml_newseq = config.createElement("newseq")
        xml_newseq.setAttribute("type", "standard")
        xml_port.appendChild(xml_newseq)
        value = config.createTextNode(f"GUNCODE_{nplayer}_{axis}AXIS")
        xml_newseq.appendChild(value)
        xml_input.appendChild(xml_port)

# Copy a port, change the type and prepend data if provided
def copyPort(port, xml_input, type, data):
    new_port = port.cloneNode(True)
    new_port.setAttribute('type', type)
    if data:
        newseq = new_port.getElementsByTagName("newseq")[0].childNodes[0]
        newseq.nodeValue = data + ' OR ' + newseq.nodeValue
    xml_input.appendChild(new_port)
