from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import toml

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, configure_emulator, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils import vulkan
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

XENIA_EDGE_BIN     = Path('/usr/xenia_edge/xenia_edge')
XENIA_EDGE_PATCHES_SRC = Path('/usr/xenia_edge/patches')  # patches packagées (lecture seule)


class XeniaEdgeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xenia-edge",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        xeniaConfig = CONFIGS / 'xenia_edge'
        xeniaCache  = CACHE  / 'xenia_edge'
        xeniaSaves  = SAVES  / 'xbox360'

        # Vulkan is mandatory for xenia-edge on Linux
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            vulkan_version = vulkan.get_version()
            if vulkan_version <= "1.3":
                _logger.warning("Vulkan version %s may not meet xenia-edge requirements (1.3+)", vulkan_version)
        else:
            _logger.error("*** Vulkan driver required by xenia-edge is not available! ***")
            sys.exit(1)

        mkdir_if_not_exists(xeniaConfig)
        mkdir_if_not_exists(xeniaCache)
        mkdir_if_not_exists(xeniaSaves)

        # xenia-edge cherche les patches dans storage_root/patches/
        # = /userdata/system/configs/xenia_edge/patches/ (persistant, hors système)
        xeniaPatches = xeniaConfig / 'patches'
        mkdir_if_not_exists(xeniaPatches)

        # resolve .xbox360 playlists (same format as xenia-canary)
        if rom.suffix == '.xbox360':
            _logger.debug('Found .xbox360 playlist: %s', rom)
            with rom.open() as f:
                first_line = f.readlines(1)[0].strip('\n').strip('\r').lstrip('/')
            xbla_path = rom.parent / first_line
            if xbla_path.exists():
                _logger.debug('Resolved playlist to: %s', xbla_path)
                rom = xbla_path
            else:
                _logger.error('Playlist target %s not found', xbla_path)

        # --- Build TOML config ---
        toml_file = xeniaConfig / 'xenia-edge.config.toml'
        config: dict[str, dict[str, Any]] = {}
        if toml_file.is_file():
            with toml_file.open() as f:
                config = toml.load(f)

        # APU
        config['APU'] = {
            'apu': system.config.get('xenia_apu', 'alsa')
        }

        # CPU
        config['CPU'] = {
            'break_on_unimplemented_instructions': False
        }

        # Content — XBLA license
        config['Content'] = {
            'license_mask': system.config.get_int('xenia_license', 1)
        }

        # Display — always fullscreen, configurable internal resolution + post-processing
        config['Display'] = {
            'fullscreen': True,
            'internal_display_resolution': system.config.get_int('xenia_resolution', 8),
            'postprocess_scaling_and_sharpening': system.config.get('xenia_postprocess_scaling_and_sharpening', 'bilinear'),
            'postprocess_antialiasing': system.config.get('xenia_postprocess_antialiasing', 'none'),
            'postprocess_ffx_cas_additional_sharpness': float(system.config.get('xenia_postprocess_ffx_cas_additional_sharpness', '0.0')),
            'postprocess_ffx_fsr_sharpness_reduction': float(system.config.get('xenia_postprocess_ffx_fsr_sharpness_reduction', '0.2')),
        }

        # General
        if 'General' not in config:
            config['General'] = {}
        config['General']['discord'] = False
        # apply_patches : si activé dans ES on force True.
        # Si désactivé (défaut ES), on préserve la valeur du TOML pour ne pas
        # écraser ce que l'utilisateur a configuré dans l'UI xenia.
        if system.config.get_bool('xenia_patches'):
            config['General']['apply_patches'] = True
        elif 'apply_patches' not in config['General']:
            config['General']['apply_patches'] = False

        # GPU — Vulkan only on Linux
        if 'GPU' not in config:
            config['GPU'] = {}
        config['GPU']['gpu'] = 'vulkan'
        config['GPU']['vsync'] = system.config.get_bool('xenia_vsync', True)
        config['GPU']['framerate_limit'] = system.config.get_int('xenia_vsync_fps', 0)
        config['GPU']['texture_cache_memory_limit_hard'] = system.config.get_int('xenia_limit_hard', 768)
        config['GPU']['texture_cache_memory_limit_render_to_texture'] = system.config.get_int('xenia_limit_render_to_texture', 24)
        config['GPU']['texture_cache_memory_limit_soft'] = system.config.get_int('xenia_limit_soft', 384)
        config['GPU']['texture_cache_memory_limit_soft_lifetime'] = system.config.get_int('xenia_limit_soft_lifetime', 30)

        # HID — SDL for gamepad support
        config['HID'] = {
            'hid': 'sdl'
        }

        # Logging — reduce log spam
        config['Logging'] = {
            'log_level': 1
        }

        # Memory
        config['Memory'] = {
            'protect_zero': False
        }

        # Storage — all paths in /userdata
        config['Storage'] = {
            'storage_root': str(xeniaConfig),
            'content_root': str(xeniaSaves),
            'cache_root':   str(xeniaCache),
            'mount_scratch': True,
            'mount_cache':   system.config.get_bool('xenia_cache', True)
        }

        # UI
        config['UI'] = {
            'headless': system.config.get_bool('xenia_headless'),
            'show_achievement_notification': system.config.get_bool('xenia_achievement')
        }

        # Vulkan tuning
        config['Vulkan'] = {
            'vulkan_sparse_shared_memory': False
        }

        # XConfig — region / language (xenia-edge uses string names, not integers)
        config['XConfig'] = {
            'user_country':  system.config.get('xenia_country', 'United States'),
            'user_language': system.config.get('xenia_language', 'English')
        }

        with toml_file.open('w') as f:
            toml.dump(config, f)

        # Les flags is_enabled dans les .patch.toml sont gérés exclusivement par
        # l'UI de xenia-edge. Le générateur ne touche pas ces fichiers pour ne pas
        # écraser les choix de l'utilisateur à chaque lancement depuis ES.

        # --- Build command ---
        # --storage_root doit être passé en CLI (underscore) AVANT que xenia lise le TOML
        # car storage_root est résolu avant SetupConfig(), qui lit ensuite xenia-edge.config.toml
        commandArray = [
            str(XENIA_EDGE_BIN),
            f'--storage_root={xeniaConfig}',
            f'--content_root={xeniaSaves}',
            f'--cache_root={xeniaCache}',
        ]
        if not configure_emulator(rom):
            commandArray.append(str(rom))

        environment = {
            'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
            'SDL_JOYSTICK_HIDAPI': '0',
        }

        # prefer discrete NVIDIA GPU when prime offload is set up
        if Path('/var/tmp/nvidia.prime').exists():
            import os
            for var in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
                if var in os.environ:
                    del os.environ[var]
            environment.update({
                'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d',
            })

        return Command.Command(array=commandArray, env=environment)

    def getMouseMode(self, config, rom):
        return True
