from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import toml

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CHEATS, CONFIGS, ROMS, SAVES
from batocera_launch import Command, Controller, Emulator, HotkeysContext
from batocera_launch.devices.video import configure_windows, find_screen

if TYPE_CHECKING:
    from pathlib import Path

_MELONDS_SAVES: Final = SAVES / 'nds'
_MELONDS_ROMS: Final = ROMS / 'nds'
_MELONDS_CHEATS: Final = CHEATS / 'melonDS'
_MELONDS_CONFIG: Final = CONFIGS / 'melonDS'

_MELONDS_MAPPING: Final = {
    'a': 'A',
    'b': 'B',
    'select': 'Select',
    'start': 'Start',
    'right': 'Right',
    'left': 'Left',
    'up': 'Up',
    'down': 'Down',
    'pagedown': 'R',
    'pageup': 'L',
    'x': 'X',
    'y': 'Y',
}


@cached_dataclass
class MelonDS(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'melonds',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure_windows(self) -> None:
        # windows position is handled by coordinates by the application (xorg) or the window manager (wayland)
        screens = await self.screens

        await configure_windows('melonds', find_screen(screens, 'primary'), find_screen(screens, 'secondary'))

    async def configure(self) -> Command:
        _MELONDS_SAVES.mkdir(parents=True, exist_ok=True)
        _MELONDS_CHEATS.mkdir(parents=True, exist_ok=True)
        _MELONDS_CONFIG.mkdir(parents=True, exist_ok=True)

        config_file = _MELONDS_CONFIG / 'melonDS.toml'

        config: dict[str, Any] = {}
        if config_file.exists():
            with config_file.open() as fp:
                config = toml.load(fp)

        base_config: dict[str, Any] = {
            'MouseHide': False,
            'LastBIOSFolder': str(BIOS),
            'PauseLostFocus': False,
            'LastROMFolder': str(_MELONDS_ROMS),
            'MouseHideSeconds': 5,
            'DS': {
                'FirmwarePath': str(BIOS / 'firmware.bin'),
                'BIOS7Path': str(BIOS / 'bios7.bin'),
                'BIOS9Path': str(BIOS / 'bios9.bin'),
            },
            'DLDI': {
                'FolderPath': str(_MELONDS_SAVES),
                'ImagePath': 'dldi.bin',
                'Enable': True,
            },
            'DSi': {
                'FullBIOSBoot': False,
                'FirmwarePath': str(BIOS / 'dsi_firmware.bin'),
                'BIOS9Path': str(BIOS / 'dsi_bios9.bin'),
                'BIOS7Path': str(BIOS / 'dsi_bios7.bin'),
                'NANDPath': str(BIOS / 'dsi_nand.bin'),
                'SD': {
                    'FolderPath': str(_MELONDS_SAVES),
                    'ImagePath': 'dsisd.bin',
                    'Enable': True,
                },
            },
            'Emu': {
                'DirectBoot': True,
                'ExternalBIOSEnable': True,
            },
            'Instance0': {
                'SaveFilePath': str(_MELONDS_SAVES),
                'SavestatePath': str(_MELONDS_SAVES),
                'CheatFilePath': str(_MELONDS_CHEATS),
                'EnableCheats': False,
                'Joystick': {},
                'Firmware': {
                    'MAC': '',
                    'BirthdayDay': 1,
                    'BirthdayMonth': 1,
                    'Language': 1,
                    'Message': '',
                    'OverrideSettings': True,
                },
                'Window0': {
                    'ScreenRotation': 0,
                    'ScreenSwap': False,
                    'ScreenLayout': 0,
                    'ScreenSizing': 0,
                    'IntegerScaling': False,
                    'ShowOSD': False,
                },
                'Window1': {
                    'Enabled': False,
                    'ScreenRotation': 0,
                    'ScreenSwap': False,
                    'ScreenLayout': 0,
                    'ScreenSizing': 5,
                    'IntegerScaling': False,
                },
            },
            '3D': {
                'Renderer': 1,
                'GL': {
                    'ScaleFactor': 5,
                    'BetterPolygons': False,
                },
            },
            'Screen': {
                'VSync': False,
                'UseGL': False,
            },
        }

        ## User selected options

        # Override Renderer and UseGL
        if 'melonds_renderer' in self.config:
            renderer = self.config.get_int('melonds_renderer')
            base_config['3D']['Renderer'] = renderer
            base_config['Screen']['UseGL'] = renderer != 0

        if vsync := self.config.get_bool('melonds_vsync'):
            base_config['Screen']['VSync'] = vsync
            base_config['Screen']['VSyncInterval'] = 1

        # Cheater! Enable cheats if the option is set
        base_config['Instance0']['EnableCheats'] = self.config.get_bool('melonds_cheats', False)

        # Framerate
        base_config['LimitFPS'] = self.config.get_bool('melonds_framerate', True)

        # Resolution
        resolution = self.config.get_int('melonds_resolution')
        if resolution is not None:
            base_config['3D']['GL']['ScaleFactor'] = resolution
            base_config['3D']['GL']['HiresCoordinates'] = resolution == 2

        # Polygons
        if polygons := self.config.get_bool('melonds_polygons'):
            base_config['3D']['GL']['BetterPolygons'] = polygons

        # OSD
        base_config['Instance0']['Window0']['ShowOSD'] = self.config.get_bool('melonds_osd', False)

        # Console
        base_config['Emu']['ConsoleType'] = self.config.get_int('melonds_console', 0)

        # Override Firmware settings
        base_config['Instance0']['Firmware']['OverrideSettings'] = self.config.get_bool(
            'melonds_use_fw_settings', False
        )

        # Firmware Language
        base_config['Instance0']['Firmware']['Language'] = self.config.get_int('melonds_language', 1)

        # Birthday date
        base_config['Instance0']['Firmware']['BirthdayDay'] = self.config.get_int('melonds_day', 1)
        base_config['Instance0']['Firmware']['BirthdayMonth'] = self.config.get_int('melonds_month', 1)

        # Scaling (matches TOML boolean type)
        scaling = self.config.get_bool('melonds_scaling', False)

        # Check if dual screen mode is enabled
        if self.config.get_bool('melonds_dual_screen', False):
            # Window0 (Top Screen)
            base_config['Instance0']['Window0']['ScreenRotation'] = 0
            base_config['Instance0']['Window0']['ScreenSwap'] = False
            base_config['Instance0']['Window0']['ScreenLayout'] = 0
            base_config['Instance0']['Window0']['ScreenSizing'] = 4
            base_config['Instance0']['Window0']['IntegerScaling'] = scaling

            # Window1 (Bottom Screen)
            base_config['Instance0']['Window1']['Enabled'] = True
            base_config['Instance0']['Window1']['ScreenRotation'] = 0
            base_config['Instance0']['Window1']['ScreenSwap'] = False
            base_config['Instance0']['Window1']['ScreenLayout'] = 0
            base_config['Instance0']['Window1']['ScreenSizing'] = 5
            base_config['Instance0']['Window1']['IntegerScaling'] = scaling
        else:
            base_config['Instance0']['Window1']['Enabled'] = False
            base_config['Instance0']['Window0']['ScreenRotation'] = self.config.get_int('melonds_rotation', 0)
            base_config['Instance0']['Window0']['ScreenSwap'] = self.config.get_bool('melonds_screenswap', False)
            base_config['Instance0']['Window0']['ScreenLayout'] = self.config.get_int('melonds_layout', 0)
            base_config['Instance0']['Window0']['ScreenSizing'] = self.config.get_int('melonds_screensizing', 0)
            base_config['Instance0']['Window0']['IntegerScaling'] = scaling

        # Map controllers - only use Player 1 controls
        pad = Controller.find_player_number(self.controllers, 1)
        if pad is not None:
            for inp in pad.inputs.values():
                if inp.name not in _MELONDS_MAPPING:
                    continue
                option = _MELONDS_MAPPING[inp.name]
                # Workaround - SDL numbers?
                val: str | int = inp.id
                if val == '0':
                    if option == 'Up':
                        val = 257
                    elif option == 'Down':
                        val = 260
                    elif option == 'Left':
                        val = 264
                    elif option == 'Right':
                        val = 258
                base_config['Instance0']['Joystick'][option] = int(val)

        # Update base_config with any existing values
        config.update(base_config)

        with config_file.open('w') as fp:
            toml.dump(config, fp)

        args: list[str | Path] = ['/usr/bin/melonDS', '-f', self.rom]
        return Command(
            args,
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
            },
        )
