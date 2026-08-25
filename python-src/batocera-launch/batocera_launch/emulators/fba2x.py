from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, LOGS
from batocera_launch import Command, Controller, Controllers, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_CONFIG_FILE: Final = CONFIGS / 'fba' / 'fba2x.cfg'

_RATIO_INDEXES: Final = {'4/3': '0', '16/9': '1'}

# Map an emulationstation button name to the corresponding fba2x name
_FBA_4BTNS: Final = {
    'a': 'Y',
    'b': 'X',
    'x': 'B',
    'y': 'A',
    'pageup': 'L',
    'pagedown': 'R',
    'start': 'START',
    'select': 'SELECT',
}
_FBA_6BTNS: Final = {
    'a': 'L',
    'b': 'Y',
    'x': 'X',
    'y': 'A',
    'pageup': 'B',
    'pagedown': 'R',
    'start': 'START',
    'select': 'SELECT',
}

# Map an emulationstation direction to the corresponding fba2x
_FBA_DIRS: Final = {'up': 'UP', 'down': 'DOWN', 'left': 'LEFT', 'right': 'RIGHT'}
_FBA_AXIS: Final = {'joystick1up': 'JA_UD', 'joystick1left': 'JA_LR'}

# Map buttons to the corresponding fba2x specials keys
_FBA_SPECIALS: Final = {'start': 'QUIT', 'hotkey': 'HOTKEY'}
_SIX_BTN_GAMES: Final = (
    'sfa',
    'sfz',
    'sf2',
    'dstlk',
    'hsf2',
    'msh',
    'mshvsf',
    'mvsc',
    'nwarr',
    'ssf2',
    'vsav',
    'vhunt',
    'xmvsf',
    'xmcota',
)


def _is_six_btn(rom: Path) -> bool:
    return any(game in rom.name for game in _SIX_BTN_GAMES)


def _update_graphics(ini: CaseSensitiveConfigParser, emulator: Emulator, /) -> None:
    if not ini.has_section('Graphics'):
        ini.add_section('Graphics')

    ini.set('Graphics', 'DisplaySmoothStretch', emulator.config.get_bool('smooth', return_values=('1', '0')))
    ini.set(
        'Graphics',
        'MaintainAspectRatio',
        _RATIO_INDEXES.get(emulator.config.get_str('ratio', '4/3'), '0'),
    )
    ini.set('Graphics', 'DisplayEffect', '1' if emulator.config.get_str('shaders') == 'scanlines' else '0')
    ini.set('Graphics', 'RotateScreen', '0')
    ini.set('Graphics', 'DisplayBorder', '0')


def _update_controller(
    ini: CaseSensitiveConfigParser,
    player: int,
    controller: Controller,
    *,
    six_btn: bool,
) -> None:
    buttons = _FBA_6BTNS if six_btn else _FBA_4BTNS

    for dir_key, dir_value in _FBA_DIRS.items():
        if (inp := controller.inputs.get(dir_key)) is not None and inp.type == 'button':
            ini.set('Joystick', f'{dir_value}_{player}', inp.id)

    for axis_key, axis_value in _FBA_AXIS.items():
        if (inp := controller.inputs.get(axis_key)) is not None:
            ini.set('Joystick', f'{axis_value}_{player}', inp.id)

    for btn_key, btn_value in buttons.items():
        if (inp := controller.inputs.get(btn_key)) is not None:
            ini.set('Joystick', f'{btn_value}_{player}', inp.id)

    if player == 1:
        for btn_key, btn_value in _FBA_SPECIALS.items():
            if (inp := controller.inputs.get(btn_key)) is not None:
                ini.set('Joystick', btn_value, inp.id)


def _update_controllers(ini: CaseSensitiveConfigParser, rom: Path, controllers: Controllers, /) -> None:
    # remove any previous section to remove all configured keys
    if ini.has_section('Joystick'):
        ini.remove_section('Joystick')
    ini.add_section('Joystick')

    # indexes
    for player in range(1, 5):
        ini.set('Joystick', f'SDLID_{player}', '-1')
    for controller in controllers:
        ini.set('Joystick', f'SDLID_{controller.player_number}', str(controller.index))

    six_btn = _is_six_btn(rom)
    for controller in controllers:
        _update_controller(ini, controller.player_number, controller, six_btn=six_btn)


@cached_dataclass
class Fba2x(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'fba2x',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'fba'

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        ini = CaseSensitiveConfigParser(interpolation=None)
        if _CONFIG_FILE.exists():
            ini.read(_CONFIG_FILE)

        _update_graphics(ini, self)
        _update_controllers(ini, self.rom, self.controllers)

        # save the ini file
        with _CONFIG_FILE.open('w') as configfile:
            ini.write(configfile)

        return Command(['/usr/bin/fba2x', '--configfile', _CONFIG_FILE, '--logfile', LOGS / 'fba2x.log', self.rom])
