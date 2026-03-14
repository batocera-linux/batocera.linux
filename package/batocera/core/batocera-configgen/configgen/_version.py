from __future__ import annotations

import re
from pathlib import Path
from typing import Final

_MAKEFILE: Final= Path(__file__).parent.parent / 'batocera-configgen.mk'
_MAKEFILE_PATTERN: Final = r'^BATOCERA_CONFIGGEN_VERSION\s+=\s+(?P<version>.*)$'
_VERSION_FILE: Final = Path(__file__).parent / 'configgen' / '__version__.py'
_VERSION_PATTERN: Final = r'(?i)^(__version__|VERSION) *= *([\'"])v?(?P<version>.+?)\2'


def _read_version(file: Path, pattern: str, /) -> str | None:
    contents = file.read_text()
    match = re.search(pattern, contents, re.MULTILINE)

    return match.group('version') if match else None


def _get_version() -> str:
    version: str | None = None

    if _MAKEFILE.exists():
        # Build is being performed in source directory
        version = _read_version(_MAKEFILE, _MAKEFILE_PATTERN)

    if _VERSION_FILE.exists():
        # Build is being performed in buildroot build directory
        version = _read_version(_VERSION_FILE, _VERSION_PATTERN)

    if version is not None:
        return version

    raise Exception('Unable to obtain version')


__version__: Final = _get_version()
