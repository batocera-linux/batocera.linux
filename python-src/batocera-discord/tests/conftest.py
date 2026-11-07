from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from batocera_discord import paths

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Every test gets its own private config directory instead of /userdata."""
    directory = tmp_path / 'configs' / 'discord'
    monkeypatch.setattr(paths, 'CONFIG_DIR', directory)
    monkeypatch.setattr(paths, 'CONFIG_FILE', directory / 'config.json')
    monkeypatch.setattr(paths, 'TOKENS_FILE', directory / 'tokens.json')
    monkeypatch.setattr(paths, 'RECENTS_FILE', directory / 'recents.json')
    return directory
