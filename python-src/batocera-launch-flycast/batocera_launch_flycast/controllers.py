from __future__ import annotations

import configparser
import logging
from typing import TYPE_CHECKING, Final, Literal

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controller

_logger = logging.getLogger(__name__)


_FLYCAST_INPUT_MAPPINGS: Final = {
    'dreamcast': {
        # Directions
        # The DPAD can be an axis (for gpio sticks for example) or a hat
        # We don't map DPad2
        'up': {'button': 'btn_dpad1_up', 'hat': 'btn_dpad1_up', 'axis': 'btn_dpad1_up'},
        'down': {'button': 'btn_dpad1_down', 'hat': 'btn_dpad1_down'},
        'left': {'button': 'btn_dpad1_left', 'hat': 'btn_dpad1_left', 'axis': 'btn_dpad1_left'},
        'right': {'button': 'btn_dpad1_right', 'hat': 'btn_dpad1_right'},
        'joystick1left': {'axis': 'btn_analog_left'},
        'joystick1up': {'axis': 'btn_analog_up'},
        'joystick2left': {'axis': 'axis2_left'},
        'joystick2up': {'axis': 'axis2_up'},
        # Buttons
        'b': {'button': 'btn_a'},
        'a': {'button': 'btn_b'},
        'y': {'button': 'btn_x'},
        'x': {'button': 'btn_y'},
        # Triggers
        'l2': {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'},
        'r2': {'axis': 'axis_trigger_right', 'button': 'btn_trigger_right'},
        # System Buttons
        'start': {'button': 'btn_start'},
    },
    'arcade': {
        # Directions
        'up': {'button': 'btn_dpad1_up', 'hat': 'btn_dpad1_up', 'axis': 'btn_dpad1_up'},
        'down': {'button': 'btn_dpad1_down', 'hat': 'btn_dpad1_down'},
        'left': {'button': 'btn_dpad1_left', 'hat': 'btn_dpad1_left', 'axis': 'btn_dpad1_left'},
        'right': {'button': 'btn_dpad1_right', 'hat': 'btn_dpad1_right'},
        'joystick1left': {'axis': 'btn_analog_left'},
        'joystick1up': {'axis': 'btn_analog_up'},
        'joystick2left': {'axis': 'axis2_left'},
        'joystick2up': {'axis': 'axis2_up'},
        # Buttons
        'b': {'button': 'btn_a'},
        'a': {'button': 'btn_b'},
        'y': {'button': 'btn_c'},
        'x': {'button': 'btn_x'},
        'pageup': {'button': 'btn_y'},
        'pagedown': {'button': 'btn_z'},
        'l3': {'button': 'btn_dpad2_up'},
        'r3': {'button': 'btn_dpad2_down'},
        # Triggers
        'l2': {'axis': 'axis_trigger_left', 'button': 'btn_trigger_left'},
        'r2': {'axis': 'axis_trigger_right', 'button': 'btn_trigger_right'},
        # System Buttons
        'start': {'button': 'btn_start'},
        # coin
        'select': {'button': 'btn_d'},
    },
}

_SECTIONS: Final = ('analog', 'digital', 'emulator')

_HAT_CODE_MAPPING: Final = {
    'up': 256,
    'down': 257,
    'left': 258,
    'right': 259,
}

# Define digital bindings for keyboard
_KEYBOARD_BINDINGS: Final = {
    'bind0': '4:btn_d',
    'bind1': '6:btn_b',
    'bind2': '7:btn_y',
    'bind3': '9:btn_trigger_left',
    'bind4': '12:btn_analog_up',
    'bind5': '13:btn_analog_left',
    'bind6': '14:btn_analog_down',
    'bind7': '15:btn_analog_right',
    'bind8': '22:btn_x',
    'bind9': '25:btn_trigger_right',
    'bind10': '27:btn_a',
    'bind11': '40:btn_start',
    'bind12': '43:btn_menu',
    'bind13': '44:btn_fforward',
    'bind14': '64:btn_escape',
    'bind15': '65:btn_jump_state',
    'bind16': '66:btn_quick_save',
    'bind17': '67:btn_screenshot',
    'bind18': '79:btn_dpad1_right',
    'bind19': '80:btn_dpad1_left',
    'bind20': '81:btn_dpad1_down',
    'bind21': '82:btn_dpad1_up',
}


# Create the controller configuration file
def generate_controller_config(
    mapping_dir: Path, controller: Controller, type: Literal['dreamcast', 'arcade'], /
) -> None:
    # Set config file name
    if type == 'dreamcast':
        _logger.debug('-=[ Dreamcast Controller Settings ]=-')
        config_file = mapping_dir / f'SDL_{controller.real_name}.cfg'
    else:  # 'arcade'
        _logger.debug('-=[ Arcade Controller Settings ]=-')
        config_file = mapping_dir / f'SDL_{controller.real_name}_arcade.cfg'

    config = configparser.ConfigParser(interpolation=None)

    config_file.parent.mkdir(parents=True, exist_ok=True)

    # create ini sections
    for section in _SECTIONS:
        config.add_section(section)

    # Parse controller inputs
    _logger.debug('*** Controller Name = %s ***', controller.real_name)
    analog_bind = 0
    digital_bind = 0
    input_mapping = _FLYCAST_INPUT_MAPPINGS[type]

    for input in controller.inputs.values():
        if input.name not in input_mapping:
            continue

        if input.type not in input_mapping[input.name]:
            _logger.debug('Input type: %s / %s - not in mapping', input.type, input.name)
            continue

        var = input_mapping[input.name][input.type]
        _logger.debug('Input Name = %s, Var = %s, Type = %s', input.name, var, input.type)
        # batocera doesn't retrieve the code for hats, however
        # SDL is 256 for up, 257 for down, 258 for left & 259 for right
        if input.type == 'hat':
            code = _HAT_CODE_MAPPING[input.name]
            option = f'bind{digital_bind}'
            digital_bind = digital_bind + 1
            config.set('digital', option, f'{code}:{var}')

        elif input.type == 'button':
            option = f'bind{digital_bind}'
            digital_bind = digital_bind + 1
            code = input.id
            config.set('digital', option, f'{code}:{var}')

        elif input.type == 'axis':
            section = 'analog'

            if input.name == 'l2' or input.name == 'r2':
                # Use positive axis for full trigger control
                code = f'{input.id}+'
            else:
                code = f'{input.id}-'

            option = f'bind{analog_bind}'
            analog_bind = analog_bind + 1

            if 'left' in input.name or 'up' in input.name:
                config.set(section, option, f'{code}:{var}')
                # becase we only take one axis input
                # now have to write the joy-right & joy-down manually
                # we use the same code number but positive axis
                option = f'bind{analog_bind}'
                analog_bind = analog_bind + 1

                if input.name == 'joystick1left':
                    code = f'{input.id}+'
                    var = 'btn_analog_right'
                    config.set(section, option, f'{code}:{var}')
                elif input.name == 'joystick1up':
                    code = f'{input.id}+'
                    var = 'btn_analog_down'
                    config.set(section, option, f'{code}:{var}')
                elif input.name == 'joystick2left':
                    code = f'{input.id}+'
                    var = 'axis2_right'
                    config.set(section, option, f'{code}:{var}')
                elif input.name == 'joystick2up':
                    code = f'{input.id}+'
                    var = 'axis2_down'
                    config.set(section, option, f'{code}:{var}')
                elif input.name == 'up':
                    code = f'{input.id}+'
                    var = 'btn_dpad1_down'
                    config.set(section, option, f'{code}:{var}')
                elif input.name == 'left':
                    code = f'{input.id}+'
                    var = 'btn_dpad1_right'
                    config.set(section, option, f'{code}:{var}')
            else:
                config.set(section, option, f'{code}:{var}')

        # Add additional controller info
        config.set('emulator', 'dead_zone', '10')
        config.set('emulator', 'mapping_name', 'Default')  # controller.real_name)
        config.set('emulator', 'rumble_power', '100')
        config.set('emulator', 'version', '3')

    with config_file.open('w') as f:
        config.write(f)


def generate_keyboard_config(mapping_dir: Path, /) -> None:
    config_file = mapping_dir / 'SDL_Keyboard.cfg'
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser(interpolation=None)

    # Add cfg sections
    config.add_section('digital')
    config.add_section('emulator')

    # Set each binding in the config
    for bind, val in _KEYBOARD_BINDINGS.items():
        config.set('digital', bind, val)

    # Add the additional keyboard info to the emulator section
    config.set('emulator', 'dead_zone', '10')
    config.set('emulator', 'mapping_name', 'Keyboard')
    config.set('emulator', 'rumble_power', '100')
    config.set('emulator', 'saturation', '100')
    config.set('emulator', 'version', '3')

    with config_file.open('w') as f:
        config.write(f)
