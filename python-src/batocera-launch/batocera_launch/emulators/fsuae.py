from __future__ import annotations

import logging
import shutil
import zipfile
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext

_logger = logging.getLogger(__name__)

FSUAE_CONFIG_DIR: Final = CONFIGS / 'fs-uae'
FSUAE_BIOS_DIR: Final = BIOS / 'amiga'
FSUAE_SAVES: Final = SAVES / 'amiga'

_TEMP_DIR: Final = Path('/tmp/fsuae')

_BUTTON_MAPPING: Final = {
    'a': 'east_button',
    'b': 'south_button',
    'x': 'north_button',
    'y': 'west_button',
    'start': 'start_button',
    'select': 'select_button',
    'up': 'dpad_up',
    'down': 'dpad_down',
    'left': 'dpad_left',
    'right': 'dpad_right',
    'l2': 'left_trigger',
    'r2': 'right_trigger',
    'pageup': 'left_shoulder',
    'pagedown': 'right_shoulder',
    'joystick1up': 'lstick_up',
    'joystick1left': 'lstick_left',
    'joystick1down': 'lstick_down',
    'joystick1right': 'lstick_right',
    'joystick2up': 'rstick_up',
    'joystick2left': 'rstick_left',
    'joystick2down': 'rstick_down',
    'joystick2right': 'rstick_right',
    'hotkey': 'menu_button',
}
_HAT_MAPPING: Final = {'1': 'up', '4': 'down', '2': 'right', '8': 'left'}
_REVERSE_AXIS_MAPPING: Final = {
    'joystick1up': 'joystick1down',
    'joystick1left': 'joystick1right',
    'joystick2up': 'joystick2down',
    'joystick2left': 'joystick2right',
}


def _build_long_config_name(name: str, buttons: int, axes: int, hats: int, /) -> str:
    # e.g.: "Xbox Wireless Controller", 11, 6, 1 -> "xbox_wireless_controller_11_6_1_0_linux"
    name = name.split('#')[0].lower().strip()
    for c in name:
        if not c.isalnum() and c != '_':
            name = name.replace(c, '_')
    while '__' in name:
        name = name.replace('__', '_')
    name = name.strip('_')
    return f'{name}_{buttons}_{axes}_{hats}_0_linux'


def _floppies_from_rom(rom: Path, /) -> list[Path]:
    # from one file (x1.zip), get the list of all existing files with the same extension +
    # last char (as number) suffix, e.g. "/path/toto0.zip" -> [toto0.zip, toto1.zip, toto2.zip]
    if not rom.stem[-1:].isdigit():
        return [rom]

    fileprefix = rom.stem[:-1]  # path without the number
    floppies: list[Path] = []

    # special case for 0 while numbering can start at 1
    zero_file = rom.with_name(f'{fileprefix}0{rom.suffix}')
    if zero_file.is_file():
        floppies.append(zero_file)

    n = 1
    while (floppy := rom.with_name(f'{fileprefix}{n}{rom.suffix}')).is_file():
        floppies.append(floppy)
        n += 1

    return floppies


def _file_prefix(rom: Path, /) -> str:
    if not rom.stem[-1:].isdigit():
        return rom.stem
    return rom.stem[:-1]


@cached_dataclass
class Fsuae(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'fsuae',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'menu': 'KEY_F12'},
        }

    @property
    def handles_bezels(self) -> bool:
        return True

    def _generate_controller_config(self) -> None:
        conf_dir = FSUAE_CONFIG_DIR / 'Controllers'
        conf_dir.mkdir(parents=True, exist_ok=True)

        for pad in self.controllers:
            mapping_lines: list[str] = []

            for inp in pad.inputs.values():
                if inp.name not in _BUTTON_MAPPING:
                    continue

                if inp.type == 'button':
                    mapping_lines.append(f'button_{inp.id} = {_BUTTON_MAPPING[inp.name]}\n')
                elif inp.type == 'hat':
                    if inp.value in _HAT_MAPPING:
                        mapping_lines.append(f'hat_{inp.id}_{_HAT_MAPPING[inp.value]} = {_BUTTON_MAPPING[inp.name]}\n')
                elif inp.type == 'axis':
                    axis_valstr, revaxis_valstr = ('pos', 'neg') if inp.value == '1' else ('neg', 'pos')
                    mapping_lines.append(f'axis_{inp.id}_{axis_valstr} = {_BUTTON_MAPPING[inp.name]}\n')
                    reverse_name = _REVERSE_AXIS_MAPPING.get(inp.name)
                    if reverse_name is not None and reverse_name in _BUTTON_MAPPING:
                        mapping_lines.append(f'axis_{inp.id}_{revaxis_valstr} = {_BUTTON_MAPPING[reverse_name]}\n')

            # Write config for both GUID lookup (joystick config) and long-name lookup (menu config)
            long_name = _build_long_config_name(pad.real_name, pad.button_count, pad.axis_count, pad.hat_count)
            for config_name in (pad.guid.lower(), long_name):
                config_file = conf_dir / f'{config_name}.conf'
                with config_file.open('w') as f:
                    f.write('[fs-uae-controller]\n')
                    f.write(f'name = {pad.real_name}\n')
                    f.write('platform = linux\n')
                    f.write('\n')
                    f.write('[default]\n')
                    f.write('include = universal_gamepad\n')
                    f.writelines(mapping_lines)

    async def configure(self) -> Command:
        self._generate_controller_config()

        args: list[str | Path] = [
            '/usr/bin/fs-uae',
            '--fullscreen',
            f'--amiga-model={self.core}',
            f'--base_dir={FSUAE_CONFIG_DIR!s}',
            f'--kickstarts_dir={FSUAE_BIOS_DIR!s}',
            f'--save_states_dir={FSUAE_SAVES / self.core / _file_prefix(self.rom)}',
            '--zoom=auto',
            '--bezel=1',
            '--theme=fsemu-classic',
        ]

        device_type = 'cdrom' if self.core in ('CD32', 'CDTV') else 'floppy'

        disk_names: list[str] = []
        zf: zipfile.ZipFile | None = None
        if self.rom.suffix.lower() == '.zip':
            zf = zipfile.ZipFile(self.rom, 'r')
            disk_names.extend(name for name in zf.namelist() if name.lower().endswith(('ipf', 'adf', 'dms', 'adz')))
            _logger.debug('Amount of disks in zip %s', len(disk_names))

        if len(disk_names) > 1 and zf is not None:
            # multidisk ZIP: extract it
            _logger.debug('extracting...')
            shutil.rmtree(_TEMP_DIR, ignore_errors=True)
            zf.extractall(_TEMP_DIR)

            for n, disk in enumerate(disk_names):
                args.append(f'--{device_type}_image_{n}={_TEMP_DIR / disk}')
                if (n <= 1 and device_type == 'floppy') or (n == 0 and device_type == 'cdrom'):
                    args.append(f'--{device_type}_drive_{n}={_TEMP_DIR / disk}')
        else:
            for n, img in enumerate(_floppies_from_rom(self.rom)):
                args.append(f'--{device_type}_image_{n}={img}')
                if (n <= 1 and device_type == 'floppy') or (n == 0 and device_type == 'cdrom'):
                    args.append(f'--{device_type}_drive_{n}={img}')

        for n, pad in enumerate(self.controllers[:4]):
            args.append(f'--joystick_port_{n}={pad.real_name}')

        return Command(args)
