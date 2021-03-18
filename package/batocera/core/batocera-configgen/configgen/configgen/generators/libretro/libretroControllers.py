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

# Systems to swap Disc/CD : Atari ST / Amstrad CPC / AMIGA 500 1200 / DOS / MSX / PC98 / X68000 / Commodore 64 128 Plus4 | Dreamcast / PSX / Saturn / SegaCD / 3DO
# Systems with internal mapping : PC88 / FDS | No multi-disc support : opera / yabasanshiro | No m3u support : PicoDrive
coreWithSwapSupport = {'hatari', 'cap32', 'bluemsx', 'dosbox_pure', 'flycast', 'np2kai', 'puae', 'px68k', 'vice_x64', 'vice_x64sc', 'vice_xplus4', 'vice_x128', 'pcsx_rearmed', 'duckstation', 'mednafen_psx', 'beetle-saturn', 'genesisplusgx'};
systemToSwapDisable = {'amigacd32', 'amigacdtv', 'naomi', 'atomiswave', 'megadrive', 'mastersystem', 'gamegear'}

# Write a configuration for a specified controller
# Warning, function used by amiberry because it reads the same retroarch formatting
def writeControllersConfig(retroconfig, system, controllers):
    # Map buttons to the corresponding retroarch specials keys
    retroarchspecials = {'x': 'load_state', 'y': 'save_state', 'a': 'reset', 'start': 'exit_emulator', \
                         'up': 'state_slot_increase', 'down': 'state_slot_decrease', 'left': 'rewind', 'right': 'hold_fast_forward', \
                         'pageup': 'screenshot', 'pagedown': 'ai_service', 'l2': 'shader_prev', 'r2': 'shader_next'}
    retroarchspecials["b"] = "menu_toggle"

    # Some input adaptations for some systems with swap Disc/CD
    if (system.config['core'] in coreWithSwapSupport) and (system.name not in systemToSwapDisable):
        retroarchspecials["pageup"] = "disk_eject_toggle"
        retroarchspecials["l2"] =     "disk_prev"
        retroarchspecials["r2"] =     "disk_next"
        retroarchspecials["l3"] =     "screenshot"

    # Full special features list to disable
    retroarchFullSpecial = {'1':  'state_slot_increase', '2':  'load_state',        '3': 'save_state', \
                            '4':  'state_slot_decrease', '5':  'reset',             '6': 'exit_emulator', \
                            '7':  'rewind',              '8':  'hold_fast_forward', '9': 'screenshot', \
                            '10': 'disk_prev',           '11': 'disk_next',         '12': 'disk_eject_toggle', \
                            '13': 'shader_prev',         '14': 'shader_next',       '15': 'ai_service', \
                            '16': 'menu_toggle'}
    cleanControllerConfig(retroconfig, controllers, retroarchFullSpecial)

    # No menu in non full uimode
    if system.config["uimode"] != "Full":
        del retroarchspecials['b']

    for controller in controllers:
        writeControllerConfig(retroconfig, controllers[controller], controller, system, retroarchspecials)
    writeHotKeyConfig(retroconfig, controllers)

# Remove all controller configurations
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
    retroarchGunbtns = {'a': 'aux_a', 'b': 'aux_b', 'y': 'aux_c', \
                        'pageup': 'offscreen_shot', 'pagedown': 'trigger', \
                        'start': 'start', 'select': 'select'}

    # Some input adaptations for some cores...
    # Z is important, in case l2 (z) is not available for this pad, use l1
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
    for btnkey in retroarchGunbtns: # Gun Mapping
        btnvalue = retroarchGunbtns[btnkey]
        if btnkey in controller.inputs:
            input = controller.inputs[btnkey]
            config['input_player%s_gun_%s_%s' % (controller.player, btnvalue, typetoname[input.type])] = getConfigValue(
                input)
    for dirkey in retroarchdirs:
        dirvalue = retroarchdirs[dirkey]
        if dirkey in controller.inputs:
            input = controller.inputs[dirkey]
            config['input_player%s_%s_%s' % (controller.player, dirvalue, typetoname[input.type])] = getConfigValue(
                input)
            # Gun Mapping
            config['input_player%s_gun_dpad_%s_%s' % (controller.player, dirvalue, typetoname[input.type])] = getConfigValue(
                input)
    for jskey in retroarchjoysticks:
        jsvalue = retroarchjoysticks[jskey]
        if jskey in controller.inputs:
            input = controller.inputs[jskey]
            if input.value == '-1':
                config['input_player%s_%s_minus_axis' % (controller.player, jsvalue)] = '-%s' % input.id
                config['input_player%s_%s_plus_axis' % (controller.player, jsvalue)] = '+%s' % input.id
            else:
                config['input_player%s_%s_minus_axis' % (controller.player, jsvalue)] = '+%s' % input.id
                config['input_player%s_%s_plus_axis' % (controller.player, jsvalue)] = '-%s' % input.id
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

# Return the retroarch analog_dpad_mode
def getAnalogMode(controller, system):
    # don't enable analog as hat mode for some systems
    if system.name == 'n64' or system.name == 'dreamcast' or system.name == '3ds':
        return '0'

    for dirkey in retroarchdirs:
        if dirkey in controller.inputs:
            if (controller.inputs[dirkey].type == 'button') or (controller.inputs[dirkey].type == 'hat'):
                return '1'
    return '0'
