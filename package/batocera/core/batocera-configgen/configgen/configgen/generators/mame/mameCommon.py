from __future__ import annotations

from typing import TypedDict, cast

import toml

from .mamePaths import MAME_DEFAULT_DATA


class _MameSystemDict(TypedDict):
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


def get_mame_system(system_name: str, /) -> _MameSystemDict | None:
    for name, item in toml.loads((MAME_DEFAULT_DATA / 'mameSystems.toml').read_text()).items():
        if name == system_name:
            return {
                'model_name': item.get('model_name', ''),
                'rom_type': item.get('rom_type', ''),
                'autorun': item.get('autorun', ''),
            }

    return None


def get_mame_roms() -> _MameRomsDict:
    return cast(_MameRomsDict, toml.loads((MAME_DEFAULT_DATA / 'mameRoms.toml').read_text()))
