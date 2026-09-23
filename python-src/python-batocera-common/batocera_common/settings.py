from __future__ import annotations

import re
from pathlib import Path
from typing import Final

from .key_value_config import KeyValueConfig
from .paths import BATOCERA_CONF, SYSCONFIG

_DEVICETREE_MODEL: Final = Path('/sys/firmware/devicetree/base/model')
_DMI_PRODUCT_NAME: Final = Path('/sys/devices/virtual/dmi/id/product_name')
_DMI_BOARD_NAME: Final = Path('/sys/devices/virtual/dmi/id/board_name')

_MODEL_SUB_RE: Final = re.compile(r'[^A-Za-z0-9]')


def _read_model(path: Path, /) -> str:
    try:
        return _MODEL_SUB_RE.sub('_', path.read_text().strip('\0\n'))
    except OSError:
        return ''


def board_model() -> str | None:
    model = _read_model(_DEVICETREE_MODEL) or _read_model(_DMI_PRODUCT_NAME)

    if not model or model == 'Default_string':
        model = _read_model(_DMI_BOARD_NAME)

    return model or None


def _lookup(config: KeyValueConfig, key: str, /) -> str | None:
    value = config.get(key)

    if value in (None, '', 'auto'):
        return None

    return value


def get_master_setting(key: str, /, *, user_config: KeyValueConfig | None = None) -> str | None:
    """A setting with the board and general sysconfig defaults as fallbacks, like batocera-settings-get-master."""
    if user_config is None:
        user_config = KeyValueConfig(BATOCERA_CONF)

    if (value := _lookup(user_config, key)) is not None:
        return value

    if (model := board_model()) is not None:
        board_conf = SYSCONFIG.with_name(f'{SYSCONFIG.name}.{model}')

        if board_conf.is_file() and (value := _lookup(KeyValueConfig(board_conf), key)) is not None:
            return value

    if SYSCONFIG.is_file():
        return _lookup(KeyValueConfig(SYSCONFIG), key)

    return None
