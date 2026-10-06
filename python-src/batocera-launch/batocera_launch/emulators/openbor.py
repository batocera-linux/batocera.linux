from __future__ import annotations

import re
from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import ROMS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controller, Controllers, Input

_CORE_TO_CONFIG_FILE = {
    'openbor4432': 'config4432.ini',
    'openbor6412': 'config6412.ini',
    'openbor7142': 'config7142.ini',
    'openbor7530': 'config7530.ini',
}
_CORE_TO_BINARY = {
    'openbor4432': 'OpenBOR4432',
    'openbor6412': 'OpenBOR6412',
    'openbor7142': 'OpenBOR7142',
    'openbor7530': 'OpenBOR7530',
}


def _guess_core(rom: Path, /) -> str:
    version_match = re.search(r'\[.*([0-9]{4})\]+', rom.name)
    if version_match is None:
        return 'openbor7530'

    version = int(version_match.group(1))
    if version < 6000:
        return 'openbor4432'
    if version < 6500:
        return 'openbor6412'
    if version < 7530:
        return 'openbor7142'
    return 'openbor7530'


def _joystick_value(
    key: str, pad: Controller, joy_max_inputs: int, new_axis_vals: bool, /, *, invert_axis: bool = False
) -> int:
    if key not in pad.inputs:
        return 0

    input_: Input = pad.inputs[key]
    value = 0

    if input_.type == 'button':
        value = 1 + pad.index * joy_max_inputs + int(input_.id)
    elif input_.type == 'hat':
        if new_axis_vals:
            hat_first = 1 + pad.index * joy_max_inputs + pad.button_count + 4 * int(input_.id)
            if input_.value == '2':  # SDL_HAT_RIGHT
                hat_first += 3
            elif input_.value == '4':  # SDL_HAT_DOWN
                hat_first += 1
            elif input_.value == '8':  # SDL_HAT_LEFT
                hat_first += 2
        else:
            hat_first = 1 + pad.index * joy_max_inputs + pad.button_count + 2 * pad.axis_count + 4 * int(input_.id)
            if input_.value == '2':  # SDL_HAT_RIGHT
                hat_first += 1
            elif input_.value == '4':  # SDL_HAT_DOWN
                hat_first += 2
            elif input_.value == '8':  # SDL_HAT_LEFT
                hat_first += 3
        value = hat_first
    elif input_.type == 'axis':
        axis_first = 1 + pad.index * joy_max_inputs + pad.button_count + 2 * int(input_.id)
        if new_axis_vals:
            axis_first += pad.hat_count * 4
        if (invert_axis and int(input_.value) < 0) or (not invert_axis and int(input_.value) > 0):
            axis_first += 1
        value = axis_first

    if input_.type != 'keyboard':
        value += 600

    return value


def _configure_controllers(config: KeyValueConfig, controllers: Controllers, core: str, /) -> None:
    if core == 'openbor4432':
        joy_max_inputs, new_axis_vals = 32, False
    elif core == 'openbor7142':
        joy_max_inputs, new_axis_vals = 64, True
    else:
        joy_max_inputs, new_axis_vals = 64, False

    for idx, pad in enumerate(controllers):
        config[f'keys.{idx}.0'] = _joystick_value('up', pad, joy_max_inputs, new_axis_vals)  # MOVEUP
        config[f'keys.{idx}.1'] = _joystick_value('down', pad, joy_max_inputs, new_axis_vals)  # MOVEDOWN
        config[f'keys.{idx}.2'] = _joystick_value('left', pad, joy_max_inputs, new_axis_vals)  # MOVELEFT
        config[f'keys.{idx}.3'] = _joystick_value('right', pad, joy_max_inputs, new_axis_vals)  # MOVERIGHT
        config[f'keys.{idx}.4'] = _joystick_value('b', pad, joy_max_inputs, new_axis_vals)  # ATTACK
        config[f'keys.{idx}.5'] = _joystick_value('x', pad, joy_max_inputs, new_axis_vals)  # ATTACK2
        config[f'keys.{idx}.6'] = _joystick_value('pageup', pad, joy_max_inputs, new_axis_vals)  # ATTACK3
        config[f'keys.{idx}.7'] = _joystick_value('pagedown', pad, joy_max_inputs, new_axis_vals)  # ATTACK4
        config[f'keys.{idx}.8'] = _joystick_value('a', pad, joy_max_inputs, new_axis_vals)  # JUMP
        config[f'keys.{idx}.9'] = _joystick_value('y', pad, joy_max_inputs, new_axis_vals)  # SPECIAL
        config[f'keys.{idx}.10'] = _joystick_value('start', pad, joy_max_inputs, new_axis_vals)  # START
        config[f'keys.{idx}.11'] = _joystick_value('l2', pad, joy_max_inputs, new_axis_vals)  # SCREENSHOT

        config[f'keys.{idx}.12'] = _joystick_value('hotkey', pad, joy_max_inputs, new_axis_vals) if idx == 0 else 0

        config[f'keys.{idx}.13'] = _joystick_value('joystick1up', pad, joy_max_inputs, new_axis_vals)
        config[f'keys.{idx}.14'] = _joystick_value('joystick1up', pad, joy_max_inputs, new_axis_vals, invert_axis=True)
        config[f'keys.{idx}.15'] = _joystick_value('joystick1left', pad, joy_max_inputs, new_axis_vals)
        config[f'keys.{idx}.16'] = _joystick_value(
            'joystick1left', pad, joy_max_inputs, new_axis_vals, invert_axis=True
        )

    # erase old values in case a pad is reused in a different position (so it's not used twice)
    for idx in range(len(controllers), 5):
        for key in range(12):
            del config[f'keys.{idx}.{key}']
        if idx != 0:
            del config[f'keys.{idx}.12']
        for key in range(13, 17):
            del config[f'keys.{idx}.{key}']


@cached_dataclass
class Openbor(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'openbor',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def execution_path(self) -> Path:
        # OpenBOR expects to be run from its own roms dir for wider mod compatibility
        return ROMS / 'openbor'

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (SAVES / 'openbor').mkdir(parents=True, exist_ok=True)

        core = self.core if self.config.core_forced else _guess_core(self.rom)

        config = KeyValueConfig(self.config_dir / _CORE_TO_CONFIG_FILE.get(core, 'config7530.ini'))

        config['fullscreen'] = 1
        config['usegl'] = 1
        config['usejoy'] = 1

        config['stretch'] = self.config.get_str('openbor_ratio', '0')
        config['swfilter'] = self.config.get_str('openbor_filter', '0')
        config['vsync'] = self.config.get_str('openbor_vsync', '1')
        config['fpslimit'] = self.config.get_str('openbor_limit', '0')

        _configure_controllers(config, self.controllers, core)

        rumble = self.config.get_str('openbor_rumble', '0')
        for pad in range(4):
            config[f'joyrumble.{pad}'] = rumble

        config.write()

        return Command([_CORE_TO_BINARY.get(core, 'OpenBOR7530'), self.rom])
