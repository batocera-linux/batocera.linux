from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SCREENSHOTS
from batocera_common.vulkan import VulkanInfo, get_vulkan_info
from batocera_launch import Command, Emulator, HotkeysContext, guns_need_crosses

if TYPE_CHECKING:
    from batocera_launch import Controller

_logger: Final = logging.getLogger(__name__)

_NVRAM_SRC: Final = Path('/usr/share/sm2-emu/nvram')

_GEAR_UP_INPUTS: Final = ['pagedown', 'r1', 'right_shoulder']  # right paddle
_GEAR_DOWN_INPUTS: Final = ['pageup', 'l1', 'left_shoulder']  # left paddle


def _wheel_button_id(pad: Controller | None, name_or_names: str | list[str], /) -> int:
    if pad is None:
        return -1
    names = [name_or_names] if isinstance(name_or_names, str) else name_or_names
    for name in names:
        if (input := pad.inputs.get(name)) is not None and input.type == 'button':
            return int(input.id)
    return -1


def _ini_bool(value: bool) -> str:
    return 'true' if value else 'false'


def _merge_ini(existing_text: str, managed: dict[str, str]) -> str:
    """Update `managed` keys in place, leave every other line (wheel calibration,
    window size) untouched."""
    remaining = dict(managed)
    lines: list[str] = []

    for line in existing_text.splitlines():
        stripped = line.strip()
        key = stripped.split('=', 1)[0].strip() if not stripped.startswith('#') and '=' in stripped else None
        if key in remaining:
            lines.append(f'{key} = {remaining.pop(key)}')
        else:
            lines.append(line)

    lines.extend(f'{key} = {value}' for key, value in remaining.items())
    return '\n'.join((*lines, ''))


async def _resolve_graphics_backend(requested: str) -> tuple[str, VulkanInfo | None]:
    if requested != 'vulkan':
        return requested, None

    vulkan_info = await get_vulkan_info()
    if not vulkan_info:
        _logger.debug('Vulkan driver is not available on the system. Falling back to OpenGL.')
        return 'opengl', None

    if vulkan_info.version is not None and vulkan_info.version >= '1.3':
        _logger.debug('Vulkan driver is available. Using Vulkan version: %s', vulkan_info.version)
        return 'vulkan', vulkan_info

    _logger.debug('Vulkan version %s is lower than 1.3. Falling back to OpenGL.', vulkan_info.version)
    return 'opengl', None


def _resolve_gpu(backend: str, vulkan_info: VulkanInfo | None) -> str:
    if backend != 'vulkan' or not vulkan_info or not (discrete_gpu := vulkan_info.active_discrete_gpu):
        return ''

    return discrete_gpu.name or ''


def _seed_nvram(dest_dir: Path) -> None:
    if not _NVRAM_SRC.is_dir():
        return

    for item in _NVRAM_SRC.iterdir():
        dest = dest_dir / item.name
        if not dest.exists():
            shutil.copy2(item, dest)


@cached_dataclass
class Sm2Emu(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sm2-emu',
            'keys': {'exit': 'KEY_F9', 'screenshot': 'KEY_F12'},
        }

    @cached_property
    def nvram_dir(self) -> Path:
        return self.saves_dir / self.name

    @cached_property
    def screenshot_dir(self) -> Path:
        return SCREENSHOTS / self.name

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.nvram_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        _seed_nvram(self.nvram_dir)

        use_guns = self.config.use_guns
        graphics_backend, vulkan_info = await _resolve_graphics_backend(
            self.config.get_str('sm2_graphics_backend', 'opengl')
        )

        wheel = next(
            (pad for pad in self.controllers if self.config.use_wheels and pad.device_path in self.wheels), None
        )
        es_wheel_rotation = self.config.get_str('wheel_rotation') if 'wheel_rotation' in self.config else None

        wheel_managed = (
            {
                'wheel_button_start': str(_wheel_button_id(wheel, 'start')),
                'wheel_button_coin': str(_wheel_button_id(wheel, 'select')),
                'wheel_button_1': str(_wheel_button_id(wheel, 'b')),
                'wheel_button_2': str(_wheel_button_id(wheel, 'a')),
                'wheel_button_3': str(_wheel_button_id(wheel, 'y')),
                'wheel_button_4': str(_wheel_button_id(wheel, 'x')),
                'wheel_button_gear_up': str(_wheel_button_id(wheel, _GEAR_UP_INPUTS)),
                'wheel_button_gear_down': str(_wheel_button_id(wheel, _GEAR_DOWN_INPUTS)),
                'wheel_button_test': str(_wheel_button_id(wheel, 'test')),
                'wheel_button_service': str(_wheel_button_id(wheel, 'service')),
                'wheel_button_menu': str(_wheel_button_id(wheel, 'hotkey')),
            }
            if wheel is not None
            else {}
        )
        if es_wheel_rotation is not None:
            wheel_managed['wheel_steer_degrees'] = es_wheel_rotation
            wheel_managed['wheel_lock_degrees'] = es_wheel_rotation

        managed = {
            'fullscreen': 'true',
            'vsync': _ini_bool(self.config.get_bool('sm2_vsync', False)),
            'show_fps': 'false',  # covered by the hud/hud_corner features instead
            'lightgun': _ini_bool(use_guns),
            'lightgun_crosshair': _ini_bool(use_guns and guns_need_crosses(self.guns)),
            'lightgun_recoil': _ini_bool(self.config.get_bool('sm2_lightgun_recoil', True)),
            'lightgun_recoil_strength': self.config.get_str('sm2_lightgun_recoil_strength', '60'),
            'wheel_ffb': _ini_bool(self.config.get_bool('sm2_wheel_ffb', True)),
            'wheel_ffb_strength': self.config.get_str('sm2_wheel_ffb_strength', '30'),
            'wheel_rumble': _ini_bool(self.config.get_bool('sm2_wheel_rumble', True)),
            'wheel_rumble_strength': self.config.get_str('sm2_wheel_rumble_strength', '40'),
            **wheel_managed,
            'pad_rumble': _ini_bool(self.config.get_bool('sm2_pad_rumble', True)),
            'pad_rumble_strength': self.config.get_str('sm2_pad_rumble_strength', '60'),
            'rom_dir': str(self.roms_dir),
            'nvram_dir': str(self.nvram_dir),
            'screenshot_dir': str(self.screenshot_dir),
            'graphics_backend': graphics_backend,
            'gpu': _resolve_gpu(graphics_backend, vulkan_info),
            'render_scale': self.config.get_str('sm2_render_scale', '1'),
            'scaling_method': self.config.get_str('sm2_scaling_method', 'sharp'),
            'aspect_mode': self.config.get_str('sm2_aspect_mode', '4:3'),
            'texture_filter': self.config.get_str('sm2_texture_filter', 'faithful'),
            'anisotropy': self.config.get_str('sm2_anisotropy', '4'),
            'upscale_2d': self.config.get_str('sm2_upscale_2d', 'faithful'),
            'crt_enabled': _ini_bool(self.config.get_bool('sm2_crt_enabled', False)),
            'crt_scanline_strength': self.config.get_str('sm2_crt_scanline_strength', '40'),
            'crt_mask_strength': self.config.get_str('sm2_crt_mask_strength', '30'),
            'crt_glow_strength': self.config.get_str('sm2_crt_glow_strength', '20'),
            'crt_curvature': self.config.get_str('sm2_crt_curvature', '0'),
        }

        config_path = self.config_dir / 'sm2-emu.ini'
        existing_text = config_path.read_text() if config_path.exists() else ''
        config_path.write_text(_merge_ini(existing_text, managed))

        return Command(
            [
                '/usr/bin/sm2-emu',
                '--config',
                self.config_dir,
                self.rom,
            ],
            env={
                'SDL_JOYSTICK_HIDAPI': '0',
                'XDG_CONFIG_HOME': self.config_dir.parent,
            },
        )
