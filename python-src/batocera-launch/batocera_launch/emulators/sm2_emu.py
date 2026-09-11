from __future__ import annotations

import platform
from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext, guns_need_crosses

if TYPE_CHECKING:
    from pathlib import Path


def _ini_bool(value: bool) -> str:
    return 'true' if value else 'false'


def _default_graphics_backend() -> str:
    return 'software' if not platform.machine().lower().startswith('x86') else 'vulkan'


def _merge_ini(existing_text: str, managed: dict[str, str]) -> str:
    """Update `managed` keys in place, leave every other line (wheel calibration,
    window size, gpu) untouched."""
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

        use_guns = self.config.use_guns

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
            'pad_rumble': _ini_bool(self.config.get_bool('sm2_pad_rumble', True)),
            'pad_rumble_strength': self.config.get_str('sm2_pad_rumble_strength', '60'),
            'rom_dir': str(self.roms_dir),
            'nvram_dir': str(self.nvram_dir),
            'screenshot_dir': str(self.screenshot_dir),
            'graphics_backend': self.config.get_str('sm2_graphics_backend', _default_graphics_backend()),
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
