from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from evdev import ecodes

from batocera_common.dataclasses import cached_dataclass
from batocera_launch import BatoceraException, Controller, Emulator, InvalidConfiguration

if TYPE_CHECKING:
    from .config import Configuration

_logger = logging.getLogger(__name__)


@cached_dataclass
class ControllersMixin(Emulator):
    def _setup_controllers(self, conf: Configuration, rom_name: str, /) -> None:
        # 1: SDL, 2: EVDEV
        if self.config.get_str('linuxloader_controller') == '1':
            input_mode = 1
        else:
            input_mode = 2

        short_rom_name = Path(rom_name.lower()).stem

        conf.set('INPUT_MODE', input_mode)

        # comment all player values
        for key in conf:
            if key.startswith(('PLAYER_', 'ANALOGUE_')) or key == 'TEST_BUTTON':
                conf.comment(key)

        # configure guns
        if input_mode == 2 and self.config.use_guns:
            self._setup_guns_evdev(conf, short_rom_name)

        # joysticks
        if input_mode == 2:
            self._setup_joysticks_evdev(conf, short_rom_name)

        # map service and test buttons for tests mode
        if self.config.get_bool('linuxloader_test') and input_mode == 2:
            self._setup_test_mode_evdev(conf)

    def _setup_test_mode_evdev(self, conf: Configuration, /) -> None:
        for pad in self.controllers[:1]:
            input_name = 'b'
            if input_name in pad.inputs and pad.inputs[input_name].type == 'button':
                conf.set('TEST_BUTTON', f'{pad.device_path}:KEY:{pad.inputs[input_name].code}')
            input_name = 'down'
            if input_name in pad.inputs and pad.inputs[input_name].type == 'hat':  # noqa: SIM102
                if pad.inputs[input_name].value == '4':  # down
                    # 16 is the HAT0 code, MAX for down/right
                    input_value = f'ABS:{16 + 1 + int(pad.inputs[input_name].id) * 2}:MAX'
                    conf.set('PLAYER_1_BUTTON_SERVICE', f'{pad.device_path}:{input_value}')
            if input_name in pad.inputs and pad.inputs[input_name].type == 'axis':
                relax_values = pad.get_mapping_axis_relaxed_values()
                if input_name in relax_values and relax_values[input_name]['reversed']:
                    input_value = f'ABS_NEG:{pad.inputs[input_name].code}'
                else:
                    input_value = f'ABS:{pad.inputs[input_name].code}'
                conf.set('PLAYER_1_BUTTON_SERVICE', f'{pad.device_path}:{input_value}:MAX')

    def _setup_joysticks_evdev(self, conf: Configuration, short_rom_name: str, /) -> None:
        # button that are common to all players
        no_player_button = {
            'TEST_BUTTON': True,
            'ANALOGUE_1': True,
            'ANALOGUE_2': True,
            'ANALOGUE_3': True,
            'ANALOGUE_4': True,
            'ANALOGUE_5': True,
            'ANALOGUE_6': True,
            'ANALOGUE_7': True,
            'ANALOGUE_8': True,
        }

        # configure joysticks if no gun configured for the user
        nplayer = 1
        continue_players = True
        for pad in self.controllers:
            # Handle two players / controllers only, don't do if already configured for guns
            if nplayer <= 2 and continue_players and not (self.config.use_guns and len(self.guns) >= nplayer):
                relax_values = pad.get_mapping_axis_relaxed_values()

                ### choose the adapted mapping
                if self.config.use_wheels:
                    if pad.device_path in self.wheels:
                        linuxloader_ctrl = self._get_mapping_for_joystick_or_wheel(
                            short_rom_name, 'wheel', nplayer, pad, True
                        )
                        _logger.debug('linuxloader wheel mapping for player %s', nplayer)
                    else:
                        linuxloader_ctrl = self._get_mapping_for_joystick_or_wheel(
                            short_rom_name, 'pad', nplayer, pad, False
                        )
                        _logger.debug('linuxloader pad mapping for player %s (not a wheel device)', nplayer)
                elif self.config.use_guns:
                    linuxloader_ctrl = self._get_mapping_for_joystick_or_wheel(
                        short_rom_name, 'gun', nplayer, pad, False
                    )
                    _logger.debug('linuxloader gun mapping for player %s', nplayer)
                else:
                    linuxloader_ctrl = self._get_mapping_for_joystick_or_wheel(
                        short_rom_name, 'pad', nplayer, pad, False
                    )
                    _logger.debug('linuxloader pad mapping for player %s', nplayer)

                # some games must be configured for player 1 only (cause it uses some buttons of the player 2), so stop after player 1
                if nplayer == 1:
                    for input_name in linuxloader_ctrl:
                        if linuxloader_ctrl[input_name].endswith('_ON_PLAYER_2'):
                            continue_players = False

                # checker on buttons mapping (just to control we have no duplicates)
                x: dict[str, bool] = {}
                for input_name in linuxloader_ctrl:
                    if linuxloader_ctrl[input_name] in x:
                        raise InvalidConfiguration(
                            f'duplicate configuration key for {input_name} with value {linuxloader_ctrl[input_name]}'
                        )
                    x[linuxloader_ctrl[input_name]] = True

                ### configure each input
                controller_name = pad.device_path
                for input_name in linuxloader_ctrl:
                    # coin is only for player 1
                    if linuxloader_ctrl[input_name] == 'COIN' and nplayer > 1:
                        continue

                    input_base_name = input_name
                    if input_name == 'joystick1right':
                        input_base_name = 'joystick1left'
                    if input_name == 'joystick1down':
                        input_base_name = 'joystick1up'
                    if input_name == 'joystick2right':
                        input_base_name = 'joystick2left'
                    if input_name == 'joystick2down':
                        input_base_name = 'joystick2up'

                    if input_base_name in pad.inputs and (
                        pad.inputs[input_base_name].code is not None or pad.inputs[input_base_name].type == 'hat'
                    ):
                        button_name = linuxloader_ctrl[input_name]

                        # some buttons of player1 are mapped on the player2...
                        player_input = nplayer
                        if button_name.endswith('_ON_PLAYER_2'):
                            button_name = button_name[:-12]
                            player_input = 2
                        ###

                        if pad.inputs[input_base_name].type == 'button':
                            input_value = f'KEY:{pad.inputs[input_base_name].code}'
                            if button_name in no_player_button:
                                if nplayer == 1:
                                    conf.set(f'{button_name}', f'{controller_name}:{input_value}')
                            else:
                                if button_name.startswith('ANALOGUE_'):
                                    if nplayer == 1:
                                        conf.set(f'{button_name}', f'{controller_name}:{input_value}')
                                else:
                                    conf.set(
                                        f'PLAYER_{player_input}_{button_name}',
                                        f'{controller_name}:{input_value}',
                                    )
                        elif pad.inputs[input_base_name].type == 'axis':
                            if input_name in relax_values and relax_values[input_name]['reversed']:
                                input_value = f'ABS_NEG:{pad.inputs[input_base_name].code}'
                            else:
                                input_value = f'ABS:{pad.inputs[input_base_name].code}'
                            if button_name.startswith('ANALOGUE_'):
                                if nplayer == 1:
                                    conf.set(f'{button_name}', f'{controller_name}:{input_value}')
                            else:
                                # here
                                minmax_value = 'MAX'
                                if input_name in (
                                    'joystick1left',
                                    'joystick1up',
                                    'joystick2left',
                                    'joystick2up',
                                    'left',
                                    'up',
                                ):
                                    minmax_value = 'MIN'
                                # reversed axis
                                if input_name in relax_values and relax_values[input_name]['reversed']:
                                    if minmax_value == 'MAX':
                                        minmax_value = 'MIN'
                                    else:
                                        minmax_value = 'MAX'
                                # set
                                conf.set(
                                    f'PLAYER_{player_input}_{button_name}',
                                    f'{controller_name}:{input_value}:{minmax_value}',
                                )
                        elif pad.inputs[input_base_name].type == 'hat':
                            if pad.inputs[input_base_name].value in ('1', '4'):  # up or down
                                # 16 is the HAT0 code
                                input_value = f'ABS:{16 + 1 + int(pad.inputs[input_base_name].id) * 2}'
                            else:
                                input_value = f'ABS:{16 + int(pad.inputs[input_base_name].id) * 2}'
                            if button_name.startswith('ANALOGUE_'):
                                if nplayer == 1:
                                    conf.set(f'{button_name}', f'{controller_name}:{input_value}')
                            else:
                                if pad.inputs[input_base_name].value in ('1', '8'):  # up or left
                                    input_value += ':MIN'
                                else:
                                    input_value += ':MAX'
                                conf.set(
                                    f'PLAYER_{player_input}_{button_name}',
                                    f'{controller_name}:{input_value}',
                                )
                        else:
                            raise BatoceraException(f'invalid input type: {pad.inputs[input_base_name].type}')
                nplayer += 1

    def _get_mapping_for_joystick_or_wheel(
        self,
        short_rom_name: str,
        device_type: Literal['wheel', 'gun', 'pad'],
        nplayer: int,
        pad: Controller,
        is_real_wheel: bool,
        /,
    ) -> dict[str, str]:
        linuxloader_ctrl_pad = {
            'a': 'BUTTON_2',
            'b': 'BUTTON_1',
            'x': 'BUTTON_4',
            'y': 'BUTTON_3',
            'start': 'BUTTON_START',
            'select': 'COIN',
            'up': 'BUTTON_UP',
            'down': 'BUTTON_DOWN',
            'left': 'BUTTON_LEFT',
            'right': 'BUTTON_RIGHT',
            'joystick1up': 'ANALOGUE_2',
            'joystick1left': 'ANALOGUE_1',
            'pageup': 'BUTTON_5',
            'pagedown': 'BUTTON_6',
            'l2': 'BUTTON_7',
            'r2': 'BUTTON_8',
            'l3': 'BUTTON_SERVICE',
        }

        linuxloader_ctrl_pad_driving = {
            'x': 'BUTTON_DOWN',  # view change
            'pageup': 'BUTTON_DOWN_ON_PLAYER_2',  # gear down
            'pagedown': 'BUTTON_UP_ON_PLAYER_2',  # gear up
            'l2': 'ANALOGUE_3',  # brake
            'r2': 'ANALOGUE_2',  # gas
        }

        linuxloader_ctrl_pad_abc = {
            'a': 'BUTTON_1',  # gun trigger
            'b': 'BUTTON_2',  # missile
            'x': 'BUTTON_3',  # climax switch
            'r2': 'ANALOGUE_3',  # throttle
        }

        # the same mapping for a wheel or a pad for a wheel game should do the job
        linuxloader_ctrl_wheel = {
            'a': 'BUTTON_2',
            'b': 'BUTTON_1',
            'x': 'BUTTON_4',
            'y': 'BUTTON_3',
            'start': 'BUTTON_START',
            'select': 'COIN',
            'left': 'BUTTON_LEFT',
            'right': 'BUTTON_RIGHT',
            'joystick1left': 'ANALOGUE_1',
            'pageup': 'BUTTON_DOWN',  # gear down
            'pagedown': 'BUTTON_UP',  # gear up
            'l2': 'ANALOGUE_3',
            'r2': 'ANALOGUE_2',
            'l3': 'BUTTON_SERVICE',
        }

        linuxloader_ctrl_gun = {
            'a': 'BUTTON_2',
            'b': 'BUTTON_1',
            'x': 'BUTTON_4',
            'y': 'BUTTON_3',
            'start': 'BUTTON_START',
            'select': 'COIN',
            'up': 'BUTTON_UP',
            'down': 'BUTTON_DOWN',
            'left': 'BUTTON_LEFT',
            'right': 'BUTTON_RIGHT',
            'joystick1up': 'ANALOGUE_2',
            'joystick1left': 'ANALOGUE_1',
            'pageup': 'BUTTON_5',
            'pagedown': 'BUTTON_6',
            'l2': 'BUTTON_7',
            'r2': 'BUTTON_8',
            'l3': 'BUTTON_SERVICE',
        }

        # mapping specific to games - wheel
        _logger.debug('linuxloader mapping for game %s', short_rom_name)

        if short_rom_name == 'hdkotr' or 'harley' in short_rom_name:
            linuxloader_ctrl_wheel['x'] = 'BUTTON_2'  # change view
            linuxloader_ctrl_wheel['l2'] = 'ANALOGUE_4'
            linuxloader_ctrl_wheel['r2'] = 'ANALOGUE_1'
            linuxloader_ctrl_wheel['joystick1left'] = 'ANALOGUE_2'
            del linuxloader_ctrl_wheel['a']
            del linuxloader_ctrl_wheel['y']
            linuxloader_ctrl_wheel['pageup'] = 'BUTTON_4'
            linuxloader_ctrl_wheel['pagedown'] = 'BUTTON_3'

        if short_rom_name == 'rtuned':
            linuxloader_ctrl_wheel['x'] = 'BUTTON_DOWN'  # change view
            linuxloader_ctrl_wheel['a'] = 'BUTTON_RIGHT'  # boost 1
            linuxloader_ctrl_wheel['y'] = 'BUTTON_1_ON_PLAYER_2'  # boost 2
            del linuxloader_ctrl_wheel['right']

        if short_rom_name.startswith('initiad'):
            linuxloader_ctrl_wheel['x'] = 'BUTTON_1'  # change view
            linuxloader_ctrl_wheel['up'] = 'BUTTON_UP'  # menu up
            linuxloader_ctrl_wheel['down'] = 'BUTTON_DOWN'  # menu down
            del linuxloader_ctrl_wheel['b']

        if short_rom_name.startswith('hummer'):
            linuxloader_ctrl_wheel['a'] = 'BUTTON_DOWN_ON_PLAYER_2'  # boost
            linuxloader_ctrl_wheel['x'] = 'BUTTON_DOWN'  # change view
            del linuxloader_ctrl_wheel['pageup']

        if short_rom_name.startswith('segartv'):
            linuxloader_ctrl_wheel['a'] = 'BUTTON_1_ON_PLAYER_2'  # boost
            linuxloader_ctrl_wheel['x'] = 'BUTTON_DOWN'  # change view
            del linuxloader_ctrl_wheel['pageup']

        if short_rom_name.startswith('outr'):
            linuxloader_ctrl_wheel['x'] = 'BUTTON_DOWN'  # view change

        # button up/down on player 2
        if short_rom_name == 'rtuned' or short_rom_name.startswith(('segartv', 'outr', 'initiad')):
            linuxloader_ctrl_wheel['pageup'] = 'BUTTON_DOWN_ON_PLAYER_2'
            linuxloader_ctrl_wheel['pagedown'] = 'BUTTON_UP_ON_PLAYER_2'

        # mapping specific to games - pad with dict for driving + ABC

        if short_rom_name.startswith('outr'):
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_driving)
            del linuxloader_ctrl_pad['joystick1up']
            del linuxloader_ctrl_pad['down']

        if short_rom_name.startswith('hummer'):
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_driving)
            linuxloader_ctrl_pad['a'] = 'BUTTON_DOWN_ON_PLAYER_2'  # boost
            linuxloader_ctrl_pad['pageup'] = 'BUTTON_5'
            linuxloader_ctrl_pad['pagedown'] = 'BUTTON_6'
            del linuxloader_ctrl_pad['joystick1up']
            del linuxloader_ctrl_pad['down']

        if short_rom_name.startswith('initiad'):
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_driving)
            linuxloader_ctrl_pad['x'] = 'BUTTON_1'  # view change (not BUTTON_DOWN)
            del linuxloader_ctrl_pad['joystick1up']
            del linuxloader_ctrl_pad['b']

        if short_rom_name == 'rtuned':
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_driving)
            linuxloader_ctrl_pad['a'] = 'BUTTON_RIGHT'  # boost
            linuxloader_ctrl_pad['y'] = 'BUTTON_1_ON_PLAYER_2'  # boost 2
            del linuxloader_ctrl_pad['joystick1up']
            del linuxloader_ctrl_pad['right']
            del linuxloader_ctrl_pad['down']

        if short_rom_name.startswith('segartv'):
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_driving)
            linuxloader_ctrl_pad['a'] = 'BUTTON_1_ON_PLAYER_2'  # boost
            del linuxloader_ctrl_pad['joystick1up']
            del linuxloader_ctrl_pad['down']

        if short_rom_name == 'hdkotr' or 'harley' in short_rom_name:
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_driving)
            linuxloader_ctrl_pad['joystick1left'] = 'ANALOGUE_2'  # steer (swapped)
            linuxloader_ctrl_pad['r2'] = 'ANALOGUE_1'  # gas (swapped)
            linuxloader_ctrl_pad['l2'] = 'ANALOGUE_4'  # brake (swapped)
            linuxloader_ctrl_pad['x'] = 'BUTTON_2'  # view change
            linuxloader_ctrl_pad['pageup'] = 'BUTTON_4'  # gear down
            linuxloader_ctrl_pad['pagedown'] = 'BUTTON_3'  # gear up
            del linuxloader_ctrl_pad['joystick1up']
            del linuxloader_ctrl_pad['a']
            del linuxloader_ctrl_pad['y']

        if short_rom_name.startswith('abcli'):
            linuxloader_ctrl_pad.update(linuxloader_ctrl_pad_abc)
            del linuxloader_ctrl_pad['l2']
            del linuxloader_ctrl_pad['y']
        ###

        # remap buttons if for non real wheel
        if device_type == 'wheel' and not is_real_wheel:
            x = None
            y = None
            l = None  # noqa: E741
            r = None
            if 'x' in linuxloader_ctrl_wheel:
                x = linuxloader_ctrl_wheel['x']
                del linuxloader_ctrl_wheel['x']
            if 'y' in linuxloader_ctrl_wheel:
                y = linuxloader_ctrl_wheel['y']
                del linuxloader_ctrl_wheel['y']
            if 'pageup' in linuxloader_ctrl_wheel:
                l = linuxloader_ctrl_wheel['pageup']  # noqa: E741
                del linuxloader_ctrl_wheel['pageup']
            if 'pagedown' in linuxloader_ctrl_wheel:
                r = linuxloader_ctrl_wheel['pagedown']
                del linuxloader_ctrl_wheel['pagedown']
            if x is not None:
                linuxloader_ctrl_wheel['pageup'] = x  # view     ## free x and y for gear up/down
            if y is not None:
                linuxloader_ctrl_wheel['b'] = y  # action 2 ## free x and y for gear up/down
            if r is not None:
                linuxloader_ctrl_wheel['x'] = r
            if l is not None:
                linuxloader_ctrl_wheel['y'] = l
        ####

        # pads without l2, but with l as a button, important for wheel
        if 'l2' not in pad.inputs and 'pageup' in pad.inputs and pad.inputs['pageup'].type == 'button':
            linuxloader_ctrl_wheel['pageup'] = linuxloader_ctrl_wheel['l2']
            del linuxloader_ctrl_wheel['l2']
        # pads without r2, but with r as a button
        if 'r2' not in pad.inputs and 'pagedown' in pad.inputs and pad.inputs['pagedown'].type == 'button':
            linuxloader_ctrl_wheel['pagedown'] = linuxloader_ctrl_wheel['r2']
            del linuxloader_ctrl_wheel['r2']

        # some pads have not analog axis, on some games, prefer the dpad
        if not short_rom_name.startswith('vf5') and not short_rom_name.startswith('vt'):  # all but vf5 and vt3
            # pads without joystick1left, but with a hat
            if (
                'joystick1left' not in pad.inputs
                and 'left' in pad.inputs
                and (pad.inputs['left'].type == 'hat' or pad.inputs['left'].type == 'axis')
            ):
                if 'joystick1left' in linuxloader_ctrl_wheel:
                    linuxloader_ctrl_wheel['left'] = linuxloader_ctrl_wheel['joystick1left']
                    if 'right' in linuxloader_ctrl_wheel:
                        del linuxloader_ctrl_wheel['right']
                    del linuxloader_ctrl_wheel['joystick1left']
                if 'joystick1left' in linuxloader_ctrl_pad:
                    linuxloader_ctrl_pad['left'] = linuxloader_ctrl_pad['joystick1left']
                    if 'right' in linuxloader_ctrl_pad:
                        del linuxloader_ctrl_pad['right']
                    del linuxloader_ctrl_pad['joystick1left']

            # pads without joystick1up, but with a hat
            if (
                'joystick1up' not in pad.inputs
                and 'up' in pad.inputs
                and (pad.inputs['up'].type == 'hat' or pad.inputs['up'].type == 'axis')
            ) and 'joystick1up' in linuxloader_ctrl_pad:
                linuxloader_ctrl_pad['up'] = linuxloader_ctrl_pad['joystick1up']
                if 'down' in linuxloader_ctrl_pad:
                    del linuxloader_ctrl_pad['down']
                del linuxloader_ctrl_pad['joystick1up']
        ###

        # choose mapping
        if device_type == 'gun':
            # adjustment for player 2 gun
            for x in linuxloader_ctrl_gun:
                if linuxloader_ctrl_gun[x] == 'ANALOGUE_1' and nplayer == 2:
                    linuxloader_ctrl_gun[x] = 'ANALOGUE_3'
                if linuxloader_ctrl_gun[x] == 'ANALOGUE_2' and nplayer == 2:
                    linuxloader_ctrl_gun[x] = 'ANALOGUE_4'
            return linuxloader_ctrl_gun

        if device_type == 'wheel':
            return linuxloader_ctrl_wheel

        return linuxloader_ctrl_pad

    def _setup_guns_evdev(self, conf: Configuration, short_rom_name: str, /) -> None:
        # common batocera mapping
        mappings_codes = {
            'left': ecodes.BTN_LEFT,
            'right': ecodes.BTN_RIGHT,
            'middle': ecodes.BTN_MIDDLE,
            '1': ecodes.BTN_1,
            '2': ecodes.BTN_2,
            '3': ecodes.BTN_3,
            '4': ecodes.BTN_4,
            '5': ecodes.BTN_5,
            '6': ecodes.BTN_6,
            '7': ecodes.BTN_7,
            '8': ecodes.BTN_8,
        }

        # linuxloader gun mapping
        mappings_actions = {
            'left': 'BUTTON_1',  # trigger = BUTTON_1
            'middle': 'BUTTON_START',
            '1': 'COIN',
            'right': 'BUTTON_3',  # action = BUTTON_3
            '2': 'BUTTON_2',  # optional reload in most case = BUTTON_2
            '3': 'BUTTON_4',
            '4': 'BUTTON_5',
            '5': 'BUTTON_UP',
            '6': 'BUTTON_DOWN',
            '7': 'BUTTON_LEFT',
            '8': 'BUTTON_RIGHT',
        }

        if short_rom_name == '2spicy':
            mappings_actions['right'] = 'BUTTON_2'
            del mappings_actions['2']

        if short_rom_name == 'ghostsev':
            mappings_actions['right'] = 'BUTTON_3'  # Action
            mappings_actions['2'] = 'BUTTON_4'  # Cycle firerate
            del mappings_actions['3']

        if short_rom_name == 'hotdex':
            mappings_actions['right'] = 'BUTTON_LEFT'
            del mappings_actions['7']
            del mappings_actions['8']

        if short_rom_name == 'hotd4sp':
            mappings_actions['2'] = 'BUTTON_4'
            del mappings_actions['3']

        if short_rom_name == 'letsgojusp':
            # if there is only one gun, let the player1 able to press BUTTON_4 of player 2 (required)
            if len(self.guns) == 1:
                mappings_actions['7'] = 'BUTTON_4'
                del mappings_actions['3']
                mapping = '8'
                action = 'BUTTON_4'
                if mapping in mappings_codes:
                    gun = self.guns[0]
                    code = mappings_codes[mapping]
                    conf.set(f'PLAYER_2_{action}', f'{gun.node}:KEY:{code}')
                    del mappings_actions[mapping]
            elif len(self.guns) > 1:
                mappings_actions['right'] = 'BUTTON_4'
                del mappings_actions['3']

        if short_rom_name == 'letsgoju' and len(self.guns) == 1:
            mapping = 'right'
            action = 'BUTTON_START'
            if mapping in mappings_codes:
                gun = self.guns[0]
                code = mappings_codes[mapping]
                conf.set(f'PLAYER_2_{action}', f'{gun.node}:KEY:{code}')
                del mappings_actions[mapping]

        for nplayer, gun in enumerate(self.guns[:2], start=1):
            _logger.debug('linuxloader gun for player %s', nplayer)
            xplayer = 1 + (nplayer - 1) * 2
            yplayer = 1 + (nplayer - 1) * 2 + 1
            evplayer = gun.node
            conf.set(f'ANALOGUE_{xplayer}', f'{evplayer}:ABS:0')
            conf.set(f'ANALOGUE_{yplayer}', f'{evplayer}:ABS:1')

            # reverse axis for let's go jungle
            if short_rom_name in ('letsgoju', 'letsgojua'):  # not for the special version
                conf.set(f'ANALOGUE_{xplayer}', f'{evplayer}:ABS_NEG:1')
                conf.set(f'ANALOGUE_{yplayer}', f'{evplayer}:ABS_NEG:0')

            # add shake for hotd4
            if short_rom_name.startswith('hotd4'):
                xplayerp4 = xplayer + 4
                yplayerp4 = yplayer + 4
                conf.set(f'ANALOGUE_{xplayerp4}', f'{evplayer}:ABS:0:SHAKE')
                conf.set(f'ANALOGUE_{yplayerp4}', f'{evplayer}:ABS:1:SHAKE')

            for mapping in mappings_actions:
                if mapping in gun.buttons and mapping in mappings_codes:
                    code = mappings_codes[mapping]
                    action = mappings_actions[mapping]
                    player = nplayer

                    # in hotdex, player2 reload is on button right (and button left for player 1...)
                    if short_rom_name == 'hotdex' and nplayer == 2 and mapping == 'right':
                        action = 'BUTTON_RIGHT'
                        player = 1

                    if not (action == 'COIN' and player != 1):  # COIN is only for player 1
                        conf.set(f'PLAYER_{player}_{action}', f'{evplayer}:KEY:{code}')
