from __future__ import annotations

import tomllib

from ..paths import LAUNCH_DATA_DIR


def get_decoration_id(system_name: str, rom_id: str, /) -> str:
    system_toml = LAUNCH_DATA_DIR / 'special' / f'{system_name}.toml'
    if not system_toml.is_file():
        return '0'

    special_dict = tomllib.loads(system_toml.read_text())

    rom_compare = rom_id.casefold()
    return next((value for key, value in special_dict.items() if rom_compare == key.casefold()), '0')
