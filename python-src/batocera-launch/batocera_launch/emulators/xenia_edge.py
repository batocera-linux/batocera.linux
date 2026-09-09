from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Final

import toml

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, SAVES
from batocera_common.vulkan import get_version as vulkan_get_version, is_available as vulkan_is_available
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext
from batocera_launch.paths import configure_emulator

_logger = logging.getLogger(__name__)

_XENIA_EDGE_BIN: Final = Path('/usr/bin/xenia-edge/xenia_edge')
_XBOX360_SAVES: Final = SAVES / 'xbox360'


@cached_dataclass
class XeniaEdge(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'xenia-edge',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'Xenia'

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.config.get_bool('xenia_edge_widescreen', True) else 4 / 3

    async def configure(self) -> Command:
        if not vulkan_is_available():
            raise BatoceraException('Vulkan driver required by xenia-edge is not available on the system')

        vulkan_version = vulkan_get_version()
        if vulkan_version <= '1.3':
            _logger.warning('Vulkan version %s may not meet xenia-edge requirements (1.3+)', vulkan_version)

        xenia_cache = CACHE / 'xenia-edge'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        xenia_cache.mkdir(parents=True, exist_ok=True)
        _XBOX360_SAVES.mkdir(parents=True, exist_ok=True)
        (self.config_dir / 'patches').mkdir(parents=True, exist_ok=True)

        rom = self.rom
        if rom.suffix == '.xbox360':
            # A digital title: the file is a playlist naming the actual XBLA/disc
            # install to launch, relative to the playlist's own directory.
            _logger.debug('Found .xbox360 playlist: %s', rom)
            first_line = rom.read_text().splitlines()[0].strip().lstrip('/')
            xbla_path = rom.parent / first_line
            if xbla_path.exists():
                _logger.debug('Resolved playlist to: %s', xbla_path)
                rom = xbla_path
            else:
                _logger.error('Playlist target %s not found', xbla_path)

        toml_file = self.config_dir / 'xenia-edge.config.toml'
        config: dict[str, dict[str, Any]] = {}
        if toml_file.is_file():
            try:
                config = toml.load(toml_file)
            except Exception:
                _logger.exception('Failed to parse Xenia config TOML')

        guest_refresh = self.config.get_str('xenia_edge_guest_refresh_rate', '60hz')
        vsync_enabled = self.config.get_bool('xenia_edge_vsync', True)

        config.update(
            APU={'apu': self.config.get_str('xenia_edge_apu', 'alsa')},
            CPU={
                'break_on_unimplemented_instructions': False,
                'disable_context_promotion': self.config.get_bool('xenia_edge_disable_context_promotion', False),
            },
            Content={'license_mask': self.config.get_int('xenia_edge_license', 1)},
            Console={
                'internal_display_resolution': self.config.get_int('xenia_edge_resolution', 8),
                'user_country': self.config.get_int('xenia_edge_country', 103),
                'user_language': self.config.get_int('xenia_edge_language', 1),
                'widescreen': self.config.get_bool('xenia_edge_widescreen', True),
                'use_50Hz_mode': guest_refresh == '50hz',
            },
            Display={
                'fullscreen': True,
                'postprocess_scaling_and_sharpening': self.config.get_str(
                    'xenia_edge_postprocess_scaling_and_sharpening', 'bilinear'
                ),
                'postprocess_antialiasing': self.config.get_str('xenia_edge_postprocess_antialiasing', 'none'),
                'postprocess_ffx_cas_additional_sharpness': self.config.get(
                    'xenia_edge_postprocess_ffx_cas_additional_sharpness', 0.0
                ),
                'postprocess_ffx_fsr_sharpness_reduction': self.config.get(
                    'xenia_edge_postprocess_ffx_fsr_sharpness_reduction', 0.2
                ),
                'present_letterbox': True,
            },
            General={
                'discord': False,
                'apply_patches': self.config.get_bool('xenia_edge_patches'),
            },
            GPU={
                'gpu': 'vulkan',
                'framerate_limit': self.config.get_int('xenia_edge_vsync_fps', 0),
                'texture_cache_memory_limit_hard': self.config.get_int('xenia_edge_limit_hard', 768),
                'texture_cache_memory_limit_render_to_texture': self.config.get_int(
                    'xenia_edge_limit_render_to_texture', 24
                ),
                'texture_cache_memory_limit_soft': self.config.get_int('xenia_edge_limit_soft', 384),
                'texture_cache_memory_limit_soft_lifetime': self.config.get_int('xenia_edge_limit_soft_lifetime', 30),
                'render_target_path': self.config.get_str('xenia_edge_render_target_path', 'performance'),
                'occlusion_query': self.config.get_str('xenia_edge_occlusion_query', 'fast'),
                'precise_interpolation': self.config.get_bool('xenia_edge_precise_interpolation', True),
                'async_shader_compilation': self.config.get_bool('xenia_edge_async_shader_compilation', True),
                # true upscaling, same factor on both axes
                'draw_resolution_scale_x': self.config.get_int('xenia_edge_resolution_scale', 1),
                'draw_resolution_scale_y': self.config.get_int('xenia_edge_resolution_scale', 1),
                'guest_display_refresh_cap': guest_refresh != 'uncapped',
            },
            HID={
                'guide_button': False,
                'hid': 'sdl',
                'left_stick_deadzone_percentage': self.config.get('xenia_edge_deadzone_left', 0.0),
                'right_stick_deadzone_percentage': self.config.get('xenia_edge_deadzone_right', 0.0),
                'vibration': self.config.get_bool('xenia_edge_vibration', True),
            },
            Linux={'use_gamemode': False, 'use_mangohud': False},
            Memory={'protect_zero': False},
            Storage={
                'storage_root': str(self.config_dir),
                'content_root': str(_XBOX360_SAVES),
                'cache_root': str(xenia_cache),
                'mount_scratch': True,
                'mount_cache': self.config.get_bool('xenia_edge_cache', True),
            },
            UI={
                'headless': self.config.get_bool('xenia_edge_headless'),
                'show_achievement_notification': self.config.get_bool('xenia_edge_achievement'),
            },
            Vulkan={
                'vulkan_sparse_shared_memory': False,
                'vulkan_allow_present_mode_immediate': not vsync_enabled,
            },
        )

        with toml_file.open('w') as f:
            toml.dump(config, f)

        args: list[str | Path] = [_XENIA_EDGE_BIN]
        if not configure_emulator(rom):
            args.append(rom)

        return Command(
            args,
            env={
                'SDL_JOYSTICK_HIDAPI': '0',
                'XDG_DATA_HOME': CONFIGS,
            },
        )
