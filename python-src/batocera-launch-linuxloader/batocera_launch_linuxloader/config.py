from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final, TypedDict

from batocera_launch import InvalidConfiguration

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

_logger = logging.getLogger(__name__)

_CONF_KEYS: Final = {
    'WIDTH',
    'HEIGHT',
    'FULLSCREEN',
    'INPUT_MODE',
    'NO_SDL',
    'REGION',
    'FREEPLAY',
    'EMULATE_JVS',
    'EMULATE_RIDEBOARD',
    'EMULATE_DRIVEBOARD',
    'EMULATE_MOTIONBOARD',
    'JVS_PATH',
    'SERIAL_1_PATH',
    'SERIAL_2_PATH',
    'SRAM_PATH',
    'EEPROM_PATH',
    'LIBCG_PATH',
    'GPU_VENDOR',
    'DEBUG_MSGS',
    'BORDER_ENABLED',
    'WHITE_BORDER_PERCENTAGE',
    'BLACK_BORDER_PERCENTAGE',
    'HUMMER_FLICKER_FIX',
    'KEEP_ASPECT_RATIO',
    'OUTRUN_LENS_GLARE_ENABLED',
    'SKIP_OUTRUN_CABINET_CHECK',
    'FPS_LIMITER_ENABLED',
    'FPS_TARGET',
    'FPS_OVERLAY_ENABLED',
    'FPS_OVERLAY_POSITION',
    'LGJ_RENDER_WITH_MESA',
    'PRIMEVAL_HUNT_SCREEN_MODE',
    'MJ4_ENABLED_ALL_THE_TIME',
    'LINDBERGH_COLOUR',
    'TEST_KEY',
    'PLAYER_1_START_KEY',
    'PLAYER_1_SERVICE_KEY',
    'PLAYER_1_COIN_KEY',
    'PLAYER_1_UP_KEY',
    'PLAYER_1_DOWN_KEY',
    'PLAYER_1_LEFT_KEY',
    'PLAYER_1_RIGHT_KEY',
    'PLAYER_1_BUTTON_1_KEY',
    'PLAYER_1_BUTTON_2_KEY',
    'PLAYER_1_BUTTON_3_KEY',
    'PLAYER_1_BUTTON_4_KEY',
    'TEST_BUTTON',
    'PLAYER_1_BUTTON_START',
    'PLAYER_1_BUTTON_SERVICE',
    'PLAYER_1_BUTTON_UP',
    'PLAYER_1_BUTTON_DOWN',
    'PLAYER_1_BUTTON_LEFT',
    'PLAYER_1_BUTTON_RIGHT',
    'PLAYER_1_BUTTON_1',
    'PLAYER_1_BUTTON_2',
    'PLAYER_1_BUTTON_3',
    'PLAYER_1_BUTTON_4',
    'PLAYER_1_BUTTON_5',
    'PLAYER_1_BUTTON_6',
    'PLAYER_1_BUTTON_7',
    'PLAYER_1_BUTTON_8',
    'PLAYER_2_BUTTON_START',
    'PLAYER_2_BUTTON_SERVICE',
    'PLAYER_2_BUTTON_UP',
    'PLAYER_2_BUTTON_DOWN',
    'PLAYER_2_BUTTON_LEFT',
    'PLAYER_2_BUTTON_RIGHT',
    'PLAYER_2_BUTTON_1',
    'PLAYER_2_BUTTON_2',
    'PLAYER_2_BUTTON_3',
    'PLAYER_2_BUTTON_4',
    'PLAYER_2_BUTTON_5',
    'PLAYER_2_BUTTON_6',
    'PLAYER_2_BUTTON_7',
    'PLAYER_2_BUTTON_8',
    'ANALOGUE_1',
    'ANALOGUE_2',
    'ANALOGUE_3',
    'ANALOGUE_4',
    'ANALOGUE_5',
    'ANALOGUE_6',
    'ANALOGUE_7',
    'ANALOGUE_8',
    'ANALOGUE_1+',
    'ANALOGUE_2+',
    'ANALOGUE_3+',
    'ANALOGUE_4+',
    'ANALOGUE_1-',
    'ANALOGUE_2-',
    'ANALOGUE_3-',
    'ANALOGUE_4-',
    'ANALOGUE_DEADZONE_1',
    'ANALOGUE_DEADZONE_2',
    'ANALOGUE_DEADZONE_3',
    'ANALOGUE_DEADZONE_4',
    'ANALOGUE_DEADZONE_5',
    'ANALOGUE_DEADZONE_6',
    'ANALOGUE_DEADZONE_7',
    'ANALOGUE_DEADZONE_8',
    'EMULATE_HW210_CARDREADER',
    'CARDFILE_01',
    'CARDFILE_02',
    'CPU_FREQ_GHZ',
    'OR2_IPADDRESS',
    'PLAYER_1_COIN',
    'BOOST_RENDER_RES',
    'HIDE_CURSOR',
    'EMULATE_ID_CARD_READER',
    'EMULATE_TOUCHSCREEN',
    'ID_CARDFILE_AUTOLOAD',
    'ID_CARDFOLDER',
    'DISABLE_BUILTIN_FONT',
    'DISABLE_BUILTIN_LOGOS',
    'CUSTOM_CURSOR_ENABLED',
    'CUSTOM_CURSOR',
    'CUSTOM_CURSOR_WIDTH',
    'CUSTOM_CURSOR_HEIGHT',
    'TOUCH_CURSOR',
    'TOUCH_CURSOR_WIDTH',
    'TOUCH_CURSOR_HEIGHT',
    'PRIMEVAL_HUNT_TEST_SCREEN_SINGLE',
    'RAMBO_GUNS_SWITCH',
    'ID5_CHINESE_LANGUAGE',
    'ID_STEERING_REDUCTION_PERCENTAGE',
    'ENABLE_CROSSHAIRS',
    'P1_CROSSHAIR_PATH',
    'P2_CROSSHAIR_PATH',
    'CUSTOM_CROSSHAIRS_WIDTH',
    'CUSTOM_CROSSHAIRS_HEIGHT',
    'GSEVO_CROSSHAIR_ALWAYS_ON',
    'GSEVO_CROSSHAIR_ALWAYS_OFF',
    'ENABLE_NETWORK_PATCHES',
    'NIC_NAME',
    'OR2_NETMASK',
    'ID_IP_SEAT_1',
    'ID_IP_SEAT_2',
    'IP_CAB1',
    'IP_CAB2',
    'IP_CAB3',
    'IP_CAB4',
    '2SPICY_IP_CAB1',
    '2SPICY_IP_CAB2',
    'SRTV_IPADDRESS',
    'EXIT_GAME',
}

_CONF_LINE_PATTERN: Final = re.compile(r'^\s*(#?)\s*([A-Z0-9_\s]+[A-Z0-9_])\s*=\s*(.*)$')


class _ConfigValue(TypedDict):
    value: str
    commented: bool
    line: int
    modified: bool


@dataclass(slots=True)
class Configuration:
    config_file: Path
    raw: list[str] = field(init=False)
    data: dict[str, _ConfigValue] = field(init=False, default_factory=dict[str, _ConfigValue])

    def __post_init__(self) -> None:
        try:
            with self.config_file.open('r') as file:
                self.raw = file.readlines()
        except FileNotFoundError:
            _logger.debug('Configuration file %s not found.', self.config_file)
            self.raw = []

        # find keys and values
        # analyze lines
        for n, line in enumerate(self.raw):
            matches = _CONF_LINE_PATTERN.match(line)
            if matches:
                key = matches.group(2).strip()

                if key in _CONF_KEYS:
                    if key in self.data:  # take care of duplicated keys
                        # if the 1st one is commented, prefer the last one
                        if self.data[key]['commented']:
                            self.data[key] = {
                                'value': matches.group(3).strip(),
                                'commented': matches.group(1) == '#',
                                'line': n,
                                'modified': False,
                            }
                        else:
                            # if the previous is not commented, prefer the last one if not commented and comment the previous
                            if matches.group(1) != '#':
                                self.raw[self.data[key]['line']] = f'# {self.raw[self.data[key]["line"]]}'
                                self.data[key] = {
                                    'value': matches.group(3).strip(),
                                    'commented': matches.group(1) == '#',
                                    'line': n,
                                    'modified': False,
                                }
                    else:
                        self.data[key] = {
                            'value': matches.group(3).strip(),
                            'commented': matches.group(1) == '#',
                            'line': n,
                            'modified': False,
                        }
                else:
                    _logger.debug('CONF: ignoring key /%s/', key)
            else:
                stripped_line = line.rstrip()
                if stripped_line != '':
                    _logger.debug('CONF: ignoring line %s', stripped_line)

    def keys(self) -> Iterator[str]:
        yield from self.data.keys()

    def __iter__(self) -> Iterator[str]:
        return self.keys()

    def set(self, key: str, value: Any, /) -> None:
        if key not in _CONF_KEYS:
            raise InvalidConfiguration(f'unknown configuration key {key}')

        # new line
        if key not in self.data:
            self.data[key] = {'line': len(self.raw), 'value': '', 'modified': False, 'commented': False}
            self.raw.append('###')

        self.data[key]['value'] = str(value)
        self.data[key]['modified'] = True
        self.data[key]['commented'] = False

    def comment(self, key: str, /) -> None:
        if key not in _CONF_KEYS:
            raise InvalidConfiguration(f'unknown configuration key {key}')

        if key in self.data:
            self.data[key]['modified'] = True
            self.data[key]['commented'] = True

    def save(self) -> None:
        # update with modified lines
        for key in self.data:
            if self.data[key]['modified']:
                nline = self.data[key]['line']
                # Updated for INI format (KEY = VALUE)
                line = f'{key} = {self.data[key]["value"]}\n'
                if self.data[key]['commented']:
                    line = f'# {line}'
                self.raw[nline] = line

        try:
            with self.config_file.open('w') as file:
                file.writelines(self.raw)

            _logger.debug('Configuration file %s updated successfully.', self.config_file)
        except Exception:
            _logger.exception('Error updating configuration file')
