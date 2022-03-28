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


flycastMapping = { 'a' :             {'button': 'btn_b'},
                   'b' :             {'button': 'btn_a'},
                   'x' :             {'button': 'btn_y'},
                   'y' :             {'button': 'btn_x'},
                   'l1':             {'button': 'btn_c'},
                   'r1':             {'button': 'btn_z'},
                   'start' :         {'button': 'btn_start'},
                   'pageup' :        {'axis': 'axis_trigger_left',  'button': 'btn_trigger_left'},
                   'pagedown' :      {'axis': 'axis_trigger_right', 'button': 'btn_trigger_right'},
                   'joystick1left' : {'axis': 'axis_x'},
                   'joystick1up' :   {'axis': 'axis_y'},
                   'joystick2left' : {'axis': 'axis_right_x'},
                   'joystick2up' :   {'axis': 'axis_right_y'},
                   # The DPAD can be an axis (for gpio sticks for example) or a hat
                   'left' :          {'hat': 'axis_dpad1_x', 'axis': 'axis_x', 'button': 'btn_dpad1_left'},
                   'up' :            {'hat': 'axis_dpad1_y', 'axis': 'axis_y', 'button': 'btn_dpad1_up'},
                   'right' :         {'button': 'btn_dpad1_right'},
                   'down' :          {'button': 'btn_dpad1_down'},
                   'r2' :            {'axis':  'axis_trigger_right', 'button': 'btn_trigger_right'},
                   'l2' :            {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'}
}

# btn_d = coin
flycastArcadeMapping = { 'a' :             {'button': 'btn_b'},
                         'b' :             {'button': 'btn_a'},
                         'x' :             {'button': 'btn_y'},
                         'y' :             {'button': 'btn_x'},
                         'select':         {'button': 'btn_d'},
                         'l3':             {'button': 'btn_c'},
                         'r3':             {'button': 'btn_z'},
                         'start' :         {'button': 'btn_start'},
                         'pageup' :        {'axis': 'axis_trigger_left',  'button': 'btn_trigger_left'},
                         'pagedown' :      {'axis': 'axis_trigger_right', 'button': 'btn_trigger_right'},
                         'joystick1left' : {'axis': 'axis_x'},
                         'joystick1up' :   {'axis': 'axis_y'},
                         'joystick2left' : {'axis': 'axis_right_x'},
                         'joystick2up' :   {'axis': 'axis_right_y'},
                         # The DPAD can be an axis (for gpio sticks for example) or a hat
                         'left' :          {'hat': 'axis_dpad1_x', 'axis': 'axis_x', 'button': 'btn_dpad1_left'},
                         'up' :            {'hat': 'axis_dpad1_y', 'axis': 'axis_y', 'button': 'btn_dpad1_up'},
                         'right' :         {'button': 'btn_dpad1_right'},
                         'down' :          {'button': 'btn_dpad1_down'},
                         'r2' :            {'axis':  'axis_trigger_right', 'button': 'btn_trigger_right'},
                         'l2' :            {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'}
}

sections = { 'emulator' : ['mapping_name'],
             'dreamcast' : ['btn_a', 'btn_b', 'btn_c', 'btn_z', 'btn_x', 'btn_y', 'btn_start', 'axis_x', 'axis_y', 'axis_trigger_left', 'axis_trigger_right', 'btn_dpad1_left', 'btn_dpad1_right', 'btn_dpad1_up', 'btn_dpad1_down', 'btn_dpad2_left', 'btn_dpad2_right', 'btn_dpad2_up', 'btn_dpad2_down'],
             'compat' : ['axis_dpad1_x', 'axis_dpad1_y', 'btn_trigger_left', 'btn_trigger_right', 'axis_dpad2_x', 'axis_dpad2_y', 'axis_x_inverted', 'axis_y_inverted', 'axis_trigger_left_inverted', 'axis_trigger_right_inverted']

}

arcadesections = { 'emulator' : ['mapping_name'],
             'dreamcast' : ['btn_a', 'btn_b', 'btn_c', 'btn_d', 'btn_z', 'btn_x', 'btn_y', 'btn_start', 'axis_x', 'axis_y', 'axis_trigger_left', 'axis_trigger_right', 'btn_dpad1_left', 'btn_dpad1_right', 'btn_dpad1_up', 'btn_dpad1_down', 'btn_dpad2_left', 'btn_dpad2_right', 'btn_dpad2_up', 'btn_dpad2_down'],
             'compat' : ['axis_dpad1_x', 'axis_dpad1_y', 'btn_trigger_left', 'btn_trigger_right', 'axis_dpad2_x', 'axis_dpad2_y', 'axis_x_inverted', 'axis_y_inverted', 'axis_trigger_left_inverted', 'axis_trigger_right_inverted']

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

    # Add controller name
    Config.set("emulator", "mapping_name", controller.realName)
    Config.set("emulator", "btn_escape", "")
    Config.set("emulator", "btn_menu", "")
    
    l2_r2_flag = False
    if 'r2' in controller.inputs:
        l2_r2_flag = True

    # Parse controller inputs
    for index in controller.inputs:
        input = controller.inputs[index]
        
        if input.name not in flycastMapping:
            continue
        if input.type not in flycastMapping[input.name]:
            continue
        var = flycastMapping[input.name][input.type]
        eslog.debug("Var: {}".format(var))
        for i in sections:
            if var in sections[i]:
                section = i
                break

        if l2_r2_flag and (input.name == 'pageup' or input.name == 'pagedown'):
            continue

        # batocera doesn't retrieve the code for hats, however, this is 16/17+input.id in linux/input.h
        if input.type == 'hat':
            if input.name == 'up':  #Default values for hat0.  Formula for calculation is 16+input.id*2 and 17+input.id*2
                code = 17 + 2*int(input.id) # ABS_HAT0Y=17
            else:
                code = 16 + 2*int(input.id) # ABS_HAT0X=16
            Config.set(section, var, str(code))
        else:
            if input.code is not None:
                code = input.code
                Config.set(section, var, code)
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

    # Add controller name
    Config.set("emulator", "mapping_name", controller.realName)
    Config.set("emulator", "btn_escape", "")
    Config.set("emulator", "btn_menu", "")
    
    l2_r2_flag = False
    if 'r2' in controller.inputs:
        l2_r2_flag = True

    # Parse controller inputs
    for index in controller.inputs:
        input = controller.inputs[index]
        
        if input.name not in flycastArcadeMapping:
            continue
        if input.type not in flycastArcadeMapping[input.name]:
            continue
        var = flycastArcadeMapping[input.name][input.type]
        eslog.debug("Var: {}".format(var))
        for i in sections:
            if var in sections[i]:
                section = i
                break

        if l2_r2_flag and (input.name == 'pageup' or input.name == 'pagedown'):
            continue

        # batocera doesn't retrieve the code for hats, however, this is 16/17+input.id in linux/input.h
        if input.type == 'hat':
            if input.name == 'up':  #Default values for hat0.  Formula for calculation is 16+input.id*2 and 17+input.id*2
                code = 17 + 2*int(input.id) # ABS_HAT0Y=17
            else:
                code = 16 + 2*int(input.id) # ABS_HAT0X=16
            Config.set(section, var, str(code))
        else:
            if input.code is not None:
                code = input.code
                Config.set(section, var, code)
            else:
                eslog.warning("code not found for key " + input.name + " on pad " + controller.realName + " (please reconfigure your pad)")

    Config.write(cfgfile)
    cfgfile.close()
