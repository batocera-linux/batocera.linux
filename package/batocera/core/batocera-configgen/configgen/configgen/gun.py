from __future__ import annotations

import logging
import re
import shutil
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Final, cast

from .batoceraPaths import BATOCERA_SHARE_DIR, CONFIGS, SAVES, mkdir_if_not_exists

if TYPE_CHECKING:
    from .Emulator import Emulator

_logger = logging.getLogger(__name__)
_input_re: Final = re.compile(r'^/dev/input/event([0-9]*)$')
_PRECALIBRATION_DIR: Final = BATOCERA_SHARE_DIR / 'guns-precalibrations'


def _copy_file(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        mkdir_if_not_exists(dst.parent)
        shutil.copyfile(src, dst)


def _copy_dir(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        mkdir_if_not_exists(dst.parent)
        shutil.copytree(src, dst)


def _copy_files_in_dir(srcdir: Path, dstdir: Path, startWith: str, endWith: str) -> None:
    for src in srcdir.iterdir():
        if src.name.startswith(startWith):  # and src.endswith(endswith):
            _copy_file(src, dstdir / src.name)


@dataclass(slots=True, kw_only=True)
class Gun:
    mouse_buttons_to_code: ClassVar[Mapping[str, int]]

    node: str
    mouse_index: int
    needs_cross: bool
    needs_borders: bool
    name: str
    buttons: list[str]
    button_map: Mapping[str, int] = field(init=False)

    def __post_init__(self) -> None:
        if not hasattr(Gun, '_mouse_buttons_to_code'):
            # delay initialization of the map so we don't have
            # to import evdev until we need it
            import evdev

            Gun.mouse_buttons_to_code = {
                'left': evdev.ecodes.BTN_LEFT,
                'right': evdev.ecodes.BTN_RIGHT,
                'middle': evdev.ecodes.BTN_MIDDLE,
                '1': evdev.ecodes.BTN_1,
                '2': evdev.ecodes.BTN_2,
                '3': evdev.ecodes.BTN_3,
                '4': evdev.ecodes.BTN_4,
                '5': evdev.ecodes.BTN_5,
                '6': evdev.ecodes.BTN_6,
                '7': evdev.ecodes.BTN_7,
                '8': evdev.ecodes.BTN_8,
            }

        self.button_map = {
            button: self.mouse_buttons_to_code[button]
            for button in self.buttons
            if button in self.mouse_buttons_to_code
        }

    @staticmethod
    def get_all() -> GunDict:
        import evdev
        import pyudev

        guns: GunDict = {}
        context = pyudev.Context()

        # guns are mouses, just filter on them
        mouses = {
            int(match.group(1)): mouse
            for mouse in context.list_devices(subsystem='input')
            if mouse.device_node is not None
            and (match := _input_re.match(mouse.device_node)) is not None
            and mouse.properties.get('ID_INPUT_MOUSE') == '1'
        }

        mouse_code_to_button = {
            evdev.ecodes.BTN_LEFT: 'left',
            evdev.ecodes.BTN_RIGHT: 'right',
            evdev.ecodes.BTN_MIDDLE: 'middle',
            evdev.ecodes.BTN_1: '1',
            evdev.ecodes.BTN_2: '2',
            evdev.ecodes.BTN_3: '3',
            evdev.ecodes.BTN_4: '4',
            evdev.ecodes.BTN_5: '5',
            evdev.ecodes.BTN_6: '6',
            evdev.ecodes.BTN_7: '7',
            evdev.ecodes.BTN_8: '8',
        }
        mouse_button_codes = set(mouse_code_to_button.keys())

        gun_index = 0
        for mouse_index, (_, mouse) in enumerate(sorted(mouses.items(), key=lambda item: item[0])):
            _logger.info('found mouse %s at %s with id_mouse=%s', mouse_index, mouse.device_node, mouse_index)
            if mouse.properties.get('ID_INPUT_GUN') != '1':
                continue

            device = evdev.InputDevice(cast(str, mouse.device_node))
            device_codes = set(device.capabilities()[evdev.ecodes.EV_KEY]) & mouse_button_codes

            gun = Gun(
                node=cast(str, mouse.device_node),
                # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE
                # (TOUCHPAD are listed after mouses)
                mouse_index=mouse_index,
                needs_cross=mouse.properties.get('ID_INPUT_GUN_NEED_CROSS') == '1',
                needs_borders=mouse.properties.get('ID_INPUT_GUN_NEED_BORDERS') == '1',
                name=device.name,
                buttons=[button for code, button in mouse_code_to_button.items() if code in device_codes],
            )
            guns[gun_index] = gun
            _logger.info(
                'found gun %s at %s with id_mouse=%s (%s)', gun_index, mouse.device_node, mouse_index, gun.name
            )

            gun_index += 1

        if not guns:
            _logger.info('no gun found')

        return guns

    @classmethod
    def get_and_precalibrate_all(cls, system: Emulator, rom: str | Path, /) -> GunDict:
        if not system.isOptSet('use_guns') or not system.getOptBoolean('use_guns'):
            _logger.info('guns disabled.')
            return {}

        dir = _PRECALIBRATION_DIR / system.name

        if dir.exists():
            rom = Path(rom)
            emulator = cast('str', system.config['emulator'])
            core = cast('str | None', system.config.get('core'))

            if system.name == 'atomiswave':
                for suffix in ['nvmem', 'nvmem2']:
                    src = dir / 'reicast' / f'{rom.name}.{suffix}'
                    dst = SAVES / 'atomiswave' / 'reicast' / f'{rom.name}.{suffix}'
                    _copy_file(src, dst)

            elif system.name == 'mame':
                target_dir: str | None = None
                if emulator == 'mame':
                    target_dir = 'mame'
                elif emulator == 'libretro':
                    if core == 'mame078plus':
                        target_dir = 'mame/mame2003-plus'
                    elif core == 'mame':
                        target_dir = 'mame/mame'

                if target_dir is not None:
                    src = dir / 'nvram' / rom.stem
                    dst = SAVES / target_dir / 'nvram' / rom.stem
                    _copy_dir(src, dst)
                    srcdir = dir / 'diff'
                    dstdir = SAVES / target_dir / 'diff'
                    _copy_files_in_dir(srcdir, dstdir, rom.stem + '_', '.dif')

            elif system.name == 'model2':
                src = dir / 'NVDATA' / f'{rom.name}.DAT'
                dst = SAVES / 'model2' / 'NVDATA' / f'{rom.name}.DAT'
                _copy_file(src, dst)

            elif system.name == 'naomi':
                for suffix in ['nvmem', 'eeprom']:
                    src = dir / 'reicast' / f'{rom.name}.{suffix}'
                    dst = SAVES / 'naomi' / 'reicast' / f'{rom.name}.{suffix}'
                    _copy_file(src, dst)

            elif system.name == 'supermodel':
                src = dir / 'NVDATA' / f'{rom.stem}.nv'
                dst = SAVES / 'supermodel' / 'NVDATA' / f'{rom.stem}.nv'
                _copy_file(src, dst)

            elif system.name == 'namco2x6':
                if emulator == 'play':
                    src = dir / 'play' / rom.stem
                    dst = CONFIGS / 'play' / 'Play Data Files' / 'arcadesaves' / f'{rom.stem}.backupram'
                    _copy_file(src, dst)

        return cls.get_all()


def guns_need_crosses(guns: GunMapping) -> bool:
    # no gun, enable the cross for joysticks, mouses...
    if not guns:
        return True

    return any(gun.needs_cross for gun in guns.values())


type GunDict = dict[int, Gun]
type GunMapping = Mapping[int, Gun]
