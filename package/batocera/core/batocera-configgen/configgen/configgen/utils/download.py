from __future__ import annotations

import logging
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import IO, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

_logger = logging.getLogger(__name__)


class DownloadException(Exception): ...


@contextmanager
def download(url: str, directory: Path, /) -> Iterator[IO[bytes]]:
    import requests  # only import requests when it's needed because it's slow to import initially

    _logger.debug('Downloading %s to %s...', url, directory)

    try:
        with NamedTemporaryFile(dir=directory) as file, requests.get(url, stream=True) as response:
            response.raise_for_status()

            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

            file.seek(0)

            yield file
    except requests.RequestException as e:
        raise DownloadException(f'Failed to download {url}') from e
