from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ...controllersConfig import getAssociatedMouse, getDevicesInformation

if TYPE_CHECKING:

    from ...controller import Controller, Controllers
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

# Write a configuration for a specified controller
# Warning, function used by amiberry because it reads the same retroarch formatting
def writeControllersConfig(
    retroconfig: UnixSettings,
    system: Emulator,
    controllers: Controllers,
    lightgun: bool,
    /,
) -> None:

    cleanControllerConfig(retroconfig, controllers)

    # hotkeys, forced to match with the hotkeys system
    retroconfig.save('input_enable_hotkey',       '"shift"')
    retroconfig.save('input_menu_toggle',         '"f1"')
    retroconfig.save('input_fps_toggle',          '"f2"')
    retroconfig.save('input_exit_emulator',       '"escape"')
    retroconfig.save('input_pause_toggle',        '"p"')
    retroconfig.save('input_save_state',          '"f3"')
    retroconfig.save('input_load_state',          '"f4"')
    retroconfig.save('input_state_slot_decrease', '"f5"')
    retroconfig.save('input_state_slot_increase', '"f6"')
    retroconfig.save('input_ai_service',          '"f9"')
    retroconfig.save('input_reset',               '"f10"')
    retroconfig.save('input_rewind',              '"f11"')
    retroconfig.save('input_hold_fast_forward',   '"f12"')
    retroconfig.save('input_screenshot',          '"nul"')
    retroconfig.save('input_audio_mute',          '"nul"')
    retroconfig.save('input_grab_mouse_toggle',   '"nul"')

    for controller in controllers:
        mouseIndex: str | None = None
        if system.name in ['nds', '3ds']:
            deviceList = getDevicesInformation()
            mouseIndex = getAssociatedMouse(deviceList, controller.device_path)
        if mouseIndex is None:
            mouseIndex = '0'
        writeControllerConfig(retroconfig, controller, controller.player_number, system, lightgun, mouseIndex)
    writeHotKeyConfig(retroconfig, controllers)

# Remove all controller configurations
def cleanControllerConfig(retroconfig: UnixSettings, controllers: Controllers, /) -> None:
    retroconfig.disable_all('input_player')

    for x in [
            'state_slot_increase',  'load_state',        'save_state',
            'state_slot_decrease',  'reset',             'exit_emulator',
            'rewind',               'hold_fast_forward', 'screenshot',
            'disk_prev',            'disk_next',         'disk_eject_toggle',
            'shader_prev',          'shader_next',       'ai_service',
            'menu_toggle'
    ]:
        retroconfig.disable_all(f'input_{x}')

# Write the hotkey for player 1
def writeHotKeyConfig(retroconfig: UnixSettings, controllers: Controllers, /) -> None:
    if controllers and 'hotkey' in controllers[0].inputs and controllers[0].inputs['hotkey'].type == 'button':
        retroconfig.save('input_enable_hotkey_btn', controllers[0].inputs['hotkey'].id)

# Write a configuration for a specified controller
def writeControllerConfig(
    retroconfig: UnixSettings,
    controller: Controller,
    playerIndex: int,
    system: Emulator,
    lightgun: bool,
    mouseIndex: str,
    /,
):
    generatedConfig = generateControllerConfig(controller, system, lightgun, mouseIndex)
    for key in generatedConfig:
        retroconfig.save(key, generatedConfig[key])

    retroconfig.save(f'input_player{playerIndex}_joypad_index', controller.index)
    retroconfig.save(f'input_player{playerIndex}_analog_dpad_mode', getAnalogMode(controller, system))

# Create a configuration for a given controller
def generateControllerConfig(
    controller: Controller,
    system: Emulator,
    lightgun: bool,
    mouseIndex: str,
    /,
) -> dict[str, object]:
# Map an emulationstation button name to the corresponding retroarch name
    retroarchbtns = {'a': 'a', 'b': 'b', 'x': 'x', 'y': 'y', \
                     'pageup': 'l', 'pagedown': 'r', 'l2': 'l2', 'r2': 'r2', \
                     'l3': 'l3', 'r3': 'r3', \
                     'start': 'start', 'select': 'select'}

    # X Y L1 L2  ---> X Y R1 L1
    # A B R1 R2  ---> A B R2 L2
    if system.config.get('altlayout') == 'fightstick':
        retroarchbtns['pageup'] = 'l2'
        retroarchbtns['pagedown'] = 'l'
        retroarchbtns['l2'] = 'r2'
        retroarchbtns['r2'] = 'r'

    retroarchGunbtns = {'a': 'aux_a', 'b': 'aux_b', 'y': 'aux_c', \
                        'pageup': 'offscreen_shot', 'pagedown': 'trigger', \
                        'start': 'start', 'select': 'select'}

    # Some input adaptations for some cores...
    # Z is important, in case l2 (z) is not available for this pad, use l1
    if system.name == "n64" and 'r2' not in controller.inputs:
        retroarchbtns["pageup"] = "l2"
        retroarchbtns["l2"] = "l"

    if system.name == "dreamcast" and system.config.core == "flycast" and 'r2' not in controller.inputs:
        retroarchbtns["pageup"] = "l2"
        retroarchbtns["l2"] = "l"
        retroarchbtns["pagedown"] = "r2"
        retroarchbtns["r2"] = "r"

    # Fix for reversed inputs in Yabasanshiro core which is unmaintained by retroarch
    if system.config.core == 'yabasanshiro':
        retroarchbtns["pageup"] = "r"
        retroarchbtns["pagedown"] = "l"

    config: dict[str, object] = {}
    # config['input_device'] = '"%s"' % controller.real_name
    for btnkey in retroarchbtns:
        btnvalue = retroarchbtns[btnkey]
        if btnkey in controller.inputs:
            input = controller.inputs[btnkey]
            config[f'input_player{controller.player_number}_{btnvalue}_{typetoname[input.type]}'] = getConfigValue(
                input)
    if lightgun:
        for btnkey in retroarchGunbtns: # Gun Mapping
            btnvalue = retroarchGunbtns[btnkey]
            if btnkey in controller.inputs:
                input = controller.inputs[btnkey]
                config[f'input_player{controller.player_number}_gun_{btnvalue}_{typetoname[input.type]}'] = getConfigValue(
                    input)
    for dirkey in retroarchdirs:
        dirvalue = retroarchdirs[dirkey]
        if dirkey in controller.inputs:
            input = controller.inputs[dirkey]
            config[f'input_player{controller.player_number}_{dirvalue}_{typetoname[input.type]}'] = getConfigValue(
                input)
            if lightgun:
                # Gun Mapping
                config[f'input_player{controller.player_number}_gun_dpad_{dirvalue}_{typetoname[input.type]}'] = getConfigValue(
                    input)
    for jskey in retroarchjoysticks:
        jsvalue = retroarchjoysticks[jskey]
        if jskey in controller.inputs:
            input = controller.inputs[jskey]
            if input.value == '-1':
                config[f'input_player{controller.player_number}_{jsvalue}_minus_axis'] = f'-{input.id}'
                config[f'input_player{controller.player_number}_{jsvalue}_plus_axis'] = f'+{input.id}'
            else:
                config[f'input_player{controller.player_number}_{jsvalue}_minus_axis'] = f'+{input.id}'
                config[f'input_player{controller.player_number}_{jsvalue}_plus_axis'] = f'-{input.id}'

    if not lightgun:
        # dont touch to it when there are connected lightguns
        config[f'input_player{controller.player_number}_mouse_index'] = mouseIndex
    return config


# Returns the value to write in retroarch config file, depending on the type
def getConfigValue(input: Input, /) -> str | None:
    if input.type == 'button':
        return input.id
    if input.type == 'axis':
        if input.value == '-1':
            return f'-{input.id}'
        return f'+{input.id}'
    if input.type == 'hat':
        return f'h{input.id}{hatstoname[input.value]}'
    if input.type == 'key':
        return input.id
    return None

# Return the retroarch analog_dpad_mode
def getAnalogMode(controller: Controller, system: Emulator, /) -> Literal['0', '1']:
    # don't enable analog as hat mode for some systems
    if system.name == 'n64' or system.name == 'dreamcast' or system.name == '3ds':
        return '0'

    for dirkey in retroarchdirs:
        if dirkey in controller.inputs and (controller.inputs[dirkey].type == 'button' or controller.inputs[dirkey].type == 'hat'):
            return '1'
    return '0'
