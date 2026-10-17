from __future__ import annotations

import json
import stat
import time
from typing import TYPE_CHECKING

from batocera_discord import paths
from batocera_discord.storage import AppConfig, Favorite, Tokens, is_snowflake

if TYPE_CHECKING:
    from pathlib import Path


def test_is_snowflake() -> None:
    assert is_snowflake('123456789012345678')
    assert not is_snowflake('1234')
    assert not is_snowflake('12345678901234567x')
    assert not is_snowflake(123456789012345678)


def test_config_round_trip_is_private(config_dir: Path) -> None:
    AppConfig('123456789012345678', 'secret', [Favorite('Glenn', '223456789012345678')]).save()

    assert stat.S_IMODE(paths.CONFIG_FILE.stat().st_mode) == 0o600
    assert stat.S_IMODE(config_dir.stat().st_mode) == 0o700
    loaded = AppConfig.load()
    assert loaded.configured
    assert loaded.client_secret == 'secret'
    assert loaded.favorites == [Favorite('Glenn', '223456789012345678')]


def test_config_drops_invalid_values(config_dir: Path) -> None:
    config_dir.mkdir(parents=True)
    paths.CONFIG_FILE.write_text(
        json.dumps({'client_id': 'abc', 'client_secret': 3, 'favorites': [{'name': 'x', 'channel_id': 'nope'}, 'junk']})
    )

    loaded = AppConfig.load()
    assert not loaded.configured
    assert loaded.client_secret == ''
    assert loaded.favorites == []


def test_unreadable_config_is_empty(config_dir: Path) -> None:
    config_dir.mkdir(parents=True)
    paths.CONFIG_FILE.write_text('{not json')

    assert AppConfig.load() == AppConfig()


def test_tokens_expire_early() -> None:
    tokens = Tokens.from_response({'access_token': 'a', 'refresh_token': 'r', 'expires_in': 600})

    assert not tokens.expired
    assert tokens.expires_at < time.time() + 600
    tokens.save()
    assert Tokens.load() == tokens
    Tokens.clear()
    assert Tokens.load() == Tokens()
