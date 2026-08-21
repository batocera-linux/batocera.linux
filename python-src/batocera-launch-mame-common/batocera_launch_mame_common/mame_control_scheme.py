from __future__ import annotations

import tomllib
from importlib import resources
from typing import Literal, cast

type MameControlScheme = Literal[
    'default',
    'neomini',
    'neocd',
    'twinstick',
    'qbert',
    'megadrive',
    'fightstick',
    'sfsnes',
    'mksnes',
    'sfstick',
    'mkmegadrive',
    'mkstick',
    'kisnes',
    'mddefault',
]


def load_mame_control_scheme(controller_type: str, rom_name: str, /) -> MameControlScheme:
    """
    Load the MAME control scheme.
    """

    if controller_type in {'default', 'neomini', 'neocd', 'twinstick', 'qbert'}:
        return controller_type  # pyright: ignore[reportReturnType]

    roms = cast('dict[str, list[str]]', tomllib.loads(resources.files().joinpath('data', 'roms.toml').read_text()))

    if rom_name in roms['capcom']:
        if controller_type in {'auto', 'snes'}:
            return 'sfsnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['mortal_kombat']:
        if controller_type in {'auto', 'snes'}:
            return 'mksnes'
        if controller_type == 'megadrive':
            return 'mkmegadrive'
        if controller_type == 'fightstick':
            return 'mkstick'
    elif rom_name in roms['killer_instinct']:
        if controller_type in {'auto', 'snes'}:
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
