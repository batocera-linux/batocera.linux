from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, SAVES
from batocera_common.vulkan import (
    get_default_gpu_name,
    get_discrete_gpu_name,
    has_discrete_gpu,
    is_available as vulkan_is_available,
)
from batocera_launch import Command, Emulator, HotkeysContext

_logger = logging.getLogger(__name__)

_XEMU_BIN: Final = Path('/usr/bin/xemu')
_XEMU_SAVES: Final = SAVES / 'xbox'


@cached_dataclass
class Xemu(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'xemu',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def saves_dir(self) -> Path:
        # shared between the xbox and chihiro systems - same HDD image either way
        return _XEMU_SAVES

    @cached_property
    def in_game_ratio(self) -> float:
        if self.config.get_str('xemu_scaling') == 'stretch' or self.config.get_str('xemu_aspect') == '16x9':
            return 16 / 9
        return 4 / 3

    async def configure(self) -> Command:
        config_file = self.config_dir / 'xemu.toml'

        ini_config = CaseSensitiveConfigParser(interpolation=None)
        if config_file.exists():
            try:
                ini_config.read(config_file, encoding='utf_8_sig')
            except Exception:
                _logger.exception('Failed to read existing xemu.toml, starting fresh')

        for section in (
            'general',
            'sys',
            'sys.files',
            'audio',
            'display',
            'display.quality',
            'display.vulkan',
            'display.window',
            'display.ui',
            'input.bindings',
            'net',
            'net.udp',
        ):
            if not ini_config.has_section(section):
                ini_config.add_section(section)

        ini_config.set('general', 'skip_boot_anim', self.config.get_str('xemu_bootanim', 'false'))
        ini_config.set('general', 'show_welcome', 'false')  # disable welcome screen on first launch
        ini_config.set('general', 'screenshot_dir', '"/userdata/screenshots"')

        ini_config.set('sys', 'mem_limit', f'"{self.config.get_str("xemu_memory", "64")}"')
        if self.system == 'chihiro':
            ini_config.set('sys', 'mem_limit', '"128"')
            ini_config.set('sys.files', 'flashrom_path', '"/userdata/bios/cerbios.bin"')
        else:
            ini_config.set('sys.files', 'flashrom_path', '"/userdata/bios/Complex_4627.bin"')

        ini_config.set('sys.files', 'bootrom_path', '"/userdata/bios/mcpx_1.0.bin"')
        ini_config.set('sys.files', 'hdd_path', '"/userdata/saves/xbox/xbox_hdd.qcow2"')
        ini_config.set('sys.files', 'eeprom_path', '"/userdata/saves/xbox/xemu_eeprom.bin"')
        ini_config.set('sys.files', 'dvd_path', f'"{self.rom}"')

        ini_config.set('audio', 'use_dsp', self.config.get_str('xemu_use_dsp', 'false'))

        renderer = self.config.get_str('xemu_api', 'VULKAN')
        if self.system == 'chihiro':
            renderer = 'OPENGL'
            _logger.debug('Chihiro system, defaulting to OpenGL due to a Xemu bug')
        ini_config.set('display', 'renderer', f'"{renderer}"')

        if renderer == 'VULKAN' and vulkan_is_available():
            gpu_name = None
            if has_discrete_gpu():
                _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                gpu_name = get_discrete_gpu_name()
                if gpu_name:
                    _logger.debug('Using Discrete GPU Name: %s for Xemu', gpu_name)
                else:
                    _logger.debug("Discrete GPU detected but couldn't get name.")

            if not gpu_name:
                _logger.debug('Using default GPU for Xemu')
                gpu_name = get_default_gpu_name()

            # empty string is the worst-case fallback: it triggers xemu's own auto-detection
            ini_config.set('display.vulkan', 'preferred_physical_device', f'"{gpu_name}"' if gpu_name else '""')

        ini_config.set('display.quality', 'surface_scale', self.config.get_str('xemu_render', '1'))
        ini_config.set('display.window', 'fullscreen_on_startup', 'true')
        ini_config.set('display.window', 'startup_size', f'"{self.resolution.width}x{self.resolution.height}"')
        ini_config.set('display.window', 'vsync', self.config.get_str('xemu_vsync', 'true'))
        ini_config.set('display.ui', 'show_menubar', 'false')
        ini_config.set('display.ui', 'fit', f'"{self.config.get_str("xemu_scaling", "scale")}"')
        ini_config.set('display.ui', 'aspect_ratio', f'"{self.config.get_str("xemu_aspect", "auto")}"')

        for i in range(1, 5):
            ini_config.remove_option('input.bindings', f'port{i}')
        for nplayer, pad in enumerate(self.controllers[:4], start=1):
            ini_config.set('input.bindings', f'port{nplayer}', f'"{pad.guid}"')

        # https://github.com/xemu-project/xemu/blob/master/config_spec.yml
        network_type = self.config.get_str('xemu_networktype')
        if network_type:
            ini_config.set('net', 'enable', 'true')
            ini_config.set('net', 'backend', f'"{network_type}"')
        else:
            ini_config.set('net', 'enable', 'false')
        # if left empty in ES, the existing udp settings (if any) are left untouched
        udp_remote = self.config.get_str('xemu_udpremote')
        if udp_remote:
            ini_config.set('net.udp', 'remote_addr', f'"{udp_remote}"')
        udp_bind = self.config.get_str('xemu_udpbind')
        if udp_bind:
            ini_config.set('net.udp', 'bind_addr', f'"{udp_bind}"')

        config_file.parent.mkdir(parents=True, exist_ok=True)
        with config_file.open('w') as fp:
            ini_config.write(fp)

        if not (self.saves_dir / 'xbox_hdd.qcow2').exists():
            self.saves_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile('/usr/share/xemu/data/xbox_hdd.qcow2', self.saves_dir / 'xbox_hdd.qcow2')

        return Command(
            [_XEMU_BIN, '-config_path', config_file],
            env={'XDG_CONFIG_HOME': CONFIGS, 'LC_NUMERIC': 'C'},
        )
