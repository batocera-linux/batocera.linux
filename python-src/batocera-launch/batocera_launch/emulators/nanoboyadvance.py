from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.paths import BIOS, CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

# NanoBoyAdvance reads $XDG_CONFIG_HOME/NanoBoyAdvance/config.toml
# Point XDG_CONFIG_HOME to CONFIGS; the app appends NanoBoyAdvance/ itself.

_GBA_BIOS: Final = BIOS / 'gba_bios.bin'

# Default Qt key codes for keyboard fallback (used with evmapy pad-to-key)
# SDFG home-row mapping: same physical position on all keyboard layouts (QWERTY, AZERTY, QWERTZ...)
_DEFAULT_KEYBOARD: Final[dict[str, int]] = {
    'a': 83,  # Qt::Key_S
    'b': 68,  # Qt::Key_D
    'select': 16777219,  # Qt::Key_Backspace
    'start': 16777220,  # Qt::Key_Return
    'right': 16777236,  # Qt::Key_Right
    'left': 16777234,  # Qt::Key_Left
    'up': 16777235,  # Qt::Key_Up
    'down': 16777237,  # Qt::Key_Down
    'r': 71,  # Qt::Key_G
    'l': 70,  # Qt::Key_F
}


def _bool(value: bool) -> str:
    return 'true' if value else 'false'


def _quoted(s: str) -> str:
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _map(gba_key: str) -> str:
    kb = _DEFAULT_KEYBOARD[gba_key]
    return f'{gba_key} = [{kb}, -1, -1, -1, 0]'


def _build_toml(
    *,
    bios_path: str,
    bios_skip: bool,
    save_folder: str,
    filter_val: str,
    color_correction: str,
    lcd_ghosting: bool,
    resampler: str,
    mp2k_hle: bool,
    integer_scaling: bool,
    force_solar_sensor: bool,
    solar_sensor_level: int,
) -> str:
    return f"""\
[general]
bios_path = {_quoted(bios_path)}
bios_skip = {_bool(bios_skip)}
save_folder = {_quoted(save_folder)}
fast_forward_speed = 2

[cartridge]
save_type = "detect"
force_rtc = true
force_solar_sensor = {_bool(force_solar_sensor)}
solar_sensor_level = {solar_sensor_level}

[video]
filter = {_quoted(filter_val)}
color_correction = {_quoted(color_correction)}
lcd_ghosting = {_bool(lcd_ghosting)}

[audio]
resampler = {_quoted(resampler)}
mp2k_hle_enable = {_bool(mp2k_hle)}
mp2k_hle_cubic = true
mp2k_hle_force_reverb = true

[window]
fullscreen = true
fullscreen_show_menu = false
scale = 2
maximum_scale = 0
show_fps = false
lock_aspect_ratio = true
use_integer_scaling = {_bool(integer_scaling)}
pause_emulator_when_inactive = false

[input]
hold_fast_forward = true
fast_forward = [32, -1, -1, -1, 0]
controller_guid = ""
[input.gba]
{_map('a')}
{_map('b')}
{_map('select')}
{_map('start')}
{_map('right')}
{_map('left')}
{_map('up')}
{_map('down')}
{_map('r')}
{_map('l')}
"""


@cached_dataclass
class Nanoboyadvance(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'nanoboyadvance',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': ['KEY_LEFTSHIFT', 'KEY_F1'],
                'restore_state': 'KEY_F1',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'NanoBoyAdvance'

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'nanoboyadvance'

    @cached_property
    def in_game_ratio(self) -> float:
        return 3 / 2

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        (self.config_dir / 'config.toml').write_text(
            _build_toml(
                bios_path=str(_GBA_BIOS),
                bios_skip=self.config.get_bool('nba_skip_bios'),
                save_folder=str(self.saves_dir),
                filter_val=self.config.get_str('nba_filter', 'nearest'),
                color_correction=self.config.get_str('nba_color_correction', 'agb'),
                lcd_ghosting=self.config.get_bool('nba_lcd_ghosting', True),
                resampler=self.config.get_str('nba_audio_resampler', 'cosine'),
                mp2k_hle=self.config.get_bool('nba_mp2k_hle'),
                integer_scaling=self.config.get_bool('nba_integer_scaling'),
                force_solar_sensor=self.config.get_bool('nba_force_solar_sensor'),
                solar_sensor_level=self.config.get_int('nba_solar_sensor_level', 23),
            ),
        )

        # NanoBoyAdvance supports archives natively via unarr (zip, 7z, tar, rar1).
        # Pass the path as-is — no extraction needed.
        return Command(
            ['/usr/bin/NanoBoyAdvance', self.rom],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'QT_QPA_PLATFORM': 'xcb',
            },
        )
