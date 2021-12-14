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

def generatePadsConfig(config, playersControllers, sysName, dpadMode, cfgPath, altButtons):
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
        "BUTTON2": "y",
        "BUTTON3": "a",
        "BUTTON4": "x",
        "BUTTON5": "pageup",
        "BUTTON6": "pagedown",
        "BUTTON7": "l2",
        "BUTTON8": "r2",
        "BUTTON9": "l3",
        "BUTTON10": "r3"
        #"BUTTON11": "",
        #"BUTTON12": "",
        #"BUTTON13": "",
        #"BUTTON14": "",
        #"BUTTON15": ""
    }
    # Buttons that change based on game/setting
    if altButtons == 1: # Capcom 6-button Mapping (Based on Street Fighter II for SNES)
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "x"})
        mappings.update({"BUTTON3": "pageup"})
        mappings.update({"BUTTON4": "b"})
        mappings.update({"BUTTON5": "a"})
        mappings.update({"BUTTON6": "pagedown"})
    elif altButtons == 2: # MK 6-button Mapping (Based on Mortal Kombat 3 for SNES)
        mappings.update({"BUTTON1": "y"})
        mappings.update({"BUTTON2": "pageup"})
        mappings.update({"BUTTON3": "x"})
        mappings.update({"BUTTON4": "b"})
        mappings.update({"BUTTON5": "a"})
        mappings.update({"BUTTON6": "pagedown"})
    elif altButtons == 3: # KI 6-button Mapping (Based on Killer Instinct for SNES)
        mappings.update({"BUTTON1": "pageup"})
        mappings.update({"BUTTON2": "y"})
        mappings.update({"BUTTON3": "x"})
        mappings.update({"BUTTON4": "pagedown"})
        mappings.update({"BUTTON5": "b"})
        mappings.update({"BUTTON6": "a"})
    
    xml_mameconfig = getRoot(config, "mameconfig")
    xml_system     = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    removeSection(config, xml_system, "input")
    xml_input = config.createElement("input")
    xml_system.appendChild(xml_input)
    
    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    if sysName in ("cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb"):
        config_alt = minidom.Document()
        configFile_alt = cfgPath + sysName + ".cfg"
        if os.path.exists(configFile_alt) and cfgPath == "/userdata/system/configs/mame/":
            writeConfig = True
            try:
                config_alt = minidom.parse(configFile_alt)
            except:
                pass # reinit the file
        elif not os.path.exists(configFile_alt):
            writeConfig = True
        else:
            writeConfig = False
            try:
                config_alt = minidom.parse(configFile_alt)
            except:
                pass # reinit the file
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
                xml_input.appendChild(generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[mappings_use[mapping]], False, dpadMode))
            else:
                rmapping = reverseMapping(mappings_use[mapping])
                if rmapping in pad.inputs:
                        xml_input.appendChild(generatePortElement(config, nplayer, pad.index, mapping, mappings_use[mapping], pad.inputs[rmapping], True, dpadMode))
                
            # Special case for CD-i - doesn't use default controls, map special controller
            # Keep orginal mapping functions for menus etc, create system-specific config file dor CD-i.
            if nplayer == 1 and sysName == "cdimono1":
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON1", int(pad.inputs["b"].id) + 1, "1", "0"))
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':slave_hle:MOUSEBTN', nplayer, pad.index, "P1_BUTTON2", int(pad.inputs["y"].id) + 1, "2", "0"))
                if dpadMode == 0:
                    xml_input_alt.appendChild(generateIncDecPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "1023", "0", "10"))
                    xml_input_alt.appendChild(generateIncDecPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "1023", "0", "10"))
                elif dpadMode == 1:
                    xml_input_alt.appendChild(generateIncDecPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "1023", "0", "10"))
                    xml_input_alt.appendChild(generateIncDecPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "1023", "0", "10"))
                else:
                    xml_input_alt.appendChild(generateIncDecPortElement(config_alt, ':slave_hle:MOUSEX', nplayer, pad.index, "P1_MOUSE_X", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "1023", "0", "10"))
                    xml_input_alt.appendChild(generateIncDecPortElement(config_alt, ':slave_hle:MOUSEY', nplayer, pad.index, "P1_MOUSE_Y", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "1023", "0", "10"))
                
                #Hide LCD display
                removeSection(config_alt, xml_system_alt, "video")
                xml_video_alt = config_alt.createElement("video")                
                xml_system_alt.appendChild(xml_video_alt)
                
                xml_screencfg_alt = config_alt.createElement("target")
                xml_screencfg_alt.setAttribute("index", "0")
                xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
                xml_video_alt.appendChild(xml_screencfg_alt)
                
            # Special case for APFM1000 - uses numpad controllers
            if nplayer <= 2 and sysName == "apfm1000":
                if nplayer == 1:
                    # Based on Colecovision button mapping, changed slightly since Enter = Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", int(pad.inputs["a"].id) + 1, "32", "32"))        # Clear
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["b"].id) + 1, "32", "32"))        # Enter/Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", int(pad.inputs["x"].id) + 1, "16", "16"))        # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["y"].id) + 1, "16", "16"))        # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", int(pad.inputs["pagedown"].id) + 1, "16", "16")) # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", int(pad.inputs["pageup"].id) + 1, "64", "64"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["r2"].id) + 1, "64", "64"))       # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "OTHER", int(pad.inputs["l2"].id) + 1, "64", "64"))       # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "OTHER", int(pad.inputs["r3"].id) + 1, "128", "128"))     # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "OTHER", int(pad.inputs["l3"].id) + 1, "128", "128"))     # 8
                    xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':joy.2', "OTHER", "5", "128", "128"))                                                  # 9
                    xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':joy.0', "OTHER", "1", "32", "32"))                                                    # 0
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["a"].id) + 1, "2", "2"))        # Clear
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["b"].id) + 1, "2", "2"))        # Enter/Fire
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["x"].id) + 1, "1", "1"))        # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["y"].id) + 1, "1", "1"))        # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["pagedown"].id) + 1, "1", "1")) # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["pageup"].id) + 1, "4", "4"))   # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["r2"].id) + 1, "4", "4"))       # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.2', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["l2"].id) + 1, "4", "4"))       # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.0', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["r3"].id) + 1, "8", "8"))       # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy.3', nplayer, pad.index, "TYPE_OTHER(243,1)", int(pad.inputs["l3"].id) + 1, "8", "8"))       # 8
                    xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':joy.2', "TYPE_OTHER(243,1)", "6", "8", "8"))                                                    # 9
                    xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':joy.0', "TYPE_OTHER(243,1)", "2", "2", "2"))                                                    # 0
            # Special case for Astrocade - numpad on console
            if nplayer == 1 and sysName == "astrocde":
                # Based on Colecovision button mapping, keypad is on the console
                # A auto maps to Fire, using B for 0, Select for 9, Start for = (which is the "enter" key)
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["b"].id) + 1, "32", "0"))        # 0
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "16", "0"))        # 1
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["y"].id) + 1, "16", "0"))        # 2
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "16", "0")) # 3
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "8", "0"))    # 4
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "8", "0"))        # 5
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD1', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "8", "0"))        # 6
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD3', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "4", "0"))        # 7
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':KEYPAD2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "4", "0"))        # 8
                xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':KEYPAD1', "KEYPAD", "6", "4", "0"))                                                     # 9
                xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':KEYPAD0', "KEYPAD", "1", "32", "0"))                                                    # = (Start)
            
            # Special case for Adam - numpad
            if nplayer == 1 and sysName == "adam":
                # Based on Colecovision button mapping - not enough buttons to map 0 & 9
                # Fire 1 & 2 map to A & B
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "2", "2"))          # 1
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["a"].id) + 1, "4", "4"))          # 2
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "8", "8"))   # 3
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "16", "16"))   # 4
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "32", "32"))       # 5
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "64", "64"))       # 6
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "128", "128"))     # 7
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "512", "512"))     # 8
                # xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "128", "128"))     9
                # xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':joy1:hand:KEYPAD', nplayer, pad.index, "KEYPAD", , "1", ""))                                      0                
                xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':joy1:hand:KEYPAD', "KEYPAD", "1", "1024", "0"))                                                   # #
                xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':joy1:hand:KEYPAD', "KEYPAD", "5", "2048", "0"))                                                   # *
            
            # Special case for Arcadia
            if nplayer <= 2 and sysName == "arcadia":
                if nplayer == 1:
                    # Based on Colecovision button mapping - not enough buttons to map clear, enter
                    # No separate fire button, Start + Select on console (automapped), Option button also on console.
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["a"].id) + 1, "8", "0"))        # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["b"].id) + 1, "8", "0"))        # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "8", "0"))        # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["y"].id) + 1, "4", "0"))        # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "4", "0")) # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "4", "0"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "2", "0"))       # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "2", "0"))       # 8
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "2", "0"))       # 9
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "1", "0"))       # 0
                    # xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Clear
                    # xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Enter
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["a"].id) + 1, "8", "0"))        # 1
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["b"].id) + 1, "8", "0"))        # 2
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["x"].id) + 1, "8", "0"))        # 3
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["y"].id) + 1, "4", "0"))        # 4
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["pagedown"].id) + 1, "4", "0")) # 5
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["pageup"].id) + 1, "4", "0"))   # 6
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col1', nplayer, pad.index, "KEYPAD", int(pad.inputs["r2"].id) + 1, "2", "0"))       # 7
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col2', nplayer, pad.index, "KEYPAD", int(pad.inputs["l2"].id) + 1, "2", "0"))       # 8
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["r3"].id) + 1, "2", "0"))       # 9
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller2_col3', nplayer, pad.index, "KEYPAD", int(pad.inputs["l3"].id) + 1, "1", "0"))       # 0
                    # xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col1', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Clear
                    # xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':controller1_col3', nplayer, pad.index, "KEYPAD", , "1", "0"))                                 # Enter
            
            # Special case for Gamecom - buttons don't map normally
            if nplayer == 1 and sysName == "gamecom":
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN0', nplayer, pad.index, "P1_BUTTON1", int(pad.inputs["y"].id) + 1, "128", "128")) # A
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN1', nplayer, pad.index, "P1_BUTTON2", int(pad.inputs["x"].id) + 1, "1", "1"))     # B
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN1', nplayer, pad.index, "P1_BUTTON3", int(pad.inputs["b"].id) + 1, "2", "2"))     # C
                xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':IN2', nplayer, pad.index, "P1_BUTTON4", int(pad.inputs["a"].id) + 1, "2", "2"))     # D
                xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':IN0', "OTHER", "5", "16", "16"))                                                    # Menu
                xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':IN0', "OTHER", "1", "32", "32"))                                                    # Pause
            
            # Special case for Tomy Tutor - directions don't map normally
            # Also maps arrow keys to directional input & enter to North button to get through the initial menu without a keyboard
            if nplayer <= 2 and sysName == "tutor":
                if nplayer == 1:
                    if dpadMode == 0:
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "16", "0"))     # Down
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "32", "0"))     # Left
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "64", "0"))           # Up
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "128", "0")) # Right
                    elif dpadMode == 1:
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "16", "0"))     # Down
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "32", "0"))     # Left
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "128", "0")) # Right
                    else:                        
                        xml_input_dChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "32", "0"))     # Left
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE4_alt', nplayer, pad.index, "P1_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "128", "0")) # Right
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':LINE6', pad.index, "KEYBOARD", "ENTER", int(pad.inputs["a"].id) + 1, "16", "0"))      # Enter Key
                    xml_input_alt.appendChild(generateComboPortElement(config_alt, ':LINE7', pad.index, "KEYBOARD", "DOWN", int(pad.inputs["pagedown"].id) + 1, "4", "0")) # Down Arrow
                elif nplayer == 2:
                    if dpadMode == 0:
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "16", "0"))     # Down
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "32", "0"))     # Left
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "64", "0"))           # Up
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "128", "0")) # Right
                    elif dpadMode == 1:
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "16", "0"))     # Down
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "32", "0"))     # Left
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "128", "0")) # Right
                    else:
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "16", "0"))     # Down
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "32", "0"))     # Left
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "64", "0"))           # Up
                        xml_input_alt.appendChild(generateDirectionPortElement(config_alt, ':LINE2_alt', nplayer, pad.index, "P2_JOYSTICK_RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "128", "0")) # Right
            
            # Special case for crvision - maps the 4 corner buttons + 2nd from upper right since MAME considers that button 2.
            if nplayer <= 2 and sysName == "crvision":
                if nplayer == 1:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA1.7', nplayer, pad.index, "P1_BUTTON1", int(pad.inputs["y"].id) + 1, "128", "128"))  # P1 Button 1 (Shift)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA0.7', nplayer, pad.index, "P1_BUTTON2", int(pad.inputs["x"].id) + 1, "128", "128"))  # P1 Button 2 (Control)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA0.2', nplayer, pad.index, "KEYBOARD", int(pad.inputs["pagedown"].id) + 1, "8", "8")) # P1 Upper Right (1)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA1.1', nplayer, pad.index, "KEYBOARD", int(pad.inputs["b"].id) + 1, "4", "4"))        # P1 Lower Left (B)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA1.4', nplayer, pad.index, "KEYBOARD", int(pad.inputs["a"].id) + 1, "64", "64"))      # P1 Lower Right (6)
                    xml_input_alt.appendChild(generateKeycodePortElement(config_alt, ':NMI', "P1_START", "1", "1", "0"))                                                      # Reset/Start
                elif nplayer == 2:
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA3.7', nplayer, pad.index, "P2_BUTTON1", int(pad.inputs["y"].id) + 1, "128", "128"))  # P2 Button 1 (-/=)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA2.7', nplayer, pad.index, "P2_BUTTON2", int(pad.inputs["x"].id) + 1, "128", "128"))  # P2 Button 2 (Right)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA2.2', nplayer, pad.index, "KEYBOARD", int(pad.inputs["pagedown"].id) + 1, "8", "8")) # P2 Upper Right (Space)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA3.1', nplayer, pad.index, "KEYBOARD", int(pad.inputs["b"].id) + 1, "4", "4"))        # P2 Lower Left (7)
                    xml_input_alt.appendChild(generateSpecialPortElement(config_alt, ':PA3.1', nplayer, pad.index, "KEYBOARD", int(pad.inputs["a"].id) + 1, "64", "64"))      # P2 Lower Right (N)
            
            # BBC Micro - joystick not emulated/supported for most games, map some to gamepad
            if nplayer == 1 and sysName == "bbcb":
                xml_kbenable_alt = config_alt.createElement("keyboard")
                xml_kbenable_alt.setAttribute("tag", ":")
                xml_kbenable_alt.setAttribute("enabled", "1")
                xml_input_alt.appendChild(xml_kbenable_alt)
                xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL8', pad.index, "KEYBOARD", "QUOTE", int(pad.inputs["y"].id) + 1, "64", "64"))        # *
                xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL8', pad.index, "KEYBOARD", "SLASH", int(pad.inputs["x"].id) + 1, "16", "16"))        # ?
                xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL1', pad.index, "KEYBOARD", "Z", int(pad.inputs["b"].id) + 1, "64", "64"))            # Z
                xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL2', pad.index, "KEYBOARD", "X", int(pad.inputs["a"].id) + 1, "16", "16"))            # X
                xml_input_alt.appendChild(generateComboPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "ENTER", int(pad.inputs["pagedown"].id) + 1, "16", "16")) # Enter
                if dpadMode == 0:
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN", "4", "4"))       # Down
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT", "2", "2"))       # Left
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP", "8", "8"))           # Up
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT", "128", "128")) # Right
                elif dpadMode == 1:
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "4", "4"))       # Down
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15", "2", "2"))       # Left
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "8", "8"))           # Up
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16", "128", "128")) # Right
                else:
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "DOWN", "JOYCODE_{}_YAXIS_DOWN_SWITCH OR JOYCODE_{}_HAT1DOWN OR JOYCODE_{}_BUTTON14", "4", "4"))       # Down
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "LEFT", "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11", "2", "2"))       # Left
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "UP", "JOYCODE_{}_YAXIS_UP_SWITCH OR JOYCODE_{}_HAT1UP OR JOYCODE_{}_BUTTON13", "8", "8"))           # Up
                    xml_input_alt.appendChild(generateComboDirPortElement(config_alt, ':COL9', pad.index, "KEYBOARD", "RIGHT", "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12", "128", "128")) # Right
            
            nplayer = nplayer + 1
            
        # Write alt config (if used, custom config is turned off or file doesn't exist yet)
        if sysName in ("cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb") and writeConfig:
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

def generatePortElement(config, nplayer, padindex, mapping, key, input, reversed, dpadMode):
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", "P{}_{}".format(nplayer, mapping))
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(key, input, padindex + 1, reversed, dpadMode))
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElement(config, tag, nplayer, padindex, mapping, key, mask, default):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode("JOYCODE_{}_BUTTON{}".format(padindex + 1, key))
    xml_newseq.appendChild(value)
    return xml_port

def generateKeycodePortElement(config, tag, mapping, key, mask, default):
    # Map a keyboard key instead of a button (for start/select due to auto pad2key)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode("KEYCODE_{}".format(key))
    xml_newseq.appendChild(value)
    return xml_port

def generateComboPortElement(config, tag, padindex, mapping, key, button, mask, default):
    # Maps a keycode + button - for important keyboard keys when available
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode("KEYCODE_{} OR JOYCODE_{}_BUTTON{}".format(key, padindex + 1, button))
    xml_newseq.appendChild(value)
    return xml_port

def generateComboDirPortElement(config, tag, padindex, mapping, key, buttontext, mask, default):
    # Maps a keyboard key + directional input - for keyboard arrow keys
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode("KEYCODE_{} OR ".format(key) + buttontext.format(padindex + 1, padindex + 1, padindex + 1))
    xml_newseq.appendChild(value)
    return xml_port

def generateDirectionPortElement(config, tag, nplayer, padindex, mapping, key, mask, default):
    # Special direction mapping for emulated controllers
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(key.format(padindex + 1, padindex + 1, padindex + 1))
    xml_newseq.appendChild(value)
    return xml_port

def generateIncDecPortElement(config, tag, nplayer, padindex, mapping, inckey, deckey, mask, default, delta):
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
    incvalue = config.createTextNode(inckey.format(padindex + 1, padindex + 1, padindex + 1))
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(deckey.format(padindex + 1, padindex + 1, padindex + 1))
    xml_newseq_dec.appendChild(decvalue)
    return xml_port

def input2definition(key, input, joycode, reversed, dpadMode):
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
                return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT".format(joycode, joycode)
            elif dpadMode == 1:
                return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON15".format(joycode, joycode, joycode)
            else:
                return "JOYCODE_{}_YAXIS_LEFT_SWITCH OR JOYCODE_{}_HAT1LEFT OR JOYCODE_{}_BUTTON11".format(joycode, joycode, joycode)
        if key == "joystick1right" or key == "right":
            if dpadMode == 0:
                return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT".format(joycode, joycode)
            elif dpadMode == 1:
                return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON16".format(joycode, joycode, joycode)
            else:
                return "JOYCODE_{}_YAXIS_RIGHT_SWITCH OR JOYCODE_{}_HAT1RIGHT OR JOYCODE_{}_BUTTON12".format(joycode, joycode, joycode)
        if key == "joystick2up":
            return "JOYCODE_{}_RYAXIS_NEG_SWITCH OR JOYCODE_{}_BUTTON4".format(joycode, joycode)
        if key == "joystick2down":
            return "JOYCODE_{}_RYAXIS_POS_SWITCH OR JOYCODE_{}_BUTTON1".format(joycode, joycode)
        if key == "joystick2left":
            return "JOYCODE_{}_RXAXIS_NEG_SWITCH OR JOYCODE_{}_BUTTON3".format(joycode, joycode)
        if key == "joystick2right":
            return "JOYCODE_{}_RXAXIS_POS_SWITCH OR JOYCODE_{}_BUTTON2".format(joycode, joycode)
    eslog.warning("unable to find input2definition for {} / {}".format(input.type, key))
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