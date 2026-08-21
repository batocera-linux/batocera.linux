from __future__ import annotations

from contextlib import contextmanager
from typing import IO, TYPE_CHECKING, Any, overload

from batocera_common.paths import (
    BATOCERA_CONF as BATOCERA_CONF,
    BATOCERA_SHARE_DIR as BATOCERA_SHARE_DIR,
    BIOS as BIOS,
    CACHE as CACHE,
    CHEATS as CHEATS,
    CONFIGS as CONFIGS,
    HOME as HOME,
    LOGS as LOGS,
    OVERLAYS as OVERLAYS,
    RECORDINGS as RECORDINGS,
    ROMS as ROMS,
    SAVES as SAVES,
    SCREENSHOTS as SCREENSHOTS,
    USERDATA as USERDATA,
)
from batocera_launch.paths import (
    BATOCERA_ES_DIR as BATOCERA_ES_DIR,
    BATOCERA_SHADERS as BATOCERA_SHADERS,
    CONF_INIT as CONF_INIT,
    CONFIGGEN_DATA_DIR as CONFIGGEN_DATA_DIR,
    DATAINIT_DIR as DATAINIT_DIR,
    DEFAULTS_DIR as DEFAULTS_DIR,
    ES_GAMES_METADATA as ES_GAMES_METADATA,
    ES_GUNS_ART_METADATA as ES_GUNS_ART_METADATA,
    ES_GUNS_METADATA as ES_GUNS_METADATA,
    ES_SETTINGS as ES_SETTINGS,
    ES_WHEELS_METADATA as ES_WHEELS_METADATA,
    EVMAPY as EVMAPY,
    HOME_INIT as HOME_INIT,
    SYSTEM_DECORATIONS as SYSTEM_DECORATIONS,
    SYSTEM_SCRIPTS as SYSTEM_SCRIPTS,
    USER_DECORATIONS as USER_DECORATIONS,
    USER_ES_DIR as USER_ES_DIR,
    USER_SCRIPTS as USER_SCRIPTS,
    USER_SHADERS as USER_SHADERS,
    configure_emulator as configure_emulator,
)

if TYPE_CHECKING:
    from _typeshed import OpenBinaryModeUpdating, OpenBinaryModeWriting, OpenTextModeUpdating, OpenTextModeWriting
    from collections.abc import Generator
    from io import BufferedRandom, BufferedWriter, TextIOWrapper
    from pathlib import Path


def mkdir_if_not_exists(dir: Path, /) -> None:
    if not dir.exists():
        dir.mkdir(parents=True)

@overload
@contextmanager
def ensure_parents_and_open(file: Path, mode: OpenTextModeWriting | OpenTextModeUpdating) -> Generator[TextIOWrapper]:
    ...

@overload
@contextmanager
def ensure_parents_and_open(file: Path, mode: OpenBinaryModeUpdating) -> Generator[BufferedRandom]:
    ...

@overload
@contextmanager
def ensure_parents_and_open(file: Path, mode: OpenBinaryModeWriting) -> Generator[BufferedWriter]:
    ...

@contextmanager
def ensure_parents_and_open(file: Path, mode: str) -> Generator[IO[Any]]:
    mkdir_if_not_exists(file.parent)
    with file.open(mode) as f:
        yield f
