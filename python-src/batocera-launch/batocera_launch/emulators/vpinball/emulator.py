from __future__ import annotations

import configparser
import logging
from typing import TYPE_CHECKING

from batocera_common.asyncio import run
from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext
from batocera_launch.devices.video import configure_windows, find_screen

from . import options, windowing

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_PLUGINS_TO_ENABLE = (
    'Plugin.AltSound',
    'Plugin.B2SLegacy',
    'Plugin.DMDUtil',
    'Plugin.FlexDMD',
    'Plugin.PinMAME',
    'Plugin.PUP',
    'Plugin.ScoreView',
    'Plugin.Serum',
    'Plugin.WMP',
    'Plugin.VNI',
    'Plugin.vpx',
    'Plugin.DOF',
    'Plugin.Inspector',
)


async def _dmd_service_started() -> bool:
    proc = await run('batocera-services status "dmd_real"', shell=True, text=True)
    return proc.stdout.strip() == 'started'


@cached_dataclass
class VPinball(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'vpinball',
            'keys': {'exit': 'KEY_ESC', 'menu': 'KEY_F12', 'reset': 'KEY_F3', 'pause': 'KEY_P', 'coin': 'KEY_5'},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure_windows(self) -> None:
        screens = await self.screens

        # windows position is handled by coordinates by the application (xorg) or the window manager (wayland)
        playfield_screen, backglass_screen = windowing.get_playfield_and_backglass_screens(self.config, screens)
        await configure_windows(
            'vpinball',
            find_screen(screens, 'primary' if playfield_screen == 0 else 'secondary'),
            find_screen(screens, 'primary' if backglass_screen == 0 else 'secondary'),
        )

    async def configure(self) -> Command:
        # files
        config_file = self.config_dir / 'VPinballX.ini'
        config_file_override = self.config_dir / 'VPinballX_override.ini'
        log_file = self.config_dir / 'vpinball.log'

        # create vpinball config directory and a fresh config file if they don't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not config_file.exists():
            config_file.write_text('')
        if log_file.exists():
            log_file.rename(log_file.with_suffix(f'{log_file.suffix}.1'))

        ## [ VPinballX.ini ] ##
        try:
            settings = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
            settings.read(config_file)
        except configparser.DuplicateOptionError as e:
            _logger.debug('Error reading VPinballX.ini: %s', e)
            _logger.debug('*** Recreating a fresh VPinballX.ini file ***')
            config_file.write_text('')
            settings = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
            settings.read(config_file)

        # plugins to enable
        for plugin in _PLUGINS_TO_ENABLE:
            if not settings.has_section(plugin):
                settings.add_section(plugin)
            settings.set(plugin, 'Enable', '1')

        # Altsound
        settings.set(
            'Plugin.AltSound', 'Enable', self.config.get_bool('vpinball_altsound', True, return_values=('1', '0'))
        )

        # DMDServer
        has_dmd = await _dmd_service_started()
        if has_dmd:
            settings.set('Plugin.DMDUtil', 'Enable', '1')
            settings.set('Plugin.DMDUtil', 'DMDServer', '1')
        else:
            settings.set('Plugin.DMDUtil', 'Enable', '0')
            settings.set('Plugin.DMDUtil', 'DMDServer', '0')

        # options
        options.configure_options(settings, self.config)

        # windows
        screens = await self.screens
        windowing.configure_ini(settings, self.config, self.resolution, screens)

        # Override values
        if config_file_override.exists():
            try:
                _logger.debug('reading VPinballX_override.ini')
                settings_override = CaseSensitiveConfigParser(interpolation=None, allow_no_value=True)
                settings_override.read(config_file_override)
                _override_ini_with(settings, settings_override)
            except Exception as e:
                _logger.debug('Error reading VPinballX_override.ini: %s', e)
        else:
            _logger.debug('no VPinballX_override.ini found')

        # Save VPinballX.ini
        with config_file.open('w') as fp:
            settings.write(fp)

        args: list[str | Path] = [
            '/usr/bin/vpinball/VPinballX_BGFX',
            '-PrefPath',
            self.config_dir,
            '-Ini',
            config_file,
            '-Play',
            self.rom,
        ]

        # SDL_RENDER_VSYNC is causing perf issues (set by the base Emulator.run())
        return Command(args, env={'SDL_RENDER_VSYNC': '0'})


def _override_ini_with(settings: CaseSensitiveConfigParser, settings_override: CaseSensitiveConfigParser) -> None:
    for section in settings_override.sections():
        if not settings.has_section(section):
            settings.add_section(section)
        for option, value in settings_override.items(section):
            settings.set(section, option, value)
            _logger.debug('Override value: [%s] %s = %s', section, option, value)
