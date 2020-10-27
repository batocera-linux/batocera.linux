#!/usr/bin/env python
# -*- coding: utf-8 -*-

import batoceraFiles
import os
from os import path
import codecs
from Emulator import Emulator
from utils.logger import eslog
import ConfigParser

# Create the controller configuration file
#first controller will ALWAYS BE A Gamepad
#additional controllers will either be a Pro Controller or Wiimote
def generateControllerConfig(system, playersControllers, rom):
    #make controller directory if it doesn't exist
    if not path.isdir(batoceraFiles.CONF + "/cemu/controllerProfiles"):
        os.mkdir(batoceraFiles.CONF + "/cemu/controllerProfiles")
    
    #purge old controller files
    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller0.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    
        
    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller1.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    
    
    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller2.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    

    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller3.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    

    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller4.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    
        
    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller5.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    

    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller6.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName)    
        
    configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller7.txt")
    if os.path.isfile(configFileName):
        os.remove(configFileName) 
    
    #We are exporting SDL_GAMECONTROLLERCONFIG in cemuGenerator, so we can assume all controllers are now working with xInput
    nplayer = 0
    sdlstring = ''
    double_pads = dict()
    
    sdlMapping = {
        'b':      'a',  'a':        'b',
        'x':      'y',  'y':        'x',
        'l2':     'lefttrigger',  'r2':    'righttrigger',
        'l3':     'leftstick',  'r3':    'rightstick',
        'pageup': 'leftshoulder', 'pagedown': 'rightshoulder',
        'start':     'start',  'select':    'back',
        'up': 'dpup', 'down': 'dpdown', 'left': 'dpleft', 'right': 'dpright',
        'joystick1up': 'lefty', 'joystick1left': 'leftx',
        'joystick2up': 'righty', 'joystick2left': 'rightx', 'hotkey': 'guide'
    }
    
    
    
    
    for playercontroller, pad in sorted(playersControllers.items()):
        #if nplayer == 0:  #For Future Hotkeys
       
        if pad.configName not in double_pads:
            double_pads[pad.configName] = 1
            sdlstring=sdlstring + pad.guid + ',' + pad.configName
            for x in pad.inputs:
                input = pad.inputs[x]
                keyname = None
                if input.name in sdlMapping:
                    keyname = sdlMapping[input.name]
                if keyname is not None:
                    sdlstring=sdlstring + write_key(keyname, input.type, input.id, input.value, pad.nbaxes, False, None)
            sdlstring=sdlstring + ',platform:Linux,\n'
            
            
 
        cemuSettings = ConfigParser.ConfigParser()    
        cemuSettings.optionxform = str    
        
        #Add Default Sections
        if not cemuSettings.has_section("General"):
            cemuSettings.add_section("General")
        if not cemuSettings.has_section("Controller"):
            cemuSettings.add_section("Controller")         

        cemuSettings.set("General", "api", "XInput")
        cemuSettings.set("General", "controller", nplayer)
        
        if (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True):
            cemuSettings.set("General", "emulate", "Wiimote")
        elif (nplayer == 0):
            cemuSettings.set("General", "emulate", "Wii U GamePad")
        else:
            cemuSettings.set("General", "emulate", "Wii U Pro Controller")
            
            
        cemuSettings.set("Controller", "rumble", "0")
        cemuSettings.set("Controller", "leftRange", "1")
        cemuSettings.set("Controller", "rightRange", "1")
        cemuSettings.set("Controller", "leftDeadzone", ".2")
        cemuSettings.set("Controller", "rightDeadzone", ".2")
        cemuSettings.set("Controller", "buttonThreshold", ".5")

        if (system.isOptSet('emulatedwiimotes') and system.getOptBoolean('emulatedwiimotes') == True):
            #Assumes a sideways wiimote configuration
            cemuSettings.set("Controller", "1", "button_4")    # A
            cemuSettings.set("Controller", "2", "button_8")    # B
            cemuSettings.set("Controller", "3", "button_1")    # 1
            cemuSettings.set("Controller", "4", "button_2")    # 2
            cemuSettings.set("Controller", "5", "button_800000000")    # C
            cemuSettings.set("Controller", "6", "button_100000000")    # Z
            cemuSettings.set("Controller", "7", "button_40")    # +
            cemuSettings.set("Controller", "8", "button_80")    # -
            cemuSettings.set("Controller", "9", "button_10000000")    # Up (Binds to Left on Controller)
            cemuSettings.set("Controller", "10", "button_20000000")   # Down (Binds to Right on Controller)
            cemuSettings.set("Controller", "11", "button_8000000")   # Left (Binds to Down on Controller)
            cemuSettings.set("Controller", "12", "button_4000000")   # Right (Binds to Up on Controller
            cemuSettings.set("Controller", "13", "button_400000000")   # Nunchuk Up (RStick)
            cemuSettings.set("Controller", "14", "button_10000000000")   # Nunchuk Down (RStick)
            cemuSettings.set("Controller", "15", "button_8000000000")   # Nunchuk Left (RStick)
            cemuSettings.set("Controller", "16", "button_200000000")   # Nunchuk Right (RStick)
            cemuSettings.set("Controller", "17", "0")   # Home 
            cemuSettings.set("Controller", "nunchuck", "1")
            cemuSettings.set("Controller", "motionPlus", "0")
        else:
            cemuSettings.set("Controller", "1", "button_2")    # A
            cemuSettings.set("Controller", "2", "button_1")    # B
            cemuSettings.set("Controller", "3", "button_8")    # X
            cemuSettings.set("Controller", "4", "button_4")    # Y
            cemuSettings.set("Controller", "5", "button_20")    # L
            cemuSettings.set("Controller", "6", "button_10")    # R
            cemuSettings.set("Controller", "7", "button_100000000")    # L2
            cemuSettings.set("Controller", "8", "button_800000000")    # R2
            cemuSettings.set("Controller", "9", "button_40")    # Start
            cemuSettings.set("Controller", "10", "button_80")   # Select
            cemuSettings.set("Controller", "11", "button_4000000")   # Up
            cemuSettings.set("Controller", "12", "button_8000000")   # Down
            cemuSettings.set("Controller", "13", "button_10000000")   # Left
            cemuSettings.set("Controller", "14", "button_20000000")   # Right
            cemuSettings.set("Controller", "15", "button_100")   # LStick Click
            cemuSettings.set("Controller", "16", "button_200")   # RStick Click
            cemuSettings.set("Controller", "17", "button_80000000")   # LStick Up
            cemuSettings.set("Controller", "18", "button_2000000000")   # LStick Down
            cemuSettings.set("Controller", "19", "button_1000000000")   # LStick Left
            cemuSettings.set("Controller", "20", "button_40000000")   # LStick Right
            cemuSettings.set("Controller", "21", "button_400000000")   # RStick Up
            cemuSettings.set("Controller", "22", "button_10000000000")   # RStick Down
            cemuSettings.set("Controller", "23", "button_8000000000")   # RStick Left
            cemuSettings.set("Controller", "24", "button_200000000")   # RStick Right

            
        configFileName = "{}/{}".format(batoceraFiles.CONF + "/cemu/controllerProfiles/", "controller" + str(nplayer) + ".txt")
                # save dolphin.ini
        with open(configFileName, 'w') as configfile:
            cemuSettings.write(configfile)
        nplayer+=1 

    return sdlstring

def write_key(keyname, input_type, input_id, input_value, input_global_id, reverse, hotkey_id):     
    #Sample Output
    #a:b1,b:b0,back:b10,dpdown:h0.4,dpleft:h0.8,dpright:h0.2,dpup:h0.1,guide:b2,leftshoulder:b6,leftstick:b13,lefttrigger:b8,leftx:a0,lefty:a1,rightshoulder:b7,rightstick:b14,righttrigger:b9,rightx:a2,righty:a3,start:b11,x:b4,y:b3
    output = "," + keyname + ":"
    if input_type == "button":
        output = output + "b" + str(input_id)
    elif input_type == "hat":
        output = output + "h" + str(input_id) + "." + str(input_value)
    elif input_type == "axis":
        output = output + "a" + str(input_id)
    return output
