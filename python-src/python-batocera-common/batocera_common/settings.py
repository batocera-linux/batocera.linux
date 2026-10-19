# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

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


def _board_sysconfig() -> Path | None:
    if (model := board_model()) is None:
        return None

    board_conf = SYSCONFIG.with_name(f'{SYSCONFIG.name}.{model}')

    return board_conf if board_conf.is_file() else None


def get_master_setting(key: str, /, *, user_config: KeyValueConfig | None = None) -> str | None:
    """A setting with the board and general sysconfig defaults as fallbacks, like batocera-settings-get-master."""
    if user_config is None:
        user_config = KeyValueConfig(BATOCERA_CONF)

    if (value := _lookup(user_config, key)) is not None:
        return value

    if (board_conf := _board_sysconfig()) is not None and (
        value := _lookup(KeyValueConfig(board_conf), key)
    ) is not None:
        return value

    if SYSCONFIG.is_file():
        return _lookup(KeyValueConfig(SYSCONFIG), key)

    return None


def get_master_section(section: str, /, *, user_config: KeyValueConfig | None = None) -> dict[str, str]:
    """Every `<section>.<key>` setting with the same precedence as get_master_setting, keyed without the section."""
    if user_config is None:
        user_config = KeyValueConfig(BATOCERA_CONF)

    values: dict[str, str] = {}

    if SYSCONFIG.is_file():
        values.update(KeyValueConfig(SYSCONFIG).section_items(section))

    if (board_conf := _board_sysconfig()) is not None:
        values.update(KeyValueConfig(board_conf).section_items(section))

    values.update(user_config.section_items(section))

    return values
