from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import Controller, Controllers
    from ...utils.configparser import CaseSensitiveConfigParser

# Map an emulationstation button name to the corresponding fba2x name
fba4bnts = {
            'a': 'Y',
            'b': 'X',
            'x': 'B',
            'y': 'A',
            'pageup': 'L',
            'pagedown': 'R',
            'start': 'START',
            'select': 'SELECT'
            }

fba6bnts = {
            'a': 'L',
            'b': 'Y',
            'x': 'X',
            'y': 'A',
            'pageup': 'B',
            'pagedown': 'R',
            'start': 'START',
            'select': 'SELECT'
            }

# Map an emulationstation direction to the corresponding fba2x
fbadirs = {
            'up': 'UP',
            'down': 'DOWN',
            'left': 'LEFT',
            'right': 'RIGHT'
          }

fbaaxis = {
            'joystick1up': 'JA_UD',
            'joystick1left': 'JA_LR'
          }
fbaHatToAxis = {
                '1': 'UP',
                '2': 'LR',
                '4': 'UD',
                '8': 'LR'
                }

# Map buttons to the corresponding fba2x specials keys
fbaspecials = {
                'start': 'QUIT',
                'hotkey': 'HOTKEY'
              }

def updateControllersConfig(iniConfig: CaseSensitiveConfigParser, rom: Path, controllers: Controllers) -> None:
    # remove any previous section to remove all configured keys
    if iniConfig.has_section("Joystick"):
        iniConfig.remove_section("Joystick")
    iniConfig.add_section("Joystick")

    # indexes
    for player in range(1, 5):
        iniConfig.set("Joystick", f"SDLID_{player}", "-1")
    for controller in controllers:
        iniConfig.set("Joystick", f"SDLID_{controller.player_number}", str(controller.index))

    for controller in controllers:
        updateControllerConfig(iniConfig, controller.player_number, controller, is6btn(rom))

# Create a configuration file for a given controller
def updateControllerConfig(iniConfig: CaseSensitiveConfigParser, player: int, controller: Controller, special6: bool = False) -> None:
    fbaBtns = fba4bnts
    if special6:
        fbaBtns = fba6bnts

    for dirkey in fbadirs:
        dirvalue = fbadirs[dirkey]
        if dirkey in controller.inputs:
            input = controller.inputs[dirkey]
            if input.type == 'button':
                iniConfig.set("Joystick", f'{dirvalue}_{player}', input.id)

    for axis in fbaaxis:
        axisvalue = fbaaxis[axis]
        if axis in controller.inputs:
            input = controller.inputs[axis]
            iniConfig.set("Joystick", f'{axisvalue}_{player}', input.id)

    for btnkey in fbaBtns:
        btnvalue = fbaBtns[btnkey]
        if btnkey in controller.inputs:
            input = controller.inputs[btnkey]
            iniConfig.set("Joystick", f'{btnvalue}_{player}', input.id)

    if player == 1:
        for btnkey in fbaspecials:
            btnvalue = fbaspecials[btnkey]
            if btnkey in controller.inputs:
                input = controller.inputs[btnkey]
                iniConfig.set("Joystick", f'{btnvalue}', input.id)

def is6btn(rom: Path) -> bool:
    sixBtnGames = ['sfa', 'sfz', 'sf2', 'dstlk', 'hsf2', 'msh', 'mshvsf', 'mvsc', 'nwarr', 'ssf2', 'vsav', 'vhunt', 'xmvsf', 'xmcota']

    return any(game in rom.name for game in sixBtnGames)
