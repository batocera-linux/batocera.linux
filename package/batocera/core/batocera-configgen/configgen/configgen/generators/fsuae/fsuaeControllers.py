from __future__ import annotations

from typing import TYPE_CHECKING

from ...batoceraPaths import mkdir_if_not_exists
from .fsuaePaths import FSUAE_CONFIG_DIR

if TYPE_CHECKING:
    from ...controller import Controllers
    from ...Emulator import Emulator


def _build_long_config_name(name, buttons, axes, hats):
    # e.g.: "Xbox Wireless Controller", 11, 6, 1 → "xbox_wireless_controller_11_6_1_0_linux"
    name = name.split('#')[0].lower().strip()
    for c in name:
        if not c.isalnum() and c != '_':
            name = name.replace(c, '_')
    # collapse consecutive underscores
    while '__' in name:
        name = name.replace('__', '_')
    name = name.strip('_')
    return f"{name}_{buttons}_{axes}_{hats}_0_linux"

# Create the controller configuration file
def generateControllerConfig(system: Emulator, playersControllers: Controllers) -> None:

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

    for pad in playersControllers:
        # Build mapping lines to reuse for both config files
        mapping_lines = []

        for x in pad.inputs:
            input = pad.inputs[x]
            #f.write(f"# undefined key: name={input.name}, type={input.type}, id={input.id}, value={input.value}\n")

            if input.name in fsuaeMapping:
                if input.type == "button":
                    mapping_lines.append(f"button_{input.id} = {fsuaeMapping[input.name]}\n")
                elif input.type == "hat":
                    if input.value in fsuaeHatMapping:
                        mapping_lines.append(f"hat_{input.id}_{fsuaeHatMapping[input.value]} = {fsuaeMapping[input.name]}\n")
                elif input.type == "axis":
                    if input.value == "1":
                        axis_valstr = "pos"
                        revaxis_valstr = "neg"
                    else:
                        axis_valstr = "neg"
                        revaxis_valstr = "pos"
                    mapping_lines.append(f"axis_{input.id}_{axis_valstr} = {fsuaeMapping[input.name]}\n")
                    if input.name in fsuaeReverseAxisMapping and fsuaeReverseAxisMapping[input.name] in fsuaeMapping:
                        mapping_lines.append(f"axis_{input.id}_{revaxis_valstr} = {fsuaeMapping[fsuaeReverseAxisMapping[input.name]]}\n")

        # Write config for both GUID lookup (joystick config) and long-name lookup (menu config)
        long_name = _build_long_config_name(pad.real_name, pad.button_count, pad.axis_count, pad.hat_count)
        for config_name in [pad.guid.lower(), long_name]:
            configFileName = confDirectory / f"{config_name}.conf"
            f = configFileName.open("w")

            # fs-uae-controller
            f.write("[fs-uae-controller]\n")
            f.write(f"name = {pad.real_name}\n")
            f.write("platform = linux\n")
            f.write("\n")

            # events
            f.write("[default]\n")
            f.write("include = universal_gamepad\n")

            for line in mapping_lines:
                f.write(line)
            f.close()
