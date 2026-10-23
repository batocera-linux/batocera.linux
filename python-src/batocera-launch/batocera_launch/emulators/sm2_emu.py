# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

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

# evdev codes of the gun buttons: left, right, middle, 1
_GUN_BUTTONS: Final = {'trigger': 0x110, 'reload': 0x111, 'start': 0x112, 'coin': 0x101}

_GEAR_UP_INPUTS: Final = ['pagedown', 'r1', 'right_shoulder']  # right paddle
_GEAR_DOWN_INPUTS: Final = ['pageup', 'l1', 'left_shoulder']  # left paddle

_STEER_INPUTS: Final = ['joystick1left', 'joystick1right']
_ACCEL_INPUTS: Final = ['r2', 'right_trigger']
_BRAKE_INPUTS: Final = ['l2', 'left_trigger']


def _wheel_button_id(pad: Controller | None, name_or_names: str | list[str], /) -> int:
    if pad is None:
        return -1
    names = [name_or_names] if isinstance(name_or_names, str) else name_or_names
    for name in names:
        if (input := pad.inputs.get(name)) is not None and input.type == 'button':
            return int(input.id)
    return -1


def _wheel_axis_input(pad: Controller, names: list[str], /) -> tuple[str, int] | None:
    for name in names:
        if (input := pad.inputs.get(name)) is not None and input.type == 'axis':
            return name, int(input.id)
    return None


def _wheel_axes(pad: Controller, /) -> dict[str, str]:
    steer = _wheel_axis_input(pad, _STEER_INPUTS)
    accel = _wheel_axis_input(pad, _ACCEL_INPUTS)
    brake = _wheel_axis_input(pad, _BRAKE_INPUTS)
    if steer is None and accel is None and brake is None:
        return {}  # nothing mapped, keep sm2-emu's auto-detect / gui calibration

    relaxed = pad.get_mapping_axis_relaxed_values()

    # pedals on one axis each use half of it, pressed the way es saw it pressed
    shared = accel is not None and brake is not None and accel[1] == brake[1]

    def axis_id(found: tuple[str, int] | None) -> str:
        return str(found[1]) if found is not None else '-1'

    # sm2-emu inverts a pedal that rests at the positive end, which is es's 'reversed'
    def inverted(found: tuple[str, int] | None) -> str:
        if found is None:
            return _ini_bool(False)
        if shared:
            return _ini_bool(int(pad.inputs[found[0]].value) < 0)
        return _ini_bool((axis := relaxed.get(found[0])) is not None and axis['reversed'])

    return {
        'wheel_steer_axis': axis_id(steer),
        'wheel_accel_axis': axis_id(accel),
        'wheel_brake_axis': axis_id(brake),
        'wheel_accel_invert': inverted(accel),
        'wheel_brake_invert': inverted(brake),
        'wheel_accel_half': _ini_bool(shared),
        'wheel_brake_half': _ini_bool(shared),
    }


def _ini_bool(value: bool) -> str:
    return 'true' if value else 'false'


def _merge_ini(existing_text: str, managed: dict[str, str]) -> str:
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
    cpu_cluster = 'fast'  # one interpreter thread; little cores only slow it

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sm2-emu',
            'keys': {
                'exit': 'KEY_F9',
                'menu': 'KEY_F10',
                'pause': 'KEY_P',
                'screenshot': 'KEY_F12',
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F7',
                'rewind': 'KEY_BACKSPACE',
                'fastforward': 'KEY_TAB',
                'coin': 'KEY_5',
            },
        }

    @cached_property
    def nvram_dir(self) -> Path:
        return self.saves_dir / self.name

    @cached_property
    def screenshot_dir(self) -> Path:
        return SCREENSHOTS / self.name

    @cached_property
    def gun_precalibration_dir(self) -> Path:
        return super().gun_precalibration_dir / self.name

    def precalibrate_guns(self) -> None:
        if self.system != 'model2':
            return

        # sm2-emu names a save after the set it finds in the archive, not after the file
        for src in self.gun_precalibration_dir.iterdir():
            dest = self.nvram_dir / src.name
            default = _NVRAM_SRC / src.name

            # also replace a default save that was never changed
            if dest.exists() and default.exists() and dest.read_bytes() == default.read_bytes():
                dest.unlink()

            if src.exists() and not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                src.copy(dest)

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
                'wheel_button_menu': '-1',
                **_wheel_axes(wheel),
            }
            if wheel is not None
            else {}
        )
        if es_wheel_rotation is not None:
            wheel_managed['wheel_steer_degrees'] = es_wheel_rotation
            wheel_managed['wheel_lock_degrees'] = es_wheel_rotation

        managed = {
            'fullscreen': 'true',
            'window_width': str(self.resolution.width),
            'window_height': str(self.resolution.height),
            'vsync': _ini_bool(self.config.get_bool('sm2_vsync', False)),
            'show_fps': 'false',  # covered by the hud/hud_corner features instead
            'lightgun': _ini_bool(use_guns),
            'lightgun_crosshair': _ini_bool(
                use_guns and self.config.get_bool('sm2_lightgun_crosshair', guns_need_crosses(self.guns))
            ),
            'lightgun_hide_flash': _ini_bool(self.config.get_bool('sm2_lightgun_hide_flash', False)),
            'lightgun_pad_centred': _ini_bool(self.config.get_bool('sm2_lightgun_pad_centred', False)),
            'lightgun_recoil': _ini_bool(self.config.get_bool('sm2_lightgun_recoil', True)),
            'lightgun_recoil_strength': self.config.get_str('sm2_lightgun_recoil_strength', '60'),
            **{f'gun{gun}_button_{role}': str(code) for gun in (1, 2) for role, code in _GUN_BUTTONS.items()},
            'wheel_ffb': _ini_bool(self.config.get_bool('sm2_wheel_ffb', True)),
            'wheel_ffb_strength': str(round(self.config.get_float('sm2_wheel_ffb_strength', 50))),
            'wheel_panel_spring': str(round(self.config.get_float('sm2_wheel_panel_spring', 20))),
            'wheel_drive_dip': self.config.get_str('sm2_wheel_drive_dip', '0'),
            'wheel_ffb_invert': _ini_bool(self.config.get_bool('sm2_wheel_ffb_invert', False)),
            'wheel_rumble': _ini_bool(self.config.get_bool('sm2_wheel_rumble', True)),
            'wheel_rumble_strength': self.config.get_str('sm2_wheel_rumble_strength', '40'),
            'wheel_rumble_engine': _ini_bool(self.config.get_bool('sm2_wheel_rumble_engine', True)),
            'wheel_steer_deadzone': str(round(self.config.get_float('sm2_wheel_deadzone', 0))),
            'wheel_shift_neutral_ms': self.config.get_str('sm2_shift_neutral', '0'),
            'wheel_indy_deadband': str(round(self.config.get_float('sm2_wheel_indy_deadband', 0))),
            'wheel_indy_full_power': str(round(self.config.get_float('sm2_wheel_indy_full_power', 63))),
            **wheel_managed,
            'pad_rumble': _ini_bool(self.config.get_bool('sm2_pad_rumble', True)),
            'pad_rumble_strength': str(round(self.config.get_float('sm2_pad_rumble_strength', 50))),
            'pad_rumble_cornering': _ini_bool(self.config.get_bool('sm2_pad_rumble_cornering', True)),
            'pad_stick_deadzone': str(round(self.config.get_float('sm2_pad_stick_deadzone', 5))),
            'pad_stick_sensitivity': str(round(self.config.get_float('sm2_pad_stick_sensitivity', 100))),
            'rewind': _ini_bool(self.config.get_bool('rewind', False)),
            'rewind_buffer_mb': str(round(self.config.get_float('sm2_rewind_memory', 128))),
            'pad_shortcuts': 'false',  # hotkeygen maps the hotkeys to the keys in hotkeygen_context
            'rom_dir': str(self.roms_dir),
            'nvram_dir': str(self.nvram_dir),
            'screenshot_dir': str(self.screenshot_dir),
            'graphics_backend': graphics_backend,
            'gpu': _resolve_gpu(graphics_backend, vulkan_info),
            'render_scale': self.config.get_str('sm2_render_scale', '1'),
            'scaling_method': self.config.get_str('sm2_scaling_method', 'sharp'),
            'aspect_mode': self.config.get_str('sm2_aspect_mode', '4:3'),
            'extended_draw_distance': _ini_bool(self.config.get_bool('sm2_draw_distance', True)),
            'texture_filter': self.config.get_str('sm2_texture_filter', 'faithful'),
            'anisotropy': self.config.get_str('sm2_anisotropy', '4'),
            'upscale_2d': self.config.get_str('sm2_upscale_2d', 'faithful'),
            'translucency': self.config.get_str('sm2_translucency', 'stipple'),
            'crt_enabled': _ini_bool(self.config.get_bool('sm2_crt_enabled', False)),
            'crt_scanline_strength': self.config.get_str('sm2_crt_scanline_strength', '40'),
            'crt_mask_strength': self.config.get_str('sm2_crt_mask_strength', '30'),
            'crt_glow_strength': self.config.get_str('sm2_crt_glow_strength', '20'),
            'crt_curvature': self.config.get_str('sm2_crt_curvature', '0'),
            'bezel': 'false',  # batocera draws its own bezels
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
