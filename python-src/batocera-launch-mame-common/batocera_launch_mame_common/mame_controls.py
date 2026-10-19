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

import tomllib

from .paths import MAME_DATA_DIR


def _load_mame_controls() -> dict[str, dict[str, str]]:
    return tomllib.loads(MAME_DATA_DIR.joinpath('mame_controls.toml').read_text())


def _load_mame_control_mapping(controls: dict[str, dict[str, str]], control_scheme: str, /) -> dict[str, str]:
    # Common controls
    mapping = controls['default'].copy()

    # Buttons that change based on game/setting
    if alt_control_mappings := controls.get(control_scheme):
        mapping.update(alt_control_mappings)

    return mapping


def load_mame_control_mapping(control_scheme: str, /) -> dict[str, str]:
    return _load_mame_control_mapping(_load_mame_controls(), control_scheme)


def load_all_mame_control_mappings(
    controls_scheme: str,
    use_guns: bool = False,
    use_mouse: bool = False,
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    controls = _load_mame_controls()

    control_mapping = _load_mame_control_mapping(controls, controls_scheme)

    # Only use gun buttons if lightguns are enabled to prevent conflicts with mouse
    gun_mapping = controls['gunbuttons'].copy() if use_guns else {}

    # For a standard mouse, left, right, scroll wheel should be mapped to action buttons, and if side buttons are available, they will be coin & start
    mouse_mapping = controls['mousebuttons'].copy() if use_mouse else {}

    return control_mapping, gun_mapping, mouse_mapping
