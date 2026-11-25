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

import argparse
import contextlib
import logging
import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BATOCERA_CONF, CONFIGS, ROMS, SAVES, SCREENSHOTS
from batocera_common.vulkan import VulkanInfo, get_vulkan_info
from batocera_launch import Command, Emulator, HotkeysContext, guns_need_crosses, state_manager

if TYPE_CHECKING:
    from collections.abc import Callable

    from batocera_launch import Controller

_logger: Final = logging.getLogger(__name__)

_NVRAM_SRC: Final = Path('/usr/share/keisho/nvram')

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
        return {}  # nothing mapped, keep keisho's auto-detect / gui calibration

    relaxed = pad.get_mapping_axis_relaxed_values()

    # pedals on one axis each use half of it, pressed the way es saw it pressed
    shared = accel is not None and brake is not None and accel[1] == brake[1]

    def axis_id(found: tuple[str, int] | None) -> str:
        return str(found[1]) if found is not None else '-1'

    # keisho inverts a pedal that rests at the positive end, which is es's 'reversed'
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


# keisho's default keys, held there as hotkeygen_context relies on them
_DEFAULT_KEYS = {
    'key_exit': 'Escape',
    'key_quit': 'F9',
    'key_overlay': 'F10',
    'key_fullscreen': 'F11',
    'key_screenshot': 'F12',
    'key_pause': 'P',
    'key_quick_save': 'F6',
    'key_quick_load': 'F7',
    'key_fps': 'F8',
    'key_fast_forward': 'Tab',
    'key_rewind': 'Backspace',
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

    # before the first [section], where no game's gamepad section claims them
    first_section = next((i for i, line in enumerate(lines) if line.strip().startswith('[')), len(lines))
    lines[first_section:first_section] = [f'{key} = {value}' for key, value in remaining.items()]
    return '\n'.join((*lines, ''))


async def _resolve_graphics_backend(requested: str) -> tuple[str, VulkanInfo | None]:
    if requested != 'vulkan':
        return requested, None

    vulkan_info = await get_vulkan_info()
    if not vulkan_info:
        _logger.debug('Vulkan driver is not available on the system. Falling back to OpenGL.')
        return 'opengl', None

    # Below 1.3 keisho uses the extensions for the same features, and falls
    # back to OpenGL itself when a device lacks them.
    _logger.debug('Vulkan driver is available. Using Vulkan version: %s', vulkan_info.version)
    return 'vulkan', vulkan_info


def _resolve_gpu(backend: str, vulkan_info: VulkanInfo | None) -> str:
    if backend != 'vulkan' or not vulkan_info or not (discrete_gpu := vulkan_info.active_discrete_gpu):
        return ''

    return discrete_gpu.name or ''


def _seed_nvram(src_dir: Path, dest_dir: Path) -> None:
    if not src_dir.is_dir():
        return

    for item in src_dir.iterdir():
        dest = dest_dir / item.name
        if not dest.exists():
            shutil.copy2(item, dest)


# keisho was sm2-emu, and replaces supermodel for model3

_OLD_NAME: Final = 'sm2-emu'
_OLD_EMULATORS: Final = {_OLD_NAME, 'supermodel'}
_SUPERMODEL_NVRAM: Final = SAVES / 'supermodel' / 'NVRAM'


def _move_tree(src: Path, dest: Path, /) -> None:
    """Move what dest doesn't already have, then remove the emptied src directories."""
    if src.is_dir() and not src.is_symlink():
        for item in src.iterdir():
            _move_tree(item, dest / item.name)
        with contextlib.suppress(OSError):
            src.rmdir()
    elif not src.exists() and not src.is_symlink():
        return
    elif dest.exists() or dest.is_symlink():
        _logger.info('%s already exists, leaving %s', dest, src)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dest)
        _logger.info('moved %s to %s', src, dest)


def migrate_files() -> None:
    old_config = CONFIGS / _OLD_NAME
    new_config = CONFIGS / 'keisho'
    if old_config.is_dir():
        old_ini = old_config / f'{_OLD_NAME}.ini'
        _move_tree(old_ini, new_config / 'keisho.ini')
        for item in old_config.iterdir():
            if item != old_ini:
                _move_tree(item, new_config / item.name)
        with contextlib.suppress(OSError):
            old_config.rmdir()

    for system in ('model1', 'model2'):
        _move_tree(SAVES / system / _OLD_NAME, SAVES / system / 'keisho')
    _move_tree(SCREENSHOTS / _OLD_NAME, SCREENSHOTS / 'keisho')

    # supermodel's .nv files load as they are; its save states don't, so they stay
    if _SUPERMODEL_NVRAM.is_dir():
        for nvram in _SUPERMODEL_NVRAM.glob('*.nv'):
            _move_tree(nvram, SAVES / 'model3' / 'keisho' / nvram.name)
        with contextlib.suppress(OSError):
            _SUPERMODEL_NVRAM.rmdir()
    _move_tree(SCREENSHOTS / 'supermodel', SCREENSHOTS / 'keisho')


def _on(new_key: str, value: str, /) -> Callable[[str], tuple[str, str] | None]:
    return lambda old: (new_key, value) if old == '1' else None


def _same(new_key: str, /) -> Callable[[str], tuple[str, str] | None]:
    return lambda old: (new_key, old)


# model3 settings of supermodel that keisho has; None drops the rest
_SUPERMODEL_SETTINGS: Final[dict[str, Callable[[str], tuple[str, str] | None] | None]] = {
    'graphics_backend': lambda old: (
        ('keisho_graphics_backend', old.lower()) if old.lower() in ('opengl', 'vulkan') else None
    ),
    'm3_wideScreen': _on('keisho_aspect_mode', '16:9'),
    'm3_stretch': _on('keisho_aspect_mode', 'stretch'),
    'm3_vsync': _same('keisho_vsync'),
    'm3_renderscale': lambda old: (
        ('keisho_render_scale', old) if old in {str(scale) for scale in range(1, 9)} else None
    ),
    'crosshairs': lambda old: ('keisho_lightgun_crosshair', '0' if old == '0' else '1'),
    'forceFeedback': _same('keisho_wheel_ffb'),
    'm3_audio_channels': lambda old: ('keisho_surround', '1' if old == '4' else '0'),
    'm3_outputs': lambda old: ('keisho_outputs_network', '1' if old == 'net' else '0'),
    'm3_outputs_tcp': _same('keisho_outputs_network_port'),
    'engine3D': None,
    'quadRendering': None,
    'm3_supersampling': None,
    'm3_true_hz': None,
    'crt_colour': None,
    'upscale_mode': None,
    'm3_no_white_flash': None,
    'm3_ffb_strength': None,
    'ppcFreq': None,
    'm3_scsp': None,
    'm3_outputs_lf': None,
    'm3_outputs_udp': None,
}

_SETTING: Final = re.compile(r'(?P<scope>[^#=\s][^=]*?)\.(?P<key>\w+)=(?P<value>.*)')


def _migrate_setting(scope: str, key: str, value: str, /) -> tuple[str, str] | None:
    if key in ('emulator', 'core') and value in _OLD_EMULATORS:
        return key, 'keisho'
    if key.startswith('sm2_'):
        return f'keisho_{key.removeprefix("sm2_")}', value
    if (scope == 'model3' or scope.startswith('model3[')) and key in _SUPERMODEL_SETTINGS:
        convert = _SUPERMODEL_SETTINGS[key]
        return convert(value) if convert is not None else None
    return key, value


def migrate_batocera_conf_text(text: str, /) -> str:
    settings = [_SETTING.fullmatch(line) for line in text.splitlines()]
    # a keisho setting already made wins over one carried over
    taken = {(m['scope'], m['key']) for m in settings if m is not None and m['key'].startswith('keisho_')}

    lines: list[str] = []
    for line, setting in zip(text.splitlines(), settings, strict=True):
        if setting is None:
            lines.append(line)
            continue
        scope, key, value = setting['scope'], setting['key'], setting['value']
        migrated = _migrate_setting(scope, key, value)
        if migrated == (key, value):
            lines.append(line)
            continue
        if migrated is None or (scope, migrated[0]) in taken:
            _logger.info('dropped %s', line)
            continue
        taken.add((scope, migrated[0]))
        lines.append(f'{scope}.{migrated[0]}={migrated[1]}')
        _logger.info('%s is now %s', line, lines[-1])
    return '\n'.join((*lines, '')) if lines else ''


def migrate_batocera_conf(path: Path, /) -> None:
    if not path.is_file():
        return
    text = path.read_text()
    migrated = migrate_batocera_conf_text(text)
    if migrated != text:
        tmp = path.with_name(f'{path.name}.keisho-migrate')
        tmp.write_text(migrated)
        tmp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description='Move sm2-emu and supermodel settings and saves over to keisho.')
    parser.add_argument('--conf', action='store_true', help='also rewrite batocera.conf, only while ES is stopped')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.conf:
        migrate_batocera_conf(BATOCERA_CONF)
    migrate_files()


@cached_dataclass
class Keisho(Emulator):
    needs_sdl_game_controller_config = True
    cpu_cluster = 'fast'  # one interpreter thread; little cores only slow it

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'keisho',
            'keys': {
                'exit': 'KEY_F9',
                'menu': 'KEY_F10',
                'pause': 'KEY_P',
                'screenshot': 'KEY_F12',
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
    def nvram_src(self) -> Path:
        return _NVRAM_SRC / self.system

    @cached_property
    def gun_precalibration_dir(self) -> Path:
        system_dir = super().gun_precalibration_dir
        if not (precalibration_dir := system_dir / self.name).is_dir():
            precalibration_dir = system_dir / _OLD_NAME  # until the precalibrations are renamed
        return precalibration_dir

    def precalibrate_guns(self) -> None:
        # keisho names a save after the set it finds in the archive, not after the file
        for src in self.gun_precalibration_dir.iterdir():
            dest = self.nvram_dir / src.name
            default = self.nvram_src / src.name

            # also replace a default save that was never changed
            if dest.exists() and default.exists() and dest.read_bytes() == default.read_bytes():
                dest.unlink()

            if src.exists() and not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                src.copy(dest)

    async def configure(self) -> Command:
        migrate_files()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.nvram_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        _seed_nvram(self.nvram_src, self.nvram_dir)

        use_guns = self.config.use_guns
        graphics_backend, vulkan_info = await _resolve_graphics_backend(
            self.config.get_str('keisho_graphics_backend', 'opengl')
        )

        wheel = next(
            (pad for pad in self.controllers if self.config.use_wheels and pad.device_path in self.wheels), None
        )
        # keisho otherwise numbers the pads in SDL's order, not ES's
        pad_paths = [pad.device_path for pad in self.controllers if pad.device_path not in self.wheels][:2]
        pad_paths += [''] * (2 - len(pad_paths))

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
            'vsync': _ini_bool(self.config.get_bool('keisho_vsync', False)),
            'show_fps': 'false',  # covered by the hud/hud_corner features instead
            'lightgun': 'on' if use_guns else 'auto',
            'lightgun_crosshair': _ini_bool(
                use_guns and self.config.get_bool('keisho_lightgun_crosshair', guns_need_crosses(self.guns))
            ),
            'lightgun_hide_flash': _ini_bool(self.config.get_bool('keisho_lightgun_hide_flash', False)),
            'lightgun_pad_centred': _ini_bool(self.config.get_bool('keisho_lightgun_pad_centred', False)),
            'lightgun_recoil': _ini_bool(self.config.get_bool('keisho_lightgun_recoil', True)),
            'lightgun_recoil_strength': self.config.get_str('keisho_lightgun_recoil_strength', '60'),
            **{f'gun{gun}_button_{role}': str(code) for gun in (1, 2) for role, code in _GUN_BUTTONS.items()},
            'wheel_ffb': _ini_bool(self.config.get_bool('keisho_wheel_ffb', True)),
            'wheel_ffb_strength': str(round(self.config.get_float('keisho_wheel_ffb_strength', 50))),
            'wheel_panel_spring': str(round(self.config.get_float('keisho_wheel_panel_spring', 20))),
            'wheel_drive_dip': self.config.get_str('keisho_wheel_drive_dip', '0'),
            'wheel_ffb_invert': _ini_bool(self.config.get_bool('keisho_wheel_ffb_invert', False)),
            'wheel_rumble': _ini_bool(self.config.get_bool('keisho_wheel_rumble', True)),
            'wheel_rumble_strength': self.config.get_str('keisho_wheel_rumble_strength', '40'),
            'wheel_rumble_engine': _ini_bool(self.config.get_bool('keisho_wheel_rumble_engine', True)),
            'wheel_steer_deadzone': str(round(self.config.get_float('keisho_wheel_deadzone', 0))),
            'wheel_shift_neutral_ms': self.config.get_str('keisho_shift_neutral', '0'),
            'wheel_indy_deadband': str(round(self.config.get_float('keisho_wheel_indy_deadband', 0))),
            'wheel_indy_full_power': str(round(self.config.get_float('keisho_wheel_indy_full_power', 63))),
            **wheel_managed,
            'pad_rumble': _ini_bool(self.config.get_bool('keisho_pad_rumble', True)),
            'pad_rumble_strength': str(round(self.config.get_float('keisho_pad_rumble_strength', 50))),
            'pad_rumble_cornering': _ini_bool(self.config.get_bool('keisho_pad_rumble_cornering', True)),
            'pad_stick_deadzone': str(round(self.config.get_float('keisho_pad_stick_deadzone', 5))),
            'pad_stick_sensitivity': str(round(self.config.get_float('keisho_pad_stick_sensitivity', 100))),
            'rewind': _ini_bool(self.config.get_bool('rewind', False)),
            'rewind_buffer_mb': str(round(self.config.get_float('keisho_rewind_memory', 128))),
            'pad1_device': pad_paths[0],
            'pad2_device': pad_paths[1],
            'pad_shortcuts': 'false',  # hotkeygen maps the hotkeys to the keys in hotkeygen_context
            **_DEFAULT_KEYS,
            'model1_rom_dir': str(ROMS / 'model1'),
            'model2_rom_dir': str(ROMS / 'model2'),
            'model3_rom_dir': str(ROMS / 'model3'),
            'nvram_dir': str(self.nvram_dir),
            'screenshot_dir': str(self.screenshot_dir),
            'graphics_backend': graphics_backend,
            'gpu': _resolve_gpu(graphics_backend, vulkan_info),
            'render_scale': self.config.get_str('keisho_render_scale', '1'),
            'scaling_method': self.config.get_str('keisho_scaling_method', 'sharp'),
            'aspect_mode': self.config.get_str('keisho_aspect_mode', '4:3'),
            'extended_draw_distance': _ini_bool(self.config.get_bool('keisho_draw_distance', True)),
            'texture_filter': self.config.get_str('keisho_texture_filter', 'faithful'),
            'anisotropy': self.config.get_str('keisho_anisotropy', '4'),
            'upscale_2d': self.config.get_str('keisho_upscale_2d', 'faithful'),
            'translucency': self.config.get_str('keisho_translucency', 'stipple'),
            'brightness': str(round(self.config.get_float('keisho_brightness', 50))),
            'music_volume': str(round(self.config.get_float('keisho_music_volume', 100))),
            'surround': _ini_bool(self.config.get_bool('keisho_surround', False)),
            'outputs_network': _ini_bool(self.config.get_bool('keisho_outputs_network', False)),
            'outputs_network_port': self.config.get_str('keisho_outputs_network_port', '8000'),
            'crt_enabled': _ini_bool(self.config.get_bool('keisho_crt_enabled', False)),
            'crt_scanline_strength': self.config.get_str('keisho_crt_scanline_strength', '40'),
            'crt_mask_strength': self.config.get_str('keisho_crt_mask_strength', '30'),
            'crt_glow_strength': self.config.get_str('keisho_crt_glow_strength', '20'),
            'crt_curvature': self.config.get_str('keisho_crt_curvature', '0'),
            'bezel': 'false',  # batocera draws its own bezels
        }

        config_path = self.config_dir / 'keisho.ini'
        existing_text = config_path.read_text() if config_path.exists() else ''
        config_path.write_text(_merge_ini(existing_text, managed))

        return Command(
            [
                '/usr/bin/keisho',
                '--config',
                self.config_dir,
                *state_manager(self.config).boot_args,
                self.rom,
            ],
            env={
                'SDL_JOYSTICK_HIDAPI': '0',
                'XDG_CONFIG_HOME': self.config_dir.parent,
            },
        )
