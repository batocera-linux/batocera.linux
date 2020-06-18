#!/usr/bin/env python
import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from settings.unixSettings import UnixSettings
import batoceraFiles

# Map an emulationstation direction to the corresponding retroarch
retroarchdirs = {'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right'}

# Map an emulationstation joystick to the corresponding retroarch
retroarchjoysticks = {'joystick1up': 'l_y', 'joystick1left': 'l_x', 'joystick2up': 'r_y', 'joystick2left': 'r_x'}

# Map an emulationstation input type to the corresponding retroarch type
typetoname = {'button': 'btn', 'hat': 'btn', 'axis': 'axis', 'key': 'key'}

# Map an emulationstation input hat to the corresponding retroarch hat value
hatstoname = {'1': 'up', '2': 'right', '4': 'down', '8': 'left'}

# Write a configuration for a specified controller
# Warning, function used by amiberry because it reads the same retroarch formatting
def writeControllersConfig(retroconfig, system, controllers):
    # Map buttons to the corresponding retroarch specials keys
    retroarchspecials = {'x': 'load_state', 'y': 'save_state', 'pageup': 'screenshot', \
                         'start': 'exit_emulator', 'up': 'state_slot_increase', \
                         'down': 'state_slot_decrease', 'left': 'rewind', 'right': 'hold_fast_forward', \
                         'l2': 'shader_prev', 'r2': 'shader_next', 'a': 'reset', 'pagedown': 'ai_service'}
    retroarchspecials['b'] = 'menu_toggle'

    cleanControllerConfig(retroconfig, controllers, retroarchspecials)

    # no menu in non full uimode
    if system.config["uimode"] != "Full":
        del retroarchspecials['b']

    for controller in controllers:
        writeControllerConfig(retroconfig, controllers[controller], controller, system, retroarchspecials)
    writeHotKeyConfig(retroconfig, controllers)

# remove all controller configurations
def cleanControllerConfig(retroconfig, controllers, retroarchspecials):
    retroconfig.disableAll('input_player')
    for specialkey in retroarchspecials:
        retroconfig.disableAll('input_{}'.format(retroarchspecials[specialkey]))


# Write the hotkey for player 1
def writeHotKeyConfig(retroconfig, controllers):
    if '1' in controllers:
        if 'hotkey' in controllers['1'].inputs:
            retroconfig.save('input_enable_hotkey_btn', controllers['1'].inputs['hotkey'].id)


# Write a configuration for a specified controller
def writeControllerConfig(retroconfig, controller, playerIndex, system, retroarchspecials):
    generatedConfig = generateControllerConfig(controller, retroarchspecials, system)
    for key in generatedConfig:
        retroconfig.save(key, generatedConfig[key])

    retroconfig.save('input_player{}_joypad_index'.format(playerIndex), controller.index)
    retroconfig.save('input_player{}_analog_dpad_mode'.format(playerIndex), getAnalogMode(controller, system))


# Create a configuration for a given controller
def generateControllerConfig(controller, retroarchspecials, system):
# Map an emulationstation button name to the corresponding retroarch name
    retroarchbtns = {'a': 'a', 'b': 'b', 'x': 'x', 'y': 'y', \
                     'pageup': 'l', 'pagedown': 'r', 'l2': 'l2', 'r2': 'r2', \
                     'l3': 'l3', 'r3': 'r3', \
                     'start': 'start', 'select': 'select'}

    # some input adaptations for some cores...
    # z is important, in case l2 (z) is not available for this pad, use l1
    if system.name == "n64":
        if 'r2' not in controller.inputs:
            retroarchbtns["pageup"] = "l2"
            retroarchbtns["l2"] = "l"

    config = dict()
    # config['input_device'] = '"%s"' % controller.realName
    for btnkey in retroarchbtns:
        btnvalue = retroarchbtns[btnkey]
        if btnkey in controller.inputs:
            input = controller.inputs[btnkey]
            config['input_player%s_%s_%s' % (controller.player, btnvalue, typetoname[input.type])] = getConfigValue(
                input)
    for dirkey in retroarchdirs:
        dirvalue = retroarchdirs[dirkey]
        if dirkey in controller.inputs:
            input = controller.inputs[dirkey]
            config['input_player%s_%s_%s' % (controller.player, dirvalue, typetoname[input.type])] = getConfigValue(
                input)
    for jskey in retroarchjoysticks:
        jsvalue = retroarchjoysticks[jskey]
        if jskey in controller.inputs:
            input = controller.inputs[jskey]
            config['input_player%s_%s_minus_axis' % (controller.player, jsvalue)] = '-%s' % input.id
            config['input_player%s_%s_plus_axis' % (controller.player, jsvalue)] = '+%s' % input.id
    if controller.player == '1':
        specialMap = retroarchspecials
        for specialkey in specialMap:
            specialvalue = specialMap[specialkey]
            if specialkey in controller.inputs:
                input = controller.inputs[specialkey]
                config['input_%s_%s' % (specialvalue, typetoname[input.type])] = getConfigValue(input)
        specialvalue = retroarchspecials['start']
        input = controller.inputs['start']
        config['input_%s_%s' % (specialvalue, typetoname[input.type])] = getConfigValue(input)
    return config


# Returns the value to write in retroarch config file, depending on the type
def getConfigValue(input):
    if input.type == 'button':
        return input.id
    if input.type == 'axis':
        if input.value == '-1':
            return '-%s' % input.id
        else:
            return '+%s' % input.id
    if input.type == 'hat':
        return 'h' + input.id + hatstoname[input.value]
    if input.type == 'key':
        return input.id

# return the retroarch analog_dpad_mode
def getAnalogMode(controller, system):
    # don't enable analog as hat mode for some systems
    if system.name == 'n64' or system.name == 'dreamcast':
        return '0'

    for dirkey in retroarchdirs:
        if dirkey in controller.inputs:
            if (controller.inputs[dirkey].type == 'button') or (controller.inputs[dirkey].type == 'hat'):
                return '1'
    return '0'
