"""Real audio devices (PipeWire through pactl): is there a microphone, which output is used.

Updated live from ``pactl subscribe``. When a real microphone is present but the default source is a
monitor (what the TV plays), the default source is switched to the microphone: otherwise Discord would
send the game sound instead of the user's voice.
"""

from __future__ import annotations

import json
import logging
import re
import select
import subprocess
import threading
import time
from typing import TYPE_CHECKING, Any, Final, cast

from .state import AudioDevices

if TYPE_CHECKING:
    from .state import State

_logger: Final = logging.getLogger(__name__)
_DEBOUNCE: Final = 0.4
_ERRORS: Final = (OSError, ValueError, subprocess.TimeoutExpired)


def pactl_json(*args: str) -> Any:
    try:
        result = subprocess.run(['pactl', '-f', 'json', *args], capture_output=True, timeout=5, check=False)
        return json.loads(result.stdout or b'null')
    except _ERRORS:
        return None


def _list(kind: str, /) -> list[dict[str, Any]]:
    data = pactl_json('list', kind)
    if not isinstance(data, list):
        return []
    return [cast('dict[str, Any]', item) for item in cast('list[object]', data) if isinstance(item, dict)]


def friendly_name(device: dict[str, Any], /) -> str:
    props = cast('dict[str, str]', device.get('properties') or {})
    name, description = str(device.get('name', '')), str(device.get('description') or '')
    if name.startswith('bluez_'):
        alias = props.get('device.alias') or props.get('bluez5.alias') or description
        return re.sub(r'\s+-\s+Find My$', '', alias)[:24]
    if 'hdmi' in name.lower() or 'hdmi' in description.lower():
        return 'TV (HDMI)'
    if props.get('device.bus') == 'usb':
        return (props.get('device.product.name') or description)[:24]
    return (description or name)[:24]


def is_microphone(source: dict[str, Any], /) -> bool:
    props = cast('dict[str, str]', source.get('properties') or {})
    if props.get('device.class') == 'monitor' or str(source.get('name', '')).endswith('.monitor'):
        return False
    ports = cast('list[dict[str, Any]]', source.get('ports') or [])
    return all(port.get('availability') != 'not available' for port in ports)


def snapshot(*, fix_default_source: bool = True) -> AudioDevices:
    info = pactl_json('info')
    info = cast('dict[str, Any]', info) if isinstance(info, dict) else {}
    sinks, sources, cards = _list('sinks'), _list('sources'), _list('cards')
    mics = [source for source in sources if is_microphone(source)]
    default_source = info.get('default_source_name')
    mic = next((m for m in mics if m.get('name') == default_source), mics[0] if mics else None)
    if mic is not None and fix_default_source and default_source != mic.get('name'):
        subprocess.run(['pactl', 'set-default-source', str(mic['name'])], capture_output=True, timeout=5, check=False)
        _logger.info('default source set to %s', mic['name'])
    sink = next((s for s in sinks if s.get('name') == info.get('default_sink_name')), sinks[0] if sinks else None)
    hifi_headsets = [
        card
        for card in cards
        if str(card.get('name', '')).startswith('bluez_card.') and 'a2dp' in str(card.get('active_profile') or '')
    ]
    return AudioDevices(
        mic=friendly_name(mic) if mic is not None else None,
        output=friendly_name(sink) if sink is not None else '',
        headset_without_mic=friendly_name(hifi_headsets[0]) if hifi_headsets and mic is None else None,
    )


def _refresh(state: State, /) -> None:
    devices = snapshot()
    with state.lock:
        if devices != state.audio:
            state.audio = devices
            state.bump()


def _watch(state: State, /) -> None:
    _refresh(state)
    while True:
        try:
            with subprocess.Popen(
                ['pactl', 'subscribe'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
            ) as proc:
                assert proc.stdout is not None
                due = 0.0
                while True:
                    ready, _, _ = select.select([proc.stdout], [], [], 0.25)
                    if ready:
                        line = proc.stdout.readline()
                        if not line:
                            break
                        # sink/source/card/server changes matter; stream (sink-input/source-output) churn does not
                        if (
                            re.search(r'on (sink|source|card|server)\b', line)
                            and 'input' not in line
                            and 'output' not in line
                        ):
                            due = time.monotonic() + _DEBOUNCE
                    if due and time.monotonic() >= due:
                        due = 0.0
                        _refresh(state)
                proc.kill()
        except OSError:
            _logger.exception('pactl subscribe failed')
        time.sleep(2)
        _refresh(state)


def start_watcher(state: State, /) -> None:
    threading.Thread(target=_watch, args=(state,), name='discord-audio', daemon=True).start()
