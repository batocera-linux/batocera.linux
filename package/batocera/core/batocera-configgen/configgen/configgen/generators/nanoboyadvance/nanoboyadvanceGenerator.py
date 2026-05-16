from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import BIOS, CONFIGS, SAVES, mkdir_if_not_exists
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

nbaSaves = SAVES / 'nanoboyadvance'

# NanoBoyAdvance reads $XDG_CONFIG_HOME/NanoBoyAdvance/config.toml
# Point XDG_CONFIG_HOME to CONFIGS; the app appends NanoBoyAdvance/ itself.
nbaXdgConfig  = CONFIGS
nbaConfigDir  = CONFIGS / 'NanoBoyAdvance'
nbaConfigFile = nbaConfigDir / 'config.toml'

_GBA_BIOS = BIOS / 'gba_bios.bin'

# Default Qt key codes for keyboard fallback (used with evmapy pad-to-key)
# SDFG home-row mapping: same physical position on all keyboard layouts (QWERTY, AZERTY, QWERTZ...)
_DEFAULT_KEYBOARD: dict[str, int] = {
    'a':      83,        # Qt::Key_S
    'b':      68,        # Qt::Key_D
    'select': 16777219,  # Qt::Key_Backspace
    'start':  16777220,  # Qt::Key_Return
    'right':  16777236,  # Qt::Key_Right
    'left':   16777234,  # Qt::Key_Left
    'up':     16777235,  # Qt::Key_Up
    'down':   16777237,  # Qt::Key_Down
    'r':      71,        # Qt::Key_G
    'l':      70,        # Qt::Key_F
}


class NanoboyadvanceGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "nanoboyadvance",
            "keys": {
                "exit":          ["KEY_LEFTALT", "KEY_F4"],
                "save_state":    ["KEY_LEFTSHIFT", "KEY_F1"],
                "restore_state": "KEY_F1",
            },
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(nbaConfigDir)
        mkdir_if_not_exists(nbaSaves)

        cfg = system.config

        bios_path        = str(_GBA_BIOS)
        bios_skip        = cfg.get('nba_skip_bios', 'false') == 'true'
        save_folder      = str(nbaSaves)
        filter_val       = cfg.get('nba_filter',           'nearest')
        color_correction = cfg.get('nba_color_correction', 'agb')
        lcd_ghosting     = cfg.get('nba_lcd_ghosting',     'true') == 'true'
        resampler        = cfg.get('nba_audio_resampler',  'cosine')
        mp2k_hle         = cfg.get('nba_mp2k_hle',         'false') == 'true'
        integer_scaling     = cfg.get('nba_integer_scaling',     'false') == 'true'
        force_solar_sensor  = cfg.get('nba_force_solar_sensor',  'false') == 'true'
        solar_sensor_level  = int(cfg.get('nba_solar_sensor_level', '23'))

        nbaConfigFile.write_text(
            _build_toml(
                bios_path=bios_path,
                bios_skip=bios_skip,
                save_folder=save_folder,
                filter_val=filter_val,
                color_correction=color_correction,
                lcd_ghosting=lcd_ghosting,
                resampler=resampler,
                mp2k_hle=mp2k_hle,
                integer_scaling=integer_scaling,
                force_solar_sensor=force_solar_sensor,
                solar_sensor_level=solar_sensor_level,
            ),
            encoding='utf-8',
        )

        # NanoBoyAdvance supports archives natively via unarr (zip, 7z, tar, rar1).
        # Pass the path as-is — no extraction needed.
        return Command.Command(
            array=['/usr/bin/NanoBoyAdvance', rom],
            env={
                'XDG_CONFIG_HOME': str(nbaXdgConfig),
                'QT_QPA_PLATFORM': 'xcb',
            },
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 3 / 2


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
