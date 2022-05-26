#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import configparser
import batoceraFiles
from utils.logger import get_logger

eslog = get_logger(__name__)

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import batoceraFiles

flycastMapping = { # Directions
                   # The DPAD can be an axis (for gpio sticks for example) or a hat
                   # We don't map DPad2
                   'up' :            {'button': 'btn_dpad1_up', 'hat': 'btn_dpad1_up', 'axis': 'btn_dpad1_up'},
                   'down' :          {'button': 'btn_dpad1_down', 'hat': 'btn_dpad1_down'},
                   'left' :          {'button': 'btn_dpad1_left', 'hat': 'btn_dpad1_left', 'axis': 'btn_dpad1_left'},
                   'right' :         {'button': 'btn_dpad1_right', 'hat': 'btn_dpad1_right'},
                   'joystick1left' : {'axis': 'btn_analog_left'},
                   'joystick1up' :   {'axis': 'btn_analog_up'},
                   'joystick2left' : {'axis': 'axis2_left'},
                   'joystick2up' :   {'axis': 'axis2_up'},
                   # Buttons
                   'b' :             {'button': 'btn_a'},
                   'a' :             {'button': 'btn_b'},
                   'y' :             {'button': 'btn_x'},
                   'x' :             {'button': 'btn_y'},
                   # Triggers
                   'l2' :            {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'},
                   'r2' :            {'axis': 'axis_trigger_right', 'button': 'btn_trigger_right'},
                   # System Buttons
                   'start' :         {'button': 'btn_start'}
}

flycastArcadeMapping = { # Directions
                         'up' :            {'button': 'btn_dpad1_up', 'hat': 'btn_dpad1_up', 'axis': 'btn_dpad1_up'},
                         'down' :          {'button': 'btn_dpad1_down', 'hat': 'btn_dpad1_down'},
                         'left' :          {'button': 'btn_dpad1_left', 'hat': 'btn_dpad1_left', 'axis': 'btn_dpad1_left'},
                         'right' :         {'button': 'btn_dpad1_right', 'hat': 'btn_dpad1_right'},
                         'joystick1left' : {'axis': 'btn_analog_left'},
                         'joystick1up' :   {'axis': 'btn_analog_up'},
                         'joystick2left' : {'axis': 'axis2_left'},
                         'joystick2up' :   {'axis': 'axis2_up'},
                         # Buttons
                         'b' :             {'button': 'btn_a'},
                         'a' :             {'button': 'btn_b'},
                         'y':              {'button': 'btn_c'},
                         'x' :             {'button': 'btn_x'},
                         'pageup' :        {'button': 'btn_y'},
                         'pagedown':       {'button': 'btn_z'},
                         'l3':             {'button': 'btn_dpad2_left'},
                         'r3':             {'button': 'btn_dpad2_right'},
                         # Triggers
                         'l2' :            {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'},
                         'r2' :            {'axis': 'axis_trigger_right', 'button': 'btn_trigger_right'},
                         # System Buttons
                         'start' :         {'button': 'btn_start'},
                         # coin
                         'select':         {'button': 'btn_d'}
}

sections = { 'analog', 'digital', 'emulator' }

# Create the controller configuration file
def generateControllerConfig(controller, type):
    # Set config file name
    if type == 'dreamcast':
        eslog.debug("-=[ Dreamcast Controller Settings ]=-")
        configFileName = "{}/SDL_{}.cfg".format(batoceraFiles.flycastMapping, controller.realName)
    if type == 'arcade':
        eslog.debug("-=[ Arcade Controller Settings ]=-")
        configFileName = "{}/SDL_{}_arcade.cfg".format(batoceraFiles.flycastMapping, controller.realName)
    Config = configparser.ConfigParser(interpolation=None)

    if not os.path.exists(os.path.dirname(configFileName)):
        os.makedirs(os.path.dirname(configFileName))
         
    cfgfile = open(configFileName,'w+')
    # create ini sections
    for section in sections:
        Config.add_section(section)

    # Parse controller inputs
    eslog.debug("*** Controller Name = {} ***".format(controller.realName))
    analogbind = 0
    digitalbind = 0
    for index in controller.inputs:
        input = controller.inputs[index]
        if type == 'dreamcast':
            if input.name not in flycastMapping:
                continue
            if input.type not in flycastMapping[input.name]:
                eslog.debug("Input type: {} / {} - not in mapping".format(input.type, input.name))
                continue
            var = flycastMapping[input.name][input.type]
        if type == 'arcade':
            if input.name not in flycastArcadeMapping:
                continue
            if input.type not in flycastArcadeMapping[input.name]:
                eslog.debug("Input type: {} - not in mapping".format(input.type))
                continue
            var = flycastArcadeMapping[input.name][input.type]
        eslog.debug("Input Name = {}, Var = {}, Type = {}".format(input.name, var, input.type))
        # batocera doesn't retrieve the code for hats, however
        # SDL is 256 for up, 257 for down, 258 for left & 259 for right
        if input.type == 'hat':
            section = 'digital'
            if input.name == 'up':
                code = 256
            if input.name == 'down':
                code = 257
            if input.name == 'left':
                code = 258
            if input.name == 'right':
                code = 259
            option = "bind{}".format(digitalbind)
            digitalbind = digitalbind +1
            val = "{}:{}".format(code, var)
            Config.set(section, option, val)
        
        if input.type == 'button':
            section = 'digital'
            option = "bind{}".format(digitalbind)
            digitalbind = digitalbind +1
            code = input.id
            val = "{}:{}".format(code, var)
            Config.set(section, option, val)
        
        if input.type == 'axis':
            section = 'analog'
            if input.name == 'l2' or input.name == 'r2':
                # Use positive axis for full trigger control
                code = input.id + "+"
            else:
                code = input.id + "-"
            option = "bind{}".format(analogbind)
            analogbind = analogbind +1
            val = "{}:{}".format(code, var)
            if 'left' in input.name or 'up' in input.name:
                Config.set(section, option, val)
                # becase we only take one axis input
                # now have to write the joy-right & joy-down manually
                # we use the same code number but positive axis
                option = "bind{}".format(analogbind)
                analogbind = analogbind +1
                if input.name == 'joystick1left':
                    code = input.id + "+"
                    var = 'btn_analog_right'
                    val = "{}:{}".format(code, var)
                    Config.set(section, option, val)
                if input.name == 'joystick1up':
                    code = input.id + "+"
                    var = 'btn_analog_down'
                    val = "{}:{}".format(code, var)
                    Config.set(section, option, val)
                if input.name == 'joystick2left':
                    code = input.id + "+"
                    var = 'axis2_right'
                    val = "{}:{}".format(code, var)
                    Config.set(section, option, val)
                if input.name == 'joystick2up':
                    code = input.id + "+"
                    var = 'axis2_down'
                    val = "{}:{}".format(code, var)
                    Config.set(section, option, val)
                if input.name == 'up':
                    code = input.id + "+"
                    var = 'btn_dpad1_down'
                    val = "{}:{}".format(code, var)
                    Config.set(section, option, val)
                if input.name == 'left':
                    code = input.id + "+"
                    var = 'btn_dpad1_right'
                    val = "{}:{}".format(code, var)
                    Config.set(section, option, val)
            else:
                Config.set(section, option, val)

        # Add additional controller info
        Config.set("emulator", "dead_zone", "10")
        Config.set("emulator", "mapping_name", "Default") #controller.realName)
        Config.set("emulator", "rumble_power", "100")
        Config.set("emulator", "version", "3")
    
    Config.write(cfgfile)
    cfgfile.close()
