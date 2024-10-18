from __future__ import annotations

from typing import TYPE_CHECKING

from ...batoceraPaths import mkdir_if_not_exists

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import ControllerMapping
    from ...Emulator import Emulator

# inputtype:
# 0      axis
# 1      button
# 2      hat
# 3      ball
#
# Note that each axis has 2 inputindex entries and each hat has 4.
#
# action [action_parameters]:
# 0               none
# 1 port pin      joystick (pin: 1/2/4/8/16/32/64/128/256/512/1024/2048 = u/d/l/r/fire(A)/fire2(B)/fire3(X)/Y/LB/RB/select/start)
# 2 row col       keyboard
# 3               map
# 4               UI activate
# 5 path&to&item  UI function
# 6 pot axis      joystick (pot: 1/2/3/4 = x1/y1/x2/y2)

viceJoystick = {
            "up":       "# 2 0 1 / 1",
            "down":     "# 2 1 1 / 2",
            "left":     "# 2 2 1 / 4",
            "right":    "# 2 3 1 / 8",
            "start":    "# 1 ? 0",
            "select":   "# 1 ? 4",
            "hotkey":   "# 1 ? 5 Quit emulator",
            "a":        "# 1 ? 1 / 32", # Space
            "b":        "# 1 ? 1 / 16", # Fire button
            "x":        "# 1 ? 0",
            "y":        "# 1 ? 1 / 64", # Y
            "pageup":   "# 1 ? 0",
            "pagedown": "# 1 ? 0",
            "l1":       "# 1 ? 0",
            "r1":       "# 1 ? 0",
}

# Create the controller configuration file
def generateControllerConfig(system: Emulator, viceConfigFile: Path, playersControllers: ControllerMapping):
    # vjm file
    viceFile = viceConfigFile / "sdl-joymap.vjm"
    # vic20 uses a slightly different port
    if(system.config['core'] == 'xvic'):
        joy_port = "0"
    else:
        joy_port = "1"

    mkdir_if_not_exists(viceFile.parent)

    listVice = [];
    listVice.append("# Batocera configured controllers")
    listVice.append("")
    listVice.append("!CLEAR")
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        listVice.append("")
        listVice.append("# " + pad.real_name)
        for x in pad.inputs:
            input = pad.inputs[x]
            for indexName, indexValue in viceJoystick.items():
                if indexName == input.name:
                    listVice.append(indexValue.replace('#', str(pad.index)).replace('?', str(input.id)).replace('/', joy_port))
        listVice.append("")
        nplayer += 1

    f = viceFile.open('w')
    for i in range(len(listVice)):
        f.write(str(listVice[i]) + "\n")
    f.close()
