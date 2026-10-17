"""Downloads Discord avatars and server icons to a local cache, in the background."""

from __future__ import annotations

import logging
import queue
import re
import threading
import urllib.request
from typing import TYPE_CHECKING, Final

from . import paths
from .oauth import USER_AGENT

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)
_KEY_RE: Final = re.compile(r'[A-Za-z0-9_]+')
_ALLOWED_HOSTS: Final = ('https://cdn.discordapp.com/',)
_MAX_SIZE: Final = 2 * 1024 * 1024


class ImageCache:
    def __init__(self, on_ready: Callable[[], None], /, directory: Path = paths.CACHE_DIR) -> None:
        self.directory = directory
        self._on_ready = on_ready
        self._queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._asked: set[str] = set()

    def path(self, key: str, /) -> Path:
        return self.directory / f'{key}.png'

    def want(self, key: str, url: str, /) -> None:
        if key in self._asked or not _KEY_RE.fullmatch(key) or not url.startswith(_ALLOWED_HOSTS):
            return
        self._asked.add(key)
        if not self.path(key).exists():
            self._queue.put((key, url))

    def start(self) -> None:
        threading.Thread(target=self._loop, name='discord-images', daemon=True).start()

    def _loop(self) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        while True:
            key, url = self._queue.get()
            target = self.path(key)
            request = urllib.request.Request(f'{url.split("?")[0]}?size=128', headers={'User-Agent': USER_AGENT})
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    data = response.read(_MAX_SIZE)
                tmp = target.with_suffix('.tmp')
                tmp.write_bytes(data)
                tmp.replace(target)
            except OSError as exc:
                _logger.info('image %s: %s', key, exc)
                continue
            self._on_ready()
