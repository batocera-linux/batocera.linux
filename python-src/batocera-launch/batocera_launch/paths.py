from __future__ import annotations

from pathlib import Path
from typing import Final

from batocera_common.paths import BATOCERA_SHARE_DIR, CONFIGS, HOME, USERDATA

DATAINIT_DIR: Final = BATOCERA_SHARE_DIR / 'datainit'

HOME_INIT: Final = DATAINIT_DIR / 'system'
CONF_INIT: Final = HOME_INIT / 'configs'

EVMAPY: Final = CONFIGS / 'evmapy'

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
