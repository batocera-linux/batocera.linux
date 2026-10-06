from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final, TypedDict, cast

import toml

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, SAVES, SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)


class _BindData(TypedDict):
    sdl_map: dict[str, list[str]]
    keyboard_map: dict[int, dict[str, list[str]]]


# Mappings based on stock Ymir.toml
_PERIPHERAL_BINDS: Final[dict[str, _BindData]] = {
    'AnalogPad': {
        'sdl_map': {
            'A': ['GamepadX'],
            'B': ['GamepadA'],
            'C': ['GamepadB'],
            'X': ['GamepadLeftBumper'],
            'Y': ['GamepadY'],
            'Z': ['GamepadRightBumper'],
            'Start': ['GamepadStart'],
            'SwitchMode': ['GamepadLeftThumb'],
            'DPad': ['GamepadDPad'],
            'AnalogStick': ['GamepadLeftStick'],
            'AnalogL': ['GamepadLeftTrigger'],
            'AnalogR': ['GamepadRightTrigger'],
        },
        'keyboard_map': {
            1: {
                'A': ['J'],
                'B': ['K'],
                'C': ['L'],
                'X': ['U'],
                'Y': ['I'],
                'Z': ['O'],
                'L': ['Q'],
                'R': ['E'],
                'Up': ['W'],
                'Down': ['S'],
                'Left': ['A'],
                'Right': ['D'],
                'Start': ['F', 'G', 'H'],
                'SwitchMode': ['Ctrl+B'],
            },
            2: {
                'A': ['KeyPad1'],
                'B': ['KeyPad2'],
                'C': ['KeyPad3'],
                'X': ['KeyPad4'],
                'Y': ['KeyPad5'],
                'Z': ['KeyPad6'],
                'L': ['Insert', 'KeyPad7'],
                'R': ['PageUp', 'KeyPad9'],
                'Up': ['Home', 'Up'],
                'Down': ['End', 'Down'],
                'Left': ['Delete', 'Left'],
                'Right': ['PageDown', 'Right'],
                'Start': ['KeyPadEnter'],
                'SwitchMode': ['KeyPadAdd'],
            },
        },
    },
    'ControlPad': {
        'sdl_map': {
            'A': ['GamepadX'],
            'B': ['GamepadA'],
            'C': ['GamepadB'],
            'X': ['GamepadLeftBumper'],
            'Y': ['GamepadY'],
            'Z': ['GamepadRightBumper'],
            'L': ['GamepadLeftTriggerButton'],
            'R': ['GamepadRightTriggerButton'],
            'Start': ['GamepadStart'],
            'DPad': ['GamepadLeftStick', 'GamepadDPad'],
        },
        'keyboard_map': {
            1: {
                'A': ['J'],
                'B': ['K'],
                'C': ['L'],
                'X': ['U'],
                'Y': ['I'],
                'Z': ['O'],
                'L': ['Q'],
                'R': ['E'],
                'Up': ['W'],
                'Down': ['S'],
                'Left': ['A'],
                'Right': ['D'],
                'Start': ['F', 'G', 'H'],
            },
            2: {
                'A': ['KeyPad1'],
                'B': ['KeyPad2'],
                'C': ['KeyPad3'],
                'X': ['KeyPad4'],
                'Y': ['KeyPad5'],
                'Z': ['KeyPad6'],
                'L': ['Insert', 'KeyPad7'],
                'R': ['PageUp', 'KeyPad9'],
                'Up': ['Home', 'Up'],
                'Down': ['End', 'Down'],
                'Left': ['Delete', 'Left'],
                'Right': ['PageDown', 'Right'],
                'Start': ['KeyPadEnter'],
            },
        },
    },
    'ArcadeRacer': {
        'sdl_map': {
            'A': ['GamepadX'],
            'B': ['GamepadA'],
            'C': ['GamepadB'],
            'X': ['GamepadLeftBumper'],
            'Y': ['GamepadY'],
            'Z': ['GamepadRightBumper'],
            'Start': ['GamepadStart'],
            'Up': ['GamepadDpadDown', 'GamepadRightTriggerButton'],
            'Down': ['GamepadDpadUp', 'GamepadLeftTriggerButton'],
            'Wheel': ['GamepadLeftStickX'],
        },
        'keyboard_map': {
            1: {
                'A': ['J'],
                'B': ['K'],
                'C': ['L'],
                'X': ['U'],
                'Y': ['I'],
                'Z': ['O'],
                'Start': ['F', 'G', 'H'],
                'Up': ['S'],
                'Down': ['W'],
                'WheelLeft': ['A'],
                'WheelRight': ['D'],
            },
            2: {
                'A': ['KeyPad1'],
                'B': ['KeyPad2'],
                'C': ['KeyPad3'],
                'X': ['KeyPad4'],
                'Y': ['KeyPad5'],
                'Z': ['KeyPad6'],
                'Start': ['KeyPadEnter'],
                'Up': ['Down', 'End'],
                'Down': ['Up', 'Home'],
                'WheelLeft': ['Delete', 'Left'],
                'WheelRight': ['PageDown', 'Right'],
            },
        },
    },
    'MissionStick': {
        'sdl_map': {
            'A': ['GamepadX'],
            'B': ['GamepadA'],
            'C': ['GamepadB'],
            'X': ['GamepadLeftBumper'],
            'Y': ['GamepadY'],
            'Z': ['GamepadRightBumper'],
            'L': ['GamepadLeftThumb'],
            'R': ['GamepadRightThumb'],
            'Start': ['GamepadStart'],
            'SwitchMode': ['GamepadBack'],
            'MainStick': ['GamepadLeftStick', 'GamepadDPad'],
            'MainThrottle': ['GamepadLeftTrigger'],
            'SubStick': ['GamepadRightStick'],
            'SubThrottle': ['GamepadRightTrigger'],
        },
        'keyboard_map': {
            1: {
                'A': ['X'],
                'B': ['C'],
                'C': ['V'],
                'X': ['B'],
                'Y': ['N'],
                'Z': ['M'],
                'L': ['Q'],
                'R': ['E'],
                'Start': ['G'],
                'SwitchMode': ['Ctrl+B'],
                'MainUp': ['W'],
                'MainDown': ['S'],
                'MainLeft': ['A'],
                'MainRight': ['D'],
                'MainThrottleUp': ['R'],
                'MainThrottleDown': ['F'],
                'MainThrottleMax': ['Shift+R'],
                'MainThrottleMin': ['Shift+F'],
                'SubUp': ['I'],
                'SubDown': ['K'],
                'SubLeft': ['J'],
                'SubRight': ['L'],
                'SubThrottleUp': ['Y'],
                'SubThrottleDown': ['H'],
                'SubThrottleMax': ['Shift+Y'],
                'SubThrottleMin': ['Shift+H'],
            },
            2: {},  # Player 2 keyboard for Mission Stick has no defaults in stock file
        },
    },
}


@cached_dataclass
class Ymir(Emulator):
    needs_sdl_controller_db = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ymir',
            'keys': {
                'exit': 'killall -9 ymir',
                'save_state': 'KEY_F2',
                'restore_state': 'KEY_F3',
            },
        }

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.config_dir / 'gamecontrollerdb.txt'

    @cached_property
    def saves_dir(self) -> Path:
        # Ymir's saves live under a single emulator-scoped directory (not per-system),
        # matching the stock Ymir.toml layout.
        return SAVES / 'ymir'

    @cached_property
    def in_game_ratio(self) -> float:
        if self.config.get_float('ymir_aspect') == 1.3333333333333333:
            return 4 / 3
        return 16 / 9

    async def configure(self) -> Command:
        toml_file = self.config_dir / 'Ymir.toml'
        backup_path = self.saves_dir / 'backup'
        exported_path = backup_path / 'exported'
        dumps_path = self.saves_dir / 'dumps'
        screenshot_path = SCREENSHOTS / 'ymir'

        # Create all necessary directories (saves_dir itself is already created by the
        # base class's __aenter__ by the time configure() runs)
        for path in (self.config_dir, backup_path, exported_path, dumps_path, screenshot_path):
            path.mkdir(parents=True, exist_ok=True)

        # Adjust the Ymir.toml file
        config: dict[str, dict[str, object]] = {}

        # Check if the file exists
        if toml_file.is_file():
            try:
                config = toml.loads(toml_file.read_text())
            except Exception as e:
                _logger.error('Failed to load existing ymir config: %s. Will create default.', e)

        # If config is empty, create default structure
        if not config:
            _logger.info('Creating default ymir config at %s', toml_file)
            config = {
                'ConfigVersion': 5,  # pyright: ignore[reportAssignmentType]
                'Cartridge': {
                    'AutoLoadGameCarts': True,
                    'Type': 'None',
                },
                'General': {
                    'BoostEmuThreadPriority': True,
                    'BoostProcessPriority': True,
                    'EnableRewindBuffer': False,
                    'PauseWhenUnfocused': False,
                    'PreloadDiscImagesToRAM': False,
                    'RewindCompressionLevel': 12,
                },
                'System': {
                    'AutoDetectRegion': True,
                    'InternalBackupRAMPerGame': False,
                },
                'Video': {
                    'AutoResizeWindow': False,
                    'FullScreen': True,
                    'ForceAspectRatio': True,
                    'ForceIntegerScaling': False,
                    'SoftwareRenderer': {
                        'ThreadedVDP1': True,
                        'ThreadedVDP2': True,
                        'ThreadedDeinterlacer': True,
                    },
                    'Enhancements': {
                        'Deinterlace': False,
                    },
                },
            }

        # As of ConfigVersion 5, Ymir moved these keys around (see settings.cpp's own
        # "Change history" comment); always keep the ConfigVersion current so Ymir reads
        # our writes from the locations we actually write them to below, rather than
        # falling back to (and never updating) the pre-v4/v5 flat key layout.
        config['ConfigVersion'] = 5  # pyright: ignore[reportArgumentType]

        # --- Apply Batocera Specific Overrides ---

        # General
        general_config = config.setdefault('General', {})
        general_config.update(
            {
                'CheckForUpdates': False,
                'IncludeNightlyBuilds': False,
            }
        )

        # adds [General.PathOverrides]
        path_overrides = cast('dict[str, str]', general_config.setdefault('PathOverrides', {}))
        path_overrides.update(
            {
                'BackupMemory': str(backup_path),
                'CDBlockROMImages': str(self.roms_dir / 'cdb/'),
                'Dumps': str(dumps_path),
                'ExportedBackups': str(exported_path),
                'IPLROMImages': str(BIOS),
                'PersistentState': str(self.config_dir / 'state/'),
                'ROMCartImages': str(self.roms_dir),
                'SaveStates': str(self.saves_dir),
                'Screenshots': str(screenshot_path),
            }
        )

        # System
        system_config = config.setdefault('System', {})
        system_config.update(
            {
                'AutoDetectRegion': True,
                'InternalBackupRAMPerGame': self.config.get_bool('ymir_backup_ram_per_game', False),
            }
        )

        # Cartridge
        cartridge_config = config.setdefault('Cartridge', {})
        cartridge_config.update(
            {
                'AutoLoadGameCarts': True,
            }
        )

        # Video
        video_config = config.setdefault('Video', {})
        video_config.update(
            {
                'AutoResizeWindow': False,
                'DisplayVideoOutputInWindow': False,
                'FullScreen': True,
                'ForceAspectRatio': True,
                'ForceIntegerScaling': self.config.get_bool('ymir_integer_scaling', False),
            }
        )

        # ConfigVersion 5 moved these two sub-tables out of the flat Video.* namespace
        sw_renderer_config = cast('dict[str, object]', video_config.setdefault('SoftwareRenderer', {}))
        sw_renderer_config.update(
            {
                'ThreadedVDP1': True,
                'ThreadedVDP2': True,
                'ThreadedDeinterlacer': True,
            }
        )

        enhancements_config = cast('dict[str, object]', video_config.setdefault('Enhancements', {}))
        enhancements_config.update(
            {
                'Deinterlace': self.config.get_bool('ymir_interlace', True),
                'TransparentMeshes': self.config.get_bool('ymir_meshes', False),
            }
        )

        # Options
        video_config.update(
            {
                'ForcedAspect': self.config.get_float('ymir_aspect', 1.5),
                'Rotation': self.config.get_str('ymir_rotation', 'Normal'),
            }
        )

        # Controllers
        input_config = config.setdefault('Input', {})

        # ConfigVersion 4 moved these from flat Input.Gamepad* keys to a nested Input.Gamepad.* table
        gamepad_config = cast('dict[str, object]', input_config.setdefault('Gamepad', {}))
        gamepad_config.update(
            {
                'AnalogToDigitalSensitivity': 0.20000000298023224,
                'LSDeadzone': 0.15000000596046448,
                'RSDeadzone': 0.15000000596046448,
            }
        )

        # Clear existing port configurations for the 2 supported ports
        for i in range(1, 3):
            if f'Port{i}' in input_config:
                del input_config[f'Port{i}']

        # Pre-initialize Port 1 and Port 2 as "None" (fallback if player is not connected)
        for i in range(1, 3):
            port_config = cast('dict[str, object]', input_config.setdefault(f'Port{i}', {}))
            port_config['PeripheralType'] = 'None'

        # Configure up to a maximum of two controllers
        for pad in self.controllers[:2]:
            player_num = pad.player_number
            port_key = f'Port{player_num}'
            port_config = cast('dict[str, object]', input_config.setdefault(port_key, {}))

            # Default to 'ControlPad' (Sega Saturn standard layout)
            peripheral_type = self.config.get(f'ymir_peripheral_p{player_num}', 'ControlPad')
            port_config['PeripheralType'] = peripheral_type
            port_config['DevicePath'] = pad.device_path

            # Generate config sections for all known peripheral types for consistency
            for peripheral_name, bind_data in _PERIPHERAL_BINDS.items():
                peripheral_config = cast('dict[str, object]', port_config.setdefault(peripheral_name, {}))
                binds_config = cast('dict[str, list[str]]', peripheral_config.setdefault('Binds', {}))

                # Start with a clean slate, then apply keyboard defaults
                binds_config.clear()
                player_keyboard_map = bind_data['keyboard_map'].get(player_num, {})
                binds_config.update({key: val.copy() for key, val in player_keyboard_map.items()})

                # ArcadeRacer default Sensitivity
                if peripheral_name == 'ArcadeRacer':
                    peripheral_config['Sensitivity'] = 0.5

                # Append the SDL gamepad maps to the keyboard maps
                for ymir_key, sdl_suffixes in bind_data['sdl_map'].items():
                    bind_list = binds_config.setdefault(ymir_key, [])
                    for sdl_suffix in sdl_suffixes:
                        bind_list.append(f'{sdl_suffix}@{pad.index}')

        # Now write the updated toml
        toml_file.write_text(toml.dumps(config))

        return Command(['/usr/bin/ymir', '-p', self.config_dir, self.rom])
