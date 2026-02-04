from __future__ import annotations

import re
from pathlib import Path
from typing import Final

_MAKEFILE: Final = (
    Path(__file__).parent.parent.parent
    / 'package'
    / 'batocera'
    / 'emulationstation'
    / 'batocera-es-system'
    / 'batocera-es-system.mk'
)
_MAKEFILE_PATTERN: Final = r'^BATOCERA_ES_SYSTEM_VERSION\s*=\s*(?P<version>.*)$'
_VERSION_FILE: Final = Path(__file__).parent / 'batocera_es_system' / '__version__.py'
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
