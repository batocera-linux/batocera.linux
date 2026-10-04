from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

import toml

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, SCREENSHOTS
from batocera_common.vulkan import get_vulkan_info
from batocera_launch import Command, Emulator, HotkeysContext

from .bindings import DEPRECATED, ControlsBuilder

if TYPE_CHECKING:
    from collections.abc import Sequence

    from batocera_launch import Controller
    from batocera_launch.devices.gun import Gun

_logger: Final = logging.getLogger(__name__)

_XEMU_BIN: Final = Path('/usr/bin/xemu-chihiro')
_CROSSHAIRS: Final = Path('/usr/share/xemu-chihiro/crosshairs')
_BIOS_DIR: Final = BIOS / 'chihiro'

# SDL scancode, with Shift, Ctrl and Alt in bits 16-18; kept in step with the hotkeygen keys below
_HOTKEYS: Final = {
    'settings': 58,  # F1
    'quick_menu': 59,  # F2
    'quit': 131092,  # Ctrl+Q
    'pause': 131091,  # Ctrl+P
    'reset': 131093,  # Ctrl+R
    'quick_save1': 65598,  # Shift+F5
    'quick_load1': 62,  # F5
    'screenshot': 69,  # F12
}


def _section(config: dict[str, Any], path: str, /) -> dict[str, Any]:
    for key in path.split('.'):
        config = config.setdefault(key, {})
    return config


@cached_dataclass
class XemuChihiro(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'xemu-chihiro',
            'keys': {
                'exit': ['KEY_LEFTCTRL', 'KEY_Q'],
                'menu': 'KEY_F2',
                'pause': ['KEY_LEFTCTRL', 'KEY_P'],
                'reset': ['KEY_LEFTCTRL', 'KEY_R'],
                'save_state': ['KEY_LEFTSHIFT', 'KEY_F5'],
                'restore_state': 'KEY_F5',
                'screenshot': 'KEY_F12',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        if (
            self.config.get_str('xemu_chihiro_scaling') == 'stretch'
            or self.config.get_str('xemu_chihiro_aspect') == '16x9'
        ):
            return 16 / 9
        return 4 / 3

    @cached_property
    def wheel(self) -> Controller | None:
        if not self.config.use_wheels:
            return None
        return next((pad for pad in self.controllers[:4] if pad.device_path in self.wheels), None)

    async def configure(self) -> Command:
        config_file = self.config_dir / 'xemu.toml'

        config: dict[str, Any] = {}
        if config_file.is_file():
            try:
                config = toml.load(config_file)
            except Exception:
                _logger.exception('Failed to read existing xemu.toml, starting fresh')

        general = _section(config, 'general')
        general['show_welcome'] = False
        general['screenshot_dir'] = str(SCREENSHOTS)
        _section(config, 'general.updates')['check'] = False

        _section(config, 'input.hotkeys').update(_HOTKEYS)

        _section(config, 'sys')['default_machine'] = 'chihiro'
        _section(config, 'sys.files')['dvd_path'] = str(self.rom)

        perf = _section(config, 'perf')
        perf['cache_shaders'] = True
        perf['optimizations'] = self.config.get_bool('xemu_chihiro_gpu_boost', True)
        perf['native_sse'] = self.config.get_bool('xemu_chihiro_cpu_boost', True)
        perf['real_hw_speed'] = self.config.get_bool('xemu_chihiro_real_hw_speed')
        perf['shader_seeding'] = self.config.get_bool('xemu_chihiro_shader_seeding', True)
        _section(config, 'audio')['use_dsp'] = self.config.get_bool('xemu_chihiro_use_dsp')

        await self._configure_display(config)
        self._configure_chihiro(config)
        self._configure_controls(config)

        config_file.parent.mkdir(parents=True, exist_ok=True)
        with config_file.open('w') as fp:
            toml.dump(config, fp)

        self.saves_dir.mkdir(parents=True, exist_ok=True)

        return Command(
            [_XEMU_BIN, '-config_path', config_file],
            env={'LC_NUMERIC': 'C'},
        )

    async def _configure_display(self, config: dict[str, Any], /) -> None:
        renderer = self.config.get_str('xemu_chihiro_api', 'OPENGL')
        display = _section(config, 'display')
        display['renderer'] = renderer
        display['crt_gamma'] = self.config.get_float('xemu_chihiro_gamma', 1.0)

        if renderer == 'VULKAN' and (vulkan_info := await get_vulkan_info()):
            gpu = vulkan_info.active_discrete_gpu or vulkan_info.default_gpu
            # empty lets xemu pick the device itself
            _section(config, 'display.vulkan')['preferred_physical_device'] = (gpu.name if gpu else None) or ''

        _section(config, 'display.quality')['surface_scale'] = self.config.get_int('xemu_chihiro_render', 1)

        window = _section(config, 'display.window')
        window['fullscreen_on_startup'] = True
        window['vsync'] = self.config.get_bool('xemu_chihiro_vsync', True)

        ui = _section(config, 'display.ui')
        ui['show_menubar'] = False
        ui['fit'] = self.config.get_str('xemu_chihiro_scaling', 'scale')
        ui['aspect_ratio'] = self.config.get_str('xemu_chihiro_aspect', 'auto')

    def _configure_chihiro(self, config: dict[str, Any], /) -> None:
        # the media board flash and the EEPROMs are found next to the BIOS
        roms = _section(config, 'chihiro.roms')
        roms['bios_path'] = str(_BIOS_DIR / 'chihiro_xbox_bios.bin')
        for key in ('mediaboard_path', 'ic10_path', 'ic11_path', 'pc20_path'):
            roms[key] = ''
        net_firmware = _BIOS_DIR / 'ver1305.bin'
        roms['net_firmware_path'] = str(net_firmware) if net_firmware.is_file() else ''

        settings = _section(config, 'chihiro.settings')
        settings['freeplay'] = self.config.get_bool('xemu_chihiro_freeplay')
        settings['region'] = self.config.get_str('xemu_chihiro_region', 'ex')
        settings['dimm_size'] = 'auto'
        settings['board_type'] = 'auto'
        # batocera draws the gun borders
        settings['sinden_border'] = False

        settings['force_feedback'] = self.config.get_bool('xemu_chihiro_ffb', True)
        settings['ffb_strength'] = self.config.get_int('xemu_chihiro_ffb_strength', 100)
        settings['ffb_invert'] = self.config.get_bool('xemu_chihiro_ffb_invert')
        settings['wheel_weight'] = self.config.get_int('xemu_chihiro_wheel_weight', 40)
        autocenter = self.config.get_int('xemu_chihiro_wheel_autocenter', 50)
        settings['wheel_autocenter'] = autocenter > 0
        if autocenter > 0:
            settings['wheel_autocenter_strength'] = autocenter
        # batocera sets the wheel's range itself, so the whole wheel is the game's lock
        if self.wheel is not None:
            settings['wheel_rotation'] = 0

        _section(config, 'chihiro.card_reader')['enable'] = self.config.get_bool('xemu_chihiro_card_reader', True)

        link = _section(config, 'chihiro.link')
        link['enable'] = self.config.get_bool('xemu_chihiro_link')
        link['cabinets'] = self.config.get_int('xemu_chihiro_link_cabinets', 2)
        link['cabinet'] = self.config.get_int('xemu_chihiro_link_cabinet', 1)
        link['host'] = self.config.get_str('xemu_chihiro_link_host', '').strip()
        port = self.config.get_str('xemu_chihiro_link_port', '').strip()
        link['port'] = int(port) if port.isdigit() else 9100

    def _configure_controls(self, config: dict[str, Any], /) -> None:
        bindings = _section(config, 'input.bindings')
        for port in range(1, 5):
            bindings.pop(f'port{port}', None)
        # the event node tells twins apart
        for port, pad in enumerate(self.controllers[:4], start=1):
            bindings[f'port{port}'] = f'{pad.guid}#{pad.device_path}'

        guns: Sequence[Gun] = self.guns if self.config.use_guns else ()
        settings = _section(config, 'chihiro.settings')
        settings['pointer_devices'] = bool(guns)
        settings['lightgun_mode'] = bool(guns)
        # a grab would hide the gun buttons from evmapy
        settings['pointer_grab'] = False

        crosshairs = self.config.get_bool('xemu_chihiro_crosshairs', self.guns_need_crosses)
        jvs = _section(config, 'chihiro.jvs')
        jvs_p2 = _section(config, 'chihiro.jvs_p2')
        for player, (section, crosshair) in enumerate(((jvs, 'p1_crosshair.png'), (jvs_p2, 'p2_crosshair.png'))):
            gun = guns[player] if player < len(guns) else None
            if gun is not None:
                section['pointer_device'] = f'node:{gun.node}'
            else:
                section['pointer_device'] = 'mouse' if player == 0 else ''
            section['crosshair_path'] = str(_CROSSHAIRS / crosshair) if gun is not None and crosshairs else ''

        for path, keys in DEPRECATED.items():
            section = _section(config, path)
            for key in keys:
                section.pop(key, None)

        for path, values in ControlsBuilder(self.controllers[:4], self.wheel, guns).build().items():
            _section(config, path).update(values)
