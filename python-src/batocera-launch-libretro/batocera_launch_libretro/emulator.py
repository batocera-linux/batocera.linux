from __future__ import annotations

import logging
import shutil
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common import vulkan
from batocera_common.asyncio import is_connected_to_internet
from batocera_common.paths import CONFIGS, OVERLAYS
from batocera_launch import (
    BezelInfo,
    Command,
    Controller,
    Emulator,
    HotkeysContext,
    Input,
    MissingCore,
    SpecialDecorationsMixin,
    cached_dataclass,
    cached_property,
)
from batocera_launch.devices.video import get_gl_info, supports_system_rotation
from batocera_launch.draw.gun_borders import create_gun_border_image
from batocera_launch.draw.pil import add_qr_code, add_tattoo_image, create_transparent_image, get_image_size, pad_image
from batocera_launch.paths import BATOCERA_SHADERS, DEFAULTS_DIR, ES_GAMES_METADATA, USER_SHADERS

from .config import LibretroConfig
from .load import load_core

if TYPE_CHECKING:
    from .core import Core

_logger = logging.getLogger(__name__)

_RETROARCH_BIN: Final = Path('/usr/bin/retroarch')
_RETROARCH_CORES_DIR: Final = Path('/usr/lib/libretro')
_RETROARCH_SHARE_DIR: Final = Path('/usr/share/libretro')

# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L188
_RATIOS: Final = [
    '4/3',
    '16/9',
    '16/10',
    '16/15',
    '21/9',
    '1/1',
    '2/1',
    '3/2',
    '3/4',
    '4/1',
    '9/16',
    '5/4',
    '6/5',
    '7/9',
    '8/3',
    '8/7',
    '19/12',
    '19/14',
    '30/17',
    '32/9',
    'config',
    'squarepixel',
    'core',
    'custom',
    'full',
]

# Map an emulationstation joystick to the corresponding retroarch
_JOYSTICK_MAPPINGS: Final = {'joystick1up': 'l_y', 'joystick1left': 'l_x', 'joystick2up': 'r_y', 'joystick2left': 'r_x'}

# Map an emulationstation input type to the corresponding retroarch type
_TYPE_TO_NAME: Final = {'button': 'btn', 'hat': 'btn', 'axis': 'axis', 'key': 'key'}

# Map an emulationstation input hat to the corresponding retroarch hat value
_HATS_TO_NAME: Final = {'1': 'up', '2': 'right', '4': 'down', '8': 'left'}

_PEDAL_TO_KEY: Final = {1: 'c', 2: 'v', 3: 'b', 4: 'n'}


# Returns the value to write in retroarch config file, depending on the type
def _get_input_value(input: Input, /) -> str | None:
    match input.type:
        case 'button' | 'key':
            return input.id
        case 'axis':
            if input.value == '-1':
                return f'-{input.id}'

            return f'+{input.id}'
        case 'hat':
            return f'h{input.id}{_HATS_TO_NAME[input.value]}'
        case _:
            return None


_GUN_BORDER_PRESETS: Final = {
    'thin': (1, 0),
    'medium': (2, 0),
    'big': (2, 1),
}


def _gun_border_pixels(width: int, borders_size: str, /) -> int:
    inner, outer = _GUN_BORDER_PRESETS.get(borders_size, (0, 0))
    return (width * (inner + outer)) // 100


def _write_overlay_config(overlay_config_path: Path, overlay_png_file: Path, /) -> None:
    overlay_config_path.write_text(
        f'overlays = 1\noverlay0_overlay = "{overlay_png_file}"\noverlay0_full_screen = true\noverlay0_descs = 0\n'
    )


@cached_dataclass
class Libretro(SpecialDecorationsMixin, Emulator):
    core_object: Core = field(init=False)

    def __post_init__(self) -> None:
        # Fix for the removed MESS/MAMEVirtual cores
        if self.config.core in {'mess', 'mamevirtual'}:
            self.config['core'] = 'mame'

        self.core_object = load_core(self)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        # f12 for coin : set in libretroMameConfig.py, others in libretroControllers.py
        return {
            'name': 'retroarch',
            'keys': {
                'exit': ['KEY_LEFTSHIFT', 'KEY_ESC'],
                'menu': ['KEY_LEFTSHIFT', 'KEY_F1'],
                'pause': ['KEY_LEFTSHIFT', 'KEY_P'],
                'coin': 'KEY_F12',
                'save_state': ['KEY_LEFTSHIFT', 'KEY_F3'],
                'restore_state': ['KEY_LEFTSHIFT', 'KEY_F4'],
                'previous_slot': ['KEY_LEFTSHIFT', 'KEY_F6'],
                'next_slot': ['KEY_LEFTSHIFT', 'KEY_F5'],
                'rewind': ['KEY_LEFTSHIFT', 'KEY_F11'],
                'fastforward': ['KEY_LEFTSHIFT', 'KEY_F12'],
                'reset': ['KEY_LEFTSHIFT', 'KEY_F10'],
                'translation': ['KEY_LEFTSHIFT', 'KEY_F9'],
            },
        }

    @cached_property
    def bezel(self) -> str | None:
        bezel = self.config.get_str('bezel') or None

        if bezel == 'none' or self.config.get_bool('forceNoBezel') or self.core_object.disables_bezel:
            return None

        if ratio := self.config.get_str('ratio'):
            if ratio == 'full':
                return None

            # Check if game natively supports widescreen from metadata (not widescreen hack)
            if self.config.get_bool(f'{self.core}-autowidescreen'):
                metadata = self.get_games_metadata(ES_GAMES_METADATA)
                if metadata.get('video_widescreen') == 'true':
                    return None

            # Independently check if the ratio is numerically widescreen to disable bezels.
            # This handles cases like "16/9", "16/10", etc., where bezels are not wanted.
            try:
                if '/' in ratio:
                    numerator, denominator = map(float, ratio.split('/'))
                    if denominator != 0 and (numerator / denominator) > (4 / 3):
                        _logger.debug(
                            'Bezel set to none for widescreen ratio. Ratio %s:%s selected',
                            int(numerator),
                            int(denominator),
                        )
                        return None
            except ValueError:
                pass

        return bezel

    @property
    def handles_bezels(self) -> bool:
        return True

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'retroarch'

    @cached_property
    def custom_config_path(self) -> Path:
        return self.config_dir / 'retroarchcustom.cfg'

    @cached_property
    def core_options_path(self) -> Path:
        return self.config_dir / 'cores' / 'retroarch-core-options.cfg'

    @cached_property
    def overlay_config_path(self) -> Path:
        return self.config_dir / 'overlay.cfg'

    async def configure(self) -> Command:
        gfx_backend = await self.get_gfx_backend()

        game_shader: str | None = None
        shader_bezel = False
        video_shader: Path | None = None

        if self.decoration_id == '0':
            if 'shader' in self.render_config:
                game_shader = self.render_config.get('shader')
        else:
            if f'shader_{self.decoration_id}' in self.render_config:
                game_shader = self.render_config.get(f'shader_{self.decoration_id}')
            elif 'shader' in self.render_config:
                game_shader = self.render_config.get('shader')

        if 'shader' in self.render_config and game_shader is None:
            shader_filename = f'{game_shader}.{
                "slangp"
                if (gfx_backend == "glcore" or gfx_backend == "vulkan") or self.core_object.force_slang_shaders
                else "glslp"
            }'

            _logger.debug('searching shader %s', shader_filename)

            if (USER_SHADERS / shader_filename).exists():
                _logger.debug('shader %s found in %s', shader_filename, USER_SHADERS)
                video_shader_dir = USER_SHADERS
            else:
                video_shader_dir = BATOCERA_SHADERS

            video_shader = video_shader_dir / shader_filename

            # If the shader filename contains noBezel, activate Shader Bezel mode.
            if 'noBezel' in video_shader.name:
                shader_bezel = True

        config_file = self.config.get_str('configfile')

        if config_file is None:
            # Use the batocera config file if no user defined file
            config_file = str(self.custom_config_path)

            custom_config = self.get_custom_config()
            core_options = self.get_core_options()

            self.set_controllers_config(custom_config)
            self.set_paths_config(custom_config)
            self.core_object.generate_special_configs()
            await self.set_config(custom_config, gfx_backend, shader_bezel)
            self.set_guns_config(custom_config, core_options)

            # write core_options a bit late while guns configs can modify it
            core_options.write()

            try:
                self.write_bezel_config(custom_config, shader_bezel, self.bezel)
            except Exception as e:
                # error with bezels, disabling them
                self.write_bezel_config(custom_config, shader_bezel, None)
                _logger.error('Error with bezel %s: %s', self.bezel, e, exc_info=e, stack_info=True)

            # allow the user to configure directly retroarch.cfg via batocera.conf
            # with lines like `snes.retroarch.menu_driver=rgui`
            for key, value in self.config.items(starts_with='retroarch.'):
                custom_config.set(key, value)

            custom_config.write()

            # duplicate config to mapping files while ra now split in 2 parts
            remap_config_dir = self.config_dir / 'config' / 'remaps' / 'common'
            remap_config_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.custom_config_path, remap_config_dir / 'common.rmp')

        # for each core, a file /usr/lib/<core>.info must exit, otherwise, info such as rewinding/netplay will not work
        # to do a global check : cd /usr/lib/libretro && for i in *.so; do INF=$(echo $i | sed -e s+/usr/lib/libretro+/usr/share/libretro/info+ -e s+\.so+.info+); test -e "$INF" || echo $i; done
        if not (_RETROARCH_SHARE_DIR / 'info' / f'{self.core}_libretro.info').exists():
            raise MissingCore

        args: list[str | Path] = [
            _RETROARCH_BIN,
            '-L',
            # Retroarch core on the filesystem
            _RETROARCH_CORES_DIR / f'{self.core_object.library_prefix}_libretro.so',
            '--config',
            config_file,
        ]

        if (core_arguments := self.core_object.get_command_arguments()) is not None:
            args.extend(core_arguments)

        # RetroArch 1.7.8 (Batocera 5.24) now requires the shaders to be passed as command line argument
        if video_shader is not None:
            args.extend(['--set-shader', video_shader])

        # Custom configs
        configs_to_append: list[Path] = [
            config
            for config in [
                # per system
                self.config_dir / f'{self.system}.cfg',
                # per rom
                self.config_dir / self.system / f'{self.rom.source.name}.cfg',
                self.config_dir / self.system / f'{self.rom.id}.cfg',
                # overlay management
                OVERLAYS / self.system / f'{self.rom.source.name}.cfg',
                OVERLAYS / self.system / f'{self.rom.id}.cfg',
            ]
            if config.is_file()
        ]

        if configs_to_append:
            args.extend(['--appendconfig', '|'.join(str(config) for config in configs_to_append)])

        # Netplay mode
        if netplay_mode := self.config.get('netplay.mode'):
            if netplay_mode == 'host':
                args.append('--host')
            elif netplay_mode == 'client' or netplay_mode == 'spectator':
                args.extend(['--connect', self.config['netplay.server.ip']])
            if 'netplay.server.port' in self.config:
                args.extend(['--port', self.config['netplay.server.port']])
            if 'netplay.server.session' in self.config:
                args.extend(['--mitm-session', self.config['netplay.server.session']])
            if 'netplay.nickname' in self.config:
                args.extend(['--nick', self.config['netplay.nickname']])

        # Verbose logs
        args.extend(['--verbose'])

        if (rom_argument := self.core_object.rom_argument) is not None:
            args.append(rom_argument)

        if (state_slot := self.config.get_str('state_slot')) and not self.config.get(
            'state_filename', '.auto'
        ).endswith('.auto'):
            # if the file ends by .auto, this is the auto loading, else it is the states
            # retroarch need the file be named with .entry at the end to load the state
            # a link would work, but on fat32, we need to copy
            args.extend(['-e', state_slot])

        return Command(args, {'XDG_CONFIG_HOME': CONFIGS})

    async def get_gfx_backend(self) -> str:
        # Start with the selected option
        # Pick glcore or gl based on drivers if not selected
        backend = self.config.get('gfxbackend')

        if backend:
            set_manually = True
        else:
            set_manually = False
            gl_info = await get_gl_info()
            # glvendor check first, to avoid a 2nd testing on intel boards
            if gl_info.vendor in {'nvidia', 'amd'} and gl_info.version >= 3.1:
                backend = 'glcore'
            else:
                backend = 'gl'

        # Retroarch has flipped between using opengl or gl, correct the setting here if needed.
        if backend == 'opengl':
            backend = 'gl'

        if (forced_backend := self.core_object.force_gfx_backend(backend)) is not None:
            # Force the backend if the core requires it, regardless of manual selection
            backend = forced_backend
        elif (
            not set_manually
            and (override_backend := self.core_object.override_default_gfx_backend(backend)) is not None
        ):
            # Override the backend if the core requires it, but only if not set manually
            backend = override_backend

        return backend

    def get_custom_config(self) -> LibretroConfig:
        custom_config = LibretroConfig(self.config, self.custom_config_path)

        if not self.custom_config_path.is_file():
            self.custom_config_path.parent.mkdir(parents=True, exist_ok=True)

            # Use Interface
            custom_config.set('menu_driver', 'ozone')
            custom_config.set('content_show_favorites', False)
            custom_config.set('content_show_images', False)
            custom_config.set('content_show_music', False)
            custom_config.set('content_show_video', False)
            custom_config.set('content_show_history', False)
            custom_config.set('content_show_playlists', False)
            custom_config.set('content_show_add', False)
            custom_config.set('menu_show_load_core', False)
            custom_config.set('menu_show_load_content', False)
            custom_config.set('menu_show_online_updater', False)
            custom_config.set('menu_show_core_updater', False)

            # Input
            custom_config.set('input_autodetect_enable', False)
            custom_config.set('input_joypad_driver', 'sdl2')
            custom_config.set('input_player1_analog_dpad_mode', 1)
            custom_config.set('input_player2_analog_dpad_mode', 1)
            custom_config.set('input_player3_analog_dpad_mode', 1)
            custom_config.set('input_player4_analog_dpad_mode', 1)
            custom_config.set('input_enable_hotkey_btn', 'nul')
            custom_config.set('input_enable_hotkey', 'shift')
            custom_config.set('input_menu_toggle', 'f1')
            custom_config.set('input_exit_emulator', 'escape')

            # Video
            custom_config.set('video_aspect_ratio_auto', False)
            custom_config.set('video_gpu_screenshot', True)
            custom_config.set('video_shader_enable', False)
            custom_config.set('aspect_ratio_index', 22)

            # Audio
            custom_config.set('audio_volume', 2.0)

            # Settings
            custom_config.set('global_core_options', True)
            custom_config.set('config_save_on_exit', False)
            custom_config.set('savestate_auto_save', False)
            custom_config.set('savestate_auto_load', False)
            custom_config.set('menu_swap_ok_cancel_buttons', True)

            # Accentuation
            custom_config.set('rgui_extended_ascii', True)

            # Hide the welcome message in Retroarch
            custom_config.set('rgui_show_start_screen', False)

            # Enable usage of OSD messages (Text messages not in badge)
            custom_config.set('video_font_enable', True)

            # Take a screenshot of the savestate
            custom_config.set('savestate_thumbnail_enable', True)

            # Allow any RetroPad to control the menu (Only the player 1)
            custom_config.set('all_users_control_menu', False)

            # Show badges in Retroarch cheevos list
            custom_config.set('cheevos_badges_enable', True)

            # Disable builtin image viewer (done in ES, and prevents from loading pico-8 .png carts)
            custom_config.set('builtin_imageviewer_enable', False)

            # Set fps counter interval (in frames)
            custom_config.set('fps_update_interval', 30)

        return custom_config

    def set_controllers_config(self, custom_config: LibretroConfig) -> None:
        # Remove all controller configurations
        for suffix in [
            'player',
            'state_slot_increase',
            'load_state',
            'save_state',
            'state_slot_decrease',
            'reset',
            'exit_emulator',
            'rewind',
            'hold_fast_forward',
            'toggle_fast_forward',
            'screenshot',
            'disk_prev',
            'disk_next',
            'disk_eject_toggle',
            'shader_prev',
            'shader_next',
            'ai_service',
            'menu_toggle',
        ]:
            custom_config.remove_all_starting_with(f'input_{suffix}')

        # hotkeys, forced to match with the hotkeys system
        custom_config.set('input_enable_hotkey', 'shift')
        custom_config.set('input_menu_toggle', 'f1')
        custom_config.set('input_fps_toggle', 'f2')
        custom_config.set('input_exit_emulator', 'escape')
        custom_config.set('input_pause_toggle', 'p')
        custom_config.set('input_save_state', 'f3')
        custom_config.set('input_load_state', 'f4')
        custom_config.set('input_state_slot_decrease', 'f5')
        custom_config.set('input_state_slot_increase', 'f6')
        custom_config.set('input_ai_service', 'f9')
        custom_config.set('input_reset', 'f10')
        custom_config.set('input_rewind', 'f11')

        # See if FF is toggle or hold
        ff_action = 'toggle_fast_forward' if self.config.get_bool('toggle_fast_forward') else 'hold_fast_forward'

        custom_config.set(f'input_{ff_action}', 'f12')
        custom_config.set('input_screenshot', 'nul')
        custom_config.set('input_audio_mute', 'nul')
        custom_config.set('input_grab_mouse_toggle', 'nul')

        for controller in self.controllers:
            self.set_controller_config(custom_config, controller)

        # Write the hotkey for player 1
        if (
            self.controllers
            and 'hotkey' in self.controllers[0].inputs
            and self.controllers[0].inputs['hotkey'].type == 'button'
        ):
            custom_config.set('input_enable_hotkey_btn', self.controllers[0].inputs['hotkey'].id)

    def set_controller_config(self, custom_config: LibretroConfig, controller: Controller, /) -> None:
        # Map an emulationstation button name to the corresponding retroarch name
        button_mappings = {
            'a': 'a',
            'b': 'b',
            'x': 'x',
            'y': 'y',
            'pageup': 'l',
            'pagedown': 'r',
            'l2': 'l2',
            'r2': 'r2',
            'l3': 'l3',
            'r3': 'r3',
            'start': 'start',
            'select': 'select',
        }

        # X Y L1 L2  ---> X Y R1 L1
        # A B R1 R2  ---> A B R2 L2
        if self.config.get('altlayout') == 'fightstick':
            button_mappings['pageup'] = 'l2'
            button_mappings['pagedown'] = 'l'
            button_mappings['l2'] = 'r2'
            button_mappings['r2'] = 'r'

        gun_button_mappings = {
            'a': 'aux_a',
            'b': 'aux_b',
            'y': 'aux_c',
            'pageup': 'offscreen_shot',
            'pagedown': 'trigger',
            'start': 'start',
            'select': 'select',
        }

        self.core_object.set_button_mappings(controller, button_mappings)

        for btnkey, btnvalue in button_mappings.items():
            if input := controller.inputs.get(btnkey):
                custom_config.set(f'input_player{controller.player_number}_{btnvalue}', _get_input_value(input))
                custom_config.set(
                    f'input_player{controller.player_number}_{btnvalue}_{_TYPE_TO_NAME[input.type]}',
                    _get_input_value(input),
                )

        if self.core_object.map_lightguns:
            # Gun Mapping
            for btnkey, btnvalue in gun_button_mappings:
                if input := controller.inputs.get(btnkey):
                    custom_config.set(
                        f'input_player{controller.player_number}_gun_{btnvalue}_{_TYPE_TO_NAME[input.type]}',
                        _get_input_value(input),
                    )

        for direction in ('up', 'down', 'left', 'right'):
            if input := controller.inputs.get(direction):
                custom_config.set(
                    f'input_player{controller.player_number}_{direction}_{_TYPE_TO_NAME[input.type]}',
                    _get_input_value(input),
                )

                if self.core_object.map_lightguns:
                    # Gun Mapping
                    custom_config.set(
                        f'input_player{controller.player_number}_gun_dpad_{direction}_{_TYPE_TO_NAME[input.type]}',
                        _get_input_value(input),
                    )

        for jskey, jsvalue in _JOYSTICK_MAPPINGS.items():
            if input := controller.inputs.get(jskey):
                if input.value == '-1':
                    custom_config.set(
                        f'input_player{controller.player_number}_{jsvalue}_minus_axis',
                        f'-{input.id}',
                    )
                    custom_config.set(
                        f'input_player{controller.player_number}_{jsvalue}_plus_axis',
                        f'+{input.id}',
                    )
                else:
                    custom_config.set(
                        f'input_player{controller.player_number}_{jsvalue}_minus_axis',
                        f'+{input.id}',
                    )
                    custom_config.set(
                        f'input_player{controller.player_number}_{jsvalue}_plus_axis',
                        f'-{input.id}',
                    )

        if not self.core_object.map_lightguns:
            # dont touch to it when there are connected lightguns
            custom_config.set(
                f'input_player{controller.player_number}_mouse_index', self.core_object.get_mouse_index(controller)
            )

        custom_config.set(f'input_player{controller.player_number}_joypad_index', controller.index)
        custom_config.set(
            f'input_player{controller.player_number}_analog_dpad_mode', self.core_object.get_analog_mode(controller)
        )

    def set_paths_config(self, custom_config: LibretroConfig, /) -> None:
        # Path Retroarch
        custom_config.set('core_options_path', '/userdata/system/configs/retroarch/cores/retroarch-core-options.cfg')
        custom_config.set('assets_directory', '/usr/share/libretro/assets')
        custom_config.set('screenshot_directory', '/userdata/screenshots/')
        custom_config.set('recording_output_directory', '/userdata/screenshots/')
        custom_config.set('savestate_directory', '/userdata/saves/')
        custom_config.set('savefile_directory', '/userdata/saves/')
        custom_config.set('extraction_directory', '/userdata/extractions/')
        custom_config.set('cheat_database_path', '/userdata/cheats/cht/')
        custom_config.set('cheat_settings_path', '/userdata/cheats/saves/')
        custom_config.set('system_directory', '/userdata/bios/')
        custom_config.set('joypad_autoconfig_dir', '/userdata/system/configs/retroarch/inputs/')
        custom_config.set('video_shader_dir', '/usr/share/batocera/shaders/')
        custom_config.set('video_font_path', '/usr/share/fonts/dejavu/DejaVuSansMono.ttf')
        custom_config.set('video_filter_dir', '/usr/share/video_filters')
        custom_config.set('audio_filter_dir', '/usr/share/audio_filters')

    def get_core_options(self) -> LibretroConfig:
        self.core_options_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            core_options = LibretroConfig(self.config, self.core_options_path)
        except UnicodeError:
            # invalid retroarch-core-options.cfg
            # remove it and try again
            self.core_options_path.unlink()
            core_options = LibretroConfig(self.config, self.core_options_path)

        self.core_object.set_core_options(core_options)
        # Custom : Allow the user to configure directly retroarchcore.cfg via batocera.conf via lines like : snes.retroarchcore.opt=val
        for user_config, value in self.config.items(starts_with='retroarchcore.'):
            core_options.set(user_config, value)

        return core_options

    async def set_config(self, custom_config: LibretroConfig, gfx_backend: str, shader_bezel: bool, /) -> None:
        # Basic configuration

        # not aligned behavior on other emus
        custom_config.set('quit_press_twice', False)

        # this option messes everything up on Batocera if ever clicked
        custom_config.set('menu_show_restart_retroarch', False)

        # hide popup when starting a game
        custom_config.set('menu_show_load_content_animation', False)

        # Set the correct value to match ES confirm /cancel inputs
        custom_config.set('menu_swap_ok_cancel_buttons', not self.es_settings.get_bool('InvertButtons'))

        custom_config.set('video_viewport_bias_x', '0.500000')
        custom_config.set('video_viewport_bias_y', '0.500000')

        # needed for the ozone menu
        custom_config.set('video_driver', gfx_backend)
        # Set Vulkan
        if self.config.get('gfxbackend') == 'vulkan' and vulkan.is_available():
            _logger.debug('Vulkan driver is available on the system.')
            if vulkan.has_discrete_gpu():
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                discrete_index = vulkan.get_discrete_gpu_index()
                if discrete_index:
                    _logger.debug('Using Discrete GPU Index: %s for RetroArch', discrete_index)
                    custom_config.set('vulkan_gpu_index', discrete_index)
                else:
                    _logger.debug("Couldn't get discrete GPU index")
            else:
                _logger.debug('Discrete GPU is not available on the system. Using default.')

        custom_config.set('audio_driver', self.config.get('audio_driver', 'pulse'))
        # 64 = best balance with audio perf
        custom_config.set('audio_latency', self.config.get('audio_latency', 64))
        custom_config.set('audio_volume', self.config.get('audio_volume', 0))

        display_rotate = self.config.get_str('display.rotate')
        video_rotation = 0

        if display_rotate and not await supports_system_rotation():
            # only for systems that don't support global rotation (xorg, wayland, ...)
            # 0 => 0 ; 1 => 270; 2 => 180 ; 3 => 90
            if display_rotate == '1':
                video_rotation = 3
            elif display_rotate == '2':
                video_rotation = 2
            elif display_rotate == '3':
                video_rotation = 1

        custom_config.set('video_rotation', video_rotation)
        custom_config.set_bool_from_config('video_threaded')
        custom_config.set_bool_from_config('video_allow_rotate', default=True)

        # variable refresh rate
        custom_config.set_bool_from_config('vrr_runloop_enable')

        # required at least for vulkan (to get the correct resolution)
        custom_config.set('video_fullscreen_x', self.resolution.width)
        custom_config.set('video_fullscreen_y', self.resolution.height)

        # don't use anymore this value while it doesn't allow the shaders to work
        custom_config.set('video_black_frame_insertion', False)
        # required at least on x86 x86_64 otherwise, the game is paused at launch
        custom_config.set('pause_nonactive', False)

        cache_dir = self.config_dir / 'cache'
        cache_dir.mkdir(parents=True, exist_ok=True)

        custom_config.set('cache_directory', cache_dir)

        # require for core informations
        custom_config.set('libretro_directory', '/usr/lib/libretro')
        custom_config.set('libretro_info_path', '/usr/share/libretro/info')

        custom_config.set('video_fullscreen', True)  # Fullscreen is required at least for x86* and odroidn2

        custom_config.set('sort_savefiles_enable', False)  # ensure we don't save system.name + core
        custom_config.set('sort_savestates_enable', False)  # ensure we don't save system.name + core
        custom_config.set('savestate_directory', self.saves_dir)
        custom_config.set('savefile_directory', self.saves_dir)

        # Disable internal image viewer (ES does it, and pico-8 won't load .p8.png)
        custom_config.set('builtin_imageviewer_enable', False)

        # Input configuration
        custom_config.set('input_joypad_driver', 'udev')
        custom_config.set('input_driver', 'udev')  # driver for mouse/keyboard. udev required for guns.
        custom_config.set('input_max_users', 16)  # Allow up to 16 players

        custom_config.set('input_libretro_device_p1', 1)  # Default devices choices
        custom_config.set('input_libretro_device_p2', 1)

        # force notification messages, but not the "remap" one
        custom_config.set('video_font_enable', True)
        custom_config.set('notification_show_remap_load', False)

        language = self.config.get_str('retroarch.user_language', self.config.get_str('system.language'))
        # RETRO_LANGUAGE_JAPANESE = 1
        if language == '1' or language == 'ja_JP':
            custom_config.set('video_font_path', '/usr/share/fonts/truetype/noto/NotoSansJP-VF.ttf')
        # RETRO_LANGUAGE_KOREAN = 10
        elif language == '10' or language == 'ko_KR':
            custom_config.set('video_font_path', '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf')
        # RETRO_LANGUAGE_CHINESE_TRADITIONAL = 11
        elif language == '11' or language == 'zh_TW':
            custom_config.set('video_font_path', '/usr/share/fonts/truetype/noto/NotoSansTC-VF.ttf')
        # RETRO_LANGUAGE_CHINESE_SIMPLIFIED = 12
        elif language == '12' or language == 'zh_CN':
            custom_config.set('video_font_path', '/usr/share/fonts/truetype/noto/NotoSansSC-VF.ttf')

        # prevent displaying "QUICK MENU" with "No Items" after DOSBox Pure, TyrQuake and PrBoom games exit
        custom_config.set('load_dummy_on_core_shutdown', False)

        ## Specific choices
        if (device_type := self.core_object.player1_device_type) is not None:
            custom_config.set('input_libretro_device_p1', device_type)

        if (device_type := self.core_object.player2_device_type) is not None:
            custom_config.set('input_libretro_device_p2', device_type)

        if (device_type := self.core_object.player3_device_type) is not None:
            custom_config.set('input_libretro_device_p3', device_type)

        if (device_type := self.core_object.player4_device_type) is not None:
            custom_config.set('input_libretro_device_p4', device_type)

        self.core_object.set_config(custom_config)

        # Smooth option
        custom_config.set_bool_from_config('video_smooth', 'smooth')

        # Shader option
        if 'shader' in self.render_config:
            if self.render_config['shader'] is not None and self.render_config['shader'] != 'none':
                custom_config.set('video_shader_enable', True)
                custom_config.set('video_smooth', False)  # seems to be necessary for weaker SBCs
        else:
            custom_config.set('video_shader_enable', False)

        # Ratio option
        custom_config.set('aspect_ratio_index', '')  # reset in case config was changed (or for overlays)
        if ratio := self.config.get_str('ratio'):
            index = '22'  # default value (core)
            if ratio in _RATIOS:
                index = _RATIOS.index(ratio)
            # Check if game natively supports widescreen from metadata (not widescreen hack)
            # (for easy scalability ensure all values for respective systems start with core
            # name and end with "-autowidescreen")
            if ratio != 'full' and self.config.get_bool(f'{self.config.core}-autowidescreen'):
                metadata = self.get_games_metadata(ES_GAMES_METADATA)
                if metadata.get('video_widescreen') == 'true':
                    index = str(_RATIOS.index('16/9'))

            custom_config.set('video_aspect_ratio_auto', False)
            custom_config.set('aspect_ratio_index', index)

        # Rewind option
        custom_config.set('rewind_enable', self.core_object.can_rewind)

        # Run-ahead option (latency reduction)
        run_ahead_frames = self.core_object.runahead
        run_ahead_enabled = False
        preemptive_frames_enable = False
        run_ahead_secondary_instance = False

        if run_ahead_frames > 0:
            if self.config.get_bool('preemptiveframes'):
                preemptive_frames_enable = True
            else:
                run_ahead_enabled = True

            if self.config.get_bool('secondinstance'):
                run_ahead_secondary_instance = True

        custom_config.set('run_ahead_enabled', run_ahead_enabled)
        custom_config.set('preemptive_frames_enable', preemptive_frames_enable)
        custom_config.set('run_ahead_frames', run_ahead_frames)
        custom_config.set('run_ahead_secondary_instance', run_ahead_secondary_instance)

        # Auto frame delay (input delay reduction via frame timing)
        custom_config.set_bool_from_config('video_frame_delay_auto')

        # Retroachievement option
        if (ra_sound := self.config.get('retroachievements.sound', 'none')) != 'none':
            custom_config.set('cheevos_unlock_sound_enable', True)
            custom_config.set('cheevos_unlock_sound', ra_sound)
        else:
            custom_config.set('cheevos_unlock_sound_enable', False)

        # Autosave option
        autosave = self.config.get_bool('autosave')
        custom_config.set('savestate_auto_save', autosave)
        custom_config.set('savestate_auto_load', autosave)

        if self.config.get_bool('incrementalsavestates', True):
            custom_config.set('savestate_auto_index', True)
            custom_config.set('savestate_max_keep', 0)
        else:
            custom_config.set('savestate_auto_index', False)
            custom_config.set('savestate_max_keep', 50)

        # state_slot option
        custom_config.set_from_config('state_slot', default=0)

        # in case of the auto state_filename, do an autoload
        self.config.get_str('state_filename', 'foo')
        if (state_filename := self.config.get_str('state_filename')) and state_filename.endswith('.auto'):
            custom_config.set('savestate_auto_load', True)

        # Retroachievements option
        custom_config.set('cheevos_enable', False)
        custom_config.set('cheevos_hardcore_mode_enable', False)
        custom_config.set('cheevos_leaderboards_enable', False)
        custom_config.set('cheevos_verbose_enable', False)
        custom_config.set('cheevos_auto_screenshot', False)
        custom_config.set('cheevos_challenge_indicators', False)
        custom_config.set('cheevos_start_active', False)
        custom_config.set('cheevos_richpresence_enable', False)

        cheevos_enable = self.config.get_bool('retroachievements')
        if cheevos_enable and (self.core_object.supports_retroachievements or self.config.get_bool('cheevos_force')):
            custom_config.set_from_config('cheevos_username', 'retroachievements.username', default='')
            custom_config.set('cheevos_password', '')  # clear the password - only use the token
            custom_config.set_from_config('cheevos_token', 'retroachievements.token', default='')
            custom_config.set('cheevos_cmd', DEFAULTS_DIR / 'call_achievements_hooks.sh')
            # retroachievements_hardcore_mode
            custom_config.set_bool_from_config('cheevos_hardcore_mode_enable', 'retroachievements.hardcore')
            # retroachievements_leaderboards
            custom_config.set_bool_from_config('cheevos_leaderboards_enable', 'retroachievements.leaderboards')
            # retroachievements_verbose_mode
            custom_config.set_bool_from_config('cheevos_verbose_enable', 'retroachievements.verbose')
            # retroachievements_automatic_screenshot
            custom_config.set_bool_from_config('cheevos_auto_screenshot', 'retroachievements.screenshot')
            # retroarchievements_challenge_indicators
            custom_config.set_bool_from_config('cheevos_challenge_indicators', 'retroachievements.challenge_indicators')
            # retroarchievements_encore_mode
            custom_config.set_bool_from_config('cheevos_start_active', 'retroachievements.encore')
            # retroarchievements_rich_presence
            custom_config.set_bool_from_config('cheevos_richpresence_enable', 'retroachievements.richpresence')
            # retroarchievements_unofficial
            custom_config.set_bool_from_config('cheevos_test_unofficial', 'retroachievements.unofficial')

            if not await is_connected_to_internet():
                cheevos_enable = False

        custom_config.set('cheevos_enable', cheevos_enable)

        custom_config.set_bool_from_config('video_scale_integer', 'integerscale')

        # Netplay management
        if (netplay_mode := self.config.get('netplay.mode')) in {'host', 'client', 'spectator'}:
            # Security : hardcore mode disables save states, which would kill netplay
            custom_config.set('cheevos_hardcore_mode_enable', False)
            # Quite strangely, host mode requires netplay_mode to be set to false when launched from command line
            custom_config.set('netplay_mode', False)
            custom_config.set_from_config('netplay_ip_port', 'netplay.port')
            custom_config.set_from_config('netplay_delay_frames', 'netplay.frames')
            custom_config.set_from_config('netplay_nickname', 'netplay.nickname')
            custom_config.set('netplay_client_swap_input', False)
            if netplay_mode == 'client' or self.config['netplay.mode'] == 'spectator':
                # But client needs netplay_mode = true ... bug ?
                custom_config.set('netplay_mode', True)
                custom_config.set_from_config('netplay_ip_address', 'netplay.server.ip')
                custom_config.set_from_config('netplay_ip_port', 'netplay.server.port')
                custom_config.set('netplay_client_swap_input', True)

            # Connect as client
            if netplay_mode == 'client':
                custom_config.set_from_config('netplay_password', 'netplay.password')

            # Connect as spectator
            if netplay_mode == 'spectator':
                custom_config.set('netplay_start_as_spectator', True)
                custom_config.set_from_config('netplay_spectate_password', 'netplay.password')
            else:
                custom_config.set('netplay_start_as_spectator', False)

            # Netplay host passwords
            if netplay_mode == 'host':
                custom_config.set_from_config('netplay_password', 'netplay.password')
                custom_config.set_from_config('netplay_spectate_password', 'netplay.spectatepassword')

            # Netplay hide the gameplay
            custom_config.set_bool_from_config('netplay_public_announce', 'netplay_public_announce', default=True)

            # Enable or disable server spectator mode
            custom_config.set_bool_from_config('netplay_spectator_mode_enable', 'netplay.spectator')

            # Relay
            if (netplay_relay := self.config.get('netplay.relay')) and netplay_relay != 'none':
                custom_config.set('netplay_use_mitm_server', True)
                custom_config.set('netplay_mitm_server', netplay_relay)
                if (
                    netplay_relay == 'custom'
                    and (netplay_customserver := self.config.get('netplay.customserver')) is not None
                ):
                    custom_config.set('netplay_custom_mitm_server', netplay_customserver)
            else:
                custom_config.set('netplay_use_mitm_server', False)

        # Display FPS
        custom_config.set('fps_show', self.config.show_fps)

        # rumble (to reduce force feedback on devices like RG552)
        custom_config.set_from_config('input_rumble_gain', 'rumble_gain')

        # On-Screen Display
        custom_config.set('width', self.resolution.width)  # default value
        custom_config.set('height', self.resolution.height)  # default value
        # force the assets directory while it was wrong in some beta versions
        custom_config.set('assets_directory', '/usr/share/libretro/assets')

        # Adaptation for small resolution (GPICase)
        if self.resolution.width < 480 or self.resolution.height < 480:
            custom_config.set('menu_enable_widgets', False)
            custom_config.set('video_msg_bgcolor_enable', True)
            custom_config.set('video_font_size', 11)
        else:
            custom_config.set('menu_enable_widgets', True)

        # AI option (service for game translations)
        if self.config.get_bool('ai_service_enabled'):
            custom_config.set('ai_service_enable', True)
            custom_config.set('ai_service_mode', 0)
            custom_config.set('ai_service_source_lang', 0)
            custom_config.set(
                'ai_service_url',
                f'{
                    self.config.get("ai_service_url", "http://ztranslate.net/service?api_key=BATOCERA")
                }&mode=Fast&output=png&target_lang={self.config.get("ai_target_lang", "En")}',
            )
            custom_config.set_bool_from_config('ai_service_pause')
        else:
            custom_config.set('ai_service_enable', False)

    def set_guns_config(self, custom_config: LibretroConfig, core_options: LibretroConfig, /) -> None:
        if self.config.use_guns:
            # clear premapping for each player gun to make new one. Useful for libretro-mame and flycast-dreamcast
            for gun_index in range(1, len(self.guns) + 1):
                for type in ['btn', 'mbtn']:
                    for gun_key in [
                        'gun_trigger',
                        'gun_offscreen_shot',
                        'gun_aux_a',
                        'gun_aux_b',
                        'gun_aux_c',
                        'gun_start',
                        'gun_select',
                        'gun_dpad_up',
                        'gun_dpad_down',
                        'gun_dpad_left',
                        'gun_dpad_right',
                    ]:
                        custom_config.set(f'input_player{gun_index}_{gun_key}_{type}', None)

            # apply gun mapping
            if core_gun_mapping := self.core_object.gun_mapping:
                gun_custom_config = core_gun_mapping.get(self.system)
                if gun_custom_config is None:
                    gun_custom_config = core_gun_mapping.get('default', {})

                gun_core_options: dict[str, str] = {}

                # overwrite configuration by gungames.xml
                if 'gameDependant' in gun_custom_config:
                    for game_dependant in gun_custom_config['gameDependant']:
                        if (
                            f'gun_{game_dependant["key"]}' in self.metadata
                            and self.metadata[f'gun_{game_dependant["key"]}'] == game_dependant['value']
                            and 'mapkey' in game_dependant
                            and 'mapvalue' in game_dependant
                        ):
                            gun_custom_config[game_dependant['mapkey']] = game_dependant['mapvalue']

                        if (
                            f'gun_{game_dependant["key"]}' in self.metadata
                            and self.metadata[f'gun_{game_dependant["key"]}'] == game_dependant['value']
                            and 'mapcorekey' in game_dependant
                            and 'mapcorevalue' in game_dependant
                        ):
                            gun_core_options[game_dependant['mapcorekey']] = game_dependant['mapcorevalue']

                guns_length = len(self.guns)
                max_gun_index = guns_length - 1

                for player_number in range(1, 4):
                    if max_gun_index >= (gun_index := gun_custom_config.get(f'p{player_number}', guns_length)):
                        device_p_value: int | None = gun_custom_config.get(f'device_p{player_number}')

                        if device_p_value is None:
                            device_p_value = gun_custom_config.get('device')

                        custom_config.set(f'input_libretro_device_p{player_number}', device_p_value)

                        pedal_controllers_name = f'controllers.pedals{player_number}'
                        pedal_key = self.config.get_str(pedal_controllers_name, _PEDAL_TO_KEY[player_number])
                        gun = self.guns[gun_index]

                        # gun mapping
                        custom_config.set(f'input_player{player_number}_mouse_index', gun.mouse_index)
                        custom_config.set(f'input_player{player_number}_gun_trigger_mbtn', 1)
                        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', 2)
                        custom_config.set(f'input_player{player_number}_gun_start_mbtn', 3)
                        custom_config.set(f'input_player{player_number}_gun_select_mbtn', 4)
                        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 5)
                        custom_config.set(f'input_player{player_number}_gun_aux_b_mbtn', 6)
                        custom_config.set(f'input_player{player_number}_gun_aux_c_mbtn', 7)
                        custom_config.set(f'input_player{player_number}_gun_dpad_up_mbtn', 8)
                        custom_config.set(f'input_player{player_number}_gun_dpad_down_mbtn', 9)
                        custom_config.set(f'input_player{player_number}_gun_dpad_left_mbtn', 10)
                        custom_config.set(f'input_player{player_number}_gun_dpad_right_mbtn', 11)
                        custom_config.set(self.core_object.get_pedal_config_name_for_player(player_number), pedal_key)

                        self.core_object.set_gun_config_for_player(custom_config, player_number, gun)

                for key, value in gun_core_options.items():
                    core_options.set(key, value)

                self.core_object.set_gun_core_options(core_options)

                custom_config.set('input_overlay_show_mouse_cursor', False)
        else:
            custom_config.set('input_overlay_show_mouse_cursor', True)

    def write_bezel_config(self, custom_config: LibretroConfig, shader_bezel: bool, bezel: str | None, /) -> None:
        # disable the overlay
        # if all steps are passed, enable them
        custom_config.set('input_overlay_hide_in_menu', False)

        # bezel are disabled
        # default values in case something wrong append
        custom_config.set('input_overlay_enable', False)
        custom_config.set('video_message_pos_x', 0.05)
        custom_config.set('video_message_pos_y', 0.05)

        _logger.debug('libretro bezel: %s', bezel)

        guns_borders_size = self.guns_borders_size
        overlay_png_file: Path
        overlay_info_file: Path | None
        bezel_game: bool

        # create a fake bezel if guns need it
        if bezel is None and guns_borders_size is not None:
            _logger.debug('guns need border')
            gun_bezel_file = Path('/tmp/bezel_gun_black.png')
            gun_bezel_info_file = Path('/tmp/bezel_gun_black.info')

            width = self.resolution.width
            height = self.resolution.height
            border = _gun_border_pixels(width, guns_borders_size)

            # could be better to compute the ratio while on ra it is forced to 4/3...
            top = border
            left = border
            bottom = border
            right = border
            if self.in_game_ratio == 4 / 3:
                left = int((width - (height * 4 / 3)) // 2 + border)
                right = left

            gun_bezel_info_file.write_text(
                f'{{ "width":{width}, "height":{height}, "top":{top}, "left":{left},'
                f' "bottom":{bottom}, "right":{right}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000}}'
            )
            create_transparent_image(gun_bezel_file, width, height)
            # if the game needs a specific bezel, to draw border, consider it as a specific game bezel, like for thebezelproject to avoid caches
            overlay_png_file = gun_bezel_file
            overlay_info_file = gun_bezel_info_file
            bezel_game = True
        else:
            if bezel is None:
                return
            bz_infos = self.bezel_files
            if bz_infos is None:
                return

            overlay_png_file = bz_infos.png
            overlay_info_file = bz_infos.info
            bezel_game = bz_infos.specific_to_game

        bezel_info = BezelInfo.load_from_json(overlay_info_file)

        info_width = bezel_info.width
        info_height = bezel_info.height
        info_top = bezel_info.top
        info_left = bezel_info.left
        info_bottom = bezel_info.bottom
        info_right = bezel_info.right
        opacity = 1.0 if bezel_info.opacity is None else bezel_info.opacity
        message_x = 0.0 if bezel_info.message_x is None else bezel_info.message_x
        message_y = 0.0 if bezel_info.message_y is None else bezel_info.message_y

        viewport_used = (
            info_width is not None
            and info_height is not None
            and info_top is not None
            and info_left is not None
            and info_bottom is not None
            and info_right is not None
            and not shader_bezel
        )

        game_ratio = self.resolution.width / self.resolution.height
        bezel_need_adaptation = False
        aspect_ratio_index: str | int = ''

        if viewport_used:
            if self.resolution.width != info_width or self.resolution.height != info_height:
                if game_ratio < 1.6 and guns_borders_size is None:
                    # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios ; don't skip if gun borders are needed
                    return

                bezel_need_adaptation = True

            aspect_ratio_index = str(_RATIOS.index('custom'))
            custom_config.set('aspect_ratio_index', aspect_ratio_index)
            if (ratio := self.config.get_str('ratio')) and ratio in _RATIOS:
                aspect_ratio_index = _RATIOS.index(ratio)
                custom_config.set('aspect_ratio_index', aspect_ratio_index)
                custom_config.set('video_aspect_ratio_auto', False)
        else:
            # when there is no information about width and height in the .info, assume that the tv is HD 16/9 and infos are core provided
            if game_ratio < 1.6 and guns_borders_size is None:
                # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios ; don't skip if gun borders are needed
                return

            # No info on the bezel, let's get the bezel image width and height and apply the
            # ratios from usual 16:9 1920x1080 bezels (example: theBezelProject)
            try:
                info_width, info_height = get_image_size(overlay_png_file)
                info_top = int(info_height * 2 / 1080)
                info_left = int(
                    info_width * 241 / 1920
                )  # 241 = (1920 - (1920 / (4:3))) / 2 + 1 pixel = where viewport start
                info_bottom = int(info_height * 2 / 1080)
                info_right = int(info_width * 241 / 1920)
                bezel_need_adaptation = True
            except Exception:
                pass  # outch, no ratio will be applied.
            if (
                info_width is not None
                and info_height is not None
                and self.resolution.width == info_width
                and self.resolution.height == info_height
            ):
                bezel_need_adaptation = False
            if not shader_bezel:
                aspect_ratio_index = str(_RATIOS.index('custom'))
                custom_config.set('aspect_ratio_index', aspect_ratio_index)
                if (ratio := self.config.get_str('ratio')) and ratio in _RATIOS:
                    aspect_ratio_index = _RATIOS.index(ratio)
                    custom_config.set('aspect_ratio_index', aspect_ratio_index)
                    custom_config.set('video_aspect_ratio_auto', False)

        if not shader_bezel:
            custom_config.set('input_overlay_enable', True)
        custom_config.set('input_overlay_scale', '1.0')
        custom_config.set('input_overlay', str(self.overlay_config_path))
        custom_config.set('input_overlay_hide_in_menu', True)

        custom_config.set('input_overlay_opacity', opacity)

        if aspect_ratio_index == str(_RATIOS.index('custom')):
            custom_config.set('video_viewport_bias_x', '0.000000')
            custom_config.set('video_viewport_bias_y', '0.000000')
        else:
            custom_config.set('video_viewport_bias_x', '0.500000')
            custom_config.set('video_viewport_bias_y', '0.500000')

        # stretch option
        bezel_stretch = self.config.get_bool('bezel_stretch')

        tattoo_output_png = Path('/tmp/bezel_tattooed.png')
        qrcode_output_png = Path('/tmp/bezel_qrcode.png')

        if bezel_need_adaptation:
            if (
                info_width is None
                or info_height is None
                or info_top is None
                or info_left is None
                or info_bottom is None
                or info_right is None
            ):
                return

            wratio = self.resolution.width / float(info_width)
            hratio = self.resolution.height / float(info_height)

            # Stretch also takes care of cutting off the bezel and adapting viewport, if aspect ratio is < 16:9
            if self.resolution.width < info_width or self.resolution.height < info_height:
                _logger.debug('Screen resolution smaller than bezel: forcing stretch')
                bezel_stretch = True

            create_new_bezel_file = True
            if bezel_game:
                output_png_file = Path('/tmp/bezel_per_game.png')
            else:
                # The logic to cache system bezels is not always true anymore now that we have tattoos
                output_png_file = Path('/tmp') / f'{overlay_png_file.stem}_adapted.png'
                if self.config.get_str('bezel.tattoo', '0') != '0' or self.config.get_str('bezel.qrcode', '0') != '0':
                    create_new_bezel_file = True
                elif not tattoo_output_png.exists() and not qrcode_output_png.exists() and output_png_file.exists():
                    create_new_bezel_file = False
                    _logger.debug('Using cached bezel file %s', output_png_file)
                else:
                    tattoo_output_png.unlink(missing_ok=True)
                    qrcode_output_png.unlink(missing_ok=True)
                    create_new_bezel_file = True

                if create_new_bezel_file:
                    adapted = [path for path in Path('/tmp').iterdir() if path.name.endswith('_adapted.png')]
                    adapted.sort(key=lambda path: path.stat().st_mtime)
                    # Keep only last 10 generated bezels to save space on tmpfs /tmp
                    if len(adapted) >= 10:
                        for _ in range(10):
                            adapted.pop()
                        _logger.debug('Removing unused bezel file: %s', adapted)
                        for adapted_file in adapted:
                            adapted_file.unlink(missing_ok=True)

            if bezel_stretch:
                border_x = 0
                viewport_ratio = float(info_width) / float(info_height)
                if viewport_ratio - game_ratio > 0.01:
                    new_x = int(info_width * game_ratio / viewport_ratio)
                    delta = int(info_width - new_x)
                    border_x = delta // 2
                _logger.debug('Bezel_stretch: need to cut off %s pixels', border_x)
                custom_config.set('custom_viewport_x', (info_left - border_x / 2) * wratio)
                custom_config.set('custom_viewport_y', info_top * hratio)
                custom_config.set('custom_viewport_width', (info_width - info_left - info_right + border_x) * wratio)
                custom_config.set('custom_viewport_height', (info_height - info_top - info_bottom) * hratio)
                custom_config.set('video_message_pos_x', message_x * wratio)
                custom_config.set('video_message_pos_y', message_y * hratio)
            else:
                xoffset = self.resolution.width - info_width
                yoffset = self.resolution.height - info_height
                custom_config.set('custom_viewport_x', info_left + xoffset / 2)
                custom_config.set('custom_viewport_y', info_top + yoffset / 2)
                custom_config.set('custom_viewport_width', info_width - info_left - info_right)
                custom_config.set('custom_viewport_height', info_height - info_top - info_bottom)
                custom_config.set('video_message_pos_x', message_x + xoffset / 2)
                custom_config.set('video_message_pos_y', message_y + yoffset / 2)

            if create_new_bezel_file:
                # Padding left and right borders for ultrawide screens (larger than 16:9 aspect ratio)
                # or up/down for 4K
                _logger.debug('Generating a new adapted bezel file %s', output_png_file)
                try:
                    pad_image(
                        overlay_png_file,
                        output_png_file,
                        self.resolution.width,
                        self.resolution.height,
                        stretch=bezel_stretch,
                    )
                except Exception as e:
                    _logger.debug('Failed to create the adapated image: %s', e)
                    return

            overlay_png_file = output_png_file  # replace by the new file (recreated or cached in /tmp)
        else:
            if (
                viewport_used
                and info_width is not None
                and info_height is not None
                and info_top is not None
                and info_left is not None
                and info_bottom is not None
                and info_right is not None
            ):
                custom_config.set('custom_viewport_x', info_left)
                custom_config.set('custom_viewport_y', info_top)
                custom_config.set('custom_viewport_width', info_width - info_left - info_right)
                custom_config.set('custom_viewport_height', info_height - info_top - info_bottom)
            custom_config.set('video_message_pos_x', message_x)
            custom_config.set('video_message_pos_y', message_y)

        if self.config.get_str('bezel.tattoo', '0') != '0':
            add_tattoo_image(overlay_png_file, tattoo_output_png, self.config)
            overlay_png_file = tattoo_output_png

        if (
            self.config.get_str('bezel.qrcode', '0') != '0'
            and (cheevos_id := self.game_info.get('cheevosId', '0')) != '0'
        ):
            add_qr_code(overlay_png_file, qrcode_output_png, cheevos_id, self.config.get_str('bezel.qrcode', '0'))
            overlay_png_file = qrcode_output_png

        if guns_borders_size is not None:
            _logger.debug('Draw gun borders')
            output_png_file = Path('/tmp/bezel_gunborders.png')
            create_gun_border_image(
                overlay_png_file,
                output_png_file,
                guns_borders_size,
                self.guns_border_ratio,
                inner_color=self.gun_borders_color,
            )
            overlay_png_file = output_png_file

        _logger.debug('Bezel file set to %s', overlay_png_file)
        _write_overlay_config(self.overlay_config_path, overlay_png_file)

        # For shaders that will want to use Batocera's decoration as part of the shader instead of an overlay
        if shader_bezel:
            # Create path if needed, clear old bezels
            shader_bezel_path = Path('/var/run/shader_bezels')
            shader_bezel_file = shader_bezel_path / 'bezel.png'
            shader_bezel_path.mkdir(parents=True, exist_ok=True)
            if shader_bezel_file.exists():
                _logger.debug('Removing old shader bezel %s', shader_bezel_file)
                shader_bezel_file.unlink()

            # Link bezel png file to the fixed path.
            # Shaders should use this path to find the art.
            shader_bezel_file.symlink_to(overlay_png_file)
            _logger.debug('Symlinked bezel file %s to %s for selected shader', overlay_png_file, shader_bezel_file)
