from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, SAVES
from batocera_common.vulkan import get_discrete_gpu_name, has_discrete_gpu, is_available as vulkan_is_available
from batocera_launch import Command, Controller, Emulator, HotkeysContext
from batocera_launch.paths import CONF_INIT

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch.devices.controller import Controller as ControllerType

_logger = logging.getLogger(__name__)

# PPSSPP internal "NKCodes" https://github.com/hrydgard/ppsspp/blob/master/Common/Input/KeyCodes.h

# Will later be used to convert SDL input ids
NKCODE_BUTTON_1 = 188
NKCODE_BUTTON_2 = 189
NKCODE_BUTTON_3 = 190
NKCODE_BUTTON_4 = 191
NKCODE_BUTTON_5 = 192
NKCODE_BUTTON_6 = 193
NKCODE_BUTTON_9 = 196
NKCODE_BUTTON_10 = 197
JOYSTICK_AXIS_X = 0
JOYSTICK_AXIS_Y = 1
JOYSTICK_AXIS_Z = 11
JOYSTICK_AXIS_RZ = 14
JOYSTICK_AXIS_LTRIGGER = 17
JOYSTICK_AXIS_RTRIGGER = 18
NKCODE_DPAD_UP = 19
NKCODE_DPAD_DOWN = 20
NKCODE_DPAD_LEFT = 21
NKCODE_DPAD_RIGHT = 22

# PPSSPP defined an offset for axis
AXIS_BIND_NKCODE_START = 4000

DEVICE_ID_PAD_0 = 10
# SDL2 input ids conversion table to NKCodes
# See https://hg.libsdl.org/SDL/file/e12c38730512/include/SDL_gamecontroller.h#l262
_SDL_NAME_TO_NKCODE: Final = {
    'b': NKCODE_BUTTON_2,  # A
    'a': NKCODE_BUTTON_3,  # B
    'y': NKCODE_BUTTON_4,  # X
    'x': NKCODE_BUTTON_1,  # Y
    'select': NKCODE_BUTTON_9,  # SELECT/BACK
    'start': NKCODE_BUTTON_10,  # START
    'pageup': NKCODE_BUTTON_6,  # L
    'pagedown': NKCODE_BUTTON_5,  # R
    'up': NKCODE_DPAD_UP,
    'down': NKCODE_DPAD_DOWN,
    'left': NKCODE_DPAD_LEFT,
    'right': NKCODE_DPAD_RIGHT,
}

_SDL_HAT_MAP: Final = {
    'up': NKCODE_DPAD_UP,
    'down': NKCODE_DPAD_DOWN,
    'left': NKCODE_DPAD_LEFT,
    'right': NKCODE_DPAD_RIGHT,
}

_SDL_JOY_AXIS_MAP: Final = {
    '0': JOYSTICK_AXIS_X,
    '1': JOYSTICK_AXIS_Y,
    '2': JOYSTICK_AXIS_Z,
    '3': JOYSTICK_AXIS_RZ,
    '4': JOYSTICK_AXIS_LTRIGGER,
    '5': JOYSTICK_AXIS_RTRIGGER,
}

_PPSSPP_MAPPING: Final = {
    'a': {'button': 'Circle'},
    'b': {'button': 'Cross'},
    'x': {'button': 'Triangle'},
    'y': {'button': 'Square'},
    'start': {'button': 'Start'},
    'select': {'button': 'Select'},
    'pageup': {'button': 'L'},
    'pagedown': {'button': 'R'},
    'joystick1left': {'axis': 'An.Left'},
    'joystick1up': {'axis': 'An.Up'},
    'joystick2left': {'axis': 'RightAn.Left'},
    'joystick2up': {'axis': 'RightAn.Up'},
    # The DPAD can be an axis (for gpio sticks for example) or a hat
    'up': {'hat': 'Up', 'axis': 'Up', 'button': 'Up'},
    'down': {'hat': 'Down', 'axis': 'Down', 'button': 'Down'},
    'left': {'hat': 'Left', 'axis': 'Left', 'button': 'Left'},
    'right': {'hat': 'Right', 'axis': 'Right', 'button': 'Right'},
    # Need to add pseudo inputs as PPSSPP doesn't manually invert axises, and these are not referenced in es_input.cfg
    'joystick1right': {'axis': 'An.Right'},
    'joystick1down': {'axis': 'An.Down'},
    'joystick2right': {'axis': 'RightAn.Right'},
    'joystick2down': {'axis': 'RightAn.Down'},
}


def _axis_to_code(axis_id: int, direction: int, /) -> int:
    direction = 1 if direction < 0 else 0
    return AXIS_BIND_NKCODE_START + axis_id * 2 + direction


def _option_value(config: CaseSensitiveConfigParser, section: str, option: str, value: str, /) -> str:
    if config.has_option(section, option):
        return f'{config.get(section, option)},{value}'
    return value


def _generate_controller_config(controls_ini: Path, controls_init: Path, controller: ControllerType, /) -> None:
    config = CaseSensitiveConfigParser(interpolation=None)
    config.read(controls_init)
    # As we start with the default ini file, no need to create the section
    section = 'ControlMapping'
    if not config.has_section(section):
        config.add_section(section)

    for input_ in controller.inputs.values():
        if input_.name not in _PPSSPP_MAPPING or input_.type not in _PPSSPP_MAPPING[input_.name]:
            continue

        var = _PPSSPP_MAPPING[input_.name][input_.type]
        padnum = controller.index

        if input_.type == 'button':
            pspcode = _SDL_NAME_TO_NKCODE[input_.name]
            val = f'{DEVICE_ID_PAD_0 + padnum}-{pspcode}'
            val = _option_value(config, section, var, val)
            config.set(section, var, val)

        elif input_.type == 'axis':
            nk_axis_id = _SDL_JOY_AXIS_MAP[input_.id]
            pspcode = _axis_to_code(nk_axis_id, int(input_.value))
            val = f'{DEVICE_ID_PAD_0 + padnum}-{pspcode}'
            val = _option_value(config, section, var, val)
            _logger.debug('Adding %s to %s', var, val)
            config.set(section, var, val)

            # Skip the rest if it's an axis dpad
            if input_.name in ('up', 'down', 'left', 'right'):
                continue
            # Also need to do the opposite direction manually. The input id is the same as up/left, but the
            # direction is opposite
            if input_.name == 'joystick1up':
                var = _PPSSPP_MAPPING['joystick1down'][input_.type]
            elif input_.name == 'joystick1left':
                var = _PPSSPP_MAPPING['joystick1right'][input_.type]
            elif input_.name == 'joystick2up':
                var = _PPSSPP_MAPPING['joystick2down'][input_.type]
            elif input_.name == 'joystick2left':
                var = _PPSSPP_MAPPING['joystick2right'][input_.type]

            pspcode = _axis_to_code(nk_axis_id, -int(input_.value))
            val = f'{DEVICE_ID_PAD_0 + padnum}-{pspcode}'
            val = _option_value(config, section, var, val)
            config.set(section, var, val)

        elif input_.type == 'hat' and input_.name in _SDL_HAT_MAP:
            var = _PPSSPP_MAPPING[input_.name][input_.type]
            pspcode = _SDL_HAT_MAP[input_.name]
            val = f'{DEVICE_ID_PAD_0 + padnum}-{pspcode}'
            val = _option_value(config, section, var, val)
            config.set(section, var, val)

    # hotkey controls are called via evmapy.
    # configuring specific hotkey in ppsspp is not simple without patching
    config.set(section, 'Rewind', '1-131')
    config.set(section, 'Fast-forward', '1-132')
    config.set(section, 'Save State', '1-133')
    config.set(section, 'Load State', '1-134')
    config.set(section, 'Previous Slot', '1-135')
    config.set(section, 'Next Slot', '1-136')
    config.set(section, 'Screenshot', '1-137')
    config.set(section, 'Pause', '1-139')

    controls_ini.parent.mkdir(parents=True, exist_ok=True)
    with controls_ini.open('w+') as fp:
        config.write(fp)


@cached_dataclass
class PPSSPP(Emulator):
    needs_sdl_game_controller_config = True
    sdl_game_controller_config_ignore_buttons = ('hotkey',)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ppsspp',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_F9',
                'pause': 'KEY_F9',
                'rewind': 'KEY_F1',
                'fastforward': 'KEY_F2',
                'next_slot': 'KEY_F6',
                'previous_slot': 'KEY_F5',
                'save_state': 'KEY_F3',
                'restore_state': 'KEY_F4',
            },
        }

    @property
    def needs_mouse(self) -> bool:
        # Show mouse on screen for the Config Screen
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @cached_property
    def psp_system_dir(self) -> Path:
        return self.config_dir / 'PSP' / 'SYSTEM'

    def _write_retroachievements_token(self, token: str, /) -> None:
        if token:
            retroach_file = self.psp_system_dir / 'ppsspp_retroachievements.dat'
            retroach_file.parent.mkdir(parents=True, exist_ok=True)
            retroach_file.write_text(token)

    def _write_config(self) -> None:
        config_file = self.psp_system_dir / 'ppsspp.ini'
        ini_config = CaseSensitiveConfigParser(interpolation=None)
        if config_file.exists():
            try:
                ini_config.read(config_file, encoding='utf_8_sig')
            except Exception:
                _logger.warning('Failed to read existing ppsspp.ini, starting fresh', exc_info=True)

        ## [GRAPHICS]
        if not ini_config.has_section('Graphics'):
            ini_config.add_section('Graphics')

        # Graphics Backend
        gfxbackend = self.config.get_str('gfxbackend', 'OPENGL')
        ini_config.set('Graphics', 'GraphicsBackend', gfxbackend)
        # If Vulkan
        if gfxbackend == 'VULKAN':
            # Check if we have a discrete GPU & if so, set the Name
            if vulkan_is_available():
                _logger.debug('Vulkan driver is available on the system.')
                if has_discrete_gpu():
                    _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                    discrete_name = get_discrete_gpu_name()
                    if discrete_name:
                        _logger.debug('Using Discrete GPU Name: %s for PPSSPP', discrete_name)
                        ini_config.set('Graphics', 'VulkanDevice', discrete_name)
                    else:
                        _logger.debug("Couldn't get discrete GPU Name")
                else:
                    _logger.debug('Discrete GPU is not available on the system. Using default.')
            else:
                _logger.debug('Vulkan driver is not available on the system. Falling back to OpenGL')
                ini_config.set('Graphics', 'GraphicsBackend', 'OPENGL')

        # Resolution
        ini_config.set('Graphics', 'InternalResolution', self.config.get_str('internal_resolution', '1'))

        # Software rendering (always false)
        ini_config.set('Graphics', 'SoftwareRenderer', 'False')

        # Always fullscreen
        ini_config.set('Graphics', 'FullScreen', 'True')

        # VSync
        ini_config.set('Graphics', 'VerticalSync', str(self.config.get_bool('vsync', False)))

        # Frame skipping
        ini_config.set('Graphics', 'FrameSkip', self.config.get_str('frameskip', '0'))

        # Auto frameskip
        ini_config.set('Graphics', 'AutoFrameSkip', str(self.config.get_bool('autoframeskip', False)))

        # Skip Buffer Effects
        ini_config.set('Graphics', 'SkipBufferEffects', str(self.config.get_bool('skip_buffer_effects', False)))

        # Disable Culling
        ini_config.set('Graphics', 'DisableRangeCulling', str(self.config.get_bool('disable_culling', False)))

        # Skip GPU Readbacks
        ini_config.set('Graphics', 'SkipGPUReadbackMode', self.config.get_str('skip_gpu_readbacks', '0'))

        # Lazy texture caching
        ini_config.set('Graphics', 'TextureBackoffCache', str(self.config.get_bool('lazy_texture_caching', False)))

        # Spline / Bezier curves quality
        ini_config.set('Graphics', 'SplineBezierQuality', self.config.get_str('curves_quality', '2'))

        # Duplicate Frames
        ini_config.set('Graphics', 'RenderDuplicateFrames', str(self.config.get_bool('duplicate_frames', False)))

        # Buffer Graphics Commands
        ini_config.set('Graphics', 'InflightFrames', self.config.get_str('buffer_graphics', '3'))

        # Hardware transform - always true
        ini_config.set('Graphics', 'HardwareTransform', 'True')

        # Software skinning
        ini_config.set('Graphics', 'SoftwareSkinning', str(self.config.get_bool('software_skinning', True)))

        # Hardware Tessellation
        ini_config.set('Graphics', 'HardwareTessellation', str(self.config.get_bool('hardware_tessellation', False)))

        # Texture Scaling Type
        ini_config.set('Graphics', 'TexScalingType', self.config.get_str('texture_scaling_type', '0'))

        # Texture Scaling Level
        ini_config.set('Graphics', 'TexScalingLevel', self.config.get_str('texture_scaling_level', '1'))

        # Texture Deposterize
        ini_config.set('Graphics', 'TexDeposterize', str(self.config.get_bool('texture_deposterize', False)))

        # Anisotropic Filtering
        ini_config.set('Graphics', 'AnisotropyLevel', self.config.get_str('anisotropic_filtering', '4'))

        # Texture Filtering
        ini_config.set('Graphics', 'TextureFiltering', self.config.get_str('texture_filtering', '1'))

        # Smart 2D texture filtering
        ini_config.set('Graphics', 'Smart2DTexFiltering', str(self.config.get_bool('smart_2d', False)))

        # Display FPS/Speed status flags (bitmask: FPS_COUNTER=2, SPEED_COUNTER=4, BATTERY_PERCENT=8)
        ini_config.set('Graphics', 'iShowStatusFlags', '6' if self.config.show_fps else '0')

        # Set other defaults
        ini_config.set('Graphics', 'DisplayIntegerScale', 'False')

        ## [SYSTEM PARAM]
        if not ini_config.has_section('SystemParam'):
            ini_config.add_section('SystemParam')

        # Forcing Nickname to Batocera or User name
        username = 'Batocera'
        if self.config.get_bool('retroachievements') and (
            config_username := self.config.get('retroachievements.username')
        ):
            username = config_username
        ini_config.set('SystemParam', 'NickName', username)
        # Disable Encrypt Save (permit to exchange save with different machines)
        ini_config.set('SystemParam', 'EncryptSave', 'False')

        # Set 32GB memstick size
        ini_config.set('SystemParam', 'MemStickSize', '32')

        ## [GENERAL]
        if not ini_config.has_section('General'):
            ini_config.add_section('General')

        # First run, false
        ini_config.set('General', 'FirstRun', 'False')

        # Rewinding (interval is now expressed in seconds upstream, not frames)
        ini_config.set('General', 'RewindSnapshotInterval', self.config.get_bool('rewind', return_values=('5', '0')))
        # Cheats
        ini_config.set('General', 'EnableCheats', str(self.config.get_bool('enable_cheats', False)))
        # Don't check for a new version
        ini_config.set('General', 'CheckForNewVersion', 'False')

        # SaveState
        ini_config.set('General', 'StateSlot', self.config.get_str('state_slot', '0'))

        ## [UPGRADE] - don't upgrade
        if not ini_config.has_section('Upgrade'):
            ini_config.add_section('Upgrade')
        ini_config.set('Upgrade', 'UpgradeMessage', '')
        ini_config.set('Upgrade', 'UpgradeVersion', '')
        ini_config.set('Upgrade', 'DismissedVersion', '')

        ## [RetroAchievements]
        if not ini_config.has_section('Achievements'):
            ini_config.add_section('Achievements')

        if self.config.get_bool('retroachievements'):
            ini_config.set(
                'Achievements', 'AchievementsUserName', self.config.get_str('retroachievements.username', '')
            )
            ini_config.set(
                'Achievements',
                'AchievementsChallengeMode',
                str(self.config.get_bool('retroachievements.hardcore', False)),
            )
            ini_config.set(
                'Achievements', 'AchievementsEncoreMode', str(self.config.get_bool('retroachievements.encore', False))
            )
            ini_config.set(
                'Achievements',
                'AchievementsUnofficial',
                str(self.config.get_bool('retroachievements.unofficial', False)),
            )
            ini_config.set('Achievements', 'AchievementsSoundEffects', 'True')
            ini_config.set('Achievements', 'AchievementsEnable', 'True')
            self._write_retroachievements_token(self.config.get_str('retroachievements.token', ''))
        else:
            ini_config.set('Achievements', 'AchievementsEnable', 'False')
            ini_config.set('Achievements', 'AchievementsChallengeMode', 'False')

        ## [NETWORK]
        if not ini_config.has_section('Network'):
            ini_config.add_section('Network')

        network_enable = self.config.get_bool('network_enable', False)
        ini_config.set('Network', 'EnableWlan', str(network_enable))

        if network_enable:
            lan_adhoc_mode = self.config.get_str('lan_adhoc_mode', 'off')
            port_offset = self.config.get_str('adhoc_port_offset', '10000')

            # LAN host mode
            ini_config.set('Network', 'EnableAdhocServer', str(lan_adhoc_mode == 'host'))

            # proAdhocServer is always controlled by the ADHOC SERVER choice
            adhoc_server = self.config.get_str('adhoc_server', '')
            if adhoc_server and adhoc_server != '__manual__':
                ini_config.set('Network', 'proAdhocServer', adhoc_server)

            # Common settings
            ini_config.set('Network', 'PortOffset', port_offset)
            ini_config.set('Network', 'EnableUPnP', str(self.config.get_bool('upnp_enable', False)))

            # Relay-specific settings (only when not in LAN host mode)
            if lan_adhoc_mode == 'off':
                ini_config.set('Network', 'AdhocServerRelayMode', self.config.get_str('adhoc_relay_mode', '0'))
                ini_config.set(
                    'Network', 'ForcedFirstConnect', str(self.config.get_bool('adhoc_forced_connect', False))
                )

                # Infrastructure DNS
                if not ini_config.has_option('Network', 'PrimaryDNSServer'):
                    ini_config.set('Network', 'PrimaryDNSServer', '67.222.156.250')
                infra_auto_dns = self.config.get_str('infra_auto_dns', 'auto')
                ini_config.set('Network', 'InfrastructureAutoDNS', 'False' if infra_auto_dns == 'manual' else 'True')

        # Custom : allow the user to configure directly PPSSPP via batocera.conf via lines like : ppsspp.section.option=value
        for section_option, user_config_value in self.config.items(starts_with='ppsspp.'):
            custom_section, _, custom_option = section_option.partition('.')
            if not ini_config.has_section(custom_section):
                ini_config.add_section(custom_section)
            ini_config.set(custom_section, custom_option, str(user_config_value))

        config_file.parent.mkdir(parents=True, exist_ok=True)
        with config_file.open('w') as fp:
            ini_config.write(fp)

    async def configure(self) -> Command:
        self._write_config()

        # Remove the old gamecontrollerdb.txt file
        dbpath = self.config_dir / 'gamecontrollerdb.txt'
        if dbpath.exists():
            dbpath.unlink()

        # Generate the controls.ini
        if controller := Controller.find_player_number(self.controllers, 1):
            controls_ini = self.psp_system_dir / 'controls.ini'
            controls_init = CONF_INIT / 'ppsspp' / 'PSP' / 'SYSTEM' / 'controls.ini'
            _generate_controller_config(controls_ini, controls_init, controller)

        # The command to run
        args: list[str | Path] = ['/usr/bin/PPSSPP', self.rom, '--fullscreen']

        # Adapt the menu size to low definition
        # I've played with this option on PC to fix menu size in Hi-Resolution and it not working fine.
        # I'm almost sure this option break the emulator (Darknior)
        if self.resolution.width <= 480 or self.resolution.height <= 480:
            args.extend(['--dpi', '0.5'])

        # state_slot option
        if state_filename := self.config.state_filename:
            args.append(f'--state={state_filename}')

        return Command(
            args,
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
            },
        )
