from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, Final, overload

if TYPE_CHECKING:
    from _typeshed import OpenBinaryModeUpdating, OpenBinaryModeWriting, OpenTextModeUpdating, OpenTextModeWriting
    from collections.abc import Iterator
    from io import BufferedRandom, BufferedWriter, TextIOWrapper

BATOCERA_SHARE_DIR: Final = Path('/usr/share/batocera')
DATAINIT_DIR: Final = BATOCERA_SHARE_DIR / 'datainit'
USERDATA: Final = Path('/userdata')

HOME_INIT: Final = DATAINIT_DIR / 'system'
CONF_INIT: Final = HOME_INIT / 'configs'

HOME: Final = USERDATA / 'system'
CONFIGS: Final = HOME / 'configs'
EVMAPY: Final = CONFIGS / 'evmapy'
SAVES: Final = USERDATA / 'saves'
SCREENSHOTS: Final = USERDATA / 'screenshots'
RECORDINGS: Final = USERDATA / 'recordings'
BIOS: Final = USERDATA / 'bios'
OVERLAYS: Final = USERDATA / 'overlays'
CACHE: Final = HOME / 'cache'
ROMS: Final = USERDATA / 'roms'
CHEATS: Final = USERDATA / 'cheats'
LOGS: Final = HOME / 'logs'
BATOCERA_CONF: Final = HOME / 'batocera.conf'

USER_ES_DIR: Final = CONFIGS / 'emulationstation'
BATOCERA_ES_DIR: Final = Path('/usr/share/emulationstation')
CONFIGGEN_DATA_DIR: Final = Path('/usr/share/batocera/configgen/data')

_ES_RESOURCES_DIR: Final = BATOCERA_ES_DIR / 'resources'

ES_SETTINGS: Final = USER_ES_DIR / 'es_settings.cfg'
ES_GUNS_METADATA: Final = _ES_RESOURCES_DIR / 'gungames.xml'
ES_WHEELS_METADATA: Final = _ES_RESOURCES_DIR / 'wheelgames.xml'
ES_GAMES_METADATA: Final = _ES_RESOURCES_DIR / 'gamesdb.xml'
ES_GUNS_ART_METADATA: Final = CONFIGGEN_DATA_DIR / 'gamesbuttonsdb.xml'

DEFAULTS_DIR: Final = BATOCERA_SHARE_DIR / 'configgen'

USER_SHADERS: Final = USERDATA / 'shaders'
BATOCERA_SHADERS: Final = BATOCERA_SHARE_DIR / 'shaders'

USER_DECORATIONS: Final = USERDATA / 'decorations'
SYSTEM_DECORATIONS: Final = DATAINIT_DIR / 'decorations'

USER_SCRIPTS: Final = HOME / 'scripts'
SYSTEM_SCRIPTS: Final = DEFAULTS_DIR / 'scripts'


def configure_emulator(rom: Path, /) -> bool:
    return str(rom) == 'config'


def mkdir_if_not_exists(dir: Path, /) -> None:
    if not dir.exists():
        dir.mkdir(parents=True)

@overload
@contextmanager
def ensure_parents_and_open(file: Path, mode: OpenTextModeWriting | OpenTextModeUpdating) -> Iterator[TextIOWrapper]:
    ...

@overload
@contextmanager
def ensure_parents_and_open(file: Path, mode: OpenBinaryModeUpdating) -> Iterator[BufferedRandom]:
    ...

@overload
@contextmanager
def ensure_parents_and_open(file: Path, mode: OpenBinaryModeWriting) -> Iterator[BufferedWriter]:
    ...

@contextmanager
def ensure_parents_and_open(file: Path, mode: str) -> Iterator[IO[Any]]:
    mkdir_if_not_exists(file.parent)
    with file.open(mode) as f:
        yield f
