from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

pytest.importorskip('pygame')

from batocera_discord.demo import render_demo

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize('language', ['en', 'fr'])
def test_every_screen_renders(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, language: str) -> None:
    monkeypatch.setenv('SDL_VIDEODRIVER', 'dummy')

    assert render_demo(tmp_path, language) == 0

    names = {path.name for path in tmp_path.iterdir()}
    assert names >= {
        'servers.png',
        'channels.png',
        'friends.png',
        'call.png',
        'settings.png',
        'setup.png',
        'install.png',
    }
