"""Private, atomic JSON storage for the Discord application settings and OAuth tokens.

Everything lives in a 0700 directory and every file is written 0600: the client secret (when one is
needed at all) and the tokens never leave this directory.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any, Final, cast

from . import paths
from .errors import IO_ERRORS

if TYPE_CHECKING:
    from pathlib import Path
    from typing import TypeIs

_logger: Final = logging.getLogger(__name__)
_SNOWFLAKE_RE: Final = re.compile(r'\d{15,22}')


def is_snowflake(value: object) -> TypeIs[str]:
    """Discord ids (application, channel, user) are 15 to 22 digit integers."""
    return isinstance(value, str) and _SNOWFLAKE_RE.fullmatch(value) is not None


def _ensure_private_dir(directory: Path, /) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    directory.chmod(0o700)


def read_json(path: Path, /) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except IO_ERRORS:
        _logger.warning('unreadable %s, ignoring it', path)
        return {}
    return cast('dict[str, Any]', data) if isinstance(data, dict) else {}


def write_json(path: Path, data: object, /) -> None:
    _ensure_private_dir(path.parent)
    tmp = path.with_suffix(path.suffix + '.tmp')
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as fp:
        json.dump(data, fp, indent=1)
    tmp.replace(path)


@dataclass(slots=True)
class Favorite:
    name: str
    channel_id: str


@dataclass(slots=True)
class AppConfig:
    client_id: str = ''
    client_secret: str = ''
    favorites: list[Favorite] = field(default_factory=list[Favorite])

    @property
    def configured(self) -> bool:
        return is_snowflake(self.client_id)

    @classmethod
    def load(cls, path: Path | None = None, /) -> AppConfig:
        raw = read_json(path or paths.CONFIG_FILE)
        favorites: list[Favorite] = []
        raw_favorites = raw.get('favorites')
        for item in cast('list[object]', raw_favorites) if isinstance(raw_favorites, list) else []:
            if isinstance(item, dict):
                fav = cast('dict[str, object]', item)
                channel_id = fav.get('channel_id')
                if is_snowflake(channel_id):
                    favorites.append(Favorite(str(fav.get('name') or 'Discord')[:40], str(channel_id)))
        client_id = raw.get('client_id')
        secret = raw.get('client_secret')
        return cls(
            client_id=client_id if is_snowflake(client_id) else '',
            client_secret=secret if isinstance(secret, str) else '',
            favorites=favorites,
        )

    def save(self, path: Path | None = None, /) -> None:
        write_json(path or paths.CONFIG_FILE, asdict(self))


@dataclass(slots=True)
class Tokens:
    access_token: str = ''
    refresh_token: str = ''
    expires_at: float = 0.0

    @property
    def expired(self) -> bool:
        return time.time() >= self.expires_at

    @classmethod
    def from_response(cls, data: dict[str, Any], /) -> Tokens:
        return cls(
            access_token=str(data.get('access_token', '')),
            refresh_token=str(data.get('refresh_token', '')),
            # refresh five minutes early so a token never expires in the middle of a session
            expires_at=time.time() + int(data.get('expires_in', 604800)) - 300,
        )

    @classmethod
    def load(cls, path: Path | None = None, /) -> Tokens:
        raw = read_json(path or paths.TOKENS_FILE)
        return cls(
            access_token=str(raw.get('access_token', '')),
            refresh_token=str(raw.get('refresh_token', '')),
            expires_at=float(raw.get('expires_at', 0.0)),
        )

    def save(self, path: Path | None = None, /) -> None:
        write_json(path or paths.TOKENS_FILE, asdict(self))

    @staticmethod
    def clear(path: Path | None = None, /) -> None:
        (path or paths.TOKENS_FILE).unlink(missing_ok=True)
