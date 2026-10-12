from __future__ import annotations

from pathlib import Path

from batocera_common.connman import interfaces
from batocera_common.dbus._generate_proxies import generate_proxies


def test_connman_proxies() -> None:
    proxy_file = Path(interfaces.__file__).parent.joinpath('proxies.py')
    assert proxy_file.read_text() == generate_proxies(interfaces, proxy_file, 'generate-proxies', None)
