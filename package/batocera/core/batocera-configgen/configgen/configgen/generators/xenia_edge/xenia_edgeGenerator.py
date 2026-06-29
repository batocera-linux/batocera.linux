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

XENIA_EDGE_BIN     = Path('/usr/bin/xenia-edge/xenia_edge')

class XeniaEdgeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xenia-edge",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        xeniaConfig = CONFIGS / 'Xenia'
        xeniaCache  = CACHE  / 'xenia-edge'
        xeniaSaves  = SAVES  / 'xbox360'

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

        xeniaPatches = xeniaConfig / 'patches'
        mkdir_if_not_exists(xeniaPatches)

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

        toml_file = xeniaConfig / 'xenia-edge.config.toml'
        config: dict[str, dict[str, Any]] = {}
        if toml_file.is_file():
            with toml_file.open() as f:
                try:
                    config = toml.load(f)
                except Exception as e:
                    _logger.error("Failed to parse Xenia config TOML: %s", e)

        def get_section(name: str) -> dict[str, Any]:
            if name not in config:
                config[name] = {}
            return config[name]

        apu_sec = get_section('APU')
        apu_sec['apu'] = system.config.get('xenia_edge_apu', 'alsa')

        cpu_sec = get_section('CPU')
        cpu_sec['break_on_unimplemented_instructions'] = False
        cpu_sec['disable_context_promotion'] = system.config.get_bool('xenia_edge_disable_context_promotion', False)

        content_sec = get_section('Content')
        content_sec['license_mask'] = system.config.get_int('xenia_edge_license', 1)

        console_sec = get_section('Console')
        console_sec['internal_display_resolution'] = system.config.get_int('xenia_edge_resolution', 8)
        console_sec['user_country'] = system.config.get_int('xenia_edge_country', 103)
        console_sec['user_language'] = system.config.get_int('xenia_edge_language', 1)
        console_sec['widescreen'] = system.config.get_bool('xenia_edge_widescreen', True)

        display_sec = get_section('Display')
        display_sec['fullscreen'] = True
        display_sec['postprocess_scaling_and_sharpening'] = system.config.get('xenia_edge_postprocess_scaling_and_sharpening', 'bilinear')
        display_sec['postprocess_antialiasing'] = system.config.get('xenia_edge_postprocess_antialiasing', 'none')
        display_sec['postprocess_ffx_cas_additional_sharpness'] = float(system.config.get('xenia_edge_postprocess_ffx_cas_additional_sharpness', '0.0'))
        display_sec['postprocess_ffx_fsr_sharpness_reduction'] = float(system.config.get('xenia_edge_postprocess_ffx_fsr_sharpness_reduction', '0.2'))
        display_sec['present_letterbox'] = True

        general_sec = get_section('General')
        general_sec['discord'] = False
        if system.config.get_bool('xenia_edge_patches'):
            general_sec['apply_patches'] = True
        elif 'apply_patches' not in general_sec:
            general_sec['apply_patches'] = False

        gpu_sec = get_section('GPU')
        gpu_sec['gpu'] = 'vulkan'

        gpu_sec['framerate_limit'] = system.config.get_int('xenia_edge_vsync_fps', 0)
        gpu_sec['texture_cache_memory_limit_hard'] = system.config.get_int('xenia_edge_limit_hard', 768)
        gpu_sec['texture_cache_memory_limit_render_to_texture'] = system.config.get_int('xenia_edge_limit_render_to_texture', 24)
        gpu_sec['texture_cache_memory_limit_soft'] = system.config.get_int('xenia_edge_limit_soft', 384)
        gpu_sec['texture_cache_memory_limit_soft_lifetime'] = system.config.get_int('xenia_edge_limit_soft_lifetime', 30)
        gpu_sec['render_target_path'] = system.config.get('xenia_edge_render_target_path', 'performance')
        gpu_sec['occlusion_query'] = system.config.get('xenia_edge_occlusion_query', 'fast')
        gpu_sec['precise_interpolation'] = system.config.get_bool('xenia_edge_precise_interpolation', True)
        gpu_sec['async_shader_compilation'] = system.config.get_bool('xenia_edge_async_shader_compilation', True)

        # Resolution Scaling Multiplier (Sets true upscaling factors)
        res_scale = system.config.get_int('xenia_edge_resolution_scale', 1)
        gpu_sec['draw_resolution_scale_x'] = res_scale
        gpu_sec['draw_resolution_scale_y'] = res_scale

        guest_refresh = system.config.get('xenia_edge_guest_refresh_rate', '60hz')
        if guest_refresh == 'uncapped':
            gpu_sec['guest_display_refresh_cap'] = False
            console_sec['use_50Hz_mode'] = False
        elif guest_refresh == '50hz':
            gpu_sec['guest_display_refresh_cap'] = True
            console_sec['use_50Hz_mode'] = True
        else:  # 60hz (Default)
            gpu_sec['guest_display_refresh_cap'] = True
            console_sec['use_50Hz_mode'] = False

        hid_sec = get_section('HID')
        hid_sec['guide_button'] = False
        hid_sec['hid'] = 'sdl'
        hid_sec['left_stick_deadzone_percentage'] = float(system.config.get('xenia_edge_deadzone_left', '0.0'))
        hid_sec['right_stick_deadzone_percentage'] = float(system.config.get('xenia_edge_deadzone_right', '0.0'))
        hid_sec['vibration'] = system.config.get_bool('xenia_edge_vibration', True)

        linux_sec = get_section('Linux')
        linux_sec['use_gamemode'] = False
        linux_sec['use_mangohud'] = False

        memory_sec = get_section('Memory')
        memory_sec['protect_zero'] = False

        storage_sec = get_section('Storage')
        storage_sec['storage_root'] = str(xeniaConfig)
        storage_sec['content_root'] = str(xeniaSaves)
        storage_sec['cache_root'] = str(xeniaCache)
        storage_sec['mount_scratch'] = True
        storage_sec['mount_cache'] = system.config.get_bool('xenia_edge_cache', True)

        ui_sec = get_section('UI')
        ui_sec['headless'] = system.config.get_bool('xenia_edge_headless')
        ui_sec['show_achievement_notification'] = system.config.get_bool('xenia_edge_achievement')

        vulkan_sec = get_section('Vulkan')
        vulkan_sec['vulkan_sparse_shared_memory'] = False
        vsync_enabled = system.config.get_bool('xenia_edge_vsync', True)
        vulkan_sec['vulkan_allow_present_mode_immediate'] = not vsync_enabled

        # Save the structured config
        with toml_file.open('w') as f:
            toml.dump(config, f)

        commandArray = [str(XENIA_EDGE_BIN)]

        if not configure_emulator(rom):
            commandArray.append(str(rom))

        environment = {
            'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
            'SDL_JOYSTICK_HIDAPI': '0',
            'XDG_DATA_HOME': CONFIGS
        }

        return Command.Command(array=commandArray, env=environment)

    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get("xenia_edge_widescreen") != "False":
            return 16/9
        return 4/3
