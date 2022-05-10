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
from xml.dom import minidom
from PIL import Image, ImageOps

def generatePadsConfig(cfgPath, playersControllers, sysName, dpadMode, altButtons, customCfg, specialController, decorations):
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
    
    # Common controls
    mappings = {
        "JOYSTICK_UP":    "joystick1up",
        "JOYSTICK_DOWN":  "joystick1down",
        "JOYSTICK_LEFT":  "joystick1left",
        "JOYSTICK_RIGHT": "joystick1right",
        "JOYSTICKLEFT_UP":    "joystick1up",
        "JOYSTICKLEFT_DOWN":  "joystick1down",
        "JOYSTICKLEFT_LEFT":  "joystick1left",
        "JOYSTICKLEFT_RIGHT": "joystick1right",
        "JOYSTICKRIGHT_UP": "joystick2up",
        "JOYSTICKRIGHT_DOWN": "joystick2down",
        "JOYSTICKRIGHT_LEFT": "joystick2left",
        "JOYSTICKRIGHT_RIGHT": "joystick2right",
        "BUTTON1": "b",
        "BUTTON2": "a",
        "BUTTON3": "y",
        "BUTTON4": "x",
        "BUTTON5": "pageup",
        "BUTTON6": "pagedown",
        "BUTTON7": "l2",
        "BUTTON8": "r2",
        "BUTTON9": "l3",
        "BUTTON10": "r3",
        "START": "start",
        "COIN": "select"
        #"BUTTON11": "",
        #"BUTTON12": "",
        #"BUTTON13": "",
        #"BUTTON14": "",
        #"BUTTON15": ""
    }

    # Buttons that change based on game/setting
    if altButtons == "sfsnes": # Capcom 6-button Mapping (Based on Street Fighter II for SNES)
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pageup"})
        mappings.update({"BUTTON4": "b"})
        mappings.update({"BUTTON5": "a"})
        mappings.update({"BUTTON6": "pagedown"})
    elif altButtons == "mksnes": # MK 6-button Mapping (Based on Mortal Kombat 3 for SNES)
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "pageup"})
        mappings.update({"BUTTON3": "x"})
        mappings.update({"BUTTON4": "b"})
        mappings.update({"BUTTON5": "a"})
        mappings.update({"BUTTON6": "pagedown"})
    elif altButtons == "kisnes": # KI 6-button Mapping (Based on Killer Instinct for SNES)
        mappings.update({"BUTTON1": "pageup"})
        mappings.update({"BUTTON2": "y"})
        mappings.update({"BUTTON3": "x"})
        mappings.update({"BUTTON4": "pagedown"})
        mappings.update({"BUTTON5": "b"})
        mappings.update({"BUTTON6": "a"})
    elif altButtons == "sfstick": # Capcom 6-button Mapping (the "modern fightstick" layout used in SFIV and above)
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pagedown"})
        mappings.update({"BUTTON4": "b"})
        mappings.update({"BUTTON5": "a"})
        mappings.update({"BUTTON6": "r2"})
        mappings.update({"BUTTON8": "pageup"})
    elif altButtons == "mkstick": # Similar to the Genesis mapping
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pagedown"})
        mappings.update({"BUTTON4": "b"})
        mappings.update({"BUTTON5": "r2"})
        mappings.update({"BUTTON6": "a"})
        mappings.update({"BUTTON7": "pageup"})
        mappings.update({"BUTTON8": "l2"})
    elif altButtons == "mddefault": # Swap of the default controls to match Megadrive, puts buttons 1 - 3 on the bottom row for 3-button controller support.
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "b"})
        mappings.update({"BUTTON3": "a"})
        mappings.update({"BUTTON4": "pageup"})
        mappings.update({"BUTTON5": "x"})
        mappings.update({"BUTTON6": "pagedown"})
    elif altButtons == "megadrive": # Genesis-style controller layout
        mappings.update({"BUTTON1": "pageup"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pagedown"})
        mappings.update({"BUTTON4": "y"})
        mappings.update({"BUTTON5": "b"})
        mappings.update({"BUTTON6": "a"})
    elif altButtons == "mkmegadrive": # Genesis-style controller layout (Ultimate Mortal Kombat 3 version)
        mappings.update({"BUTTON1": "pageup"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pagedown"})
        mappings.update({"BUTTON4": "y"})
        mappings.update({"BUTTON5": "a"})
        mappings.update({"BUTTON6": "b"})
    elif altButtons == "neomini": # Neo Geo Mini
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "b"})
        mappings.update({"BUTTON3": "x"})
        mappings.update({"BUTTON4": "a"})
    elif altButtons == "neoccd": # Neo Geo CD
        mappings.update({"BUTTON1": "b"})
        mappings.update({"BUTTON2": "a"})
        mappings.update({"BUTTON3": "y"})
        mappings.update({"BUTTON4": "x"})
    elif altButtons == "neostick": # Neo Geo Fightstick
        mappings.update({"BUTTON1": "b"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pagedown"})
        mappings.update({"BUTTON4": "pageup"})
        mappings.update({"BUTTON5": "y"})
        mappings.update({"BUTTON6": "a"})
    elif altButtons == "twinstick": # Twinstick with Buttons (Battle Zone, virtual On)
        mappings.update({"BUTTON1": "l2"})
        mappings.update({"BUTTON2": "pageup"})
        mappings.update({"BUTTON3": "r2"})
        mappings.update({"BUTTON4": "pagedown"})
        mappings.update({"BUTTON5": "l3"})
        mappings.update({"BUTTON6": "r3"})
        mappings.update({"BUTTON7": ""})
        mappings.update({"BUTTON8": ""})
        mappings.update({"BUTTON9": ""})
        mappings.update({"BUTTON10": ""})
    elif altButtons == "fightstick": # Generic 8-button Fightstick
        mappings.update({"BUTTON1": "b"})
        mappings.update({"BUTTON2": "a"})
        mappings.update({"BUTTON3": "r2"})
        mappings.update({"BUTTON4": "l2"})
        mappings.update({"BUTTON5": "y"})
        mappings.update({"BUTTON6": "x"})
        mappings.update({"BUTTON7": "pagedown"})
        mappings.update({"BUTTON8": "pageup"})
    
    xml_mameconfig = getRoot(config, "mameconfig")
    xml_mameconfig.setAttribute("version", "10") # otherwise, config of pad won't work at first run (batocera v33)
    xml_system     = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    removeSection(config, xml_system, "input")
    xml_input = config.createElement("input")
    xml_system.appendChild(xml_input)
    
    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    specialControlList = [ "cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb", "bbcm", "bbcm512", "bbcmc", "xegs", "socrates", "vgmplay", "pdp1", "vc4000", "fmtmarty" ]
    if sysName in specialControlList:
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
        xml_system_alt = getSection(config_alt, xml_mameconfig_alt, "system")
        xml_system_alt.setAttribute("name", sysName)
        
        removeSection(config_alt, xml_system_alt, "input")
        xml_input_alt = config_alt.createElement("input")
        xml_system_alt.appendChild(xml_input_alt)
    
    nplayer = 1
    maxplayers = len(playersControllers)
    for playercontroller, pad in sorted(playersControllers.items()):
        mappings_use = mappings
        if "joystick1up" not in pad.inputs:
            mappings_use["JOYSTICK_UP"] = "up"
            mappings_use["JOYSTICK_DOWN"] = "down"
            mappings_use["JOYSTICK_LEFT"] = "left"
            mappings_use["JOYSTICK_RIGHT"] = "right"
            
        for mapping in mappings_use:
            if mappings_use[mapping] in pad.inputs:
                if mapping in [ 'START', 'COIN' ]:
                    xml_input.appendChild(generateSpecialPortElement(config, 'standard', nplayer, pad.index, mapping + str(nplayer), mappings_use[mapping], pad.inputs[mappings_use[mapping]], False, dpadMode, "", ""))
                else:
                    xml_input.appendChild(generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[mappings_use[mapping]], False, dpadMode, altButtons))
            else:
                rmapping = reverseMapping(mappings_use[mapping])
                if rmapping in pad.inputs:
                        xml_input.appendChild(generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[rmapping], True, dpadMode, altButtons))

            #UI Mappings
            if nplayer == 1:
                xml_input.appendChild(generateComboPortElement(config, 'standard', pad.index, "UI_DOWN", "DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "", ""))      # Down
                xml_input.appendChild(generateComboPortElement(config, 'standard', pad.index, "UI_LEFT", "LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "", ""))    # Left
                xml_input.appendChild(generateComboPortElement(config, 'standard', pad.index, "UI_UP", "UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "", ""))            # Up
                xml_input.appendChild(generateComboPortElement(config, 'standard', pad.index, "UI_RIGHT", "RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "", "")) # Right

            # Special case for CD-i - doesn't use default controls, map special controller
            # Keep orginal mapping functions for menus etc, create system-specific config file dor CD-i.
            if nplayer == 1 and sysName == "cdimono1":
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "1", "0"))
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON2", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "2", "0"))
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON3", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "4", "0"))
                xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", mappings_use["JOYSTICK_RIGHT"], mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "65535", "0", "10", "XAXIS"))
                xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", mappings_use["JOYSTICK_DOWN"], mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], pad.inputs[mappings_use["JOYSTICK_UP"]],False, dpadMode, "65535", "0", "10", "YAXIS"))
                
                #Hide LCD display
                removeSection(config_alt, xml_system_alt, "video")
                xml_video_alt = config_alt.createElement("video")
                xml_system_alt.appendChild(xml_video_alt)
                
                xml_screencfg_alt = config_alt.createElement("target")
                xml_screencfg_alt.setAttribute("index", "0")
                if decorations == None:
                    xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
                else:
                    xml_screencfg_alt.setAttribute("view", "Upright_Artwork")
                xml_video_alt.appendChild(xml_screencfg_alt)
                
            # Special case for APFM1000 - uses numpad controllers
            if nplayer <= 2 and sysName == "apfm1000":
                if nplayer == 1:
                    # Based on Colecovision button mapping, changed slightly since Enter = Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "32", "32"))     # Clear
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "32", "32"))     # Enter/Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "16", "16"))     # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "16", "16"))     # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "16", "16"))     # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "64", "64"))     # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "64", "64"))     # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "64", "64"))     # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "128", "128")) # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "128", "128"))   # 8
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "128", "128"))         # 9
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "32", "32"))         # 0
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "2", "2"))   # Clear
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "2", "2"))   # Enter/Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "1", "1"))   # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "1", "1"))   # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "1", "1"))   # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "4", "4"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "4", "4"))   # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "4", "4"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "8", "8")) # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "8", "8"))   # 8
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "8", "8"))         # 9
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "2", "2"))       # 0

            # Special case for Astrocade - numpad on console
            if nplayer == 1 and sysName == "astrocde":
                # Based on Colecovision button mapping, keypad is on the console
                # A auto maps to Fire, using B for 0, Select for 9, Start for = (which is the "enter" key)
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "32", "0"))  # 0
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "16", "0"))  # 1
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "16", "0"))  # 2
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "16", "0"))  # 3
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "8", "0"))   # 4
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "8", "0"))   # 5
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "8", "0"))   # 6
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "4", "0")) # 7
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "4", "0"))   # 8
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "4", "0"))         # 9
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD0', nplayer, pad.index, "KEYPAD", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "32", "0"))      # = (Start)
            
            # Special case for Adam - numpad
            if nplayer == 1 and sysName == "adam":
                # Based on Colecovision button mapping - not enough buttons to map 0 & 9
                # Fire 1 & 2 map to A & B
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "2", "2"))       # 1
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "4", "4"))       # 2
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "8", "8"))       # 3
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "16", "16"))     # 4
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "32", "32"))     # 5
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "64", "64"))     # 6
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "128", "128")) # 7
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "512", "512"))   # 8
                # ':joy1:hand:KEYPAD', "KEYPAD", 128", "128"                                                                                                                                                                          9
                # ':joy1:hand:KEYPAD', "KEYPAD", 1", "1"                                                                                                                                                                              0
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "1024", "0"))        # #
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "2048", "0"))          # *
            
            # Special case for Arcadia
            if nplayer <= 2 and sysName == "arcadia":
                if nplayer == 1:
                    # Based on Colecovision button mapping - not enough buttons to map clear, enter
                    # No separate fire button, Start + Select on console (automapped), Option button also on console.
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "8", "0"))   # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "8", "0"))   # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "8", "0"))   # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "4", "0"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "4", "0"))   # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "4", "0"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "2", "0"))   # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "2", "0"))   # 8
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "2", "0")) # 9
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "1", "0"))   # 0
                    # ':controller1_col1', "KEYPAD", 1", "0"                                                                                                                                                                          Clear
                    # ':controller1_col3', "KEYPAD", 1", "0"                                                                                                                                                                          Enter
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "8", "0"))   # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "8", "0"))   # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "8", "0"))   # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "4", "0"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "4", "0"))   # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "4", "0"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "2", "0"))   # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "2", "0"))   # 8
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "2", "0")) # 9
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "1", "0"))   # 0
                    # ':controller1_col1', "KEYPAD", "1", "0"                                                                                                                                                                         Clear
                    # ':controller1_col3', "KEYPAD", "1", "0"                                                                                                                                                                         Enter
            
            # Special case for Gamecom - buttons don't map normally
            if nplayer == 1 and sysName == "gamecom":
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN0', nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "128", "128")) # A
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN1', nplayer, pad.index, "P1_BUTTON2", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "1", "1"))     # B
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN1', nplayer, pad.index, "P1_BUTTON3", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "2", "2"))     # C
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN2', nplayer, pad.index, "P1_BUTTON4", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "2", "2"))     # D
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN0', nplayer, pad.index, "OTHER", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "16", "16"))              # Menu
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN0', nplayer, pad.index, "OTHER", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "32", "32"))            # Pause
            
            # Special case for Tomy Tutor - directions don't map normally
            # Also maps arrow keys to directional input & enter to North button to get through the initial menu without a keyboard
            if nplayer <= 2 and sysName == "tutor":
                if nplayer == 1:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "16", "0"))      # Down
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "32", "0"))    # Left
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "64", "0"))          # Up
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "128", "0")) # Right
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':LINE6', pad.index, "KEYBOARD", "ENTER", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "16", "0"))                              # Enter Key
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':LINE7', pad.index, "KEYBOARD", "DOWN", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "4", "0"))                                # Down Arrow
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "16", "0"))      # Down
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "32", "0"))    # Left
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "64", "0"))          # Up
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "128", "0")) # Right
            
            # Special case for crvision - maps the 4 corner buttons + 2nd from upper right since MAME considers that button 2.
            if nplayer <= 2 and sysName == "crvision":
                if nplayer == 1:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA1.7', nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "128", "128")) # P1 Button 1 (Shift)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA0.7', nplayer, pad.index, "P1_BUTTON2", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "128", "128")) # P1 Button 2 (Control)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA0.2', nplayer, pad.index, "KEYBOARD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "8", "8"))       # P1 Upper Right (1)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA1.1', nplayer, pad.index, "KEYBOARD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "4", "4"))       # P1 Lower Left (B)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA1.4', nplayer, pad.index, "KEYBOARD", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "64", "64"))     # P1 Lower Right (6)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':NMI', nplayer, pad.index, "P1_START", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "1", "0"))             # Reset/Start
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA3.7', nplayer, pad.index, "P2_BUTTON1", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "128", "128"))  # P2 Button 1 (-/=)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA2.7', nplayer, pad.index, "P2_BUTTON2", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "128", "128"))  # P2 Button 2 (Right)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA2.2', nplayer, pad.index, "KEYBOARD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "8", "8")) # P2 Upper Right (Space)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA3.1', nplayer, pad.index, "KEYBOARD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "4", "4"))        # P2 Lower Left (7)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA3.1', nplayer, pad.index, "KEYBOARD", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "64", "64"))      # P2 Lower Right (N)
            
            # BBC Micro - joystick not emulated/supported for most games, map some to gamepad
            if nplayer <= 2 and sysName in [ "bbcb", "bbcm", "bbcm512", "bbcmc" ]:
                if specialController == 'none' and nplayer == 1:
                    xml_kbenable_alt = config_alt.createElement("keyboard")
                    xml_kbenable_alt.setAttribute("tag", ":")
                    xml_kbenable_alt.setAttribute("enabled", "1")
                    xml_input_alt.appendChild(xml_kbenable_alt)
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL8', pad.index, "KEYBOARD", "QUOTE", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "64", "64"))                # *
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL8', pad.index, "KEYBOARD", "SLASH", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "16", "16"))                # ?
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL1', pad.index, "KEYBOARD", "Z", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "64", "64"))                    # Z
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL2', pad.index, "KEYBOARD", "X", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "16", "16"))                    # X
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "ENTER", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "16", "16"))                # Enter
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "4", "4"))         # Down
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "2", "2"))       # Left
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "8", "8"))             # Up
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "128", "128")) # Right
                elif specialController in ['acornjoy','voltmace3b']:
                    if nplayer == 1:
                        xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':analogue:{}:BUTTONS'.format(specialController), nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "16", "16"))                                                             # P1 Button
                        xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:JOY0'.format(specialController), nplayer, pad.index, "P1_AD_STICK_X", mappings_use["JOYSTICK_RIGHT"], mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "255", "128", "10", "XAXIS")) # P1 X Axis
                        xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:JOY1'.format(specialController), nplayer, pad.index, "P1_AD_STICK_Y", mappings_use["JOYSTICK_DOWN"], mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], pad.inputs[mappings_use["JOYSTICK_UP"]] ,False, dpadMode, "255", "128", "10", "YAXIS"))      # P1 Y Axis
                    elif nplayer == 2:
                        xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':analogue:{}:BUTTONS'.format(specialController), nplayer, pad.index, "P2_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "32", "32"))                                                             # P2 Button
                        xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:JOY2'.format(specialController), nplayer, pad.index, "P2_AD_STICK_X", mappings_use["JOYSTICK_RIGHT"], mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "255", "128", "10", "XAXIS")) # P2 X Axis
                        xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:JOY3'.format(specialController), nplayer, pad.index, "P2_AD_STICK_Y", mappings_use["JOYSTICK_DOWN"], mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "255", "128", "10", "YAXIS"))      # P2 Y Axis
                elif specialController in ['bitstik1','bitstik2'] and nplayer == 1:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':analogue:{}:BUTTONS'.format(specialController), nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "16", "16"))                                                               # P1 Button 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':analogue:{}:BUTTONS'.format(specialController), nplayer, pad.index, "P1_BUTTON2", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "32", "32"))                                                               # P1 Button 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':analogue:{}:BUTTONS'.format(specialController), nplayer, pad.index, "P1_BUTTON3", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "255", "255"))                                                             # P1 Button 3
                    xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:CHANNEL0'.format(specialController), nplayer, pad.index, "P1_AD_STICK_X", mappings_use["JOYSTICK_RIGHT"], mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "255", "0", "10", "XAXIS")) # P1 X Axis
                    xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:CHANNEL1'.format(specialController), nplayer, pad.index, "P1_AD_STICK_Y", mappings_use["JOYSTICK_DOWN"], mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "255", "0", "10", "YAXIS"))      # P1 Y Axis
                    xml_input_alt.appendChild(generateAnalogPortElement(config_alt, ':analogue:{}:CHANNEL2'.format(specialController), nplayer, pad.index, "P1_AD_STICK_Z", mappings_use["BUTTON5"], mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON5"]], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "255", "0", "10", "ZAXIS"))                    # P1 Z Axis

            # Special case for Atari XEGS, normally maps only to analog stick and buttons do not use normal button 1/2.
            if nplayer <= 2 and sysName == "xegs":
                if nplayer == 1:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P1_JOYSTICK_DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "2", "2"))    # Down
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P1_JOYSTICK_LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "4", "4"))  # Left
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P1_JOYSTICK_UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "1", "1"))        # Up
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P1_JOYSTICK_RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "8", "8")) # Right
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_b', nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "1", "1"))                      # P1 Button 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_b', nplayer, pad.index, "P1_BUTTON2", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "16", "16"))                    # P1 Button 2
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P2_JOYSTICK_DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "32", "32"))       # Down
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P2_JOYSTICK_LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "64", "64"))     # Left
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P2_JOYSTICK_UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "16", "16"))           # Up
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_0_1', nplayer, pad.index, "P2_JOYSTICK_RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "128", "128")) # Right
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_b', nplayer, pad.index, "P2_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "2", "2"))                           # P2 Button 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':djoy_b', nplayer, pad.index, "P2_BUTTON2", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "32", "32"))                         # P2 Button 2

            # Socrates uses a keyboard + 2 detachable D-pad controllers, map the controllers to gamepads.
            if nplayer <= 2 and sysName == "socrates":
                if nplayer == 1:
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "2PAD", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "8", "0"))    # Down
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "4PAD", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "4", "0"))  # Left
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "8PAD", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "2", "0"))      # Up
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "6PAD", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "1", "0")) # Right
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "ENTERPAD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "256", "0"))        # P1 Button
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "DOWN", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "16", "0"))      # Down
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "32", "0"))    # Left
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "UP", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "64", "0"))          # Up
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "128", "0")) # Right
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':IN5', pad.index, "KEYBOARD", "RALT", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "512", "0"))               # P2 Button

            #VGM Player mapping
            if nplayer == 1 and sysName == "vgmplay":
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "1", "0"))            # Stop
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON2", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "2", "0"))                # Pause
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON3", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "4", "0"))            # Play
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON4", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "8", "0"))            # Restart
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON5", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "16", "0"))           # Loop
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON6", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "32", "0"))           # Change Visualization Mode
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON7", mappings_use["JOYSTICK_DOWN"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "64", "0")) # Rate Down
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON8", mappings_use["JOYSTICK_UP"], pad.inputs[mappings_use["JOYSTICK_UP"]], False, dpadMode, "128", "0"))  # Rate Up
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON9", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "256", "0"))          # Rate Reset
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':CONTROLS', nplayer, pad.index, "P1_BUTTON10", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "512", "0"))         # Rate Hold
                xml_input.appendChild(generateSpecialPortElement(config, 'standard', nplayer, pad.index, "UI_CONFIGURE", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "", ""))                           # MAME Menu
        
            # FM Towns (Marty) Run button mapping, the rest map properly automatically.
            if nplayer == 1 and sysName == "fmtmarty":
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1_ex', nplayer, pad.index, "P1_START", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "1", "0")) # Run

            # Punchtape loading & Spacewar controls for PDP-1
            if nplayer <= 2 and sysName == "pdp1":
                if nplayer == 1:
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':CSW', pad.index, "KEYBOARD", "LCONTROL", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "1", "0"))                                # Control Panel Switch
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':CSW', pad.index, "KEYBOARD", "ENTER", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "256", "0"))                                 # Load Punchtape
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P1_JOYSTICK_LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "1", "0"))    # P1 Spin Left
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P1_JOYSTICK_RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "2", "0"))  # P1 Spin Right
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P1_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "4", "0"))                      # P1 Thrust
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P1_BUTTON2", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "8", "0"))                      # P1 Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P1_BUTTON3", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "256", "0"))                    # P1 Hyperspace
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P2_JOYSTICK_LEFT", mappings_use["JOYSTICK_LEFT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "16", "0"))   # P2 Spin Left
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P2_JOYSTICK_RIGHT", mappings_use["JOYSTICK_RIGHT"], pad.inputs[mappings_use["JOYSTICK_LEFT"]], False, dpadMode, "32", "0")) # P2 Spin Right
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P2_BUTTON1", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "64", "0"))                     # P2 Thrust
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P2_BUTTON2", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "128", "0"))                    # P2 Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':SPACEWAR', nplayer, pad.index, "P2_BUTTON3", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "512", "0"))                    # P2 Hyperspace

            # Special case for VC4000 - uses numpad controllers
            if nplayer <= 2 and sysName == "vc4000":
                if nplayer == 1:
                    # Based on Colecovision button mapping, rearranged slightly since 2 = fire, not enough inputs
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "128", "0"))  # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "128", "0"))  # 2/Button
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "128", "0"))  # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "64", "0"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "64", "0"))   # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "64", "0"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "32", "0"))   # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "32", "0"))   # 8
                    # ':KEYPAD1_3', 'KEYPAD', '32', '0'                                                                                                                                                                         9
                    # ':KEYPAD1_2', 'KEYPAD', '16', '0'                                                                                                                                                                         0
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "16", "0")) # Enter
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1_3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "16", "0"))   # Clear
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PANEL', nplayer, pad.index, "P1_SELECT", mappings_use["COIN"], pad.inputs[mappings_use["COIN"]], False, dpadMode, "128", "0"))         # Game Select
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PANEL', nplayer, pad.index, "P1_START", mappings_use["START"], pad.inputs[mappings_use["START"]], False, dpadMode, "64", "0"))         # Start
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON3"], pad.inputs[mappings_use["BUTTON3"]], False, dpadMode, "128", "0"))  # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON1"], pad.inputs[mappings_use["BUTTON1"]], False, dpadMode, "128", "0"))  # 2/Button
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON4"], pad.inputs[mappings_use["BUTTON4"]], False, dpadMode, "128", "0"))  # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON2"], pad.inputs[mappings_use["BUTTON2"]], False, dpadMode, "64", "0"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON6"], pad.inputs[mappings_use["BUTTON6"]], False, dpadMode, "64", "0"))   # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON5"], pad.inputs[mappings_use["BUTTON5"]], False, dpadMode, "64", "0"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON8"], pad.inputs[mappings_use["BUTTON8"]], False, dpadMode, "32", "0"))   # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_2', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON7"], pad.inputs[mappings_use["BUTTON7"]], False, dpadMode, "32", "0"))   # 8
                    # ':KEYPAD2_3', 'KEYPAD', '32', '0'                                                                                                                                                                         9
                    # ':KEYPAD2_2', 'KEYPAD', '16', '0'                                                                                                                                                                         0
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_1', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON10"], pad.inputs[mappings_use["BUTTON10"]], False, dpadMode, "16", "0")) # Enter
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2_3', nplayer, pad.index, "KEYPAD", mappings_use["BUTTON9"], pad.inputs[mappings_use["BUTTON9"]], False, dpadMode, "16", "0"))   # Clear

        nplayer = nplayer + 1
        
        # save the config file
        #mameXml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        if overwriteMAME:
            mameXml = codecs.open(configFile, "w", "utf-8")
            dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            mameXml.write(dom_string)
        
        # Write alt config (if used, custom config is turned off or file doesn't exist yet)
        if sysName in specialControlList and overwriteSystem:
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

def generatePortElement(config, nplayer, padindex, mapping, key, input, reversed, dpadMode, altButtons):
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(key, input, padindex + 1, reversed, dpadMode, altButtons))
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElement(config, tag, nplayer, padindex, mapping, key, input, reversed, dpadMode, mask, default):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(key, input, padindex + 1, reversed, dpadMode, 0))
    xml_newseq.appendChild(value)
    return xml_port

def generateComboPortElement(config, tag, padindex, mapping, kbkey, key, input, reversed, dpadMode, mask, default):
    # Maps a keycode + button - for important keyboard keys when available
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode("KEYCODE_{} OR ".format(kbkey) + input2definition(key, input, padindex + 1, reversed, dpadMode, 0))
    xml_newseq.appendChild(value)
    return xml_port

def generateAnalogPortElement(config, tag, nplayer, padindex, mapping, inckey, deckey, mappedinput, mappedinput2, reversed, dpadMode, mask, default, delta, axis = ''):
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
    incvalue = config.createTextNode(input2definition(inckey, mappedinput, padindex + 1, reversed, dpadMode, 0))
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(input2definition(deckey, mappedinput2, padindex + 1, reversed, dpadMode, 0))
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

def input2definition(key, input, joycode, reversed, dpadMode, altButtons):
    if input.type == "button":
        return "JOYCODE_{}_BUTTON{}".format(joycode, int(input.id)+1)
    elif input.type == "hat":
        if input.value == "1":
            return "JOYCODE_{}_HAT1UP".format(joycode)
        elif input.value == "2":
            return "JOYCODE_{}_HAT1RIGHT".format(joycode)
        elif input.value == "4":
            return "JOYCODE_{}_HAT1DOWN".format(joycode)
        elif input.value == "8":
            return "JOYCODE_{}_HAT1LEFT".format(joycode)
    elif input.type == "axis":
        if altButtons == "qbert": # Q*Bert Joystick
            if key == "joystick1up" or key == "up":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH JOYCODE_{}_XAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1UP JOYCODE_{}_HAT1RIGHT".format(joycode, joycode, joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH JOYCODE_{}_XAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1UP JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON13 JOYCODE_{}_BUTTON16".format(joycode, joycode, joycode, joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH JOYCODE_{}_XAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1UP JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON13 JOYCODE_{}_BUTTON12".format(joycode, joycode, joycode, joycode, joycode, joycode)
            if key == "joystick1down" or key == "down":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH JOYCODE_{}_XAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1DOWN JOYCODE_{}_HAT1LEFT".format(joycode, joycode, joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH JOYCODE_{}_XAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1DOWN JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON14 JOYCODE_{}_BUTTON15".format(joycode, joycode, joycode, joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH JOYCODE_{}_XAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1DOWN JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON14 JOYCODE_{}_BUTTON11".format(joycode, joycode, joycode, joycode, joycode, joycode)
            if key == "joystick1left" or key == "left":
                if dpadMode == 0:
                    return "JOYCODE_{}_XAXIS_LEFT_SWITCH JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1LEFT JOYCODE_{}_HAT1UP".format(joycode, joycode, joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_XAXIS_LEFT_SWITCH JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1LEFT JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON15 JOYCODE_{}_BUTTON13".format(joycode, joycode, joycode, joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_XAXIS_LEFT_SWITCH JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1LEFT JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON11 JOYCODE_{}_BUTTON13".format(joycode, joycode, joycode, joycode, joycode, joycode)
            if key == "joystick1right" or key == "right":
                if dpadMode == 0:
                    return "JOYCODE_{}_XAXIS_RIGHT_SWITCH JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1RIGHT JOYCODE_{}_HAT1DOWN".format(joycode, joycode, joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_XAXIS_RIGHT_SWITCH JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1RIGHT JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON16 JOYCODE_{}_BUTTON14".format(joycode, joycode, joycode, joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_XAXIS_RIGHT_SWITCH JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1RIGHT JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON12 JOYCODE_{}_BUTTON14".format(joycode, joycode, joycode, joycode, joycode, joycode)
        else:        
            if key == "joystick1up" or key == "up":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP".format(joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13".format(joycode, joycode, joycode)
            if key == "joystick1down" or key == "down":
                if dpadMode == 0:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN".format(joycode, joycode)
                else:
                    return "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14".format(joycode, joycode, joycode)
            if key == "joystick1left" or key == "left":
                if dpadMode == 0:
                    return "JOYCODE_{}_XAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT".format(joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_XAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15".format(joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_XAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11".format(joycode, joycode, joycode)
            if key == "joystick1right" or key == "right":
                if dpadMode == 0:
                    return "JOYCODE_{}_XAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT".format(joycode, joycode)
                elif dpadMode == 1:
                    return "JOYCODE_{}_XAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16".format(joycode, joycode, joycode)
                else:
                    return "JOYCODE_{}_XAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12".format(joycode, joycode, joycode)
        if key == "joystick2up":
            return "JOYCODE_{}_RYAXIS_NEG_SWITCH OR JOYCODE_{}_BUTTON4".format(joycode, joycode)
        if key == "joystick2down":
            return "JOYCODE_{}_RYAXIS_POS_SWITCH OR JOYCODE_{}_BUTTON1".format(joycode, joycode)
        if key == "joystick2left":
            return "JOYCODE_{}_RXAXIS_NEG_SWITCH OR JOYCODE_{}_BUTTON3".format(joycode, joycode)
        if key == "joystick2right":
            return "JOYCODE_{}_RXAXIS_POS_SWITCH OR JOYCODE_{}_BUTTON2".format(joycode, joycode)
        if int(input.id) == 2: # XInput L2
            return "JOYCODE_{}_ZAXIS_POS_SWITCH".format(joycode)
        if int(input.id) == 5: # XInput R2
            return "JOYCODE_{}_RZAXIS_POS_SWITCH".format(joycode)
    return "unknown"

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
