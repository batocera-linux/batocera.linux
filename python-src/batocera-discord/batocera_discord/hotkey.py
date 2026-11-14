"""Opening the panel through hotkeygen, the global hotkey daemon of Batocera.

The service does not watch the controllers while the panel is closed. It declares a ``discord`` action
in the *user* configuration of hotkeygen (``/userdata/system/configs/hotkeygen``, never the system one):
the action runs ``batocera-discord toggle``, and a controller key triggers it, in EmulationStation as in
games. The default key is the Share / Capture button of recent controllers (``KEY_RECORD``);
``discord.hotkey`` in batocera.conf picks another one, and ``discord.hotkey=none`` leaves hotkeygen alone.

Existing user entries are never changed, and a key already used by a system action is never taken.
Controllers with their own hotkeygen mapping file (some handhelds) ignore the default mapping: their
key is set in that file instead.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from typing import TYPE_CHECKING, Any, Final, cast

from . import paths
from .errors import IO_ERRORS, PROCESS_ERRORS

if TYPE_CHECKING:
    from pathlib import Path

_logger: Final = logging.getLogger(__name__)

ACTION: Final = 'discord'
DEFAULT_KEY: Final = 'KEY_RECORD'


def toggle_command() -> str:
    if executable := shutil.which('batocera-discord'):
        return f'{executable} toggle'
    return f'kill -USR1 $(cat {paths.PID_FILE})'  # development install, outside of PATH


def key_code(name: str, /) -> int | None:
    """The evdev code of a ``KEY_*`` / ``BTN_*`` name, None if hotkeygen would reject it."""
    if not name.startswith(('KEY_', 'BTN_')):
        return None
    from evdev import ecodes  # Linux only

    code = ecodes.ecodes.get(name)
    return code if isinstance(code, int) else None


def _read(path: Path, /) -> dict[str, Any] | None:
    """The JSON object in ``path`` ({} when missing), None when it cannot be read safely."""
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except IO_ERRORS:
        _logger.warning('%s is not valid JSON: leaving it alone', path)
        return None
    return cast('dict[str, Any]', data) if isinstance(data, dict) else None


def _add(path: Path, key: str, value: str, /) -> bool:
    """Add ``key`` to a hotkeygen JSON file unless it is already there. Returns True when written."""
    data = _read(path)
    if data is None or key in data:
        return False
    data[key] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)
    return True


def register(key: str = DEFAULT_KEY, /) -> bool:
    """Declare the action and its key in the user hotkeygen configuration.

    Returns True when ``key`` opens the panel (already, or from now on).
    """
    if key.lower() == 'none':
        return False
    if key_code(key) is None:
        _logger.warning('discord.hotkey=%s is not a KEY_ or BTN_ name: no hotkey', key)
        return False
    system = _read(paths.HOTKEYGEN_SYSTEM_DIR / 'default_mapping.conf') or {}
    if system.get(key, ACTION) != ACTION:
        _logger.warning('%s is already the %r hotkey of Batocera: no hotkey', key, system[key])
        return False
    user_mapping = paths.HOTKEYGEN_USER_DIR / 'default_mapping.conf'
    try:
        changed = _add(paths.HOTKEYGEN_USER_DIR / 'common_context.conf', ACTION, toggle_command())
        changed |= _add(user_mapping, key, ACTION)
    except OSError:
        _logger.exception('cannot write the hotkeygen configuration')
        return False
    if (_read(user_mapping) or {}).get(key) != ACTION:
        _logger.warning('%s is set to another action in %s: no hotkey', key, user_mapping)
        return False
    if changed:
        _logger.info('hotkeygen: %s opens the panel', key)
        reload_hotkeygen()
    return True


def reload_hotkeygen() -> None:
    if shutil.which('hotkeygen') is None:
        return
    try:
        subprocess.run(['hotkeygen', '--reload'], capture_output=True, timeout=10, check=False)
    except PROCESS_ERRORS:
        _logger.warning('cannot reload hotkeygen', exc_info=True)
