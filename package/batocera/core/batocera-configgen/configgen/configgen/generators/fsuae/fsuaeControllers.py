from __future__ import annotations

from typing import TYPE_CHECKING

from ...batoceraPaths import mkdir_if_not_exists
from .fsuaePaths import FSUAE_CONFIG_DIR

if TYPE_CHECKING:
    from ...controller import ControllerMapping
    from ...Emulator import Emulator


# Create the controller configuration file
def generateControllerConfig(system: Emulator, playersControllers: ControllerMapping) -> None:

    fsuaeMapping = {
        'a':      'east_button',   'b':        'south_button',
        'x':      'north_button',  'y':        'west_button',
        'start':  'start_button',  'select':   'select_button',
        'up':     'dpad_up',       'down':     'dpad_down',
        'left':   'dpad_left',     'right':    'dpad_right',
        'l2':     'left_trigger',  'r2':       'right_trigger',
        'pageup': 'left_shoulder', 'pagedown': 'right_shoulder',
        'joystick1up': 'lstick_up', 'joystick1left': 'lstick_left',
        'joystick1down': 'lstick_down', 'joystick1right': 'lstick_right',
        'joystick2up': 'rstick_up', 'joystick2left': 'rstick_left',
        'joystick2down': 'rstick_down', 'joystick2right': 'rstick_right',
        'hotkey': 'menu_button'
        }
    fsuaeHatMapping = { "1": "up", "4": "down", "2": "right", "8": "left" }
    fsuaeReverseAxisMapping = { 'joystick1up': 'joystick1down', 'joystick1left': 'joystick1right',
                                'joystick2up': 'joystick2down', 'joystick2left': 'joystick2right',}

    # create the directory for the first time
    confDirectory = FSUAE_CONFIG_DIR / "Controllers"
    mkdir_if_not_exists(confDirectory)

    for playercontroller, pad in sorted(playersControllers.items()):
        configFileName = confDirectory / f"{pad.guid}_linux.conf"
        f = configFileName.open("w")

        # fs-uae-controller
        f.write("[fs-uae-controller]\n")
        f.write("name = " + pad.real_name + "\n")
        f.write("platform = linux\n")
        f.write("\n")

        # events
        f.write("[default]\n")
        f.write("include = universal_gamepad\n")

        for x in pad.inputs:
            input = pad.inputs[x]
            #f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")

            if input.name in fsuaeMapping:
                if input.type == "button":
                    f.write("button_" + str(input.id) + " = " + fsuaeMapping[input.name] + "\n")
                elif input.type == "hat":
                    if input.value in fsuaeHatMapping:
                        f.write("hat_" + str(input.id) + "_" + fsuaeHatMapping[input.value] + " = " + fsuaeMapping[input.name] + "\n")
                elif input.type == "axis":
                    if input.value == "1":
                        axis_valstr = "pos"
                        revaxis_valstr = "neg"
                    else:
                        axis_valstr = "neg"
                        revaxis_valstr = "pos"
                    f.write("axis_" + str(input.id) + "_" +    axis_valstr + " = " + fsuaeMapping[input.name] + "\n")
                    if input.name in fsuaeReverseAxisMapping and fsuaeReverseAxisMapping[input.name] in fsuaeMapping:
                        f.write("axis_" + str(input.id) + "_" + revaxis_valstr + " = " + fsuaeMapping[fsuaeReverseAxisMapping[input.name]] + "\n")
        f.close()
