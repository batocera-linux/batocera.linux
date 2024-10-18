from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...controller import Controller, ControllerMapping
    from ...settings.unixSettings import UnixSettings


eslog = logging.getLogger(__name__)

def generateControllerConfig(config: UnixSettings, playersControllers: ControllerMapping, core: str):
    if core == "openbor4432":
        setupControllers(config, playersControllers, 32, False)
    elif core == "openbor7142":
        setupControllers(config, playersControllers, 64, True)
    else:
        setupControllers(config, playersControllers, 64, False)

def JoystickValue(key: str, pad: Controller, joy_max_inputs: int, new_axis_vals: bool, invertAxis: bool = False) -> int:
    if key not in pad.inputs:
        return 0

    value = 0
    input = pad.inputs[key]

    if input.type == "button":
        value = 1 + pad.index * joy_max_inputs + int(input.id)

    elif input.type == "hat":
        if new_axis_vals:
            hatfirst = 1 + pad.index * joy_max_inputs + int(pad.button_count) + 4 * int(input.id)
            if (input.value == "2"):   # SDL_HAT_RIGHT
                hatfirst += 3
            elif (input.value == "4"): # SDL_HAT_DOWN
                hatfirst += 1
            elif (input.value == "8"): # SDL_HAT_LEFT
                hatfirst += 2
        else:
            hatfirst = 1 + pad.index * joy_max_inputs + int(pad.button_count) + 2 * int(pad.axis_count) + 4 * int(input.id)
            if (input.value == "2"):   # SDL_HAT_RIGHT
                hatfirst += 1
            elif (input.value == "4"): # SDL_HAT_DOWN
                hatfirst += 2
            elif (input.value == "8"): # SDL_HAT_LEFT
                hatfirst += 3
        value = hatfirst

    elif input.type == "axis":
        axisfirst = 1 + pad.index * joy_max_inputs + int(pad.button_count) + 2 * int(input.id)
        if new_axis_vals:
            axisfirst += int(pad.hat_count)*4
        if ((invertAxis and int(input.value) < 0) or (not invertAxis and int(input.value) > 0)):
            axisfirst += 1
        value = axisfirst

    if input.type != "keyboard":
        value += 600

    #eslog.debug("input.type={} input.id={} input.value={} => result={}".format(input.type, input.id, input.value, value))
    return value

def setupControllers(config: UnixSettings, playersControllers: ControllerMapping, joy_max_inputs: int, new_axis_vals: bool) -> None:
    idx = 0
    for playercontroller, pad in sorted(playersControllers.items()):
        config.save("keys." + str(idx) + ".0" , JoystickValue("up",       pad, joy_max_inputs, new_axis_vals)) # MOVEUP
        config.save("keys." + str(idx) + ".1" , JoystickValue("down",     pad, joy_max_inputs, new_axis_vals)) # MOVEDOWN
        config.save("keys." + str(idx) + ".2" , JoystickValue("left",     pad, joy_max_inputs, new_axis_vals)) # MOVELEFT
        config.save("keys." + str(idx) + ".3" , JoystickValue("right",    pad, joy_max_inputs, new_axis_vals)) # MOVERIGHT
        config.save("keys." + str(idx) + ".4" , JoystickValue("b",        pad, joy_max_inputs, new_axis_vals)) # ATTACK
        config.save("keys." + str(idx) + ".5" , JoystickValue("x",        pad, joy_max_inputs, new_axis_vals)) # ATTACK2
        config.save("keys." + str(idx) + ".6" , JoystickValue("pageup",   pad, joy_max_inputs, new_axis_vals)) # ATTACK3
        config.save("keys." + str(idx) + ".7" , JoystickValue("pagedown", pad, joy_max_inputs, new_axis_vals)) # ATTACK4
        config.save("keys." + str(idx) + ".8" , JoystickValue("a",        pad, joy_max_inputs, new_axis_vals)) # JUMP
        config.save("keys." + str(idx) + ".9" , JoystickValue("y",        pad, joy_max_inputs, new_axis_vals)) # SPECIAL
        config.save("keys." + str(idx) + ".10", JoystickValue("start",    pad, joy_max_inputs, new_axis_vals)) # START
        config.save("keys." + str(idx) + ".11", JoystickValue("l2",       pad, joy_max_inputs, new_axis_vals)) # SCREENSHOT

        # hotkey
        if idx == 0:
            config.save("keys." + str(idx) + ".12", JoystickValue("hotkey", pad, joy_max_inputs, new_axis_vals)) # ESC
        else:
            config.save("keys." + str(idx) + ".12", "0") # ESC

        # axis
        config.save("keys." + str(idx) + ".13", JoystickValue("joystick1up",       pad, joy_max_inputs, new_axis_vals))        # axis up
        config.save("keys." + str(idx) + ".14", JoystickValue("joystick1up",       pad, joy_max_inputs, new_axis_vals, True))  # axis down
        config.save("keys." + str(idx) + ".15", JoystickValue("joystick1left",     pad, joy_max_inputs, new_axis_vals))        # axis left
        config.save("keys." + str(idx) + ".16", JoystickValue("joystick1left",     pad, joy_max_inputs, new_axis_vals, True))  # axis right

        # next one
        idx += 1

    # erase old values in case a pad is reused in an other position (so it is not used twice)
    for idx in range(len(playersControllers), 5):
        config.remove("keys." + str(idx) + ".0")
        config.remove("keys." + str(idx) + ".1")
        config.remove("keys." + str(idx) + ".2")
        config.remove("keys." + str(idx) + ".3")
        config.remove("keys." + str(idx) + ".4")
        config.remove("keys." + str(idx) + ".5")
        config.remove("keys." + str(idx) + ".6")
        config.remove("keys." + str(idx) + ".7")
        config.remove("keys." + str(idx) + ".8")
        config.remove("keys." + str(idx) + ".9")
        config.remove("keys." + str(idx) + ".10")
        config.remove("keys." + str(idx) + ".11")

        # hotkey
        if idx != 0:
            config.remove("keys." + str(idx) + ".12")

        config.remove("keys." + str(idx) + ".13")
        config.remove("keys." + str(idx) + ".14")
        config.remove("keys." + str(idx) + ".15")
        config.remove("keys." + str(idx) + ".16")
