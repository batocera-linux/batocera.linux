from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from batocera_common.yaml import safe_dump_yaml12
from batocera_launch_rpcs3.paths import RPCS3_CONFIG_DIR

if TYPE_CHECKING:
    from batocera_launch.config.config import SystemConfig
    from batocera_launch.devices.controller import Controllers

_logger = logging.getLogger(__name__)

_RPCS3_INPUT_DIR: Final = RPCS3_CONFIG_DIR / 'input_configs' / 'global'

# Fixed keyboard input config for the arcade titles: players 1 and 2 on a single
# keyboard, the remaining slots disabled. Written verbatim as the global Default.yml.
_ARCADE_KEYBOARD_CONFIG: Final = """\
Player 1 Input:
  Handler: Keyboard
  Device: Keyboard
  Config:
    Left Stick Left: ""
    Left Stick Down: ""
    Left Stick Right: ""
    Left Stick Up: ""
    Right Stick Left: ""
    Right Stick Down: ""
    Right Stick Right: ""
    Right Stick Up: ""
    Start: 1
    Select: F2
    PS Button: ""
    Square: E
    Cross: T
    Circle: Y
    Triangle: R
    Left: A
    Down: S
    Right: D
    Up: W
    R1: U
    R2: ""
    R3: F1
    L1: I
    L2: ""
    L3: 5
    IR Nose: ""
    IR Tail: ""
    IR Left: ""
    IR Right: ""
    Tilt Left: ""
    Tilt Right: ""
    Motion Sensor X:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor Y:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor Z:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor G:
      Axis: ""
      Mirrored: false
      Shift: 0
    Orientation Reset Button: ""
    Orientation Enabled: false
    Pressure Intensity Button: ""
    Pressure Intensity Percent: 50
    Pressure Intensity Toggle Mode: false
    Pressure Intensity Deadzone: 0
    Analog Limiter Button: ""
    Analog Limiter Toggle Mode: false
    Left Stick Multiplier: 100
    Right Stick Multiplier: 100
    Left Stick Deadzone: 0
    Right Stick Deadzone: 0
    Left Stick Anti-Deadzone: 0
    Right Stick Anti-Deadzone: 0
    Left Trigger Threshold: 0
    Right Trigger Threshold: 0
    Left Pad Squircling Factor: 8000
    Right Pad Squircling Factor: 8000
    Color Value R: 0
    Color Value G: 0
    Color Value B: 0
    Blink LED when battery is below 20%: true
    Use LED as a battery indicator: false
    LED battery indicator brightness: 50
    Player LED enabled: true
    Large Vibration Motor Multiplier: 100
    Small Vibration Motor Multiplier: 100
    Switch Vibration Motors: false
    Vibration Threshold: 63
    Mouse Movement Mode: Relative
    Mouse Deadzone X Axis: 60
    Mouse Deadzone Y Axis: 60
    Mouse Acceleration X Axis: 200
    Mouse Acceleration Y Axis: 250
    Left Stick Lerp Factor: 100
    Right Stick Lerp Factor: 100
    Analog Button Lerp Factor: 100
    Trigger Lerp Factor: 100
    Device Class Type: 0
    Vendor ID: 1356
    Product ID: 616
  Buddy Device: ""
Player 2 Input:
  Handler: Keyboard
  Device: Keyboard
  Config:
    Left Stick Left: ""
    Left Stick Down: ""
    Left Stick Right: ""
    Left Stick Up: ""
    Right Stick Left: ""
    Right Stick Down: ""
    Right Stick Right: ""
    Right Stick Up: ""
    Start: 2
    Select: F2
    PS Button: ""
    Square: F
    Cross: H
    Circle: J
    Triangle: G
    Left: Left
    Down: Down
    Right: Right
    Up: Up
    R1: K
    R2: ""
    R3: F1
    L1: L
    L2: ""
    L3: 6
    IR Nose: ""
    IR Tail: ""
    IR Left: ""
    IR Right: ""
    Tilt Left: ""
    Tilt Right: ""
    Motion Sensor X:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor Y:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor Z:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor G:
      Axis: ""
      Mirrored: false
      Shift: 0
    Orientation Reset Button: ""
    Orientation Enabled: false
    Pressure Intensity Button: ""
    Pressure Intensity Percent: 50
    Pressure Intensity Toggle Mode: false
    Pressure Intensity Deadzone: 0
    Analog Limiter Button: ""
    Analog Limiter Toggle Mode: false
    Left Stick Multiplier: 100
    Right Stick Multiplier: 100
    Left Stick Deadzone: 0
    Right Stick Deadzone: 0
    Left Stick Anti-Deadzone: 0
    Right Stick Anti-Deadzone: 0
    Left Trigger Threshold: 0
    Right Trigger Threshold: 0
    Left Pad Squircling Factor: 8000
    Right Pad Squircling Factor: 8000
    Color Value R: 0
    Color Value G: 0
    Color Value B: 0
    Blink LED when battery is below 20%: true
    Use LED as a battery indicator: false
    LED battery indicator brightness: 50
    Player LED enabled: true
    Large Vibration Motor Multiplier: 100
    Small Vibration Motor Multiplier: 100
    Switch Vibration Motors: false
    Vibration Threshold: 63
    Mouse Movement Mode: Relative
    Mouse Deadzone X Axis: 60
    Mouse Deadzone Y Axis: 60
    Mouse Acceleration X Axis: 200
    Mouse Acceleration Y Axis: 250
    Left Stick Lerp Factor: 100
    Right Stick Lerp Factor: 100
    Analog Button Lerp Factor: 100
    Trigger Lerp Factor: 100
    Device Class Type: 0
    Vendor ID: 1356
    Product ID: 616
  Buddy Device: "Null"
""" + ''.join(
    f"""Player {nplayer} Input:
  Handler: "Null"
  Device: "Null"
  Config:
    Left Stick Left: ""
    Left Stick Down: ""
    Left Stick Right: ""
    Left Stick Up: ""
    Right Stick Left: ""
    Right Stick Down: ""
    Right Stick Right: ""
    Right Stick Up: ""
    Start: ""
    Select: ""
    PS Button: ""
    Square: ""
    Cross: ""
    Circle: ""
    Triangle: ""
    Left: ""
    Down: ""
    Right: ""
    Up: ""
    R1: ""
    R2: ""
    R3: ""
    L1: ""
    L2: ""
    L3: ""
    IR Nose: ""
    IR Tail: ""
    IR Left: ""
    IR Right: ""
    Tilt Left: ""
    Tilt Right: ""
    Motion Sensor X:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor Y:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor Z:
      Axis: ""
      Mirrored: false
      Shift: 0
    Motion Sensor G:
      Axis: ""
      Mirrored: false
      Shift: 0
    Orientation Reset Button: ""
    Orientation Enabled: false
    Pressure Intensity Button: ""
    Pressure Intensity Percent: 50
    Pressure Intensity Toggle Mode: false
    Pressure Intensity Deadzone: 0
    Analog Limiter Button: ""
    Analog Limiter Toggle Mode: false
    Left Stick Multiplier: 100
    Right Stick Multiplier: 100
    Left Stick Deadzone: 0
    Right Stick Deadzone: 0
    Left Stick Anti-Deadzone: 0
    Right Stick Anti-Deadzone: 0
    Left Trigger Threshold: 0
    Right Trigger Threshold: 0
    Left Pad Squircling Factor: 8000
    Right Pad Squircling Factor: 8000
    Color Value R: 0
    Color Value G: 0
    Color Value B: 0
    Blink LED when battery is below 20%: true
    Use LED as a battery indicator: false
    LED battery indicator brightness: 50
    Player LED enabled: true
    Large Vibration Motor Multiplier: 100
    Small Vibration Motor Multiplier: 100
    Switch Vibration Motors: false
    Vibration Threshold: 63
    Mouse Movement Mode: Relative
    Mouse Deadzone X Axis: 60
    Mouse Deadzone Y Axis: 60
    Mouse Acceleration X Axis: 200
    Mouse Acceleration Y Axis: 250
    Left Stick Lerp Factor: 100
    Right Stick Lerp Factor: 100
    Analog Button Lerp Factor: 100
    Trigger Lerp Factor: 100
    Device Class Type: 0
    Vendor ID: 0
    Product ID: 0
  Buddy Device: "Null"
"""
    for nplayer in range(3, 8)
)

# Sony pad GUIDs grouped by the RPCS3 handler / device prefix they map to.
_DS3_GUIDS: Final = (
    '030000004c0500006802000011010000',
    '030000004c0500006802000011810000',
    '050000004c0500006802000000800000',
    '050000004c0500006802000000000000',
)
_DS4_GUIDS: Final = (
    '030000004c050000c405000011810000',
    '050000004c050000c405000000810000',
    '030000004c050000cc09000011010000',
    '050000004c050000cc09000000010000',
    '030000004c050000cc09000011810000',
    '050000004c050000cc09000000810000',
    '030000004c050000a00b000011010000',
    '030000004c050000a00b000011810000',
)
_DS5_GUIDS: Final = (
    '030000004c050000e60c000011810000',
    '050000004c050000e60c000000810000',
)

# guid -> (handler, device name prefix)
_SONY_GUIDS: Final[dict[str, tuple[str, str]]] = {
    **dict.fromkeys(_DS3_GUIDS, ('DualShock 3', 'DS3 Pad')),
    **dict.fromkeys(_DS4_GUIDS, ('DualShock 4', 'DS4 Pad')),
    **dict.fromkeys(_DS5_GUIDS, ('DualSense', 'DualSense Pad')),
}

# Static config block for DualShock / DualSense pads. The two vibration motor
# entries are overwritten per pad (key order is preserved on overwrite).
_DUALSHOCK_CONFIG: Final[dict[str, Any]] = {
    'Left Stick Left': 'LS X-',
    'Left Stick Down': 'LS Y-',
    'Left Stick Right': 'LS X+',
    'Left Stick Up': 'LS Y+',
    'Right Stick Left': 'RS X-',
    'Right Stick Down': 'RS Y-',
    'Right Stick Right': 'RS X+',
    'Right Stick Up': 'RS Y+',
    'Start': 'Options',
    'Select': 'Share',
    'PS Button': 'PS Button',
    'Square': 'Square',
    'Cross': 'Cross',
    'Circle': 'Circle',
    'Triangle': 'Triangle',
    'Left': 'Left',
    'Down': 'Down',
    'Right': 'Right',
    'Up': 'Up',
    'R1': 'R1',
    'R2': 'R2',
    'R3': 'R3',
    'L1': 'L1',
    'L2': 'L2',
    'L3': 'L3',
    'Motion Sensor X': {'Axis': '', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor Y': {'Axis': '', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor Z': {'Axis': '', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor G': {'Axis': '', 'Mirrored': False, 'Shift': 0},
    'Pressure Intensity Button': '',
    'Pressure Intensity Percent': 50,
    'Pressure Intensity Toggle Mode': False,
    'Left Stick Multiplier': 100,
    'Right Stick Multiplier': 100,
    'Left Stick Deadzone': 40,
    'Right Stick Deadzone': 40,
    'Left Trigger Threshold': 0,
    'Right Trigger Threshold': 0,
    'Left Pad Squircling Factor': 8000,
    'Right Pad Squircling Factor': 8000,
    'Color Value R': 0,
    'Color Value G': 0,
    'Color Value B': 20,
    'Blink LED when battery is below 20%': True,
    'Use LED as a battery indicator': False,
    'LED battery indicator brightness': 10,
    'Player LED enabled': True,
    'Enable Large Vibration Motor': 'true',
    'Enable Small Vibration Motor': 'true',
    'Switch Vibration Motors': False,
    'Mouse Movement Mode': 'Relative',
    'Mouse Deadzone X Axis': 60,
    'Mouse Deadzone Y Axis': 60,
    'Mouse Acceleration X Axis': 200,
    'Mouse Acceleration Y Axis': 250,
    'Left Stick Lerp Factor': 100,
    'Right Stick Lerp Factor': 100,
    'Analog Button Lerp Factor': 100,
    'Trigger Lerp Factor': 100,
    'Device Class Type': 0,
    'Vendor ID': 1356,
    'Product ID': 616,
}

# Evdev mapping: batocera input name -> (RPCS3 config name, event variations).
# Each variation is (evdev event type, RPCS3 value name); the event type is
# matched against the pad's input type (button / hat / axis).
# from evdev_joystick_handler.h
_EVDEV_INPUT_MAPPING: Final[dict[str, tuple[str, tuple[tuple[str, str], ...]]]] = {
    'up': ('Up', (('BTN_DPAD_UP', 'D-Pad Up'), ('ABS_HAT0Y', 'Hat0 Y-'))),
    'down': ('Down', (('BTN_DPAD_DOWN', 'D-Pad Down'), ('ABS_HAT0Y', 'Hat0 Y+'))),
    'left': ('Left', (('BTN_DPAD_LEFT', 'D-Pad Left'), ('ABS_HAT0X', 'Hat0 X-'))),
    'right': ('Right', (('BTN_DPAD_RIGHT', 'D-Pad Right'), ('ABS_HAT0X', 'Hat0 X+'))),
    'l2': ('L2', (('BTN_TL2', 'TL 2'), ('ABS_Z', 'LZ+'))),
    'r2': ('R2', (('BTN_TR2', 'TR 2'), ('ABS_RZ', 'RZ+'))),
    'a': ('Cross', (('BTN_A', 'A'),)),
    'b': ('Circle', (('BTN_B', 'B'),)),
    'x': ('Square', (('BTN_X', 'X'),)),
    'y': ('Triangle', (('BTN_Y', 'Y'),)),
    'joystick1up': ('Left Stick Up', (('ABS_Y', 'LY-'),)),
    'joystick1left': ('Left Stick Left', (('ABS_X', 'LX-'),)),
    'joystick2up': ('Right Stick Up', (('ABS_RY', 'RY-'),)),
    'joystick2left': ('Right Stick Left', (('ABS_RX', 'RX-'),)),
}

# Paired secondary axis written alongside the primary stick axis.
_EVDEV_AXIS_PAIRS: Final = {
    'Left Stick Up': ('Left Stick Down', 'LY+'),
    'Left Stick Left': ('Left Stick Right', 'LX+'),
    'Right Stick Up': ('Right Stick Down', 'RY+'),
    'Right Stick Left': ('Right Stick Right', 'RX+'),
}

# Static tail for Evdev pads, appended after the dynamically mapped inputs.
_EVDEV_CONFIG_TAIL: Final[dict[str, Any]] = {
    'R1': 'TR',
    'R3': 'Thumb R',
    'L1': 'TL',
    'L3': 'Thumb L',
    'Motion Sensor X': {'Axis': 'X', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor Y': {'Axis': 'Y', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor Z': {'Axis': 'Z', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor G': {'Axis': 'RY', 'Mirrored': False, 'Shift': 0},
    'Pressure Intensity Button': '',
    'Pressure Intensity Percent': 50,
    'Pressure Intensity Toggle Mode': False,
    'Left Stick Multiplier': 100,
    'Right Stick Multiplier': 100,
    'Left Stick Deadzone': 30,
    'Right Stick Deadzone': 30,
    'Left Trigger Threshold': 0,
    'Right Trigger Threshold': 0,
    'Left Pad Squircling Factor': 5000,
    'Right Pad Squircling Factor': 5000,
    'Color Value R': 0,
    'Color Value G': 0,
    'Color Value B': 0,
    'Blink LED when battery is below 20%': True,
    'Use LED as a battery indicator': False,
    'LED battery indicator brightness': 50,
    'Player LED enabled': True,
    'Enable Large Vibration Motor': 'true',
    'Enable Small Vibration Motor': 'true',
    'Switch Vibration Motors': False,
    'Mouse Movement Mode': 'Relative',
    'Mouse Deadzone X Axis': 60,
    'Mouse Deadzone Y Axis': 60,
    'Mouse Acceleration X Axis': 200,
    'Mouse Acceleration Y Axis': 250,
    'Left Stick Lerp Factor': 100,
    'Right Stick Lerp Factor': 100,
    'Analog Button Lerp Factor': 100,
    'Trigger Lerp Factor': 100,
    'Device Class Type': 0,
    'Vendor ID': 1356,
    'Product ID': 616,
}

# Static config block for the default SDL handler. The two vibration motor
# entries are overwritten per pad (key order is preserved on overwrite).
_SDL_CONFIG: Final[dict[str, Any]] = {
    'Left Stick Left': 'LS X-',
    'Left Stick Down': 'LS Y-',
    'Left Stick Right': 'LS X+',
    'Left Stick Up': 'LS Y+',
    'Right Stick Left': 'RS X-',
    'Right Stick Down': 'RS Y-',
    'Right Stick Right': 'RS X+',
    'Right Stick Up': 'RS Y+',
    'Start': 'Start',
    'Select': 'Back',
    'PS Button': 'Guide',
    'Square': 'West',
    'Cross': 'South',
    'Circle': 'East',
    'Triangle': 'North',
    'Left': 'Left',
    'Down': 'Down',
    'Right': 'Right',
    'Up': 'Up',
    'R1': 'RB',
    'R2': 'RT',
    'R3': 'RS',
    'L1': 'LB',
    'L2': 'LT',
    'L3': 'LS',
    'IR Nose': '',
    'IR Tail': '',
    'IR Left': '',
    'IR Right': '',
    'Tilt Left': '',
    'Tilt Right': '',
    'Motion Sensor X': {'Axis': 'X', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor Y': {'Axis': 'Y', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor Z': {'Axis': 'Z', 'Mirrored': False, 'Shift': 0},
    'Motion Sensor G': {'Axis': 'RY', 'Mirrored': False, 'Shift': 0},
    'Orientation Reset Button': '',
    'Orientation Enabled': False,
    'Pressure Intensity Button': '',
    'Pressure Intensity Percent': 50,
    'Pressure Intensity Toggle Mode': False,
    'Pressure Intensity Deadzone': 0,
    'Analog Limiter Button': '',
    'Analog Limiter Toggle Mode': False,
    'Left Stick Multiplier': 100,
    'Right Stick Multiplier': 100,
    'Left Stick Deadzone': 8000,
    'Right Stick Deadzone': 8000,
    'Left Stick Anti-Deadzone': 4259,
    'Right Stick Anti-Deadzone': 4259,
    'Left Trigger Threshold': 0,
    'Right Trigger Threshold': 0,
    'Left Pad Squircling Factor': 8000,
    'Right Pad Squircling Factor': 8000,
    'Color Value R': 0,
    'Color Value G': 0,
    'Color Value B': 20,
    'Blink LED when battery is below 20%': True,
    'Use LED as a battery indicator': False,
    'LED battery indicator brightness': 10,
    'Player LED enabled': True,
    'Enable Large Vibration Motor': 0,
    'Enable Small Vibration Motor': 0,
    'Switch Vibration Motors': False,
    'Mouse Movement Mode': 'Relative',
    'Mouse Deadzone X Axis': 60,
    'Mouse Deadzone Y Axis': 60,
    'Mouse Acceleration X Axis': 200,
    'Mouse Acceleration Y Axis': 250,
    'Left Stick Lerp Factor': 100,
    'Right Stick Lerp Factor': 100,
    'Analog Button Lerp Factor': 100,
    'Trigger Lerp Factor': 100,
    'Device Class Type': 0,
    'Vendor ID': 1356,
    'Product ID': 616,
}


def generate_controllers_config(config: SystemConfig, controllers: Controllers, /, *, keyboard: bool = False) -> None:
    _RPCS3_INPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Lightgun arcade titles are driven through the keyboard (two players on one keyboard).
    if keyboard:
        (_RPCS3_INPUT_DIR / 'Default.yml').write_text(_ARCADE_KEYBOARD_CONFIG)
        return

    # Per-handler device counters: RPCS3 appends a unique index per device name.
    sony_counts: dict[str, int] = {}
    sdl_counts: dict[str, int] = {}

    controllers_config: dict[str, Any] = {}
    for nplayer, pad in enumerate(controllers[:7], start=1):
        _logger.debug('Controller #%s - %s', nplayer, pad.guid)
        controller_type = config.get(f'rpcs3_controller{nplayer}')
        rumble = config.get_bool(f'rpcs3_rumble{nplayer}', True)

        # DualShock / DualSense
        if pad.guid in _SONY_GUIDS and controller_type == 'Sony':
            _logger.debug('*** Using DualShock / DualSense configuration ***')
            handler, prefix = _SONY_GUIDS[pad.guid]
            count = sony_counts[prefix] = sony_counts.get(prefix, 0) + 1

            pad_config = dict(_DUALSHOCK_CONFIG)
            pad_config['Enable Large Vibration Motor'] = rumble
            pad_config['Enable Small Vibration Motor'] = rumble

            controllers_config[f'Player {nplayer} Input'] = {
                'Handler': handler,
                'Device': f'{prefix} #{count}',
                'Config': pad_config,
                'Buddy Device': '',
            }
        # Evdev
        elif controller_type == 'Evdev':
            _logger.debug('*** Using EVDEV configuration ***')
            pad_config: dict[str, Any] = {'Start': 'Start', 'Select': 'Select', 'PS Button': 'Mode'}

            for input in pad.inputs.values():
                mapping = _EVDEV_INPUT_MAPPING.get(input.name)
                if mapping is None:
                    continue

                config_name, event_variations = mapping
                for event_type, value_name in event_variations:
                    if ('BTN' in event_type and input.type == 'button') or (
                        'HAT' in event_type and input.type == 'hat'
                    ):
                        pad_config[config_name] = value_name
                    elif 'ABS' in event_type and input.type == 'axis':
                        pad_config[config_name] = value_name
                        # write the matching secondary stick axis as well
                        if (pair := _EVDEV_AXIS_PAIRS.get(config_name)) is not None:
                            pad_config[pair[0]] = pair[1]

            pad_config.update(_EVDEV_CONFIG_TAIL)
            pad_config['Enable Large Vibration Motor'] = rumble
            pad_config['Enable Small Vibration Motor'] = rumble

            controllers_config[f'Player {nplayer} Input'] = {
                'Handler': 'Evdev',
                'Device': pad.device_path,
                'Config': pad_config,
                'Buddy Device': '',
            }
        # Default SDL handler
        else:
            _logger.debug('*** Using default SDL3 configuration ***')
            # workaround controllers with commas in their name - like Nintendo
            ctrlname = pad.real_name.replace(',', '.')
            count = sdl_counts[ctrlname] = sdl_counts.get(ctrlname, 0) + 1

            pad_config = dict(_SDL_CONFIG)
            motor = 100 if rumble else 0
            pad_config['Enable Large Vibration Motor'] = motor
            pad_config['Enable Small Vibration Motor'] = motor

            controllers_config[f'Player {nplayer} Input'] = {
                'Handler': 'SDL',
                'Device': f'{ctrlname} {count}',
                'Config': pad_config,
                'Buddy Device': '',
            }

    safe_dump_yaml12(controllers_config, _RPCS3_INPUT_DIR / 'Default.yml')
