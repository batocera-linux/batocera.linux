
from settings.unixSettings import UnixSettings
from utils.logger import eslog

def generateControllerConfig(configFile, playersControllers):

    config = UnixSettings(configFile, separator='')
    setupControllers(config, playersControllers)

    config.save("fullscreen", "1")
    config.save("vsync", "1")
    config.save("usegl", "1")
    config.save("usejoy", "1")

def JoystickValue(key, pad):
    if key not in pad.inputs:
        return 0

    joy_max_inputs = 64
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
        axisfirst = 1 + (int(pad.index)) * joy_max_inputs + int(pad.nbbuttons) + 2 * input.id
        if (input.value > 0):
            axisfirst += 1
        value = axisfirst

    if input.type != "keyboard":
        value += 600

    #eslog.log("input.type={} input.id={} input.value={} => result={}".format(input.type, input.id, input.value, value))
    return value

def setupControllers(config, playersControllers):
    idx = 0
    for playercontroller, pad in sorted(playersControllers.items()):
        config.save("keys." + str(idx) + ".0" , JoystickValue("up",       pad)) # MOVEUP
        config.save("keys." + str(idx) + ".1" , JoystickValue("down",     pad)) # MOVEDOWN
        config.save("keys." + str(idx) + ".2" , JoystickValue("left",     pad)) # MOVELEFT
        config.save("keys." + str(idx) + ".3" , JoystickValue("right",    pad)) # MOVERIGHT
        config.save("keys." + str(idx) + ".4" , JoystickValue("a",        pad)) # ATTACK
        config.save("keys." + str(idx) + ".5" , JoystickValue("x",        pad)) # ATTACK2
        config.save("keys." + str(idx) + ".6" , JoystickValue("y",        pad)) # ATTACK3
        config.save("keys." + str(idx) + ".7" , JoystickValue("pagedown", pad)) # ATTACK4
        config.save("keys." + str(idx) + ".8" , JoystickValue("b",        pad)) # JUMP
        config.save("keys." + str(idx) + ".9" , JoystickValue("select",   pad)) # SPECIAL
        config.save("keys." + str(idx) + ".10", JoystickValue("start",    pad)) # START
        config.save("keys." + str(idx) + ".11", JoystickValue("l2",       pad)) # SCREENSHOT

        # hotkey
        if idx == 0:
            config.save("keys." + str(idx) + ".12", JoystickValue("hotkey", pad)) # ESC
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
