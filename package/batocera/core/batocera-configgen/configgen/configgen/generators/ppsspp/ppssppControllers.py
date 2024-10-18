from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from ...batoceraPaths import mkdir_if_not_exists
from ...utils.configparser import CaseSensitiveConfigParser
from .ppssppPaths import PPSSPP_CONFIG_INIT, PPSSPP_PSP_SYSTEM_DIR

if TYPE_CHECKING:
    from ...controller import Controller

eslog = logging.getLogger(__name__)

ppssppControlsIni: Final  = PPSSPP_PSP_SYSTEM_DIR / 'controls.ini'
ppssppControlsInit: Final = PPSSPP_CONFIG_INIT / 'controls.ini'

# This configgen is based on PPSSPP 1.5.4.
# Therefore, all code/github references are valid at this version, and may not be valid with later updates

# PPSSPP internal "NKCodes" https://github.com/hrydgard/ppsspp/blob/master/Common/Input/KeyCodes.h

# Hotkeys - %d-%d
# DEVICE_ID_KEYBOARD = 1
# NKCODE_F1 = 131,
# NKCODE_F2 = 132,
# NKCODE_F3 = 133,
# NKCODE_F4 = 134,
# NKCODE_F5 = 135,
# NKCODE_F6 = 136,
# NKCODE_F7 = 137,
# NKCODE_F8 = 138,
# NKCODE_F9 = 139,
# NKCODE_F10 = 140,
# NKCODE_F11 = 141,
# NKCODE_F12 = 142,

# Will later be used to convert SDL input ids
NKCODE_BUTTON_1 = 188
NKCODE_BUTTON_2 = 189
NKCODE_BUTTON_3 = 190
NKCODE_BUTTON_4 = 191
NKCODE_BUTTON_5 = 192
NKCODE_BUTTON_6 = 193
NKCODE_BUTTON_7 = 194
NKCODE_BUTTON_8 = 195
NKCODE_BUTTON_9 = 196
NKCODE_BUTTON_10 = 197
NKCODE_BUTTON_11 = 198
NKCODE_BUTTON_12 = 199
NKCODE_BUTTON_13 = 200
NKCODE_BUTTON_14 = 201
NKCODE_BUTTON_15 = 202
NKCODE_BUTTON_16 = 203
NKCODE_BACK = 4
JOYSTICK_AXIS_X = 0
JOYSTICK_AXIS_Y = 1
JOYSTICK_AXIS_HAT_X = 15
JOYSTICK_AXIS_HAT_Y = 16
JOYSTICK_AXIS_Z = 11
JOYSTICK_AXIS_RZ = 14
JOYSTICK_AXIS_LTRIGGER = 17
JOYSTICK_AXIS_RTRIGGER = 18
NKCODE_DPAD_UP = 19
NKCODE_DPAD_DOWN = 20
NKCODE_DPAD_LEFT = 21
NKCODE_DPAD_RIGHT = 22

# PPSSPP defined an offset for axis
AXIS_BIND_NKCODE_START = 4000

DEVICE_ID_PAD_0 = 10
# SDL2 input ids conversion table to NKCodes
# See https://hg.libsdl.org/SDL/file/e12c38730512/include/SDL_gamecontroller.h#l262
sdlNameToNKCode = {
    "b" : NKCODE_BUTTON_2, # A
    "a" : NKCODE_BUTTON_3, # B
    "y" : NKCODE_BUTTON_4, # X
    "x" : NKCODE_BUTTON_1, # Y
    "select" : NKCODE_BUTTON_9, # SELECT/BACK
    "start" : NKCODE_BUTTON_10, # START
    "pageup" : NKCODE_BUTTON_6, # L
    "pagedown" : NKCODE_BUTTON_5, # R
    "up" : NKCODE_DPAD_UP,
    "down" : NKCODE_DPAD_DOWN,
    "left" : NKCODE_DPAD_LEFT,
    "right" : NKCODE_DPAD_RIGHT
}

SDLHatMap = {
    "up" : NKCODE_DPAD_UP,
    "down" : NKCODE_DPAD_DOWN,
    "left" : NKCODE_DPAD_LEFT,
    "right" : NKCODE_DPAD_RIGHT
}

SDLJoyAxisMap = {
    "0" : JOYSTICK_AXIS_X,
    "1" : JOYSTICK_AXIS_Y,
    "2" : JOYSTICK_AXIS_Z,
    "3" : JOYSTICK_AXIS_RZ,
    "4" : JOYSTICK_AXIS_LTRIGGER,
    "5" : JOYSTICK_AXIS_RTRIGGER
}

ppssppMapping =  { 'a' :             {'button': 'Circle'},
                   'b' :             {'button': 'Cross'},
                   'x' :             {'button': 'Triangle'},
                   'y' :             {'button': 'Square'},
                   'start' :         {'button': 'Start'},
                   'select' :        {'button': 'Select'},
                   'pageup' :        {'button': 'L'},
                   'pagedown' :      {'button': 'R'},
                   'joystick1left' : {'axis': 'An.Left'},
                   'joystick1up' :   {'axis': 'An.Up'},
                   'joystick2left' : {'axis': 'RightAn.Left'},
                   'joystick2up' :   {'axis': 'RightAn.Up'},
                   # The DPAD can be an axis (for gpio sticks for example) or a hat
                   'up' :            {'hat': 'Up',    'axis': 'Up',    'button': 'Up'},
                   'down' :          {'hat': 'Down',  'axis': 'Down',  'button': 'Down'},
                   'left' :          {'hat': 'Left',  'axis': 'Left',  'button': 'Left'},
                   'right' :         {'hat': 'Right', 'axis': 'Right', 'button': 'Right'},
                   # Need to add pseudo inputs as PPSSPP doesn't manually invert axises, and these are not referenced in es_input.cfg
                   'joystick1right' :{'axis': 'An.Right'},
                   'joystick1down' : {'axis': 'An.Down'},
                   'joystick2right' :{'axis': 'RightAn.Right'},
                   'joystick2down' : {'axis': 'RightAn.Down'}
}

# Create the controller configuration file
def generateControllerConfig(controller: Controller):
    # Set config file name
    configFileName = ppssppControlsIni
    Config = CaseSensitiveConfigParser(interpolation=None)
    Config.read(ppssppControlsInit)
    # As we start with the default ini file, no need to create the section
    section = "ControlMapping"
    if not Config.has_section(section):
        Config.add_section(section)

    # Parse controller inputs
    for index in controller.inputs:
        input = controller.inputs[index]
        if input.name not in ppssppMapping or input.type not in ppssppMapping[input.name]:
            continue

        var = ppssppMapping[input.name][input.type]
        padnum = controller.index

        code = input.code
        if input.type == 'button':
            pspcode = sdlNameToNKCode[input.name]
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(Config, section, var, val)
            Config.set(section, var, val)

        elif input.type == 'axis':
            # Get the axis code
            nkAxisId = SDLJoyAxisMap[input.id]
            # Apply the magic axis formula
            pspcode = axisToCode(nkAxisId, int(input.value))
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(Config, section, var, val)
            eslog.debug(f"Adding {var} to {val}")
            Config.set(section, var, val)

            # Skip the rest if it's an axis dpad
            if input.name in [ 'up', 'down', 'left', 'right' ] : continue
            # Also need to do the opposite direction manually. The input.id is the same as up/left, but the direction is opposite
            if input.name == 'joystick1up':
                var = ppssppMapping['joystick1down'][input.type]
            elif input.name == 'joystick1left':
                var = ppssppMapping['joystick1right'][input.type]
            elif input.name == 'joystick2up':
                var = ppssppMapping['joystick2down'][input.type]
            elif input.name == 'joystick2left':
                var = ppssppMapping['joystick2right'][input.type]

            pspcode = axisToCode(nkAxisId, -int(input.value))
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(Config, section, var, val)
            Config.set(section, var, val)

        elif input.type == 'hat' and input.name in SDLHatMap:
            var = ppssppMapping[input.name][input.type]
            pspcode = SDLHatMap[input.name]
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(Config, section, var, val)
            Config.set(section, var, val)

        mkdir_if_not_exists(configFileName.parent)

    # hotkey controls are called via evmapy.
    # configuring specific hotkey in ppsspp is not simple without patching
    Config.set(section, "Rewind",        "1-131")
    Config.set(section, "Fast-forward",  "1-132")
    Config.set(section, "Save State",    "1-133")
    Config.set(section, "Load State",    "1-134")
    Config.set(section, "Previous Slot", "1-135")
    Config.set(section, "Next Slot",     "1-136")
    Config.set(section, "Screenshot",    "1-137")
    Config.set(section, "Pause",         "1-139")

    with configFileName.open('w+') as cfgfile:
        Config.write(cfgfile)
    return configFileName

def axisToCode(axisId, direction) :
    if direction < 0:
        direction = 1
    else:
        direction = 0
    return AXIS_BIND_NKCODE_START + axisId * 2 + direction

# determine if the option already exists or not
def optionValue(config, section, option, value):
    if config.has_option(section, option):
        return f"{config.get(section, option)},{value}"
    else:
        return value
