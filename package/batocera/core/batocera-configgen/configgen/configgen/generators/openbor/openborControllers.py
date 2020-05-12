from utils.logger import eslog

def generateControllerConfig(config, playersControllers, core):
    if core == "openbor4432":
        setupControllers(config, playersControllers, 32)
    else:
        setupControllers(config, playersControllers, 64)

def JoystickValue(key, pad, joy_max_inputs):
    if key not in pad.inputs:
        return 0

    value = 0
    input = pad.inputs[key]

    if input.type == "button":
        value = 1 + (int(pad.index)) * joy_max_inputs + int(input.id)

    elif input.type == "hat":
        hatfirst = 1 + (int(pad.index)) * joy_max_inputs + int(pad.nbbuttons) + 2 * int(pad.nbaxes) + 4 * int(input.id)
        if (input.value == "2"):   # SDL_HAT_RIGHT
            hatfirst += 1
        elif (input.value == "4"): # SDL_HAT_DOWN
            hatfirst += 2
        elif (input.value == "8"): # SDL_HAT_LEFT
            hatfirst += 3
        value = hatfirst

    elif input.type == "axis":
        axisfirst = 1 + (int(pad.index)) * joy_max_inputs + int(pad.nbbuttons) + 2 * int(input.id)
        if (input.value > 0):
            axisfirst += 1
        value = axisfirst

    if input.type != "keyboard":
        value += 600

    #eslog.log("input.type={} input.id={} input.value={} => result={}".format(input.type, input.id, input.value, value))
    return value

def setupControllers(config, playersControllers, joy_max_inputs):
    idx = 0
    for playercontroller, pad in sorted(playersControllers.items()):
        config.save("keys." + str(idx) + ".0" , JoystickValue("up",       pad, joy_max_inputs)) # MOVEUP
        config.save("keys." + str(idx) + ".1" , JoystickValue("down",     pad, joy_max_inputs)) # MOVEDOWN
        config.save("keys." + str(idx) + ".2" , JoystickValue("left",     pad, joy_max_inputs)) # MOVELEFT
        config.save("keys." + str(idx) + ".3" , JoystickValue("right",    pad, joy_max_inputs)) # MOVERIGHT
        config.save("keys." + str(idx) + ".4" , JoystickValue("a",        pad, joy_max_inputs)) # ATTACK
        config.save("keys." + str(idx) + ".5" , JoystickValue("x",        pad, joy_max_inputs)) # ATTACK2
        config.save("keys." + str(idx) + ".6" , JoystickValue("y",        pad, joy_max_inputs)) # ATTACK3
        config.save("keys." + str(idx) + ".7" , JoystickValue("pagedown", pad, joy_max_inputs)) # ATTACK4
        config.save("keys." + str(idx) + ".8" , JoystickValue("b",        pad, joy_max_inputs)) # JUMP
        config.save("keys." + str(idx) + ".9" , JoystickValue("select",   pad, joy_max_inputs)) # SPECIAL
        config.save("keys." + str(idx) + ".10", JoystickValue("start",    pad, joy_max_inputs)) # START
        config.save("keys." + str(idx) + ".11", JoystickValue("l2",       pad, joy_max_inputs)) # SCREENSHOT

        # hotkey
        if idx == 0:
            config.save("keys." + str(idx) + ".12", JoystickValue("hotkey", pad, joy_max_inputs)) # ESC
        else:
            config.save("keys." + str(idx) + ".12", "0") # ESC

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
