from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, ROMS
from batocera_common.vulkan import get_discrete_gpu_index, get_version, has_discrete_gpu, is_available
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext
from batocera_launch.paths import configure_emulator

_logger = logging.getLogger(__name__)

_SAVES: Final = Path('/userdata/saves/shadps4')
_ROM_DIR: Final = ROMS / 'ps4'
_DLC_DIR: Final = _ROM_DIR / 'DLC'


def _default_config(discrete_index: int, width: int, height: int, /) -> dict[str, dict[str, Any]]:
    return {
        'Audio': {
            'audio_backend': 0,
            'openal_main_output_device': 'Default Device',
            'openal_mic_device': 'Default Device',
            'openal_padSpk_output_device': 'Default Device',
            'sdl_main_output_device': 'Default Device',
            'sdl_mic_device': 'Default Device',
            'sdl_padSpk_output_device': 'Default Device',
        },
        'Debug': {'config_version': 'GITDIR-NOTFOUND', 'debug_dump': False, 'shader_collect': False},
        'GPU': {
            'copy_gpu_buffers': False,
            'direct_memory_access_enabled': False,
            'dump_shaders': False,
            'fsr_enabled': False,
            'full_screen': True,
            'full_screen_mode': 'Windowed',
            'hdr_allowed': False,
            'internal_screen_height': 720,
            'internal_screen_width': 1280,
            'null_gpu': False,
            'patch_shaders': False,
            'present_mode': 'Mailbox',
            'rcas_attenuation': 250,
            'rcas_enabled': True,
            'readback_linear_images_enabled': False,
            'readbacks_mode': 0,
            'vblank_frequency': 60,
            'window_height': height,
            'window_width': width,
        },
        'General': {
            'addon_install_dir': str(_DLC_DIR),
            'big_picture_scale': 1000,
            'connected_to_network': False,
            'console_language': 1,
            'dev_kit_mode': False,
            'discord_rpc_enabled': False,
            'extra_dmem_in_mbytes': 0,
            'font_dir': '',
            'home_dir': str(_SAVES),
            'install_dirs': [{'enabled': True, 'path': str(_ROM_DIR)}],
            'neo_mode': False,
            'shad_net_enabled': False,
            'shadnet_server': '',
            'show_fps_counter': False,
            'show_splash': False,
            'sys_modules_dir': '',
            'trophy_notification_duration': 6.0,
            'trophy_notification_side': 'right',
            'trophy_popup_disabled': False,
            'volume_slider': 100,
        },
        'Input': {
            'background_controller_input': False,
            'camera_id': -1,
            'cursor_hide_timeout': 5,
            'cursor_state': 1,
            'default_controller_id': '',
            'ime_accessibility_enabled': False,
            'ime_url_mail_short_panel': False,
            'is_circle_enter': False,
            'motion_controls_enabled': True,
            'special_pad_class': 1,
            'usb_device_backend': 0,
            'use_special_pad': False,
            'use_unified_input_config': True,
        },
        'Log': {
            'append': False,
            'enable': True,
            'filter': '',
            'max_skip_duration': 5000,
            'separate': False,
            'size_limit': 104857600,
            'skip_duplicate': True,
            'sync': True,
        },
        'Vulkan': {
            'gpu_id': discrete_index,
            'pipeline_cache_archived': False,
            'pipeline_cache_enabled': False,
            'renderdoc_enabled': False,
            'vkcrash_diagnostic_enabled': False,
            'vkguest_markers': False,
            'vkhost_markers': False,
            'vkvalidation_core_enabled': True,
            'vkvalidation_enabled': False,
            'vkvalidation_gpu_enabled': False,
            'vkvalidation_sync_enabled': False,
        },
    }


@cached_dataclass
class Shadps4(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'shadps4',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'shadPS4'

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        json_file = self.config_dir / 'config.json'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        _SAVES.mkdir(parents=True, exist_ok=True)
        (self.config_dir / 'input_config').mkdir(parents=True, exist_ok=True)  # fixes hang if not present

        if not is_available():
            raise BatoceraException('Vulkan driver required is not available on the system')

        discrete_index = -1
        vulkan_version = get_version()
        if vulkan_version > '1.3':
            _logger.debug('Using Vulkan version: %s', vulkan_version)
            if has_discrete_gpu():
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                gpu_index = get_discrete_gpu_index()
                if gpu_index is not None:
                    _logger.debug('Using Discrete GPU Index: %s for shadPS4', gpu_index)
                    discrete_index = int(gpu_index)
                else:
                    _logger.debug("Couldn't get discrete GPU index")
                    discrete_index = 0
            else:
                _logger.debug('Discrete GPU is not available on the system. Using default.')
        else:
            _logger.debug('Vulkan version: %s is not compatible with shadPS4', vulkan_version)

        config: dict[str, dict[str, Any]] = {}
        if json_file.is_file():
            try:
                config = json.loads(json_file.read_text(encoding='utf-8'))
            except Exception:
                _logger.exception('Failed to load existing shadps4 config. Will create default.')

        if not config:
            _logger.info('Creating default shadps4 config at %s', json_file)
            config = _default_config(discrete_index, self.resolution.width, self.resolution.height)

        general_config = config.setdefault('General', {})
        general_config['discord_rpc_enabled'] = False
        general_config['addon_install_dir'] = str(_DLC_DIR)
        general_config['install_dirs'] = [{'enabled': True, 'path': str(_ROM_DIR)}]
        general_config['home_dir'] = str(_SAVES)

        gpu_config = config.setdefault('GPU', {})
        gpu_config['full_screen'] = True
        gpu_config['full_screen_mode'] = 'Fullscreen (Borderless)'
        gpu_config['window_width'] = self.resolution.width
        gpu_config['window_height'] = self.resolution.height

        vulkan_config = config.setdefault('Vulkan', {})
        vulkan_config['gpu_id'] = discrete_index
        vulkan_config['pipeline_cache_enabled'] = True

        # Options - GRAPHICS
        gpu_config['fsr_enabled'] = self.config.get_bool('shadps4_fsr')
        gpu_config['rcas_enabled'] = self.config.get_bool('shadps4_rcas')
        gpu_config['hdr_allowed'] = self.config.get_bool('shadps4_hdr')

        # Options - DISPLAY
        gpu_config['present_mode'] = self.config.get_str('shadps4_present_mode') or 'Mailbox'
        gpu_config['vblank_frequency'] = self.config.get_int('shadps4_vblank_freq') or 60
        general_config['show_fps_counter'] = self.config.get_bool('shadps4_show_fps')

        # Options - SYSTEM
        general_config['neo_mode'] = self.config.get_bool('shadps4_neo_mode')
        general_config['console_language'] = self.config.get_int('shadps4_console_lang') or 1

        # Options - ADVANCED
        gpu_config['copy_gpu_buffers'] = self.config.get_bool('shadps4_copy_gpu_buffers')
        gpu_config['readbacks_mode'] = self.config.get_int('shadps4_readbacks_mode') or 0
        gpu_config['direct_memory_access_enabled'] = self.config.get_bool('shadps4_dma')
        vulkan_config['pipeline_cache_archived'] = self.config.get_bool('shadps4_pipeline_cache')

        log_config = config.setdefault('Log', {})
        log_config['enable'] = self.config.get_bool('shadps4_logging')

        json_file.write_text(json.dumps(config, indent=2), encoding='utf-8')

        if configure_emulator(self.rom):
            return Command(
                ['/usr/bin/shadPS4QtLauncher'],
                env={'SDL_JOYSTICK_HIDAPI': '0', 'XDG_DATA_HOME': CONFIGS},
            )

        if self.rom.suffix == '.zar':
            eboot_path = self.rom
        elif self.rom.is_dir():
            eboot_path = self.rom / 'eboot.bin'
        else:
            eboot_path = self.rom.parent / 'eboot.bin'

        return Command(
            ['/usr/bin/shadps4', '--game', eboot_path, '--fullscreen', 'true'],
            env={'SDL_JOYSTICK_HIDAPI': '0', 'XDG_DATA_HOME': CONFIGS},
        )
