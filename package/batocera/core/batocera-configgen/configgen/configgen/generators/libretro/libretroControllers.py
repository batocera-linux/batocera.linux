from __future__ import annotations

from typing import TYPE_CHECKING

from ...controllersConfig import getAssociatedMouse, getDevicesInformation

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ...controller import Controller, ControllerMapping
    from ...Emulator import Emulator
    from ...input import Input
    from ...settings.unixSettings import UnixSettings


# Map an emulationstation direction to the corresponding retroarch
retroarchdirs = {'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right'}

# Map an emulationstation joystick to the corresponding retroarch
retroarchjoysticks = {'joystick1up': 'l_y', 'joystick1left': 'l_x', 'joystick2up': 'r_y', 'joystick2left': 'r_x'}

# Map an emulationstation input type to the corresponding retroarch type
typetoname = {'button': 'btn', 'hat': 'btn', 'axis': 'axis', 'key': 'key'}

# Map an emulationstation input hat to the corresponding retroarch hat value
hatstoname = {'1': 'up', '2': 'right', '4': 'down', '8': 'left'}

# Systems to swap Disc/CD : Atari ST / Amstrad CPC / AMIGA 500 1200 / DOS / MSX / PC98 / X68000 / Commodore 64 128 Plus4 | Dreamcast / PSX / Saturn / SegaCD / 3DO / PS2 / PC-FX
# Systems with internal mapping : PC88 / FDS | No multi-disc support : opera / yabasanshiro | No m3u support : PicoDrive
coreWithSwapSupport = {'hatari', 'cap32', 'bluemsx', 'dosbox_pure', 'flycast', 'np2kai', 'puae', 'puae2021', 'px68k', 'vice_x64', 'vice_x64sc', 'vice_xscpu64', 'vice_xplus4', 'vice_x128', 'pcsx_rearmed', 'duckstation', 'mednafen_psx', 'beetle-saturn', 'kronos', 'genesisplusgx', 'pcsx2', 'pcfx'};
systemToSwapDisable = {'amigacd32', 'amigacdtv', 'naomi', 'atomiswave', 'megadrive', 'mastersystem', 'gamegear'}

# Write a configuration for a specified controller
# Warning, function used by amiberry because it reads the same retroarch formatting
def writeControllersConfig(retroconfig: UnixSettings, system: Emulator, controllers: ControllerMapping, lightgun: bool) -> None:
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

    # hotkeys, forced to match with the hotkeys system
    retroconfig.save('input_enable_hotkey',       '"shift"')
    retroconfig.save('input_menu_toggle',         '"f1"')
    retroconfig.save('input_fps_toggle',          '"f2"')
    retroconfig.save('input_exit_emulator',       '"escape"')
    retroconfig.save('input_save_state',          '"f3"')
    retroconfig.save('input_load_state',          '"f4"')
    retroconfig.save('input_state_slot_decrease', '"f5"')
    retroconfig.save('input_state_slot_increase', '"f6"')
    retroconfig.save('input_toggle_fast_forward', '"f11"')
    retroconfig.save('input_screenshot',          '"f12"')

    # No menu in non full uimode
    if system.config["uimode"] != "Full":
        del retroarchspecials['b']

    # Check if hotkeys need to be removed/disabled (Needed for N64 controllers without a dedicated hotkey button)
    if system.config['core'] in ['mupen64plus-next', 'parallel_n64']:
        option = 'mupen64plus-controller1' if system.config['core'] == 'mupen64plus-next' else 'parallel-n64-controller1'

        if option in system.config and system.config[option] == 'n64limited':
            retroarchspecials = {'start': 'exit_emulator'}

    for controller in controllers:
        mouseIndex = None
        if system.name in ['nds', '3ds']:
            deviceList = getDevicesInformation()
            mouseIndex = getAssociatedMouse(deviceList, controllers[controller].device_path)
        if mouseIndex == None:
            mouseIndex = 0
        writeControllerConfig(retroconfig, controllers[controller], controller, system, retroarchspecials, lightgun, mouseIndex)

    writeHotKeyConfig(retroconfig, controllers)

# Remove all controller configurations
def cleanControllerConfig(retroconfig: UnixSettings, controllers: ControllerMapping, retroarchspecials: Mapping[str, str]):
    retroconfig.disable_all('input_player')
    for specialkey in retroarchspecials:
        retroconfig.disable_all(f'input_{retroarchspecials[specialkey]}')


# Write the hotkey for player 1
def writeHotKeyConfig(retroconfig: UnixSettings, controllers: ControllerMapping):
    if (controller := controllers.get(1)) is not None:
        if 'hotkey' in controller.inputs and controller.inputs['hotkey'].type == 'button':
            retroconfig.save('input_enable_hotkey_btn', controller.inputs['hotkey'].id)


# Write a configuration for a specified controller
def writeControllerConfig(retroconfig: UnixSettings, controller: Controller, playerIndex: int, system: Emulator, retroarchspecials: Mapping[str, str], lightgun: bool, mouseIndex: int | None = 0):
    generatedConfig = generateControllerConfig(controller, retroarchspecials, system, lightgun, mouseIndex)
    for key in generatedConfig:
        retroconfig.save(key, generatedConfig[key])

    retroconfig.save(f'input_player{playerIndex}_joypad_index', controller.index)
    retroconfig.save(f'input_player{playerIndex}_analog_dpad_mode', getAnalogMode(controller, system))


# Create a configuration for a given controller
def generateControllerConfig(controller: Controller, retroarchspecials: Mapping[str, str], system: Emulator, lightgun: bool, mouseIndex: int | None = 0):
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

    # Fix for reversed inputs in Yabasanshiro core which is unmaintained by retroarch
    if (system.config['core'] == 'yabasanshiro'):
        retroarchbtns["pageup"] = "r"
        retroarchbtns["pagedown"] = "l"

    config = dict()
    # config['input_device'] = '"%s"' % controller.real_name
    for btnkey in retroarchbtns:
        btnvalue = retroarchbtns[btnkey]
        if btnkey in controller.inputs:
            input = controller.inputs[btnkey]
            config['input_player{}_{}_{}'.format(controller.player_number, btnvalue, typetoname[input.type])] = getConfigValue(
                input)
    if lightgun:
        for btnkey in retroarchGunbtns: # Gun Mapping
            btnvalue = retroarchGunbtns[btnkey]
            if btnkey in controller.inputs:
                input = controller.inputs[btnkey]
                config['input_player{}_gun_{}_{}'.format(controller.player_number, btnvalue, typetoname[input.type])] = getConfigValue(
                    input)
    for dirkey in retroarchdirs:
        dirvalue = retroarchdirs[dirkey]
        if dirkey in controller.inputs:
            input = controller.inputs[dirkey]
            config['input_player{}_{}_{}'.format(controller.player_number, dirvalue, typetoname[input.type])] = getConfigValue(
                input)
            if lightgun:
                # Gun Mapping
                config['input_player{}_gun_dpad_{}_{}'.format(controller.player_number, dirvalue, typetoname[input.type])] = getConfigValue(
                    input)
    for jskey in retroarchjoysticks:
        jsvalue = retroarchjoysticks[jskey]
        if jskey in controller.inputs:
            input = controller.inputs[jskey]
            if input.value == '-1':
                config['input_player%s_%s_minus_axis' % (controller.player_number, jsvalue)] = '-%s' % input.id
                config['input_player%s_%s_plus_axis' % (controller.player_number, jsvalue)] = '+%s' % input.id
            else:
                config['input_player%s_%s_minus_axis' % (controller.player_number, jsvalue)] = '+%s' % input.id
                config['input_player%s_%s_plus_axis' % (controller.player_number, jsvalue)] = '-%s' % input.id
    if controller.player_number == 1:
        specialMap = retroarchspecials
        for specialkey in specialMap:
            specialvalue = specialMap[specialkey]
            if specialkey in controller.inputs:
                input = controller.inputs[specialkey]
                config['input_{}_{}'.format(specialvalue, typetoname[input.type])] = getConfigValue(input)
        if 'start' in controller.inputs:
            specialvalue = retroarchspecials['start']
            input = controller.inputs['start']
            config['input_{}_{}'.format(specialvalue, typetoname[input.type])] = getConfigValue(input)
    if not lightgun:
        # dont touch to it when there are connected lightguns
        config['input_player{}_mouse_index'.format(controller.player_number)] = mouseIndex
    return config


# Returns the value to write in retroarch config file, depending on the type
def getConfigValue(input: Input):
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
def getAnalogMode(controller: Controller, system: Emulator):
    # don't enable analog as hat mode for some systems
    if system.name == 'n64' or system.name == 'dreamcast' or system.name == '3ds':
        return '0'

    for dirkey in retroarchdirs:
        if dirkey in controller.inputs:
            if (controller.inputs[dirkey].type == 'button') or (controller.inputs[dirkey].type == 'hat'):
                return '1'
    return '0'
