from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib import resources
from typing import Any, Final, Literal

from batocera_launch import InvalidConfiguration

_SPECIAL_CONTROLS: Final = {
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


@dataclass(slots=True, frozen=True)
class _BaseMessControl:
    player: int
    tag: str
    key: str
    mask: int
    default: int
    reversed: bool


@dataclass(slots=True, frozen=True)
class _BaseMessControlMapping(_BaseMessControl):
    mapping: str
    useMapping: str


@dataclass(slots=True, frozen=True)
class MessSpecialMapping(_BaseMessControlMapping):
    type: Literal['special']


@dataclass(slots=True, frozen=True)
class MessMainMapping(_BaseMessControlMapping):
    type: Literal['main']


@dataclass(slots=True, frozen=True)
class MessComboMapping(_BaseMessControlMapping):
    type: Literal['combo']
    kbMapping: str


@dataclass(slots=True, frozen=True)
class MessAnalogMapping(_BaseMessControl):
    type: Literal['analog']
    incMapping: str
    incUseMapping: str
    decMapping: str
    decUseMapping: str
    delta: int
    axis: str


type MessControlMapping = MessSpecialMapping | MessMainMapping | MessComboMapping | MessAnalogMapping


def _dict_to_mess_control_mapping(control_dict: dict[str, Any]) -> MessControlMapping:
    base: dict[str, Any] = {
        'player': control_dict['player'],
        'tag': control_dict['tag'],
        'key': control_dict['key'],
        'mask': control_dict['mask'],
        'default': control_dict['default'],
        'reversed': control_dict.get('reversed', False),
    }

    match control_dict['type']:
        case 'special' | 'main' | 'combo' as type:
            mapping = control_dict['mapping']
            kwargs: dict[str, Any] = {
                **base,
                'type': type,
                'mapping': mapping,
                'useMapping': control_dict.get('useMapping', mapping),
            }

            if type == 'main':
                return MessMainMapping(**kwargs)

            if type == 'special':
                return MessSpecialMapping(**kwargs)

            kwargs['kbMapping'] = control_dict['kbMapping']
            return MessComboMapping(**kwargs)
        case 'analog':
            return MessAnalogMapping(
                **base,
                type='analog',
                incMapping=control_dict['incMapping'],
                incUseMapping=control_dict.get('incUseMapping', control_dict['incMapping']),
                decMapping=control_dict['decMapping'],
                decUseMapping=control_dict.get('decUseMapping', control_dict['decMapping']),
                delta=control_dict['delta'],
                axis=control_dict['axis'],
            )
        case _:
            raise InvalidConfiguration(f'Unknown control mapping type: {control_dict["type"]}')


def load_mess_system_controls(mess_system_name: str, control_scheme: str, /) -> dict[str, MessControlMapping] | None:
    if mess_system_name not in _SPECIAL_CONTROLS:
        return None

    mess_controls = tomllib.loads(resources.files().joinpath('data', 'mess_controls.toml').read_text())

    return {key: _dict_to_mess_control_mapping(value) for key, value in mess_controls.get(control_scheme, {}).items()}
