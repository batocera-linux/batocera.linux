#!/usr/bin/env python
import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from settings.unixSettings import UnixSettings
import recalboxFiles
import utils.slugify as slugify

libretroSettings = UnixSettings(recalboxFiles.retroarchCustom, separator=' ')
coreSettings = UnixSettings(recalboxFiles.retroarchCoreCustom, separator=' ')
recalboxConfSettings = UnixSettings(recalboxFiles.recalboxConf)

settingsRoot = recalboxFiles.retroarchRoot

# Map an emulationstation button name to the corresponding retroarch name
retroarchbtns = {'a': 'a', 'b': 'b', 'x': 'x', 'y': 'y', \
                 'pageup': 'l', 'pagedown': 'r', 'l2': 'l2', 'r2': 'r2', \
                 'l3': 'l3', 'r3': 'r3', \
                 'start': 'start', 'select': 'select'}

# Map an emulationstation direction to the corresponding retroarch
retroarchdirs = {'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right'}

# Map an emulationstation joystick to the corresponding retroarch
retroarchjoysticks = {'joystick1up': 'l_y', 'joystick1left': 'l_x', 'joystick2up': 'r_y', 'joystick2left': 'r_x'}

# Map an emulationstation input type to the corresponding retroarch type
typetoname = {'button': 'btn', 'hat': 'btn', 'axis': 'axis', 'key': 'key'}

# Map an emulationstation input hat to the corresponding retroarch hat value
hatstoname = {'1': 'up', '2': 'right', '4': 'down', '8': 'left'}

# Map buttons to the corresponding retroarch specials keys
retroarchspecialsnomenu = {'x': 'load_state', 'y': 'save_state', 'pageup': 'screenshot', \
                           'start': 'exit_emulator', 'up': 'state_slot_increase', \
                           'down': 'state_slot_decrease', 'left': 'rewind', 'right': 'hold_fast_forward', \
                           'l2': 'shader_prev', 'r2': 'shader_next', 'a': 'reset'}
retroarchspecials = retroarchspecialsnomenu.copy()
retroarchspecials['b'] = 'menu_toggle'

# Write a configuration for a specified controller
def writeControllersConfig(system, controllers):
    cleanControllerConfig(controllers)
    for controller in controllers:
        writeControllerConfig(controllers[controller], controller, system)
    writeHotKeyConfig(controllers)
    if ('inputdriver' not in system.config) or (system.config['inputdriver'] == 'auto'):
        system.config['inputdriver'] = getInputDriver(controllers)


# remove all controller configurations
def cleanControllerConfig(controllers):
    libretroSettings.disableAll('input_player')
    for specialkey in retroarchspecials:
        libretroSettings.disableAll('input_{}'.format(retroarchspecials[specialkey]))


# Write the hotkey for player 1
def writeHotKeyConfig(controllers):
    if '1' in controllers:
        if 'hotkey' in controllers['1'].inputs:
            libretroSettings.save('input_enable_hotkey_btn', controllers['1'].inputs['hotkey'].id)


# Write a configuration for a specified controller
def writeControllerConfig(controller, playerIndex, system):
    if not 'specials' in system.config:
        system.config['specials'] = 'default'
    generatedConfig = generateControllerConfig(controller, system.config['specials'])
    for key in generatedConfig:
        libretroSettings.save(key, generatedConfig[key])

    libretroSettings.save('input_player{}_joypad_index'.format(playerIndex), controller.index)
    libretroSettings.save('input_player{}_analog_dpad_mode'.format(playerIndex),
                          getAnalogMode(controller, system))


# Create a configuration for a given controller
def generateControllerConfig(controller, specials = 'default'):
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
        specialMap = dict()
        if specials == 'nomenu':
            specialMap = retroarchspecialsnomenu
        if specials == 'default':
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
    # if system.name != 'psx':
    for dirkey in retroarchdirs:
        if dirkey in controller.inputs:
            if (controller.inputs[dirkey].type == 'button') or (controller.inputs[dirkey].type == 'hat'):
                return '1'
    return '0'


# return the playstation analog mode for a controller
def getAnalogCoreMode(controller):
    for dirkey in retroarchdirs:
        if dirkey in controller.inputs:
            if (controller.inputs[dirkey].type == 'button') or (controller.inputs[dirkey].type == 'hat'):
                return 'analog'
    return 'standard'


# find the driver for controllers
# Write a configuration for a specified controller
def getInputDriver(controllers):
    for controller in controllers:
        for controllerName in sdl2driverControllers:
            if controllerName in controllers[controller].realName:
                return 'sdl2'
    return 'udev'

# list of controllers that works only with sdl2 driver
sdl2driverControllers = ['Bluetooth Wireless Controller', 'szmy-power', 'XiaoMi Bluetooth Wireless GameController', 'ipega Bluetooth Gamepad', 'ipega Bluetooth Gamepad   ']
