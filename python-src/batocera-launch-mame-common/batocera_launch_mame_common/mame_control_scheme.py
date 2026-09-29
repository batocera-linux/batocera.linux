from __future__ import annotations

import tomllib
from collections.abc import Mapping
from typing import Literal, cast

from .paths import MAME_DATA_DIR

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


type MameControlSchemeOverrides = Mapping[str, Mapping[str, MameControlScheme]]


def _get_override(
    overrides: MameControlSchemeOverrides | None, system_type: str, controller_type: str, /
) -> MameControlScheme | None:
    if overrides and system_type in overrides and controller_type in overrides[system_type]:
        return overrides[system_type][controller_type]

    return None


def load_mame_control_scheme(
    controller_type: str,
    rom_name: str,
    /,
    *,
    overrides: MameControlSchemeOverrides | None = None,
) -> MameControlScheme:
    """
    Load the MAME control scheme.
    """

    if controller_type in {'default', 'neomini', 'neocd', 'twinstick', 'qbert'}:
        return controller_type  # pyright: ignore[reportReturnType]

    roms = cast('dict[str, list[str]]', tomllib.loads(MAME_DATA_DIR.joinpath('roms.toml').read_text()))

    if rom_name in roms['capcom']:
        if (override := _get_override(overrides, 'capcom', controller_type)) is not None:
            return override

        if controller_type in {'auto', 'snes'}:
            return 'sfsnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['mortal_kombat']:
        if (override := _get_override(overrides, 'mortal_kombat', controller_type)) is not None:
            return override

        if controller_type in {'auto', 'snes'}:
            return 'mksnes'
        if controller_type == 'megadrive':
            return 'mkmegadrive'
        if controller_type == 'fightstick':
            return 'mkstick'
    elif rom_name in roms['killer_instinct']:
        if (override := _get_override(overrides, 'killer_instinct', controller_type)) is not None:
            return override

        if controller_type in {'auto', 'snes'}:
            return 'kisnes'
        if controller_type == 'megadrive':
            return 'megadrive'
        if controller_type == 'fightstick':
            return 'sfstick'
    elif rom_name in roms['neogeo']:
        if (override := _get_override(overrides, 'neogeo', controller_type)) is not None:
            return override

        return 'neomini'
    elif rom_name in roms['twin_stick']:
        if (override := _get_override(overrides, 'twin_stick', controller_type)) is not None:
            return override

        return 'twinstick'
    elif rom_name in roms['rotated_stick']:
        if (override := _get_override(overrides, 'rotated_stick', controller_type)) is not None:
            return override

        return 'qbert'
    else:
        if (override := _get_override(overrides, 'default', controller_type)) is not None:
            return override

        if controller_type == 'fightstick':
            return 'fightstick'
        if controller_type == 'megadrive':
            return 'mddefault'

    return 'default'
