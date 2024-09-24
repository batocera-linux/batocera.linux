from pathlib import Path
from typing import Final

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
LOGS: Final = HOME / 'logs'
BATOCERA_CONF: Final = HOME / 'batocera.conf'

USER_ES_DIR: Final = CONFIGS / 'emulationstation'
BATOCERA_ES_DIR: Final = Path('/usr/share/emulationstation')

_ES_RESOURCES_DIR: Final = BATOCERA_ES_DIR / 'resources'

ES_SETTINGS: Final = USER_ES_DIR / 'es_settings.cfg'
ES_GUNS_METADATA: Final = _ES_RESOURCES_DIR / 'gungames.xml'
ES_WHEELS_METADATA: Final = _ES_RESOURCES_DIR / 'wheelgames.xml'
ES_GAMES_METADATA: Final = _ES_RESOURCES_DIR / 'gamesdb.xml'

DEFAULTS_DIR: Final = BATOCERA_SHARE_DIR / 'configgen'

USER_SHADERS: Final = USERDATA / 'shaders'
BATOCERA_SHADERS: Final = BATOCERA_SHARE_DIR / 'shaders'

USER_DECORATIONS: Final = USERDATA / 'decorations'
SYSTEM_DECORATIONS: Final = DATAINIT_DIR / 'decorations'
