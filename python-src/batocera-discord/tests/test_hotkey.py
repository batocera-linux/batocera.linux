from __future__ import annotations

import json
from typing import TYPE_CHECKING

from batocera_discord import hotkey, paths

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

_CODES = {'KEY_RECORD': 167, 'KEY_MENU': 139, 'BTN_MODE': 316}


def _box(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, /) -> list[str]:
    """Batocera's hotkeygen folders in tmp_path; returns the list of hotkeygen reloads."""
    reloads: list[str] = []
    system = tmp_path / 'etc' / 'hotkeygen'
    system.mkdir(parents=True)
    (system / 'default_mapping.conf').write_text(json.dumps({'KEY_MENU': 'menu', 'KEY_CONTEXT_MENU': 'controlcenter'}))
    monkeypatch.setattr(paths, 'HOTKEYGEN_SYSTEM_DIR', system)
    monkeypatch.setattr(paths, 'HOTKEYGEN_USER_DIR', tmp_path / 'configs' / 'hotkeygen')
    monkeypatch.setattr(hotkey, 'key_code', _CODES.get)
    monkeypatch.setattr(hotkey, 'reload_hotkeygen', lambda: reloads.append('reload'))
    monkeypatch.setattr(hotkey, 'toggle_command', lambda: 'batocera-discord toggle')
    return reloads


def _user(tmp_path: Path, name: str, /) -> dict[str, str]:
    return json.loads((tmp_path / 'configs' / 'hotkeygen' / name).read_text())


def test_action_is_declared_in_the_user_configuration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloads = _box(tmp_path, monkeypatch)

    assert hotkey.register()
    assert hotkey.register()  # already there: nothing written, no reload

    assert _user(tmp_path, 'common_context.conf') == {'discord': 'batocera-discord toggle'}
    assert _user(tmp_path, 'default_mapping.conf') == {'KEY_RECORD': 'discord'}
    assert json.loads((tmp_path / 'etc' / 'hotkeygen' / 'default_mapping.conf').read_text())['KEY_MENU'] == 'menu'
    assert reloads == ['reload']


def test_user_entries_are_kept(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _box(tmp_path, monkeypatch)
    user = tmp_path / 'configs' / 'hotkeygen'
    user.mkdir(parents=True)
    (user / 'common_context.conf').write_text(json.dumps({'screenshot': 'my-screenshot'}))
    (user / 'default_mapping.conf').write_text(json.dumps({'KEY_RECORD': 'screenshot'}))

    assert not hotkey.register()  # the user gave this key to another action

    assert _user(tmp_path, 'common_context.conf') == {
        'screenshot': 'my-screenshot',
        'discord': 'batocera-discord toggle',
    }
    assert _user(tmp_path, 'default_mapping.conf') == {'KEY_RECORD': 'screenshot'}


def test_system_hotkeys_and_bad_keys_are_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reloads = _box(tmp_path, monkeypatch)

    assert not hotkey.register('KEY_MENU')  # the "menu" hotkey of Batocera
    assert not hotkey.register('KEY_NOT_A_KEY')
    assert not hotkey.register('none')

    assert not (tmp_path / 'configs' / 'hotkeygen').exists()
    assert not reloads


def test_unreadable_user_file_is_left_alone(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _box(tmp_path, monkeypatch)
    user = tmp_path / 'configs' / 'hotkeygen'
    user.mkdir(parents=True)
    (user / 'default_mapping.conf').write_text('{ not json')

    assert not hotkey.register()

    assert (user / 'default_mapping.conf').read_text() == '{ not json'
