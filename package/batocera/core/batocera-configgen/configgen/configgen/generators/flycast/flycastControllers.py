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
                   'up' :            {'button': 'btn_dpad1_up', 'hat': 'btn_dpad1_up', 'axis': 'axis_y'},
                   'down' :          {'button': 'btn_dpad1_down', 'hat': 'btn_dpad1_down'},
                   'left' :          {'button': 'btn_dpad1_left', 'hat': 'btn_dpad1_left', 'axis': 'axis_x'},
                   'right' :         {'button': 'btn_dpad1_right', 'hat': 'btn_dpad1_right'},
                   'joystick1left' : {'axis': 'btn_analog_left'},
                   'joystick1up' :   {'axis': 'btn_analog_up'},
                   # Buttons
                   'b' :             {'button': 'btn_a'},
                   'a' :             {'button': 'btn_b'},
                   'y' :             {'button': 'btn_x'},
                   'x' :             {'button': 'btn_y'},
                   'pageup':         {'button': 'btn_c'},
                   'pagedown':       {'button': 'btn_z'},
                   # Triggers
                   'l2' :            {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'},
                   'r2' :            {'axis':  'axis_trigger_right', 'button': 'btn_trigger_right'},
                   # System Buttons
                   'start' :         {'button': 'btn_start'}
}

flycastArcadeMapping = { # Directions
                         'up' :            {'button': 'btn_dpad1_up', 'hat': 'btn_dpad1_up', 'axis': 'axis_y'},
                         'down' :          {'button': 'btn_dpad1_down', 'hat': 'btn_dpad1_down'},
                         'left' :          {'button': 'btn_dpad1_left', 'hat': 'btn_dpad1_left', 'axis': 'axis_x'},
                         'right' :         {'button': 'btn_dpad1_right', 'hat': 'btn_dpad1_right'},
                         'joystick1left' : {'axis': 'btn_analog_left'},
                         'joystick1up' :   {'axis': 'btn_analog_up'},
                         # Buttons
                         'b' :             {'button': 'btn_a'},
                         'a' :             {'button': 'btn_b'},
                         'y' :             {'button': 'btn_x'},
                         'x' :             {'button': 'btn_y'},
                         'pageup':         {'button': 'btn_c'},
                         'pagedown':       {'button': 'btn_z'},
                         # Triggers
                         'l2' :            {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'},
                         'r2' :            {'axis':  'axis_trigger_right', 'button': 'btn_trigger_right'},
                         # System Buttons
                         'start' :         {'button': 'btn_start'},
                         # coin
                         'select':         {'button': 'btn_d'}
}

sections = { 'analog' : ['axis_x', 'axis_y', 'axis_trigger_left', 'axis_trigger_right', 'btn_dpad1_left', 'btn_dpad1_right', 'btn_dpad1_up', 'btn_dpad1_down', 'btn_dpad2_left', 'btn_dpad2_right', 'btn_dpad2_up', 'btn_dpad2_down', 'axis_dpad1_x', 'axis_dpad1_y', 'btn_trigger_left', 'btn_trigger_right', 'axis_dpad2_x', 'axis_dpad2_y', 'axis_x_inverted', 'axis_y_inverted', 'axis_trigger_left_inverted', 'axis_trigger_right_inverted', 'btn_analog_left', 'btn_analog_right', 'btn_analog_up', 'btn_analog_down'],
             'digital' : ['btn_a', 'btn_b', 'btn_c', 'btn_z', 'btn_x', 'btn_y', 'btn_start'],
             'emulator' : ['mapping_name']
}

arcadesections = { 'analog' : ['axis_x', 'axis_y', 'axis_trigger_left', 'axis_trigger_right', 'btn_dpad1_left', 'btn_dpad1_right', 'btn_dpad1_up', 'btn_dpad1_down', 'btn_dpad2_left', 'btn_dpad2_right', 'btn_dpad2_up', 'btn_dpad2_down', 'axis_dpad1_x', 'axis_dpad1_y', 'btn_trigger_left', 'btn_trigger_right', 'axis_dpad2_x', 'axis_dpad2_y', 'axis_x_inverted', 'axis_y_inverted', 'axis_trigger_left_inverted', 'axis_trigger_right_inverted', 'btn_analog_left', 'btn_analog_right', 'btn_analog_up', 'btn_analog_down'],
             'digital' : ['btn_a', 'btn_b', 'btn_c', 'btn_z', 'btn_x', 'btn_y', 'btn_start', 'btn_d'],
             'emulator' : ['mapping_name']
}

# Create the controller configuration file
# returns its name
def generateControllerConfig(controller):
    # Set config file name
    configFileName = "{}/evdev_{}.cfg".format(batoceraFiles.flycastMapping,controller.realName)
    Config = configparser.ConfigParser(interpolation=None)

    if not os.path.exists(os.path.dirname(configFileName)):
        os.makedirs(os.path.dirname(configFileName))
         
    cfgfile = open(configFileName,'w+')
    # create ini sections
    for section in sections:
        Config.add_section(section)
    # Add controller name etc
    Config.set("emulator", "dead_zone", "10")
    Config.set("emulator", "mapping_name", controller.realName)
    Config.set("emulator", "version", "3")
    # Parse controller inputs
    analogbind = 0
    digitalbind = 0
    for index in controller.inputs:
        input = controller.inputs[index]
        if input.name not in flycastMapping:
            continue
        if input.type not in flycastMapping[input.name]:
            eslog.warning("Input type: {} - not in mapping".format(input.type))
            continue
        name = [input.name]
        var = flycastMapping[input.name][input.type]
        eslog.debug("Name: {} - Var: {}".format(name, var))
        for i in sections:
            if var in sections[i]:
                section = i
                break
        # batocera doesn't retrieve the code for hats, however, this is 16/17+input.id in linux/input.h
        if input.type == 'hat':
            if input.name == 'up' or input.name == 'down':  #Default values for hat0.  Formula for calculation is 16+input.id*2 and 17+input.id*2
                code = 17 + 2*int(input.id) # ABS_HAT0Y=17
            else:
                code = 16 + 2*int(input.id) # ABS_HAT0X=16
            # hat's considered analog
            option = "bind{}".format(analogbind)
            if input.name == 'up' or input.name == 'left':
                code = str(code) + "-"
            else:
                code = str(code) + "+"
            analogbind = analogbind +1
            val = "{}:{}".format(code, var)
            Config.set(section, option, val)
        else:
            if input.code is not None:
                # hack to force PS controller triggers to the digital section
                if int(input.code) > 100:
                    section = 'digital'
                if section == 'analog':
                    code = input.code + "-"
                    option = "bind{}".format(analogbind)
                    analogbind = analogbind +1
                if section == 'digital':
                    code = input.code
                    option = "bind{}".format(digitalbind)
                    digitalbind = digitalbind +1
                val = "{}:{}".format(code, var)
                if input.name == 'joystick1left' or input.name == 'joystick1up':
                    Config.set(section, option, val)
                    # becase we only take one axis input
                    # now have to write the joy1right & joy1down manually
                    # same code number but positive axis
                    option = "bind{}".format(analogbind)
                    analogbind = analogbind +1
                    if input.name == 'joystick1left':
                        code = input.code + "+"
                        var = 'btn_analog_right'
                        val = "{}:{}".format(code, var)
                        Config.set(section, option, val)
                    if input.name == 'joystick1up':
                        code = input.code + "+"
                        var = 'btn_analog_down'
                        val = "{}:{}".format(code, var)
                        Config.set(section, option, val)
                else:
                    Config.set(section, option, val)
            else:
                eslog.warning("code not found for key " + input.name + " on pad " + controller.realName + " (please reconfigure your pad)")

    Config.write(cfgfile)
    cfgfile.close()
    return configFileName

# atomiswave & naomi games expect an arcade cfg
def generateArcadeControllerConfig(controller):
    # Set config file name
    configFileName = "{}/evdev_{}_arcade.cfg".format(batoceraFiles.flycastMapping,controller.realName)
    Config = configparser.ConfigParser(interpolation=None)

    if not os.path.exists(os.path.dirname(configFileName)):
        os.makedirs(os.path.dirname(configFileName))
         
    cfgfile = open(configFileName,'w+')
    # create ini sections
    for section in arcadesections:
        Config.add_section(section)
    # Add controller name etc
    Config.set("emulator", "dead_zone", "10")
    Config.set("emulator", "mapping_name", controller.realName)
    Config.set("emulator", "version", "3")
    # Parse controller inputs
    analogbind = 0
    digitalbind = 0
    for index in controller.inputs:
        input = controller.inputs[index]
        if input.name not in flycastArcadeMapping:
            continue
        if input.type not in flycastArcadeMapping[input.name]:
            eslog.warning("Input type: {} - not in mapping".format(input.type))
            continue
        name = [input.name]
        var = flycastArcadeMapping[input.name][input.type]
        eslog.debug("Name: {} - Var: {}".format(name, var))
        for i in arcadesections:
            if var in arcadesections[i]:
                section = i
                break
        # batocera doesn't retrieve the code for hats, however, this is 16/17+input.id in linux/input.h
        if input.type == 'hat':
            if input.name == 'up' or input.name == 'down':  #Default values for hat0.  Formula for calculation is 16+input.id*2 and 17+input.id*2
                code = 17 + 2*int(input.id) # ABS_HAT0Y=17
            else:
                code = 16 + 2*int(input.id) # ABS_HAT0X=16
            # hat's considered analog
            option = "bind{}".format(analogbind)
            if input.name == 'up' or input.name == 'left':
                code = str(code) + "-"
            else:
                code = str(code) + "+"
            analogbind = analogbind +1
            val = "{}:{}".format(code, var)
            Config.set(section, option, val)
        else:
            if input.code is not None:
                # hack to force PS controller triggers to the digital section
                if int(input.code) > 100:
                    section = 'digital'
                if section == 'analog':
                    code = input.code + "-"
                    option = "bind{}".format(analogbind)
                    analogbind = analogbind +1
                if section == 'digital':
                    code = input.code
                    option = "bind{}".format(digitalbind)
                    digitalbind = digitalbind +1
                val = "{}:{}".format(code, var)
                if input.name == 'joystick1left' or input.name == 'joystick1up':
                    Config.set(section, option, val)
                    # becase we only take one axis input
                    # now have to write the joy1right & joy1down manually
                    # same code number but positive axis
                    option = "bind{}".format(analogbind)
                    analogbind = analogbind +1
                    if input.name == 'joystick1left':
                        code = input.code + "+"
                        var = 'btn_analog_right'
                        val = "{}:{}".format(code, var)
                        Config.set(section, option, val)
                    if input.name == 'joystick1up':
                        code = input.code + "+"
                        var = 'btn_analog_down'
                        val = "{}:{}".format(code, var)
                        Config.set(section, option, val)
                else:
                    Config.set(section, option, val)
            else:
                eslog.warning("code not found for key " + input.name + " on pad " + controller.realName + " (please reconfigure your pad)")

    Config.write(cfgfile)
    cfgfile.close()
