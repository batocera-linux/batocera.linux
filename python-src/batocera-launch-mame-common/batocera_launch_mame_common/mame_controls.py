from __future__ import annotations

import tomllib
from importlib import resources


def _load_mame_controls() -> dict[str, dict[str, str]]:
    return tomllib.loads(resources.files().joinpath('data', 'mame_controls.toml').read_text())


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
