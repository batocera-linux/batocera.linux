from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, cast

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

from ..devices.video import get_refresh_rate

if TYPE_CHECKING:
    from ..devices.input import Input


class _ButtonSequence(TypedDict):
    button: str
    keyboard: NotRequired[str]


class _ButtonComboSequence(TypedDict):
    buttons: tuple[str, str]
    keyboard: NotRequired[str]


class _KeyboardSequence(TypedDict):
    keyboard: str


class _BlankSequence(TypedDict):
    blank: None


type _ControllerSequence = _ButtonSequence | _ButtonComboSequence | _KeyboardSequence | _BlankSequence


# BigPEmu controller sequence, P1 only requires keyboard inputs
# default standard bindings
P1_BINDINGS_SEQUENCE: dict[str, _ControllerSequence] = {
    'C': {'button': 'y', 'keyboard': '4'},
    'B': {'button': 'b', 'keyboard': '22'},
    'A': {'button': 'a', 'keyboard': '7'},
    'Pause': {'button': 'select', 'keyboard': '20'},
    'Option': {'button': 'start', 'keyboard': '26'},
    'Pad-Up': {'button': 'up', 'keyboard': '82'},
    'Pad-Down': {'button': 'down', 'keyboard': '81'},
    'Pad-Left': {'button': 'left', 'keyboard': '80'},
    'Pad-Right': {'button': 'right', 'keyboard': '79'},
    'Numpad-0': {'buttons': ('r3', 'l2'), 'keyboard': '39'},
    'Numpad-1': {'buttons': ('y', 'l2'), 'keyboard': '30'},
    'Numpad-2': {'buttons': ('x', 'l2'), 'keyboard': '31'},
    'Numpad-3': {'buttons': ('a', 'l2'), 'keyboard': '32'},
    'Numpad-4': {'button': 'pageup', 'keyboard': '33'},
    'Numpad-5': {'button': 'x', 'keyboard': '34'},
    'Numpad-6': {'button': 'pagedown', 'keyboard': '35'},
    'Numpad-7': {'buttons': ('pageup', 'l2'), 'keyboard': '36'},
    'Numpad-8': {'buttons': ('b', 'l2'), 'keyboard': '37'},
    'Numpad-9': {'buttons': ('pagedown', 'l2'), 'keyboard': '38'},
    'Asterick': {'button': 'l3', 'keyboard': '18'},
    'Pound': {'button': 'r3', 'keyboard': '19'},
    'Analog-0-left': {'button': 'joystick1left'},
    # "Analog-0-right": {"button": "joystick1right"},
    'Analog-0-up': {'button': 'joystick1up'},
    # "Analog-0-down": {"button": "joystick1down"},
    'Analog-1-left': {'button': 'joystick2left'},
    # "Analog-1-right": {"button": "joystick2right"},
    'Analog-1-up': {'button': 'joystick2up'},
    # "Analog-1-down": {"button": "joystick2down"},
    'Extra-Up': {'blank': None},
    'Extra-Down': {'blank': None},
    'Extra-Left': {'blank': None},
    'Extra-Right': {'blank': None},
    'Extra-A': {'blank': None},
    'Extra-B': {'blank': None},
    'Extra-C': {'blank': None},
    'Extra-D': {'blank': None},
    'Menu': {'buttons': ('start', 'r2'), 'keyboard': '41'},
    'Fast Forward': {'buttons': ('x', 'r2'), 'keyboard': '59'},
    'Rewind': {'blank': None},
    'Save State': {'keyboard': '66'},
    'Load State': {'keyboard': '62'},
    'Screenshot': {'keyboard': '63'},
    'Overlay': {'buttons': ('l3', 'r2')},
    'Chat': {'keyboard': '23'},
    'Blank1': {'blank': None},
    'Blank2': {'blank': None},
    'Blank3': {'blank': None},
    'Blank4': {'blank': None},
    'Blank5': {'blank': None},
}

# BigPEmu controller sequence, P2+
# default standard bindings
P2_BINDINGS_SEQUENCE: dict[str, _ControllerSequence] = {
    'C': {'button': 'y'},
    'B': {'button': 'b'},
    'A': {'button': 'a'},
    'Pause': {'button': 'select'},
    'Option': {'button': 'start'},
    'Pad-Up': {'button': 'up'},
    'Pad-Down': {'button': 'down'},
    'Pad-Left': {'button': 'left'},
    'Pad-Right': {'button': 'right'},
    'Numpad-0': {'buttons': ('r3', 'l2')},
    'Numpad-1': {'buttons': ('y', 'l2')},
    'Numpad-2': {'buttons': ('x', 'l2')},
    'Numpad-3': {'buttons': ('a', 'l2')},
    'Numpad-4': {'button': 'pageup'},
    'Numpad-5': {'button': 'x'},
    'Numpad-6': {'button': 'pagedown'},
    'Numpad-7': {'buttons': ('pageup', 'l2')},
    'Numpad-8': {'buttons': ('b', 'l2')},
    'Numpad-9': {'buttons': ('pagedown', 'l2')},
    'Asterick': {'button': 'l3'},
    'Pound': {'button': 'r3'},
    'Analog-0-left': {'button': 'joystick1left'},
    # "Analog-0-right": {"button": "joystick1right"},
    'Analog-0-up': {'button': 'joystick1up'},
    # "Analog-0-down": {"button": "joystick1down"},
    'Analog-1-left': {'button': 'joystick2left'},
    # "Analog-1-right": {"button": "joystick2right"},
    'Analog-1-up': {'button': 'joystick2up'},
    # "Analog-1-down": {"button": "joystick2down"},
    'Extra-Up': {'blank': None},
    'Extra-Down': {'blank': None},
    'Extra-Left': {'blank': None},
    'Extra-Right': {'blank': None},
    'Extra-A': {'blank': None},
    'Extra-B': {'blank': None},
    'Extra-C': {'blank': None},
    'Extra-D': {'blank': None},
}


class _Binding(TypedDict):
    Triggers: list[dict[str, bool | float | str]]


type _Bindings = list[_Binding]


def _generate_button_binding(
    binding_info: _ButtonSequence, device_id: str, input: Input, /, *, button_value: float | None = None
) -> _Binding:
    device_id = device_id.upper()

    if 'keyboard' in binding_info:
        return {
            'Triggers': [
                {'B_KB': True, 'B_ID': int(binding_info['keyboard']), 'B_AH': 0.0},
                {
                    'B_KB': False,
                    'B_ID': int(input.id),
                    'B_AH': float(input.value) if button_value is None else button_value,
                    'B_DevID': device_id,
                },
            ]
        }

    return {
        'Triggers': [
            {
                'B_KB': False,
                'B_ID': int(input.id),
                'B_AH': float(input.value) if button_value is None else button_value,
                'B_DevID': device_id,
            }
        ]
    }


def _generate_combo_binding(
    binding_info: _ButtonComboSequence, device_id: str, button: Input, analog: Input, /
) -> _Binding:
    device_id = device_id.upper()

    if 'keyboard' in binding_info:
        return {
            'Triggers': [
                {'B_KB': True, 'B_ID': int(binding_info['keyboard']), 'B_AH': 0.0},
                {
                    'B_KB': False,
                    'B_ID': int(button.id),
                    'B_AH': float(button.value),
                    'B_DevID': device_id,
                    'M_KB': False,
                    'M_ID': int(analog.id),
                    'M_AH': float(analog.value),
                    'M_DevID': device_id,
                },
            ]
        }

    return {
        'Triggers': [
            {
                'B_KB': False,
                'B_ID': int(button.id),
                'B_AH': float(button.value),
                'B_DevID': device_id,
                'M_KB': False,
                'M_ID': int(analog.id),
                'M_AH': float(analog.value),
                'M_DevID': device_id,
            }
        ]
    }


def _generate_blank_binding() -> _Binding:
    return {'Triggers': []}


def _generate_keyb_binding(keyb_id: str, /) -> _Binding:
    return {'Triggers': [{'B_KB': True, 'B_ID': int(keyb_id), 'B_AH': 0.0}]}


@cached_dataclass
class BigPEmu(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'bigpemu',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F9',
                'restore_state': 'KEY_F5',
            },
        }

    async def configure(self) -> Command:
        bigpemu_config = self.config_dir / 'BigPEmuConfig.bigpcfg'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Preserve user-configured keys that BigPEmu writes in-game and that
        # are not managed by the generator (BIOS paths, screen shader).
        _PRESERVED_KEYS = ('BootROM', 'CDBIOS', 'ScreenEffect')
        preserved: dict[str, Any] = {}
        if bigpemu_config.exists():
            try:
                existing = json.loads(bigpemu_config.read_text())
                for key in _PRESERVED_KEYS:
                    if key in existing.get('BigPEmuConfig', {}):
                        preserved[key] = existing['BigPEmuConfig'][key]
            except Exception:
                pass
            # Delete the config file to update controllers
            # As it doesn't like to be updated
            # ¯\_(ツ)_/¯
            bigpemu_config.unlink()

        config: dict[str, Any] = {}

        # Ensure the necessary structure in the config
        config['BigPEmuConfig'] = cast('dict[str, Any]', {})
        config['BigPEmuConfig']['Video'] = {}

        # Adjust basic settings
        config['BigPEmuConfig']['Video']['DisplayMode'] = 2
        config['BigPEmuConfig']['Video']['ScreenScaling'] = 5
        config['BigPEmuConfig']['Video']['DisplayWidth'] = self.resolution.width
        config['BigPEmuConfig']['Video']['DisplayHeight'] = self.resolution.height
        config['BigPEmuConfig']['Video']['DisplayFrequency'] = round(float(await get_refresh_rate()))

        # User selections
        config['BigPEmuConfig']['Video']['VSync'] = self.config.get('bigpemu_vsync', 1)
        config['BigPEmuConfig']['Video']['ScreenAspect'] = self.config.get_int('bigpemu_ratio', 2)
        config['BigPEmuConfig']['Video']['LockAspect'] = 1

        # Controller config
        config['BigPEmuConfig']['Input'] = {}

        # initial settings
        config['BigPEmuConfig']['Input']['DeviceCount'] = len(self.controllers)
        config['BigPEmuConfig']['Input']['AnalDeadMice'] = 0.25
        config['BigPEmuConfig']['Input']['AnalToDigi'] = 0.25
        config['BigPEmuConfig']['Input']['AnalExpo'] = 0.0
        config['BigPEmuConfig']['Input']['ConflictingPad'] = 0
        config['BigPEmuConfig']['Input']['XboxAnus'] = 0
        config['BigPEmuConfig']['Input']['OLAnchor'] = 3
        config['BigPEmuConfig']['Input']['OLScale'] = 0.75
        config['BigPEmuConfig']['Input']['MouseInput'] = 0
        config['BigPEmuConfig']['Input']['MouseSens'] = 1.0
        config['BigPEmuConfig']['Input']['MouseThresh'] = 0.5

        # per controller settings (standard controller only currently)
        for pad in self.controllers[:8]:
            device_section: dict[str, Any] = {}
            config['BigPEmuConfig']['Input'][f'Device{pad.player_number - 1}'] = device_section

            device_section['DeviceType'] = 0  # standard controller
            device_section['InvertAnally'] = 0
            device_section['RotaryScale'] = 0.5
            device_section['HeadTrackerScale'] = 8.0
            device_section['HeadTrackerSpring'] = 0
            device_section['Bindings'] = []

            bindings: _Bindings = []
            device_section['Bindings'] = bindings

            # Loop through the bindings sequence to maintain the specific order of bindings
            bindings_sequence = P1_BINDINGS_SEQUENCE if pad.player_number == 1 else P2_BINDINGS_SEQUENCE

            for binding_info in bindings_sequence.values():
                if 'button' in binding_info:
                    if input := pad.inputs.get(binding_info['button']):
                        # workaround values for SDL2
                        if input.type == 'button':
                            input.value = '0'
                        if input.type == 'hat':
                            input.id = '134'
                        if input.name == 'joystick1left':
                            input.id = '128'
                        if input.name == 'joystick1up':
                            input.id = '129'
                        if input.name == 'joystick2left':
                            input.id = '131'
                        if input.name == 'joystick2up':
                            input.id = '132'

                        if input.name.startswith(('joystick1', 'joystick2')):
                            # For joysticks, generate two bindings with positive and then negative values
                            bindings.extend(
                                [
                                    _generate_button_binding(binding_info, pad.guid, input),
                                    _generate_button_binding(
                                        binding_info, pad.guid, input, button_value=-float(input.value)
                                    ),
                                ]
                            )
                        else:
                            bindings.append(_generate_button_binding(binding_info, pad.guid, input))
                    else:
                        # no inputs match the button, generate a blank or keyboard-only binding
                        # to fill the spot in the bindings sequence
                        bindings.append(
                            _generate_keyb_binding(binding_info['keyboard'])
                            if 'keyboard' in binding_info
                            else _generate_blank_binding()
                        )
                        if binding_info['button'].startswith(('joystick1', 'joystick2')):
                            # For joysticks, generate two bindings
                            bindings.append(_generate_blank_binding())
                elif 'buttons' in binding_info:
                    button1_name, button2_name = binding_info['buttons']

                    if (button1 := pad.inputs.get(button1_name)) and (button2 := pad.inputs.get(button2_name)):
                        for button_input in [button1, button2]:
                            # workaround values for SDL2
                            if button_input.type == 'button':
                                button_input.value = '0'
                            if button_input.name == 'l2':
                                button_input.id = '130'
                            if button_input.name == 'r2':
                                button_input.id = '133'

                        bindings.append(_generate_combo_binding(binding_info, pad.guid, button1, button2))
                    else:
                        # no inputs match the buttons, generate a blank or keyboard-only binding
                        # to fill the spot in the bindings sequence
                        bindings.append(
                            _generate_keyb_binding(binding_info['keyboard'])
                            if 'keyboard' in binding_info
                            else _generate_blank_binding()
                        )
                else:
                    if 'keyboard' in binding_info:
                        bindings.append(_generate_keyb_binding(binding_info['keyboard']))
                    else:
                        bindings.append(_generate_blank_binding())

        # Scripts config
        config['BigPEmuConfig']['ScriptsEnabled'] = cast('list[str]', [])

        # User selections for ScriptsEnabled options (individual scripts)
        scripts = [
            ('avp', 'bigpemu_avp'),
            ('avp_mp', 'bigpemu_avp_mp'),
            ('brett_hull_hockey', 'bigpemu_brett_hull_hockey'),
            ('checkered_flag', 'bigpemu_checkered_flag'),
            ('cybermorph', 'bigpemu_cybermorph'),
            ('doom', 'bigpemu_doom'),
            ('iron_soldier', 'bigpemu_iron_soldier'),
            ('mc3d_vr', 'bigpemu_mc3d_vr'),
            ('t2k_rotary', 'bigpemu_t2k_rotary'),
            ('wolf3d', 'bigpemu_wolf3d'),
        ]

        config['BigPEmuConfig']['ScriptsEnabled'] += [
            script_name for script_name, script_option in scripts if self.config.get(script_option) == '1'
        ]

        # Remove duplicates just in case (as a precaution)
        config['BigPEmuConfig']['ScriptsEnabled'] = list(set(config['BigPEmuConfig']['ScriptsEnabled']))

        # ScriptSettings
        config['BigPEmuConfig']['ScriptSettings'] = {}

        config['BigPEmuConfig']['ScriptSettings']['DOOM-Music'] = self.config.get('bigpemu_doom', 0)

        # Screen filter
        config['BigPEmuConfig']['Video']['ScreenFilter'] = self.config.get('bigpemu_screenfilter', 0)

        # Close off input
        config['BigPEmuConfig']['Input']['InputVer'] = 2
        config['BigPEmuConfig']['Input']['InputPluginVer'] = 666

        config['BigPEmuConfig'].update(preserved)

        bigpemu_config.write_text(json.dumps(config, indent=4))

        return Command(
            ['/usr/bigpemu/bigpemu', self.rom, '-cfgpathabs', bigpemu_config],
            env={'SDL_JOYSTICK_HIDAPI': '0'},
        )

    @cached_property
    def in_game_ratio(self) -> float:
        if self.config.get('bigpemu_ratio') == '8':
            return 16 / 9
        return 4 / 3
