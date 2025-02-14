from __future__ import annotations

import csv
from typing import TYPE_CHECKING, Final, Literal, TypedDict, cast

import toml

from .mamePaths import MAME_CONFIG, MAME_DEFAULT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    from ...Emulator import Emulator
    from .mameTypes import MameControlScheme


class _MessSystemDict(TypedDict):
    model_name: str
    rom_type: str
    autorun: str


class _MameRomsDict(TypedDict):
    capcom: list[str]
    mortal_kombat: list[str]
    killer_instinct: list[str]
    neogeo: list[str]
    twin_stick: list[str]
    rotated_stick: list[str]


def get_mess_system(system_name: str, /) -> _MessSystemDict | None:
    mess_systems = toml.loads((MAME_DEFAULT_DATA / 'messSystems.toml').read_text())
    mess_system = mess_systems.get(system_name, None)

    # This must be an `is not None` check becuase the dictionary could be empty
    if mess_system is not None:
        return {
            'model_name': mess_system.get('model_name', ''),
            'rom_type': mess_system.get('rom_type', ''),
            'autorun': mess_system.get('autorun', ''),
        }

    return None


def get_mame_control_scheme(system: Emulator, rom: Path, /) -> MameControlScheme:
    # Controls for games with 5-6 buttons or other unusual controls
    controller_type = system.config.get('altlayout', 'auto')

    if controller_type in ['default', 'neomini', 'neocd', 'twinstick', 'qbert']:
        return controller_type  # pyright: ignore[reportReturnType]

    # Game list files
    roms = cast(_MameRomsDict, toml.loads((MAME_DEFAULT_DATA / 'mameRoms.toml').read_text()))

    rom_name = rom.stem
    if rom_name in roms['capcom']:
        if controller_type in ['auto', 'snes']:
            return 'sfsnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['mortal_kombat']:
        if controller_type in ['auto', 'snes']:
            return 'mksnes'
        if controller_type == 'megadrive':
            return 'mkmegadrive'
        if controller_type == 'fightstick':
            return 'mkstick'
    elif rom_name in roms['killer_instinct']:
        if controller_type in ['auto', 'snes']:
            return 'kisnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['neogeo']:
        return 'neomini'
    elif rom_name in roms['twin_stick']:
        return 'twinstick'
    elif rom_name in roms['rotated_stick']:
        return 'qbert'
    else:
        if controller_type == 'fightstick':
            return 'fightstick'
        if controller_type == 'megadrive':
            return 'mddefault'

    return 'default'


def get_mame_controls() -> dict[str, dict[str, str]]:
    return toml.loads((MAME_DEFAULT_DATA / 'mameControls.toml').read_text())


class _MappingBase(TypedDict):
    player: int
    tag: str
    key: str
    reversed: bool
    mask: str
    default: str


class ControlMapping(_MappingBase):
    type: Literal['main', 'special']
    mapping: str
    useMapping: str


class AnalogMapping(_MappingBase):
    type: Literal['analog']
    incMapping: str
    decMapping: str
    useMapping1: str
    useMapping2: str
    delta: str
    axis: str


class ComboMapping(_MappingBase):
    type: Literal['combo']
    kbMapping: str
    mapping: str
    useMapping: str


_SPECIAL_CONTROL_LIST: Final = {
    'cdimono1',
    'apfm1000',
    'astrocde',
    'adam',
    'arcadia',
    'gamecom',
    'tutor',
    'crvision',
    'bbcb',
    'bbcm',
    'bbcm512',
    'bbcmc',
    'xegs',
    'socrates',
    'vgmplay',
    'pdp1',
    'vc4000',
    'fmtmarty',
    'gp32',
    'apple2p',
    'apple2e',
    'apple2ee',
}


def get_mess_controls(
    system_name: str, controls: str, /
) -> dict[str, ControlMapping | AnalogMapping | ComboMapping] | None:
    if system_name not in _SPECIAL_CONTROL_LIST:
        return None

    mess_controls: dict[str, dict[str, ControlMapping | AnalogMapping | ComboMapping]] = toml.loads(
        (MAME_DEFAULT_DATA / 'messControls.toml').read_text()
    )

    return mess_controls.get(controls, {})


def _get_autorun_command(path: Path, rom_name: str, /) -> str | None:
    auto_run_command = None
    rom_name = rom_name.casefold()

    if path.exists():
        with path.open() as file:
            for row in csv.reader(file, delimiter=';', quotechar="'"):
                if row and not row[0].startswith('#') and row[0].casefold() == rom_name:
                    auto_run_command = rf'{row[1]}\n'

    return auto_run_command


def get_softlist_autorun_command(soft_list: str, rom_name: str, /) -> str | None:
    return _get_autorun_command(MAME_DEFAULT_DATA / f'{soft_list}_autoload.csv', rom_name)


def get_user_autorun_command(system_name: str, rom_type: str, rom_name: str, /) -> str | None:
    return _get_autorun_command(MAME_CONFIG / 'autoload' / f'{system_name}_{rom_type}_autoload.csv', rom_name)
