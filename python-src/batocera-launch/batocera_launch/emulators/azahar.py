from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, SAVES, SCREENSHOTS
from batocera_common.vulkan import get_discrete_gpu_index, has_discrete_gpu, is_available
from batocera_launch import Command, Controller, Emulator, HotkeysContext, Input, InputMapping, LabWCConfig
from batocera_launch.devices.video import get_screens

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_BUTTONS: Final = {
    'button_a': 'a',
    'button_b': 'b',
    'button_x': 'x',
    'button_y': 'y',
    'button_up': 'up',
    'button_down': 'down',
    'button_left': 'left',
    'button_right': 'right',
    'button_l': 'pageup',
    'button_r': 'pagedown',
    'button_start': 'start',
    'button_select': 'select',
    'button_zl': 'l2',
    'button_zr': 'r2',
    'button_home': 'hotkey',
}

_AXIS: Final = {
    'circle_pad': 'joystick1',
    'c_stick': 'joystick2',
}

_REGION: Final = {'AUTO': -1, 'JPN': 0, 'USA': 1, 'EUR': 2, 'AUS': 3, 'CHN': 4, 'KOR': 5, 'TWN': 6}
_AVAILABLE_LANGUAGES: Final = {
    'ja_JP': 'JPN',
    'en_US': 'USA',
    'de_DE': 'EUR',
    'es_ES': 'EUR',
    'fr_FR': 'EUR',
    'it_IT': 'EUR',
    'hu_HU': 'EUR',
    'pt_PT': 'EUR',
    'ru_RU': 'EUR',
    'en_AU': 'AUS',
    'zh_CN': 'CHN',
    'ko_KR': 'KOR',
    'zh_TW': 'TWN',
}


def _hat_direction(value: str) -> str:
    match int(value):
        case 1:
            return 'up'
        case 4:
            return 'down'
        case 2:
            return 'right'
        case 8:
            return 'left'
        case _:
            return 'unknown'


def _set_button(key: str, pad_guid: str, pad_inputs: InputMapping) -> str | None:
    # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
    if (inp := pad_inputs.get(key)) is None:
        return None

    if inp.type == 'button':
        return f'button:{inp.id},guid:{pad_guid},engine:sdl'
    if inp.type == 'hat':
        return f'engine:sdl,guid:{pad_guid},hat:{inp.id},direction:{_hat_direction(inp.value)}'
    if inp.type == 'axis':
        # Untested, need to configure an axis as button / triggers buttons to be tested too
        return f'engine:sdl,guid:{pad_guid},axis:{inp.id},direction:+,threshold:0.5'
    return None


def _set_axis(key: str, pad_guid: str, pad_inputs: InputMapping) -> str:
    input_x: Input | None = None
    input_y: Input | None = None

    if key == 'joystick1' and 'joystick1left' in pad_inputs:
        input_x = pad_inputs['joystick1left']
    elif key == 'joystick2' and 'joystick2left' in pad_inputs:
        input_x = pad_inputs['joystick2left']

    if key == 'joystick1' and 'joystick1up' in pad_inputs:
        input_y = pad_inputs['joystick1up']
    elif key == 'joystick2' and 'joystick2up' in pad_inputs:
        input_y = pad_inputs['joystick2up']

    if input_x is None or input_y is None:
        return ''

    return f'axis_x:{input_x.id},guid:{pad_guid},axis_y:{input_y.id},engine:sdl'


def _azahar_lang_from_config(language: str | None) -> int:
    lang = (language or '')[:5]
    if lang in _AVAILABLE_LANGUAGES:
        return _REGION[_AVAILABLE_LANGUAGES[lang]]
    return _REGION['AUTO']


@cached_dataclass
class Azahar(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'azahar',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_F4',
                'pause': 'KEY_F4',
                'reset': 'KEY_F6',
                'screen_layout': 'KEY_F10',
                'swap_screen': 'KEY_F9',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'azahar-emu'

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / '3ds'

    @property
    def needs_mouse(self) -> bool:
        return self.config.get_str('azahar_screen_layout') != '1-false'

    async def prepare_labwc(self) -> None:
        # windows position is handled by coordonnates by the application (xorg) or the windows manager (wayland)
        screens = await get_screens(self.config)

        config = LabWCConfig()
        config.window_rule(identifier='azahar').move_to_output(screens, 'primary')
        config.window_rule(identifier='azahar', title='*Secondary Window*').move_to_output(
            screens, 'backglass'
        ).toggle_fullscreen()

        config.save()

    def _write_config(self) -> None:
        config_file = self.config_dir / 'qt-config.ini'

        # ini file
        azahar_config = CaseSensitiveRawConfigParser(strict=False)
        if config_file.exists():
            azahar_config.read(config_file)

        ## [LAYOUT]
        if not azahar_config.has_section('Layout'):
            azahar_config.add_section('Layout')
        # Screen Layout
        azahar_config.set('Layout', 'custom_layout', 'false')
        azahar_config.set('Layout', r'custom_layout\default', 'false')
        layout_option, swap_screen = self.config.get_str('azahar_screen_layout', '0-false').split('-')
        azahar_config.set('Layout', 'swap_screen', swap_screen)
        azahar_config.set('Layout', r'swap_screen\default', 'false')
        azahar_config.set('Layout', 'layout_option', layout_option)
        azahar_config.set('Layout', r'layout_option\default', 'false')
        azahar_config.set(
            'Layout', 'large_screen_proportion', self.config.get_str('azahar_large_screen_proportion', '4')
        )
        azahar_config.set('Layout', r'large_screen_proportion\default', 'false')

        ## [SYSTEM]
        if not azahar_config.has_section('System'):
            azahar_config.add_section('System')
        # New 3DS Version
        azahar_config.set(
            'System',
            'is_new_3ds',
            self.config.get_bool('azahar_is_new_3ds', return_values=('true', 'false')),
        )
        azahar_config.set('System', r'is_new_3ds\default', 'false')
        # Language
        azahar_config.set(
            'System', 'region_value', str(_azahar_lang_from_config(self.config.get_str('system.language')))
        )
        azahar_config.set('System', r'region_value\default', 'false')

        ## [CORE]
        if not azahar_config.has_section('Core'):
            azahar_config.add_section('Core')
        # CPU Clock Percentage
        azahar_config.set('Core', 'cpu_clock_percentage', self.config.get_str('azahar_cpu_clock', '100'))
        azahar_config.set('Core', r'cpu_clock_percentage\default', 'false')

        ## [UI]
        if not azahar_config.has_section('UI'):
            azahar_config.add_section('UI')
        # Start Fullscreen
        azahar_config.set('UI', 'fullscreen', 'true')
        azahar_config.set('UI', r'fullscreen\default', 'false')

        # Batocera - Defaults
        azahar_config.set('UI', 'display_titlebar', 'false')
        azahar_config.set('UI', r'display_titlebar\default', 'false')
        azahar_config.set('UI', 'first_start', 'false')
        azahar_config.set('UI', r'first_start\default', 'false')
        azahar_config.set('UI', 'hide_mouse', 'true')
        azahar_config.set('UI', r'hide_mouse\default', 'false')
        azahar_config.set('UI', 'enable_discord_presence', 'false')
        azahar_config.set('UI', r'enable_discord_presence\default', 'false')

        # Remove pop-up prompt on start
        azahar_config.set('UI', 'callout_flags', '1')
        azahar_config.set('UI', r'callout_flags\default', 'false')
        # Close without confirmation
        azahar_config.set('UI', 'confirm_before_closing', 'false')
        azahar_config.set('UI', r'confirm_before_closing\default', 'false')

        # screenshots
        azahar_config.set('UI', r'Paths\screenshot_path', str(SCREENSHOTS))
        azahar_config.set('UI', r'Paths\screenshot_path\default', 'false')

        ## [MISCELLANEOUS]
        if not azahar_config.has_section('Miscellaneous'):
            azahar_config.add_section('Miscellaneous')
        # Don't check for update at start
        azahar_config.set('Miscellaneous', 'check_for_update_on_start', 'false')
        azahar_config.set('Miscellaneous', r'check_for_update_on_start\default', 'false')

        ## [RENDERER]
        if not azahar_config.has_section('Renderer'):
            azahar_config.add_section('Renderer')
        # Hardware Shader
        azahar_config.set(
            'Renderer',
            'use_hw_shader',
            self.config.get_bool('azahar_use_hw_shader', False, return_values=('true', 'false')),
        )
        azahar_config.set('Renderer', r'use_hw_shader\default', 'false')
        # Accurate Multiplication
        azahar_config.set(
            'Renderer',
            'shaders_accurate_mul',
            self.config.get_bool('azahar_accurate_multiplication', False, return_values=('true', 'false')),
        )
        azahar_config.set('Renderer', r'shaders_accurate_mul\default', 'false')
        # Shader JIT
        azahar_config.set(
            'Renderer',
            'use_shader_jit',
            self.config.get_bool('azahar_use_shader_jit', True, return_values=('true', 'false')),
        )
        azahar_config.set('Renderer', r'use_shader_jit\default', 'false')
        # Async Shader Compilation
        azahar_config.set(
            'Renderer',
            'async_shader_compilation',
            self.config.get_bool('azahar_async_shader_compilation', False, return_values=('true', 'false')),
        )
        azahar_config.set('Renderer', r'async_shader_compilation\default', 'false')
        # Async Presentation
        azahar_config.set(
            'Renderer',
            'async_presentation',
            self.config.get_bool('azahar_async_presentation', False, return_values=('true', 'false')),
        )
        azahar_config.set('Renderer', r'async_presentation\default', 'false')
        # Software, OpenGL (default) or Vulkan
        azahar_config.set('Renderer', 'graphics_api', self.config.get_str('azahar_graphics_api', '1'))
        azahar_config.set('Renderer', r'graphics_api\default', 'false')
        # Set Vulkan as necessary
        if self.config.get_str('azahar_graphics_api') == '2' and is_available():
            _logger.debug('Vulkan driver is available on the system.')
            if has_discrete_gpu():
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                discrete_index = get_discrete_gpu_index()
                if discrete_index:
                    _logger.debug('Using Discrete GPU Index: %s for Azahar', discrete_index)
                    azahar_config.set('Renderer', 'physical_device', discrete_index)
                    azahar_config.set('Renderer', r'physical_device\default', 'false')
                else:
                    _logger.debug("Couldn't get discrete GPU index")
            else:
                _logger.debug('Discrete GPU is not available on the system. Using default.')
        # Use VSYNC
        azahar_config.set(
            'Renderer',
            'use_vsync',
            self.config.get_bool('azahar_use_vsync', True, return_values=('true', 'false')),
        )
        azahar_config.set('Renderer', r'use_vsync\default', 'false')
        # Resolution Factor
        azahar_config.set('Renderer', 'resolution_factor', self.config.get_str('azahar_resolution_factor', '1'))
        azahar_config.set('Renderer', r'resolution_factor\default', 'false')
        # Texture Filter
        azahar_config.set('Renderer', 'texture_filter', self.config.get_str('azahar_texture_filter', '0'))
        azahar_config.set('Renderer', r'texture_filter\default', 'false')

        ## [AUDIO]
        if not azahar_config.has_section('Audio'):
            azahar_config.add_section('Audio')
        # Audio Stretching
        azahar_config.set(
            'Audio',
            'enable_audio_stretching',
            self.config.get_bool('azahar_audio_stretching', True, return_values=('true', 'false')),
        )
        azahar_config.set('Audio', r'enable_audio_stretching\default', 'false')

        ## [WEB SERVICE]
        if not azahar_config.has_section('WebService'):
            azahar_config.add_section('WebService')
        azahar_config.set('WebService', 'enable_telemetry', 'false')
        azahar_config.set('WebService', r'enable_telemetry\default', 'false')

        ## [UTILITY]
        if not azahar_config.has_section('Utility'):
            azahar_config.add_section('Utility')
        # Disk Shader Cache
        azahar_config.set(
            'Utility',
            'use_disk_shader_cache',
            self.config.get_bool('azahar_use_disk_shader_cache', return_values=('true', 'false')),
        )
        azahar_config.set('Utility', r'use_disk_shader_cache\default', 'false')
        # Custom Textures
        match self.config.get_str('azahar_custom_textures'):
            case None | '0':
                azahar_config.set('Utility', 'custom_textures', 'false')
                azahar_config.set('Utility', r'custom_textures\default', 'false')
                azahar_config.set('Utility', 'preload_textures', 'false')
                azahar_config.set('Utility', r'preload_textures\default', 'false')
            case textures:
                tab = textures.split('-')
                azahar_config.set('Utility', 'custom_textures', 'true')
                azahar_config.set('Utility', r'custom_textures\default', 'false')
                if tab[1] == 'normal':
                    azahar_config.set('Utility', 'async_custom_loading', 'true')
                    azahar_config.set('Utility', r'async_custom_loading\default', 'false')
                    azahar_config.set('Utility', 'preload_textures', 'false')
                    azahar_config.set('Utility', r'preload_textures\default', 'false')
                else:
                    azahar_config.set('Utility', 'async_custom_loading', 'false')
                    azahar_config.set('Utility', r'async_custom_loading\default', 'false')
                    azahar_config.set('Utility', 'preload_textures', 'true')
                    azahar_config.set('Utility', r'preload_textures\default', 'false')

        ## [CONTROLS]
        if not azahar_config.has_section('Controls'):
            azahar_config.add_section('Controls')

        # Options required to load the functions when the configuration file is created
        if not azahar_config.has_option('Controls', r'profiles\size'):
            azahar_config.set('Controls', 'profile', '0')
            azahar_config.set('Controls', r'profile\default', 'false')
            azahar_config.set('Controls', r'profiles\1\name', 'default')
            azahar_config.set('Controls', r'profiles\1\name\default', 'false')
            azahar_config.set('Controls', r'profiles\size', '1')
            azahar_config.set('Controls', r'profiles\size\default', 'false')

        if controller := Controller.find_player_number(self.controllers, 1):
            for option, button in _BUTTONS.items():
                azahar_config.set(
                    'Controls',
                    f'profiles\\1\\{option}',
                    f'"{_set_button(button, controller.guid, controller.inputs)}"',
                )
                azahar_config.set('Controls', f'profiles\\1\\{option}\\default', 'false')
            for option, axis in _AXIS.items():
                azahar_config.set(
                    'Controls',
                    f'profiles\\1\\{option}',
                    f'"{_set_axis(axis, controller.guid, controller.inputs)}"',
                )
                azahar_config.set('Controls', f'profiles\\1\\{option}\\default', 'false')

        ## Update the configuration file
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with config_file.open('w') as fp:
            azahar_config.write(fp)

    async def configure(self) -> Command:
        self._write_config()

        return Command(
            ['/usr/bin/azahar', self.rom],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': self.saves_dir,
                'XDG_CACHE_HOME': CACHE,
                'XDG_RUNTIME_DIR': self.saves_dir / 'azahar-emu',
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
