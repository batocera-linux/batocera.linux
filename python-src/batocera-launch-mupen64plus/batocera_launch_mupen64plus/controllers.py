from __future__ import annotations

from typing import TYPE_CHECKING, Final
from xml.dom import minidom

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Controller, Emulator, Input, InputMapping
from batocera_launch.paths import DATAINIT_DIR

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from batocera_common.configparser import CaseSensitiveConfigParser

_MUPEN64PLUS_SYSTEM_MAPPING: Final = DATAINIT_DIR / 'system' / 'configs' / 'mupen64' / 'input.xml'

# Must read :
# http://mupen64plus.org/wiki/index.php?title=Mupen64Plus_Plugin_Parameters

# Mupen doesn't like to have 2 buttons mapped for N64 pad entry. That's why r2 is commented for now. 1 axis and 1 button is ok
_MUPEN_HAT_TO_AXIS: Final = {'1': 'Up', '2': 'Right', '4': 'Down', '8': 'Left'}
_MUPEN_HAT_TO_REVERSE_AXIS: Final = {'1': 'Down', '2': 'Left', '4': 'Up', '8': 'Right'}
_MUPEN_DOUBLE_AXIS: Final = {0: 'X Axis', 1: 'Y Axis'}

_VALID_N64_CONTROLLER_GUIDS: Final = [
    '050000007e0500001920000001800000',  # official nintendo switch n64 controller
    '05000000c82d00006928000000010000',  # 8bitdo n64 modkit
    '030000007e0500001920000011810000',
    '05000000c82d00001930000001000000',  # 8bitdo n64 bt
    '03000000c82d00001930000011010000',  # 8bitdo n64 wired
]

_VALID_N64_CONTROLLER_NAMES: Final = [
    'N64 Controller',
    'Nintendo Co., Ltd. N64 Controller',
    '8BitDo N64 Modkit',
    '8BitDo 64 BT',
    '8BitDo 8BitDo 64 Bluetooth Controller',
]


def _get_controller_line(
    mupen_mapping: Mapping[str, str],
    input_: Input,
    mupen_setting_name: str,
    all_inputs: InputMapping,
    /,
) -> str:
    value = ''
    input_type = input_.type
    if input_type == 'button':
        if mupen_setting_name in ('X Axis', 'Y Axis'):  # special case for these 2 axis...
            # hum, a button is mapped on an axis, find the reverse button
            if input_.name == 'up':
                if 'down' in all_inputs:
                    reverse_input = all_inputs['down']
                    value = f'button({input_.id}, {reverse_input.id})'
                else:
                    value = f'button({input_.id})'
            elif input_.name == 'left':
                if 'right' in all_inputs:
                    reverse_input = all_inputs['right']
                    value = f'button({input_.id}, {reverse_input.id})'
                else:
                    value = f'button({input_.id})'
            else:
                return ''  # skip down and right
        else:
            # normal button
            value = f'button({input_.id})'
    elif input_type == 'hat':
        if mupen_setting_name in ('X Axis', 'Y Axis'):  # special case for these 2 axis...
            if input_.value == '1' or input_.value == '8':  # only for the lower value to avoid duplicate
                value = (
                    f'hat({input_.id} {_MUPEN_HAT_TO_AXIS[input_.value]} {_MUPEN_HAT_TO_REVERSE_AXIS[input_.value]})'
                )
        else:
            value = f'hat({input_.id} {_MUPEN_HAT_TO_AXIS[input_.value]})'
    elif input_type == 'axis':
        # Generic case for joystick1up and joystick1left
        if mupen_setting_name in _MUPEN_DOUBLE_AXIS.values():
            # X axis : value = -1 for left, +1 for right
            # Y axis : value = -1 for up, +1 for down
            # we configure only left and down to not configure 2 times each axis
            if input_.name in ('left', 'up', 'joystick1left', 'joystick1up', 'joystick2left', 'joystick2up'):
                if input_.value == '-1':
                    value = f'axis({input_.id}-,{input_.id}+)'
                else:
                    value = f'axis({input_.id}+,{input_.id}-)'
        else:
            if input_.value == '1':
                value = f'axis({input_.id}+)'
            else:
                value = f'axis({input_.id}-)'
    return value


def _fill_ini_player(
    controller: Controller, ini_config: CaseSensitiveConfigParser, pad_config: dict[str, str], /
) -> None:
    section = f'Input-SDL-Control{controller.player_number}'

    # set static config
    if not ini_config.has_section(section):
        ini_config.add_section(section)
    ini_config.set(section, 'Version', '2')
    ini_config.set(section, 'mode', '0')
    ini_config.set(section, 'device', str(controller.index))
    # TODO: python 3 remove hack to overcome ConfigParser limitation with utf8 in python 2.7
    name_encode = controller.real_name.encode('ascii', 'ignore')
    ini_config.set(section, 'name', str(name_encode))
    ini_config.set(section, 'plugged', 'True')
    ini_config.set(section, 'plugin', '2')
    ini_config.set(section, 'AnalogDeadzone', str(pad_config['AnalogDeadzone']))
    ini_config.set(section, 'AnalogPeak', str(pad_config['AnalogPeak']))
    ini_config.set(section, 'mouse', 'False')

    # set dynamic config - clear all keys then fill
    ini_config.set(section, 'Mempak switch', '')
    ini_config.set(section, 'Rumblepak switch', '')
    ini_config.set(section, 'C Button R', '')
    ini_config.set(section, 'A Button', '')
    ini_config.set(section, 'C Button U', '')
    ini_config.set(section, 'B Button', '')
    ini_config.set(section, 'Start', '')
    ini_config.set(section, 'L Trig', '')
    ini_config.set(section, 'R Trig', '')
    ini_config.set(section, 'Z Trig', '')
    ini_config.set(section, 'DPad U', '')
    ini_config.set(section, 'DPad D', '')
    ini_config.set(section, 'DPad R', '')
    ini_config.set(section, 'DPad L', '')
    ini_config.set(section, 'Y Axis', '')
    ini_config.set(section, 'Y Axis', '')
    ini_config.set(section, 'X Axis', '')
    ini_config.set(section, 'X Axis', '')
    ini_config.set(section, 'C Button U', '')
    ini_config.set(section, 'C Button D', '')
    ini_config.set(section, 'C Button L', '')
    ini_config.set(section, 'C Button R', '')
    for input_name in sorted(pad_config):
        ini_config.set(section, input_name, pad_config[input_name])


def _clean_player(nplayer: int, ini_config: CaseSensitiveConfigParser, /) -> None:
    section = f'Input-SDL-Control{nplayer}'

    # set static config
    if not ini_config.has_section(section):
        ini_config.add_section(section)
    ini_config.set(section, 'Version', '2')
    ini_config.set(section, 'plugged', 'False')


@cached_dataclass
class Mupen64PlusControllersMixin(Emulator):
    @cached_property
    def user_input_mapping_file(self) -> Path:
        return self.config_dir / 'input.xml'

    @cached_property
    def user_n64_input_mapping(self) -> dict[str, str]:
        return self._get_mupen_mapping(True)

    @cached_property
    def user_input_mapping(self) -> dict[str, str]:
        return self._get_mupen_mapping(False)

    def _get_mupen_mapping(self, use_n64_inputs: bool, /) -> dict[str, str]:
        # load system values and override by user values in case some user values are missing
        mapping: dict[str, str] = {}
        for file in (_MUPEN64PLUS_SYSTEM_MAPPING, self.user_input_mapping_file):
            if file.exists():
                dom = minidom.parse(str(file))
                list_name = 'n64InputList' if use_n64_inputs else 'defaultInputList'
                for inputs in dom.getElementsByTagName(list_name):
                    for input_node in inputs.childNodes:
                        if input_node.attributes and input_node.attributes['name'] and input_node.attributes['value']:
                            mapping[input_node.attributes['name'].value] = input_node.attributes['value'].value
        return mapping

    def _define_controller_keys(self, controller: Controller, is_wheel: bool, /) -> dict[str, str]:
        # check for auto-config inputs by guid and name, or es settings
        if (controller.guid in _VALID_N64_CONTROLLER_GUIDS and controller.name in _VALID_N64_CONTROLLER_NAMES) or (
            self.config.get(f'mupen64-controller{controller.player_number}', 'retropad') != 'retropad'
        ):
            mupen_mapping = dict(self.user_n64_input_mapping)
        else:
            mupen_mapping = dict(self.user_input_mapping)

        # pad_config holds the final pad configuration in the mupen style
        # ex: pad_config['DPad U'] = "button(1)"
        pad_config: dict[str, str] = {}

        # determine joystick deadzone and peak
        pad_config['AnalogPeak'] = self._get_joystick_peak(
            mupen_mapping['AnalogPeak'], f'mupen64-sensitivity{controller.player_number}'
        )

        # Analog Deadzone
        if is_wheel:
            pad_config['AnalogDeadzone'] = '0,0'
        else:
            pad_config['AnalogDeadzone'] = self._get_joystick_deadzone(
                mupen_mapping['AnalogPeak'], f'mupen64-deadzone{controller.player_number}'
            )

        # z is important, in case l2 is not available for this pad, use l1
        # assume that l2 is for "Z Trig" in the mapping
        if 'l2' not in controller.inputs:
            mupen_mapping['pageup'] = mupen_mapping['l2']

        # if joystick1up is not available, use up/left while these keys are more used
        if 'joystick1up' not in controller.inputs:
            mupen_mapping['up'] = mupen_mapping['joystick1up']
            mupen_mapping['down'] = mupen_mapping['joystick1down']
            mupen_mapping['left'] = mupen_mapping['joystick1left']
            mupen_mapping['right'] = mupen_mapping['joystick1right']

        # the input.xml adds 2 directions per joystick, ES handles just 1
        fake_sticks = {'joystick2up': 'joystick2down', 'joystick2left': 'joystick2right'}
        # Cheat on the controller
        for real_stick, fake_stick in fake_sticks.items():
            if real_stick in controller.inputs and controller.inputs[real_stick].type == 'axis':
                controller.inputs[fake_stick] = controller.inputs[real_stick].replace(
                    name=fake_stick,
                    value=str(-int(controller.inputs[real_stick].value)),
                )

        for input_idx in controller.inputs:
            pad_input = controller.inputs[input_idx]
            if pad_input.name in mupen_mapping and mupen_mapping[pad_input.name] != '':
                value = _get_controller_line(mupen_mapping, pad_input, mupen_mapping[pad_input.name], controller.inputs)
                # Handle multiple inputs for a single N64 Pad input
                if value != '':
                    if mupen_mapping[pad_input.name] not in pad_config:
                        pad_config[mupen_mapping[pad_input.name]] = value
                    else:
                        pad_config[mupen_mapping[pad_input.name]] += f' {value}'
        return pad_config

    def _get_joystick_peak(self, start_value: str, config_value: str, /) -> str:
        default_value = int(start_value.split(',')[0])
        multiplier = self.config.get_float(config_value, 1)

        # This is needed because higher peak value lowers sensitivity and vice versa
        if multiplier != 1.0:
            adjusted_value = default_value * multiplier
            difference = abs(adjusted_value - default_value)

            # Figure out if we need to add or subtract the starting peak value
            if adjusted_value < default_value:
                peak = round(default_value + difference)
            else:
                peak = round(default_value - difference)
        else:
            peak = default_value

        return f'{peak},{peak}'

    def _get_joystick_deadzone(self, default_peak: str, config_value: str, /) -> str:
        default_value = int(default_peak.split(',')[0])
        deadzone_multiplier = self.config.get_float(config_value, 0.01)

        deadzone = round(default_value * deadzone_multiplier)

        return f'{deadzone},{deadzone}'

    def set_controllers_config(self, ini_config: CaseSensitiveConfigParser, /) -> None:
        for pad in self.controllers:
            is_wheel = pad.device_path in self.wheels and self.wheels[pad.device_path].is_wheel
            pad_config = self._define_controller_keys(pad, is_wheel)
            _fill_ini_player(pad, ini_config, pad_config)

        # remove section with no player
        for x in range(len(self.controllers) + 1, 4):
            section = f'Input-SDL-Control{x}'
            if ini_config.has_section(section):
                _clean_player(x, ini_config)
