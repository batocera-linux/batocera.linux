from __future__ import annotations

import ast
import logging
import re
from typing import TYPE_CHECKING

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_launch import BatoceraException

from .paths import DOLPHIN_CONFIG

if TYPE_CHECKING:
    from _typeshed import SupportsWrite
    from collections.abc import Mapping
    from pathlib import Path

    from batocera_launch import Controller, Controllers, Emulator, Guns
    from batocera_launch.devices.device import DeviceInfoMapping

_logger = logging.getLogger(__name__)


def generate_controller_config(
    emulator: Emulator,
    players_controllers: Controllers,
    metadata: Mapping[str, str],
    wheels: DeviceInfoMapping,
    rom: Path,
    guns: Guns,
    /,
) -> None:
    if emulator.system == 'wii':
        if emulator.config.use_guns and guns:
            generate_controller_config_guns('WiimoteNew.ini', 'Wiimote', metadata, guns)
            # You can use the gamecube pads on the wii together with wiimotes
            generate_controller_config_gamecube(emulator, players_controllers, {}, rom)
        elif not emulator.config.get_bool('emulatedwiimotes', True):
            generate_controller_config_realwiimotes('WiimoteNew.ini', 'Wiimote')
            generate_controller_config_gamecube(emulator, players_controllers, {}, rom)
        elif emulator.config.get_bool('emulatedwiimotes'):
            generate_controller_config_emulatedwiimotes(emulator, players_controllers, {}, rom)
            remove_controller_config_gamecube()  # Because pads will already be used as emulated wiimotes
        elif (
            any(
                infix in rom.name
                for infix in (
                    '.cc.',
                    '.pro.',
                    '.side.',
                    '.is.',
                    '.it.',
                    '.in.',
                    '.ti.',
                    '.ts.',
                    '.tn.',
                    '.ni.',
                    '.ns.',
                    '.nt.',
                )
            )
            or 'sideWiimote' in emulator.config
        ):
            generate_controller_config_emulatedwiimotes(emulator, players_controllers, {}, rom)
            remove_controller_config_gamecube()
        else:
            generate_controller_config_realwiimotes('WiimoteNew.ini', 'Wiimote')
            generate_controller_config_gamecube(emulator, players_controllers, {}, rom)
    elif emulator.system == 'gamecube':
        used_wheels: DeviceInfoMapping = {}
        if (
            emulator.config.use_wheels
            and wheels
            and (
                metadata.get('wheel_type') == 'Steering Wheel'
                or emulator.config.get('dolphin_wheel_type') == 'Steering Wheel'
            )
        ):
            used_wheels = wheels
        # Pass ROM name to allow for per ROM configuration
        generate_controller_config_gamecube(emulator, players_controllers, used_wheels, rom)
    elif emulator.system == 'triforce':
        used_wheels = wheels if emulator.config.use_wheels and wheels else {}
        generate_controller_config_triforce(emulator, players_controllers, used_wheels, rom)
    else:
        raise BatoceraException(f"Invalid system name: '{emulator.system}'")


# https://docs.libretro.com/library/dolphin/


def _read_per_rom_overrides(rom: Path, mapping: dict[str, str | None]) -> None:
    # This section allows a per ROM override of the default key options.
    config_name = rom.with_name(f'{rom.name}.cfg')
    if not config_name.is_file():
        return

    with config_name.open() as cconfig:
        line = cconfig.readline()
        while line:
            mapping.update(ast.literal_eval(f'{{{line}}}'))
            line = cconfig.readline()


def generate_controller_config_emulatedwiimotes(
    emulator: Emulator, players_controllers: Controllers, wheels: DeviceInfoMapping, rom: Path, /
) -> None:
    wii_mapping: dict[str, str | None] = {
        'x': 'Buttons/2',
        'b': 'Buttons/A',
        'y': 'Buttons/1',
        'a': 'Buttons/B',
        'pageup': 'Buttons/-',
        'pagedown': 'Buttons/+',
        'select': 'Buttons/Home',
        'up': 'D-Pad/Up',
        'down': 'D-Pad/Down',
        'left': 'D-Pad/Left',
        'right': 'D-Pad/Right',
        'joystick1up': 'IR/Up',
        'joystick1left': 'IR/Left',
        'joystick2up': 'Tilt/Forward',
        'joystick2left': 'Tilt/Left',
        'hotkey': 'Buttons/Hotkey',
    }
    wii_reverse_axes: dict[str | None, str] = {
        'IR/Up': 'IR/Down',
        'IR/Left': 'IR/Right',
        'Swing/Up': 'Swing/Down',
        'Swing/Left': 'Swing/Right',
        'Tilt/Left': 'Tilt/Right',
        'Tilt/Forward': 'Tilt/Backward',
        'Nunchuk/Stick/Up': 'Nunchuk/Stick/Down',
        'Nunchuk/Stick/Left': 'Nunchuk/Stick/Right',
        'Classic/Right Stick/Up': 'Classic/Right Stick/Down',
        'Classic/Right Stick/Left': 'Classic/Right Stick/Right',
        'Classic/Left Stick/Up': 'Classic/Left Stick/Down',
        'Classic/Left Stick/Left': 'Classic/Left Stick/Right',
    }

    extra_options: dict[str, str] = {'Source': '1'}
    controller_mode = emulator.config.get('controller_mode')

    # Side wiimote. l2 for shaking actions
    if ('.side.' in rom.name) or (controller_mode is not None and controller_mode not in ('disabled', 'cc')):
        extra_options['Options/Sideways Wiimote'] = '1'
        wii_mapping['x'] = 'Buttons/B'
        wii_mapping['y'] = 'Buttons/A'
        wii_mapping['a'] = 'Buttons/2'
        wii_mapping['b'] = 'Buttons/1'
        wii_mapping['l2'] = 'Shake/Z'  # last of three sequential overwrites in the original code

    # i: infrared, s: swing, t: tilt, n: nunchuk
    # 12 possible combinations : is si / it ti / in ni / st ts / sn ns / tn nt

    # i
    if ('.is.' in rom.name or '.it.' in rom.name or '.in.' in rom.name) or (
        controller_mode is not None and controller_mode not in ('disabled', 'in', 'cc')
    ):
        wii_mapping['joystick1up'] = 'IR/Up'
        wii_mapping['joystick1left'] = 'IR/Left'
    if ('.si.' in rom.name or '.ti.' in rom.name or '.ni.' in rom.name) or (controller_mode == 'in'):
        wii_mapping['joystick2up'] = 'IR/Up'
        wii_mapping['joystick2left'] = 'IR/Left'

    # s
    if '.si.' in rom.name or '.st.' in rom.name or '.sn.' in rom.name:
        wii_mapping['joystick1up'] = 'Swing/Up'
        wii_mapping['joystick1left'] = 'Swing/Left'
    if ('.is.' in rom.name or '.ts.' in rom.name or '.ns.' in rom.name) or (controller_mode == 'is'):
        wii_mapping['joystick2up'] = 'Swing/Up'
        wii_mapping['joystick2left'] = 'Swing/Left'

    # t
    if '.ti.' in rom.name or '.ts.' in rom.name or '.tn.' in rom.name:
        wii_mapping['joystick1up'] = 'Tilt/Forward'
        wii_mapping['joystick1left'] = 'Tilt/Left'
    if ('.it.' in rom.name or '.st.' in rom.name or '.nt.' in rom.name) or (controller_mode == 'it'):
        wii_mapping['joystick2up'] = 'Tilt/Forward'
        wii_mapping['joystick2left'] = 'Tilt/Left'

    # n
    if (
        ('.ni.' in rom.name or '.ns.' in rom.name or '.nt.' in rom.name)
        or (controller_mode == 'in')
        or (emulator.config.get_bool('dsmotion'))
    ):
        extra_options['Extension'] = 'Nunchuk'
        wii_mapping['l2'] = 'Nunchuk/Buttons/C'
        wii_mapping['r2'] = 'Nunchuk/Buttons/Z'
        wii_mapping['joystick1up'] = 'Nunchuk/Stick/Up'
        wii_mapping['joystick1left'] = 'Nunchuk/Stick/Left'
    if '.in.' in rom.name or '.sn.' in rom.name or '.tn.' in rom.name:
        extra_options['Extension'] = 'Nunchuk'
        wii_mapping['l2'] = 'Nunchuk/Buttons/C'
        wii_mapping['r2'] = 'Nunchuk/Buttons/Z'
        wii_mapping['joystick2up'] = 'Nunchuk/Stick/Up'
        wii_mapping['joystick2left'] = 'Nunchuk/Stick/Left'

    # cc : Classic Controller Settings / pro : Classic Controller Pro Settings
    # Swap shoulder with triggers and vice versa if cc
    if ('.cc.' in rom.name or '.pro.' in rom.name) or (controller_mode in ('cc', 'pro')):
        extra_options['Extension'] = 'Classic'
        wii_mapping['x'] = 'Classic/Buttons/X'
        wii_mapping['y'] = 'Classic/Buttons/Y'
        wii_mapping['b'] = 'Classic/Buttons/B'
        wii_mapping['a'] = 'Classic/Buttons/A'
        wii_mapping['select'] = 'Classic/Buttons/-'
        wii_mapping['start'] = 'Classic/Buttons/+'
        wii_mapping['up'] = 'Classic/D-Pad/Up'
        wii_mapping['down'] = 'Classic/D-Pad/Down'
        wii_mapping['left'] = 'Classic/D-Pad/Left'
        wii_mapping['right'] = 'Classic/D-Pad/Right'
        wii_mapping['joystick1up'] = 'Classic/Left Stick/Up'
        wii_mapping['joystick1left'] = 'Classic/Left Stick/Left'
        wii_mapping['joystick2up'] = 'Classic/Right Stick/Up'
        wii_mapping['joystick2left'] = 'Classic/Right Stick/Left'
        if '.cc.' in rom.name or (controller_mode == 'cc'):
            wii_mapping['pageup'] = 'Classic/Buttons/ZL'
            wii_mapping['pagedown'] = 'Classic/Buttons/ZR'
            wii_mapping['l2'] = 'Classic/Triggers/L'
            wii_mapping['r2'] = 'Classic/Triggers/R'
        else:
            wii_mapping['pageup'] = 'Classic/Triggers/L'
            wii_mapping['pagedown'] = 'Classic/Triggers/R'
            wii_mapping['l2'] = 'Classic/Buttons/ZL'
            wii_mapping['r2'] = 'Classic/Buttons/ZR'

    _read_per_rom_overrides(rom, wii_mapping)

    _logger.debug('Extra Options: %s', extra_options)
    _logger.debug('Wii Mappings: %s', wii_mapping)

    generate_controller_config_any(
        emulator,
        players_controllers,
        wheels,
        'WiimoteNew.ini',
        'Wiimote',
        wii_mapping,
        wii_reverse_axes,
        None,
        extra_options,
    )


def generate_controller_config_gamecube(
    emulator: Emulator, players_controllers: Controllers, wheels: DeviceInfoMapping, rom: Path, /
) -> None:
    gamecube_mapping: dict[str, str | None] = {
        'b': 'Buttons/B',
        'a': 'Buttons/A',
        'y': 'Buttons/Y',
        'x': 'Buttons/X',
        'pagedown': 'Buttons/Z',
        'pageup': None,
        'start': 'Buttons/Start',
        'l2': 'Triggers/L',
        'r2': 'Triggers/R',
        'up': 'D-Pad/Up',
        'down': 'D-Pad/Down',
        'left': 'D-Pad/Left',
        'right': 'D-Pad/Right',
        'joystick1up': 'Main Stick/Up',
        'joystick1left': 'Main Stick/Left',
        'joystick2up': 'C-Stick/Up',
        'joystick2left': 'C-Stick/Left',
        'hotkey': 'Buttons/Hotkey',
    }
    gamecube_reverse_axes: dict[str | None, str] = {
        'Main Stick/Up': 'Main Stick/Down',
        'Main Stick/Left': 'Main Stick/Right',
        'C-Stick/Up': 'C-Stick/Down',
        'C-Stick/Left': 'C-Stick/Right',
    }
    # If joystick1up is missing on the pad, use up instead, and if l2/r2 is missing, use l1/r1
    gamecube_replacements = {
        'joystick1up': 'up',
        'joystick1left': 'left',
        'joystick1down': 'down',
        'joystick1right': 'right',
        'l2': 'pageup',
        'r2': 'pagedown',
    }

    _read_per_rom_overrides(rom, gamecube_mapping)

    generate_controller_config_any(
        emulator,
        players_controllers,
        wheels,
        'GCPadNew.ini',
        'GCPad',
        gamecube_mapping,
        gamecube_reverse_axes,
        gamecube_replacements,
    )


def generate_controller_config_triforce(
    emulator: Emulator, players_controllers: Controllers, wheels: DeviceInfoMapping, rom: Path, /
) -> None:
    # Based on GameCube mapping but with arcade specific overrides
    triforce_mapping: dict[str, str | None] = {
        'a': 'Buttons/B',
        'b': 'Buttons/A',
        'y': 'Buttons/Y',
        'x': 'Buttons/X',
        'pagedown': 'Buttons/Z',
        'pageup': 'Triforce/Service',
        'select': 'Triforce/Coin',
        'start': 'Buttons/Start',
        'l2': 'Triggers/L',
        'r2': 'Triggers/R',
        'up': 'D-Pad/Up',
        'down': 'D-Pad/Down',
        'left': 'D-Pad/Left',
        'right': 'D-Pad/Right',
        'joystick1up': 'Main Stick/Up',
        'joystick1left': 'Main Stick/Left',
        'joystick2up': 'C-Stick/Up',
        'joystick2left': 'C-Stick/Left',
        'hotkey': None,
    }
    triforce_reverse_axes: dict[str | None, str] = {
        'Main Stick/Up': 'Main Stick/Down',
        'Main Stick/Left': 'Main Stick/Right',
        'C-Stick/Up': 'C-Stick/Down',
        'C-Stick/Left': 'C-Stick/Right',
    }
    triforce_replacements = {
        'joystick1up': 'up',
        'joystick1left': 'left',
        'joystick1down': 'down',
        'joystick1right': 'right',
        'l2': 'pageup',
        'r2': 'pagedown',
    }

    _read_per_rom_overrides(rom, triforce_mapping)

    # Wheel mapping for Triforce arcade racing games.
    wheel_triforce_mapping: dict[str, str | None] = {
        'select': 'Triforce/Coin',
        'start': 'Buttons/Start',
        'up': 'D-Pad/Up',
        'down': 'D-Pad/Down',
        'left': 'D-Pad/Left',
        'right': 'D-Pad/Right',
        'a': 'Buttons/A',  # Boost (F-Zero AX) / Item (Mario Kart GP)
        'b': 'Buttons/B',  # VS-Cancel (Mario Kart GP)
        'y': 'Buttons/Z',  # Jump (Mario Kart GP)
        'r2': 'Triggers/R-Analog',  # Gas
        'l2': 'Triggers/L-Analog',  # Brake
        'joystick1left': 'Main Stick/Left',  # Steering
        'pageup': 'Buttons/X',  # Paddle left
        'pagedown': 'Buttons/Y',  # Paddle right
    }
    wheel_triforce_reverse_axes: dict[str | None, str] = {'Main Stick/Left': 'Main Stick/Right'}
    wheel_triforce_extra_options: dict[str, str] = {'Main Stick/Dead Zone': '0.'}

    generate_controller_config_any(
        emulator,
        players_controllers,
        wheels,
        'GCPadNew.ini',
        'GCPad',
        triforce_mapping,
        triforce_reverse_axes,
        triforce_replacements,
        wheel_mapping=wheel_triforce_mapping,
        wheel_reverse_axes=wheel_triforce_reverse_axes,
        wheel_extra_options=wheel_triforce_extra_options,
    )


def remove_controller_config_gamecube() -> None:
    config_file = DOLPHIN_CONFIG / 'GCPadNew.ini'
    if config_file.is_file():
        config_file.unlink()


def generate_controller_config_realwiimotes(filename: str, any_def_key: str, /) -> None:
    config_file = DOLPHIN_CONFIG / filename
    with config_file.open('w', encoding='utf_8_sig') as f:
        for nplayer in range(1, 5):
            f.write(f'[{any_def_key}{nplayer}]\n')
            f.write('Source = 2\n')
        f.write('[BalanceBoard]\nSource = 2\n')


def generate_controller_config_guns(
    filename: str, any_def_key: str, metadata: Mapping[str, str], guns: Guns, /
) -> None:
    config_file = DOLPHIN_CONFIG / filename

    with config_file.open('w', encoding='utf_8_sig') as f:
        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads: dict[str, int] = {}

        for nplayer in range(1, 5):
            if len(guns) < nplayer:
                continue

            f.write(f'[{any_def_key}{nplayer}]\n')
            f.write('Source = 1\n')
            f.write('Extension = Nunchuk\n')

            dolphin_mapping_names = {
                'a': 'Buttons/A',
                'b': 'Buttons/B',
                'home': 'Buttons/Home',
                '-': 'Buttons/-',
                '1': 'Buttons/1',
                '2': 'Buttons/2',
                '+': 'Buttons/+',
                'up': 'D-Pad/Up',
                'down': 'D-Pad/Down',
                'left': 'D-Pad/Left',
                'right': 'D-Pad/Right',
                'tiltforward': 'Tilt/Forward',
                'tiltbackward': 'Tilt/Backward',
                'tiltleft': 'Tilt/Left',
                'tiltright': 'Tilt/Right',
                'shake': 'Shake/Z',
                'c': 'Nunchuk/Buttons/C',
                'z': 'Nunchuk/Buttons/Z',
            }
            gun_mapping = {
                'a': 'action',
                'b': 'trigger',
                'home': 'sub3',
                '-': 'select',
                '1': 'sub1',
                '2': 'sub2',
                '+': 'start',
                'up': 'up',
                'down': 'down',
                'left': 'left',
                'right': 'right',
                'tiltforward': '',
                'tiltbackward': '',
                'tiltleft': '',
                'tiltright': '',
                'shake': '',
                'c': '',
                'z': '',
            }
            gun_buttons = {
                'trigger': {'code': 'BTN_LEFT', 'button': 'left'},
                'action': {'code': 'BTN_RIGHT', 'button': 'right'},
                'start': {'code': 'BTN_MIDDLE', 'button': 'middle'},
                'select': {'code': 'BTN_1', 'button': '1'},
                'sub1': {'code': 'BTN_2', 'button': '2'},
                'sub2': {'code': 'BTN_3', 'button': '3'},
                'sub3': {'code': 'BTN_4', 'button': '4'},
                'up': {'code': 'BTN_5', 'button': '5'},
                'down': {'code': 'BTN_6', 'button': '6'},
                'left': {'code': 'BTN_7', 'button': '7'},
                'right': {'code': 'BTN_8', 'button': '8'},
            }

            gundevname = guns[nplayer - 1].name

            # Handle x pads having the same name
            nsamepad = double_pads.get(gundevname.strip(), 0)
            double_pads[gundevname.strip()] = nsamepad + 1

            f.write(f'[{any_def_key}{nplayer}]\n')
            f.write(f'Device = evdev/{nsamepad!s}/{gundevname.strip()}\n')

            buttons = guns[nplayer - 1].buttons
            _logger.debug('Gun : %s', buttons)

            # custom remapping - erase values
            for btn in gun_buttons:
                if f'gun_{btn}' in metadata:
                    for mval in metadata[f'gun_{btn}'].split(','):
                        if mval in gun_mapping:
                            for x in gun_mapping:
                                if gun_mapping[x] == btn:
                                    _logger.info('erasing %s', x)
                                    gun_mapping[x] = ''
                        else:
                            _logger.info('custom gun mapping ignored for %s => %s (invalid value)', btn, mval)
            # setting values
            for btn in gun_buttons:
                if f'gun_{btn}' in metadata:
                    for mval in metadata[f'gun_{btn}'].split(','):
                        if mval in gun_mapping:
                            gun_mapping[mval] = btn
                            _logger.info('setting %s to %s', mval, btn)

            # write buttons
            for btn, dolphin_name in dolphin_mapping_names.items():
                val = ''
                mapped = gun_mapping.get(btn, '')
                if mapped:
                    if mapped in gun_buttons:
                        if gun_buttons[mapped]['button'] in buttons:
                            val = gun_buttons[mapped]['code']
                        else:
                            _logger.debug('gun has not the button %s', gun_buttons[mapped]['button'])
                    else:
                        _logger.debug('cannot map the button %s', mapped)
                f.write(f'{dolphin_name} = `{val}`\n')

            # map ir
            if 'gun_ir_up' not in metadata:
                f.write('IR/Up = `Axis 1-`\n')
            if 'gun_ir_down' not in metadata:
                f.write('IR/Down = `Axis 1+`\n')
            if 'gun_ir_left' not in metadata:
                f.write('IR/Left = `Axis 0-`\n')
            if 'gun_ir_right' not in metadata:
                f.write('IR/Right = `Axis 0+`\n')

            # specific games configurations
            specifics = {
                'vertical_offset': 'IR/Vertical Offset',
                'yaw': 'IR/Total Yaw',
                'pitch': 'IR/Total Pitch',
                'ir_up': 'IR/Up',
                'ir_down': 'IR/Down',
                'ir_left': 'IR/Left',
                'ir_right': 'IR/Right',
            }
            for spe, spe_key in specifics.items():
                if f'gun_{spe}' in metadata:
                    f.write(f'{spe_key} = {metadata[f"gun_{spe}"]}\n')


def _get_alt_mapping(
    emulator: Emulator, nplayer: int, any_mapping: Mapping[str, str | None], /
) -> dict[str, str | None]:
    mapping = dict(any_mapping)
    # Fixes default gamecube style controller mapping for ES from es_input (gc A confirm/gc B cancel)
    if emulator.config.get(f'dolphin_port_{nplayer}_type') == '6b':
        mapping['a'] = 'Buttons/B'
        mapping['b'] = 'Buttons/A'

    # Only rotate inputs for standard controller type so it doesn't affect other controller types.
    if (emulator.config.get(f'dolphin_port_{nplayer}_type', '6a') == '6a') and emulator.config.get_bool(
        f'alt_mappings_{nplayer}'
    ):
        mapping['a'] = 'Buttons/X'
        mapping['b'] = 'Buttons/A'
        mapping['y'] = 'Buttons/B'
        mapping['x'] = 'Buttons/Y'

    # BattlerGC Pro is a "real" GC style controller, plus full analog+digital analogs(x-input only,
    # home+B turns on/off, digital triggers are mirrored l3/r3).
    if emulator.config.get(f'dolphin_port_{nplayer}_type') == '6c':
        mapping['a'] = 'Buttons/B'
        mapping['b'] = 'Buttons/A'
        mapping['l3'] = 'Triggers/L'
        mapping['r3'] = 'Triggers/R'

    return mapping


def generate_controller_config_any(
    emulator: Emulator,
    players_controllers: Controllers,
    wheels: DeviceInfoMapping,
    filename: str,
    any_def_key: str,
    any_mapping: Mapping[str, str | None],
    any_reverse_axes: Mapping[str | None, str],
    any_replacements: Mapping[str, str] | None,
    extra_options: Mapping[str, str] | None = None,
    wheel_mapping: Mapping[str, str | None] | None = None,
    wheel_reverse_axes: Mapping[str | None, str] | None = None,
    wheel_extra_options: Mapping[str, str] | None = None,
) -> None:
    config_file = DOLPHIN_CONFIG / filename
    with config_file.open('w', encoding='utf_8_sig') as f:
        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads: dict[str, int] = {}

        for nplayer, pad in enumerate(players_controllers, start=1):
            nsamepad = double_pads.get(pad.real_name.strip(), 0)
            double_pads[pad.real_name.strip()] = nsamepad + 1

            f.write(f'[{any_def_key}{nplayer}]\n')
            f.write(f'Device = evdev/{nsamepad!s}/{pad.real_name.strip()}\n')

            if emulator.config.get_bool('use_pad_profiles'):
                if not _generate_controller_config_any_from_profiles(f, pad, emulator):
                    _generate_controller_config_any_auto(
                        f,
                        pad,
                        any_mapping,
                        any_reverse_axes,
                        any_replacements,
                        extra_options or {},
                        emulator,
                        nplayer,
                        nsamepad,
                    )
            elif pad.device_path in wheels and wheel_mapping is not None:
                _generate_controller_config_any_auto(
                    f,
                    pad,
                    wheel_mapping,
                    wheel_reverse_axes or {},
                    None,
                    wheel_extra_options or {},
                    emulator,
                    nplayer,
                    nsamepad,
                )
            elif pad.device_path in wheels:
                _generate_controller_config_wheel(f, pad, nplayer)
            else:
                _generate_controller_config_any_auto(
                    f,
                    pad,
                    any_mapping,
                    any_reverse_axes,
                    any_replacements,
                    extra_options or {},
                    emulator,
                    nplayer,
                    nsamepad,
                )


def _generate_controller_config_wheel(f: SupportsWrite[str], pad: Controller, nplayer: int, /) -> None:
    del nplayer
    wheel_mapping = {
        'select': 'Buttons/Z',
        'start': 'Buttons/Start',
        'up': 'D-Pad/Up',
        'down': 'D-Pad/Down',
        'left': 'D-Pad/Left',
        'right': 'D-Pad/Right',
        'a': 'Buttons/A',
        'b': 'Buttons/B',
        'x': 'Buttons/X',
        'y': 'Buttons/Y',
        'pageup': 'Triggers/L-Analog',
        'pagedown': 'Triggers/R-Analog',
        'r2': 'Main Stick/Up',
        'l2': 'Main Stick/Down',
        'joystick1left': 'Main Stick/Left',
        'joystick1right': 'Main Stick/Right',
    }

    _logger.debug('configuring wheel for pad %s', pad.real_name)

    f.write('Rumble/Motor = Constant\n')  # only Constant works on my wheel. maybe some other values could be good
    f.write('Rumble/Motor/Range = -100.\n')  # value must be negative, otherwise the center is in extremes
    f.write('Main Stick/Dead Zone = 0.\n')  # not really needed while this is the default

    for name, inp in pad.inputs.items():
        if inp.name in wheel_mapping:
            _write_key(f, wheel_mapping[inp.name], inp.type, inp.id, inp.value, pad.axis_count, reverse=False)
            if inp.name == 'joystick1left' and 'joystick1right' in wheel_mapping:
                _write_key(
                    f, wheel_mapping['joystick1right'], inp.type, inp.id, inp.value, pad.axis_count, reverse=True
                )
        del name


def _generate_controller_config_any_auto(
    f: SupportsWrite[str],
    pad: Controller,
    any_mapping: Mapping[str, str | None],
    any_reverse_axes: Mapping[str | None, str],
    any_replacements: Mapping[str, str] | None,
    extra_options: Mapping[str, str],
    emulator: Emulator,
    nplayer: int,
    nsamepad: int,
    /,
) -> None:
    for opt, val in extra_options.items():
        f.write(f'{opt} = {val}\n')

    # Check for alt input mappings
    current_mapping = _get_alt_mapping(emulator, nplayer, any_mapping)
    # Apply replacements
    if any_replacements is not None:
        for x, replacement in any_replacements.items():
            if x not in pad.inputs and x in current_mapping:
                current_mapping[replacement] = current_mapping[x]
                if x == 'joystick1up':
                    current_mapping[any_replacements['joystick1down']] = any_reverse_axes[
                        current_mapping['joystick1up']
                    ]
                if x == 'joystick1left':
                    current_mapping[any_replacements['joystick1right']] = any_reverse_axes[
                        current_mapping['joystick1left']
                    ]
                if x == 'joystick2up':
                    current_mapping[any_replacements['joystick2down']] = any_reverse_axes[
                        current_mapping['joystick2up']
                    ]
                if x == 'joystick2left':
                    current_mapping[any_replacements['joystick2right']] = any_reverse_axes[
                        current_mapping['joystick2left']
                    ]

    for inp in pad.inputs.values():
        keyname = current_mapping.get(inp.name)

        # Write the configuration for this key
        if keyname is not None:
            _write_key(f, keyname, inp.type, inp.id, inp.value, pad.axis_count, reverse=False)
            if 'Triggers' in keyname and inp.type == 'axis':
                _write_key(f, f'{keyname}-Analog', inp.type, inp.id, inp.value, pad.axis_count, reverse=False)
            if 'Buttons/Z' in keyname and 'pageup' in pad.inputs:
                gcz_ids = {'pageup': pad.inputs['pageup'].id, 'pagedown': pad.inputs['pagedown'].id}
                _write_key(f, keyname, inp.type, inp.id, inp.value, pad.axis_count, reverse=False, gcz_ids=gcz_ids)
        # Write the 2nd part
        if inp.name in {'joystick1up', 'joystick1left', 'joystick2up', 'joystick2left'} and keyname is not None:
            _write_key(f, any_reverse_axes[keyname], inp.type, inp.id, inp.value, pad.axis_count, reverse=True)
        # DualShock Motion control
        if emulator.config.get_bool('dsmotion'):
            dev = f'evdev/{nsamepad!s}/{pad.real_name.strip()} Motion Sensors'
            f.write(f'IMUGyroscope/Pitch Up = `{dev}:Gyro X-`\n')
            f.write(f'IMUGyroscope/Pitch Down = `{dev}:Gyro X+`\n')
            f.write(f'IMUGyroscope/Roll Left = `{dev}:Gyro Z-`\n')
            f.write(f'IMUGyroscope/Roll Right = `{dev}:Gyro Z+`\n')
            f.write(f'IMUGyroscope/Yaw Left = `{dev}:Gyro Y-`\n')
            f.write(f'IMUGyroscope/Yaw Right = `{dev}:Gyro Y+`\n')
            f.write('IMUIR/Recenter = `Button 10`\n')
            f.write(f'IMUAccelerometer/Left = `{dev}:Accel X-`\n')
            f.write(f'IMUAccelerometer/Right = `{dev}:Accel X+`\n')
            f.write(f'IMUAccelerometer/Forward = `{dev}:Accel Z-`\n')
            f.write(f'IMUAccelerometer/Backward = `{dev}:Accel Z+`\n')
            f.write(f'IMUAccelerometer/Up = `{dev}:Accel Y-`\n')
            f.write(f'IMUAccelerometer/Down = `{dev}:Accel Y+`\n')
        # Mouse to emulate Wiimote
        if emulator.config.get_bool('mouseir'):
            f.write('IR/Up = `Cursor Y-`\n')
            f.write('IR/Down = `Cursor Y+`\n')
            f.write('IR/Left = `Cursor X-`\n')
            f.write('IR/Right = `Cursor X+`\n')
        # Rumble option
        if emulator.config.get_bool('rumble'):
            f.write('Rumble/Motor = Weak\n')
        # Deadzone setting
        deadzone = emulator.config.get(f'deadzone_{nplayer}', '5.0')
        f.write(f'Main Stick/Dead Zone = {deadzone}\n')
        f.write(f'C-Stick/Dead Zone = {deadzone}\n')
        # JS gate size
        match emulator.config.get(f'jsgate_size_{nplayer}'):
            case 'smaller':
                f.write('Main Stick/Gate Size = 64.0\n')
                f.write('C-Stick/Gate Size = 56.0\n')
            case 'larger':
                f.write('Main Stick/Gate Size = 95.0\n')
                f.write('C-Stick/Gate Size = 88.0\n')
            case _:
                pass


def _generate_controller_config_any_from_profiles(
    f: SupportsWrite[str], pad: Controller, emulator: Emulator, /
) -> bool:
    glob_path: Path | None = None
    if emulator.system == 'gamecube':
        glob_path = DOLPHIN_CONFIG / 'Profiles' / 'GCPad'
    if emulator.system == 'wii':
        glob_path = DOLPHIN_CONFIG / 'Profiles' / 'Wiimote'

    if glob_path is None:
        return False

    for profile_file in glob_path.glob('*.ini'):
        try:
            _logger.debug('Looking profile : %s', profile_file)
            profile_config = CaseSensitiveConfigParser(interpolation=None)
            profile_config.read(profile_file)
            profile_device = profile_config.get('Profile', 'Device')
            _logger.debug('Profile device : %s', profile_device)

            device_vals = re.match('^([^/]*)/[0-9]*/(.*)$', profile_device)
            if (
                device_vals is not None
                and device_vals.group(1) == 'evdev'
                and device_vals.group(2).strip() == pad.real_name.strip()
            ):
                _logger.debug('Eligible profile device found')
                for key, val in profile_config.items('Profile'):
                    if key != 'Device':
                        f.write(f'{key} = {val}\n')
                return True
        except Exception:
            _logger.exception('profile %s : FAILED', profile_file)

    return False


def _write_key(
    f: SupportsWrite[str],
    keyname: str,
    input_type: str,
    input_id: str,
    input_value: str,
    input_global_id: int,
    /,
    *,
    reverse: bool,
    hotkey_id: str | None = None,
    gcz_ids: Mapping[str, str] | None = None,
) -> None:
    f.write(f'{keyname} = ')
    if hotkey_id is not None:
        f.write(f'`Button {hotkey_id}` & ')
    f.write('`')
    if input_type == 'button':
        # Map L1 & R1 both to Z with OR operator
        if keyname == 'Buttons/Z' and gcz_ids is not None:
            f.write(f'Button {gcz_ids["pageup"]}`|`Button {gcz_ids["pagedown"]}')
        else:
            f.write(f'Button {input_id}')
    elif input_type == 'hat':
        if input_value in ('1', '4'):  # up or down
            f.write(f'Axis {int(input_global_id) + 1 + int(input_id) * 2}')
        else:
            f.write(f'Axis {int(input_global_id) + int(input_id) * 2}')
        f.write('-' if input_value in ('1', '8') else '+')  # up or left
    elif input_type == 'axis':
        # Ensure full values are used for analog triggers
        prefix = 'Full ' if keyname in {'Triggers/L-Analog', 'Triggers/R-Analog'} else ''
        if (reverse and input_value == '-1') or (not reverse and input_value == '1'):
            f.write(f'{prefix}Axis {input_id}+')
        else:
            f.write(f'{prefix}Axis {input_id}-')
    f.write('`\n')
