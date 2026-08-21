from __future__ import annotations

import itertools
import os
from dataclasses import InitVar, dataclass, field
from typing import TYPE_CHECKING, Self
from xml.dom import minidom

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from pathlib import Path

    from batocera_launch import Controller, Input

    from .mame_control_scheme import MameControlScheme


def get_input_definition(
    controller: Controller,
    input: Input,
    key: str,
    reversed: bool,
    /,
    *,
    control_scheme: MameControlScheme | None = None,
    ignore_axis: bool = False,
    is_wheel: bool = False,
) -> str:
    mame_axis_mapping_names = {0: 'XAXIS', 1: 'YAXIS', 2: 'ZAXIS', 3: 'RXAXIS', 4: 'RYAXIS', 5: 'RZAXIS'}
    joycode = controller.index + 1

    if is_wheel and (key == 'joystick1left' or key == 'l2' or key == 'r2'):
        suffix = ''
        if key == 'r2':
            suffix = '_NEG'
        if key == 'l2':
            suffix = '_NEG'
        if int(input.id) in mame_axis_mapping_names:
            id_name = mame_axis_mapping_names[int(input.id)]
            return f'JOYCODE_{joycode}_{id_name}{suffix}'

    if input.type == 'button':
        return f'JOYCODE_{joycode}_BUTTON{int(input.id) + 1}'

    if input.type == 'hat':
        if input.value == '1':
            return f'JOYCODE_{joycode}_HAT1UP'
        if input.value == '2':
            return f'JOYCODE_{joycode}_HAT1RIGHT'
        if input.value == '4':
            return f'JOYCODE_{joycode}_HAT1DOWN'
        if input.value == '8':
            return f'JOYCODE_{joycode}_HAT1LEFT'

    elif input.type == 'axis':
        # Determine alternate button for D-Pad and right stick as buttons
        dpad_inputs: dict[str, str] = {}
        for direction in ['up', 'down', 'left', 'right']:
            if controller.inputs[direction].type == 'button':
                dpad_inputs[direction] = f'JOYCODE_{joycode}_BUTTON{int(controller.inputs[direction].id) + 1}'
            elif controller.inputs[direction].type == 'hat':
                if controller.inputs[direction].value == '1':
                    dpad_inputs[direction] = f'JOYCODE_{joycode}_HAT1UP'
                if controller.inputs[direction].value == '2':
                    dpad_inputs[direction] = f'JOYCODE_{joycode}_HAT1RIGHT'
                if controller.inputs[direction].value == '4':
                    dpad_inputs[direction] = f'JOYCODE_{joycode}_HAT1DOWN'
                if controller.inputs[direction].value == '8':
                    dpad_inputs[direction] = f'JOYCODE_{joycode}_HAT1LEFT'
            else:
                dpad_inputs[direction] = ''

        button_directions: dict[str, str] = {}
        # workarounds for issue #6892
        # Modified because right stick to buttons was not working after the workaround
        # Creates a blank, only modifies if the button exists in the pad.
        # Button assigment modified - blank "OR" gets removed by MAME if the button is undefined.
        for direction in ['a', 'b', 'x', 'y']:
            button_directions[direction] = ''
            if direction in controller.inputs and controller.inputs[direction].type == 'button':
                button_directions[direction] = f'JOYCODE_{joycode}_BUTTON{int(controller.inputs[direction].id) + 1}'

        if (
            ignore_axis
            and dpad_inputs['up'] != ''
            and dpad_inputs['down'] != ''
            and dpad_inputs['left'] != ''
            and dpad_inputs['right'] != ''
        ):
            if key == 'joystick1up' or key == 'up':
                return dpad_inputs['up']
            if key == 'joystick1down' or key == 'down':
                return dpad_inputs['down']
            if key == 'joystick1left' or key == 'left':
                return dpad_inputs['left']
            if key == 'joystick1right' or key == 'right':
                return dpad_inputs['right']

        if control_scheme == 'qbert':  # Q*Bert Joystick
            if key == 'joystick1up' or key == 'up':
                return f'JOYCODE_{joycode}_YAXIS_UP_SWITCH JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH OR {dpad_inputs["up"]} {dpad_inputs["right"]}'
            if key == 'joystick1down' or key == 'down':
                return f'JOYCODE_{joycode}_YAXIS_DOWN_SWITCH JOYCODE_{joycode}_XAXIS_LEFT_SWITCH OR {dpad_inputs["down"]} {dpad_inputs["left"]}'
            if key == 'joystick1left' or key == 'left':
                return f'JOYCODE_{joycode}_XAXIS_LEFT_SWITCH JOYCODE_{joycode}_YAXIS_UP_SWITCH OR {dpad_inputs["left"]} {dpad_inputs["up"]}'
            if key == 'joystick1right' or key == 'right':
                return f'JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH JOYCODE_{joycode}_YAXIS_DOWN_SWITCH OR {dpad_inputs["right"]} {dpad_inputs["down"]}'
        else:
            if key == 'joystick1up' or key == 'up':
                return f'JOYCODE_{joycode}_YAXIS_UP_SWITCH OR {dpad_inputs["up"]}'
            if key == 'joystick1down' or key == 'down':
                return f'JOYCODE_{joycode}_YAXIS_DOWN_SWITCH OR {dpad_inputs["down"]}'
            if key == 'joystick1left' or key == 'left':
                return f'JOYCODE_{joycode}_XAXIS_LEFT_SWITCH OR {dpad_inputs["left"]}'
            if key == 'joystick1right' or key == 'right':
                return f'JOYCODE_{joycode}_XAXIS_RIGHT_SWITCH OR {dpad_inputs["right"]}'
        # Fix for the workaround
        for _ in controller.inputs:
            if key == 'joystick2up':
                return f'JOYCODE_{joycode}_RYAXIS_NEG_SWITCH OR {button_directions["x"]}'
            if key == 'joystick2down':
                return f'JOYCODE_{joycode}_RYAXIS_POS_SWITCH OR {button_directions["b"]}'
            if key == 'joystick2left':
                return f'JOYCODE_{joycode}_RXAXIS_NEG_SWITCH OR {button_directions["y"]}'
            if key == 'joystick2right':
                return f'JOYCODE_{joycode}_RXAXIS_POS_SWITCH OR {button_directions["a"]}'
            if int(input.id) in mame_axis_mapping_names:
                id_name = mame_axis_mapping_names[int(input.id)]
                return f'JOYCODE_{joycode}_{id_name}_POS_SWITCH'

    return 'unknown'


@dataclass(slots=True)
class ControlConfig:
    document: minidom.Document = field(default_factory=minidom.Document)
    system_name: InitVar[str] = 'default'

    system_elem: minidom.Element = field(init=False)
    input_elem: minidom.Element = field(init=False)

    def __post_init__(self, system_name: str) -> None:
        mameconfig = self.get_or_create('mameconfig')
        mameconfig.setAttribute('version', '10')  # otherwise, config of pad won't work at first run (batocera v33)

        self.system_elem = self.get_or_create('system', parent=mameconfig)
        self.system_elem.setAttribute('name', system_name)

        self.remove_system_elements('input')

        self.input_elem = self.add_system_element('input')

    def get_or_create(self, name: str, /, *, parent: minidom.Element | None = None) -> minidom.Element:
        elements = self.document.getElementsByTagName(name)

        if elements:
            return elements[0]

        element = self.document.createElement(name)
        (parent or self.document).appendChild(element)
        return element

    def create_element(self, tag_name: str, /, **attributes: str) -> minidom.Element:
        element = self.document.createElement(tag_name)

        for key, value in attributes.items():
            element.setAttribute(key, value)

        return element

    def create_child_element(self, parent: minidom.Element, tag_name: str, /, **attributes: str) -> minidom.Element:
        element = self.create_element(tag_name, **attributes)

        parent.appendChild(element)

        return element

    def add_system_element(self, tag_name: str, /, **attributes: str) -> minidom.Element:
        return self.create_child_element(self.system_elem, tag_name, **attributes)

    def add_input_element(self, tag_name: str, /, **attributes: str) -> minidom.Element:
        return self.create_child_element(self.input_elem, tag_name, **attributes)

    def remove_system_elements(self, name: str, /) -> None:
        elements = self.system_elem.getElementsByTagName(name)

        for element in elements:
            old = self.system_elem.removeChild(element)
            old.unlink()

    def initialize_crosshairs(self, crosshairs_config: str | None, /) -> None:
        self.remove_system_elements('crosshairs')
        crosshairs_element = self.add_system_element('crosshairs')

        for p in range(4):
            crosshair_attributes: dict[str, str] = {'player': str(p)}

            if crosshairs_config == 'enabled':
                crosshair_attributes['mode'] = '1'
            elif crosshairs_config == 'onmove':
                continue  # keep no line
            else:
                crosshair_attributes['mode'] = '0'

            self.create_child_element(crosshairs_element, 'crosshair', **crosshair_attributes)

        self.system_elem.appendChild(crosshairs_element)

    def _add_port_element(
        self,
        type: str,
        /,
        tag: str | None = None,
        mask: str | None = None,
        defvalue: str | None = None,
        key_delta: str | None = None,
        sequence: str | tuple[str, str] | None = None,
        sequences: Iterable[str | tuple[str, str]] | None = None,
    ) -> None:
        port_attributes: dict[str, str] = {'type': type}

        if tag is not None:
            port_attributes['tag'] = tag
        if mask is not None:
            port_attributes['mask'] = mask
        if defvalue is not None:
            port_attributes['defvalue'] = defvalue
        if key_delta is not None:
            port_attributes['keydelta'] = key_delta

        port = self.add_input_element('port', **port_attributes)

        if sequence is not None:
            sequences = [sequence] if sequences is None else itertools.chain([sequence], sequences)

        if sequences is not None:
            for sequence_item in sequences:
                if isinstance(sequence_item, str):
                    newseq_type = 'standard'
                    value = sequence_item
                else:
                    newseq_type, value = sequence_item

                newseq = self.create_child_element(port, 'newseq', type=newseq_type)
                newseq.appendChild(self.document.createTextNode(value))

    def add_sequence_port(
        self,
        port_type: str,
        /,
        *,
        sequence: str | tuple[str, str] | None = None,
        sequences: Iterable[str | tuple[str, str]] | None = None,
        tag: str | None = None,
        mask: str | None = None,
        defvalue: str | None = None,
        key_delta: str | None = None,
    ) -> None:
        self._add_port_element(
            port_type,
            tag=tag,
            mask=mask,
            defvalue=defvalue,
            key_delta=key_delta,
            sequence=sequence,
            sequences=sequences,
        )

    def add_common_player_ports(self, player_number: int, /) -> None:
        # adstick for guns
        for axis, analog_number in [('X', 1), ('Y', 2)]:
            self._add_port_element(
                f'P{player_number}_AD_STICK_{axis}',
                tag=f':mainpcb:ANALOG{analog_number}',
                mask='255',
                defvalue='128',
                sequence=f'GUNCODE_{player_number}_{axis}AXIS',
            )

    def add_port(
        self,
        controller: Controller,
        player_number: int,
        mapping: str,
        key: str,
        input: Input,
        reversed: bool,
        control_scheme: MameControlScheme,
        gun_mappings: Mapping[str, str],
        mouse_mappings: Mapping[str, str],
        is_wheel: bool,
        multi_mouse: bool,
        pedal_key: str | None,
        /,
    ) -> None:
        # Generic input
        keyval = get_input_definition(
            controller, input, key, reversed, control_scheme=control_scheme, is_wheel=is_wheel
        )
        if mapping in gun_mappings:
            keyval = keyval + f' OR GUNCODE_{player_number}_{gun_mappings[mapping]}'
            if gun_mappings[mapping] == 'BUTTON2' and pedal_key is not None:
                keyval += f' OR KEYCODE_{pedal_key.upper()}'
        if mapping in mouse_mappings:
            if multi_mouse:
                keyval = keyval + f' OR MOUSECODE_{player_number}_{mouse_mappings[mapping]}'
            else:
                keyval = keyval + f' OR MOUSECODE_1_{mouse_mappings[mapping]}'

        self._add_port_element(f'P{player_number}_{mapping}', sequence=keyval)

    def add_gun_port(
        self,
        player_number: int,
        mapping: str,
        gun_mappings: Mapping[str, str],
        pedal_key: str | None,
    ) -> None:
        # Generic input
        keyval = None

        if mapping in gun_mappings:
            keyval = f'GUNCODE_{player_number}_{gun_mappings[mapping]}'
            if gun_mappings[mapping] == 'BUTTON2' and pedal_key is not None:
                keyval += f' OR KEYCODE_{pedal_key.upper()}'

        if keyval is None:
            return

        self._add_port_element(
            f'{mapping}{player_number}' if mapping in {'START', 'COIN'} else f'P{player_number}_{mapping}',
            sequence=keyval,
        )

    def add_special_player_port(
        self,
        controller: Controller,
        player_number: int,
        tag: str,
        mapping: str,
        key: str,
        input: Input,
        reversed: bool,
        mask: int | None,
        default: int | None,
        gun_mappings: Mapping[str, str],
        mouse_mappings: Mapping[str, str],
        multi_mouse: bool,
        pedal_key: str | None,
        /,
        *,
        port_type: str | None = None,
    ) -> None:
        # Special button input (ie mouse button to gamepad)

        # Use the custom port type if provided, otherwise default to START1/COIN1 style
        if port_type is None:
            port_type = f'{mapping}{player_number}'

        keyval = get_input_definition(controller, input, key, reversed)

        if mapping == 'COIN' and player_number <= 4:
            keyval = (
                keyval + f' OR KEYCODE_{player_number}_{player_number + 4}'
            )  # 5 for player 1, 6 for player 2, 7 for player 3 and 8 for player 4

        if mapping in gun_mappings:
            keyval = keyval + f' OR GUNCODE_{player_number}_{gun_mappings[mapping]}'
            if gun_mappings[mapping] == 'BUTTON2' and pedal_key is not None:
                keyval += f' OR KEYCODE_{pedal_key.upper()}'

        if mapping in mouse_mappings:
            if multi_mouse:
                keyval = keyval + f' OR MOUSECODE_{player_number}_{mouse_mappings[mapping]}'
            else:
                keyval = keyval + f' OR MOUSECODE_1_{mouse_mappings[mapping]}'

        self._add_port_element(
            port_type,
            tag=tag,
            mask='' if mask is None else f'{mask}',
            defvalue='' if default is None else f'{default}',
            sequence=keyval,
        )

    def add_special_port(
        self,
        controller: Controller,
        tag: str,
        mapping: str,
        key: str,
        input: Input,
        reversed: bool,
        mask: int | None,
        default: int | None,
        pedal_key: str | None,
        /,
    ) -> None:
        # Special button input (ie mouse button to gamepad)
        self._add_port_element(
            mapping,
            tag=tag,
            mask='' if mask is None else f'{mask}',
            defvalue='' if default is None else f'{default}',
            sequence=get_input_definition(controller, input, key, reversed),
        )

    def add_combo_port(
        self,
        controller: Controller,
        tag: str,
        mapping: str,
        keyboard_key: str,
        key: str,
        input: Input,
        /,
        reversed: bool = False,
        mask: int | None = None,
        default: int | None = None,
    ) -> None:
        # Maps a keycode + button - for important keyboard keys when available
        self._add_port_element(
            mapping,
            tag=tag,
            mask='' if mask is None else f'{mask}',
            defvalue='' if default is None else f'{default}',
            sequence=f'KEYCODE_{keyboard_key} OR {get_input_definition(controller, input, key, reversed)}',
        )

    def add_analog_port(
        self,
        controller: Controller,
        player_number: int,
        tag: str,
        mapping: str,
        inc_key: str,
        dec_key: str,
        mapped_input: Input,
        mapped_input2: Input,
        reversed: bool,
        mask: int | None,
        default: int | None,
        delta: int,
        axis: str,
    ) -> None:
        # Mapping analog to digital (mouse, etc)
        self._add_port_element(
            mapping,
            tag=tag,
            mask='' if mask is None else f'{mask}',
            defvalue='' if default is None else f'{default}',
            key_delta=f'{delta}',
            sequences=[
                ('increment', get_input_definition(controller, mapped_input, inc_key, reversed, ignore_axis=True)),
                ('decrement', get_input_definition(controller, mapped_input2, dec_key, reversed, ignore_axis=True)),
                ('standard', 'NONE' if not axis else f'JOYCODE_{controller.index + 1}_{axis}'),
            ],
        )

    def save(self, path: Path, /) -> None:
        path.write_text(
            # remove ugly empty lines while minicom adds them...
            os.linesep.join([s for s in self.document.toprettyxml().splitlines() if s.strip()]),
            encoding='utf-8',
        )

    @classmethod
    def load(cls, path: Path, /, *, system_name: str = 'default') -> Self:
        document = minidom.Document()

        try:
            document = minidom.parse(str(path))
        except Exception:
            pass

        return cls(document, system_name)
