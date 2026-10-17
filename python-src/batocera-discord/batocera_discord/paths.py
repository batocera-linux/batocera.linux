from __future__ import annotations

from pathlib import Path
from typing import Final

USERDATA: Final = Path('/userdata')
CONFIG_DIR: Final = USERDATA / 'system' / 'configs' / 'discord'
CONFIG_FILE: Final = CONFIG_DIR / 'config.json'
TOKENS_FILE: Final = CONFIG_DIR / 'tokens.json'
RECENTS_FILE: Final = CONFIG_DIR / 'recents.json'
CACHE_DIR: Final = USERDATA / 'system' / 'cache' / 'discord'
LOG_FILE: Final = USERDATA / 'system' / 'logs' / 'discord.log'
BATOCERA_CONF: Final = USERDATA / 'system' / 'batocera.conf'

RUN_DIR: Final = Path('/var/run')
PID_FILE: Final = RUN_DIR / 'batocera-discord.pid'
LOCK_FILE: Final = RUN_DIR / 'batocera-discord.lock'

# Flatpak apps run as root on Batocera with XDG_RUNTIME_DIR=/var/run (see batocera-launch flatpak emulator)
FLATPAK_APP_ID: Final = 'com.discordapp.Discord'
FLATPAK_RUNTIME_DIR: Final = RUN_DIR

# Fonts shipped with the image: the default ES theme font first, then broad-coverage fallbacks
FONT_REGULAR: Final = (
    Path('/usr/share/emulationstation/themes/es-theme-carbon/art/fonts/Cabin-Regular.ttf'),
    Path('/usr/share/fonts/dejavu/DejaVuSans.ttf'),
)
FONT_BOLD: Final = (
    Path('/usr/share/emulationstation/themes/es-theme-carbon/art/fonts/Cabin-Bold.ttf'),
    Path('/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'),
)
FONT_SYMBOLS: Final = (Path('/usr/share/fonts/dejavu/DejaVuSans.ttf'),)
FONT_CJK: Final = (
    Path('/usr/share/emulationstation/resources/DroidSansFallbackFull.ttf'),
    Path('/usr/share/fonts/truetype/droid/DroidSansFallback.ttf'),
)
