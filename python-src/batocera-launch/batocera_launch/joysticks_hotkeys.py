from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Final, NamedTuple

from batocera_common.paths import CONFIGS

from .paths import EVMAPY_SHARE_DIR

_SYSTEM_HOTKEYS_FILE: Final = EVMAPY_SHARE_DIR / 'hotkeys.keys'
_USER_HOTKEYS_FILE: Final = CONFIGS / 'hotkeys.keys'
_HOTKEYGEN_MAPPING = Path('/etc/hotkeygen/default_mapping.conf')


class HotkeysMapping(NamedTuple):
    by_keys: dict[str, str]
    by_names: dict[str, str]


def _read_config(
    system_config_file: Path,
    user_config_file: Path,
    system_only: bool = False,
    /,
) -> dict[str, Any]:
    if user_config_file.exists() and not system_only:
        try:
            return json.loads(user_config_file.read_text())
        except Exception:
            print(f'Unable to read user file {user_config_file}', file=sys.stderr)

    return json.loads(system_config_file.read_text())


def _read_hotkey_mapping(hotkey_mapping_file: Path, /) -> HotkeysMapping:
    by_keys = json.loads(hotkey_mapping_file.read_text())

    non_game_hotkeys = ['KEY_FILE']

    # remove hotkeys not for games
    for k in non_game_hotkeys:
        if k in by_keys:
            del by_keys['KEY_FILE']

    by_names: dict[str, str] = {}
    for m in by_keys:
        by_names[by_keys[m]] = m

    return HotkeysMapping(by_keys=by_keys, by_names=by_names)


def _list_hotkeys(
    config: dict[str, Any],
    default_config: dict[str, Any],
    hotkeys_mapping: HotkeysMapping,
    /,
) -> None:
    if sys.stdout.isatty():
        _list_hotkeys_text(config, default_config, hotkeys_mapping)
    else:
        _list_hotkeys_xml(config, default_config, hotkeys_mapping)


def _is_simple_key(key: dict[str, Any], /) -> bool:
    return (
        isinstance(key['trigger'], list)
        and len(key['trigger']) == 2  # pyright: ignore
        and key['trigger'][0] == 'hotkey'
        and key['type'] == 'key'
        and isinstance(key['target'], list)
        and len(key['target']) == 1  # pyright: ignore
    )


def _get_keys_from_config(config: dict[str, Any], /) -> dict[str, Any]:
    keys: dict[str, Any] = {}
    for key in config['actions_player1']:
        if _is_simple_key(key):
            btn = key['trigger'][1]
            action = key['target'][0]
            keys[btn] = {'action': action}
    return keys


def _list_hotkeys_xml(
    config: dict[str, Any],
    default_config: dict[str, Any],
    hotkeys_mapping: HotkeysMapping,
    /,
) -> None:
    keys = _get_keys_from_config(config)
    default_keys = _get_keys_from_config(default_config)
    order = [
        'start',
        'select',
        'up',
        'down',
        'left',
        'right',
        'a',
        'b',
        'x',
        'y',
        'pageup',
        'pagedown',
        'l2',
        'r2',
        'l3',
        'r3',
    ]

    sorted_keys: dict[str, Any] = {}
    for k in order:
        if k in keys:
            sorted_keys[k] = keys[k]
        else:
            sorted_keys[k] = None
    for k in keys:
        if k not in sorted_keys:
            sorted_keys[k] = keys[k]

    print('<hotkeys>')
    for btn in sorted_keys:
        action_name = ''
        default_action_name = ''

        if btn in keys:
            action_name = f'unknown ({keys[btn]["action"]})'
            if keys[btn]['action'] in hotkeys_mapping.by_keys:
                action_name = hotkeys_mapping.by_keys[keys[btn]['action']]

        if btn in default_keys:
            default_action_name = f'unknown ({default_keys[btn]["action"]})'
            if default_keys[btn]['action'] in hotkeys_mapping.by_keys:
                default_action_name = hotkeys_mapping.by_keys[default_keys[btn]['action']]

        print(f'  <hotkey button="{btn}" action="{action_name}" default="{default_action_name}" />')

    print('</hotkeys>')


def _list_hotkeys_text(
    config: dict[str, Any],
    default_config: dict[str, Any],
    hotkeys_mapping: HotkeysMapping,
    /,
) -> None:
    keys = _get_keys_from_config(config)
    default_keys = _get_keys_from_config(default_config)
    order = [
        'start',
        'select',
        'up',
        'down',
        'left',
        'right',
        'a',
        'b',
        'x',
        'y',
        'pageup',
        'pagedown',
        'l2',
        'r2',
        'l3',
        'r3',
    ]

    sorted_keys: dict[str, Any] = {}
    for k in order:
        if k in keys:
            sorted_keys[k] = keys[k]
        else:
            sorted_keys[k] = None
    for k in keys:
        if k not in sorted_keys:
            sorted_keys[k] = keys[k]

    for btn in sorted_keys:
        action_name = None
        default_action_name = None

        if btn in keys:
            action_name = f'unknown ({keys[btn]["action"]})'
            if keys[btn]['action'] in hotkeys_mapping.by_keys:
                action_name = hotkeys_mapping.by_keys[keys[btn]['action']]

        if btn in default_keys:
            default_action_name = f'unknown ({default_keys[btn]["action"]})'
            if default_keys[btn]['action'] in hotkeys_mapping.by_keys:
                default_action_name = hotkeys_mapping.by_keys[default_keys[btn]['action']]

        if btn == 'pageup':
            btn = 'l'
        if btn == 'pagedown':
            btn = 'r'

        help = ''
        if action_name != default_action_name:
            help = f' (default: {default_action_name})'
        print(f'hotkey + {btn:6} : {action_name}{help}')


def _update_hotkeys(
    config: dict[str, Any],
    new_keys: dict[str, Any],
    user_config_file: Path,
    default_config: dict[str, Any],
    /,
) -> None:
    # update keys
    for new_key in new_keys:
        if gdebug:
            print(f'updating key {new_key}', file=sys.stderr)
        found = False
        for index, key in enumerate(config['actions_player1']):
            if _is_simple_key(key) and key['trigger'][1] == new_key:
                if gdebug:
                    print(f'key {new_key} already set. reaffecting it.', file=sys.stderr)
                found = True
                if new_keys[new_key] == 'none':
                    del config['actions_player1'][index]
                else:
                    if new_keys[new_key] == 'default':
                        # get default
                        for default_key in default_config['actions_player1']:
                            if _is_simple_key(default_key) and default_key['trigger'][1] == new_key:
                                config['actions_player1'][index]['target'] = default_key['target']
                    else:
                        config['actions_player1'][index]['target'] = [new_keys[new_key]]
        # the key was removed, add it back from default config
        if not found:
            if gdebug:
                print(f'key {new_key} is not defined. affecting it.', file=sys.stderr)
            if new_keys[new_key] != 'none':
                found = False
                for key in default_config['actions_player1']:
                    if _is_simple_key(key) and key['trigger'][1] == new_key:
                        # find the default key and append it
                        found = True
                        print(f'key {new_key} initialized with default value, before reaffecting.', file=sys.stderr)
                        if new_keys[new_key] != 'default':
                            key['target'] = [new_keys[new_key]]
                        config['actions_player1'].append(key)
                if not found and new_keys[new_key] != 'default':
                    print(f'key {new_key} has no default value. affect a default mapping.', file=sys.stderr)
                    key = {'trigger': ['hotkey', new_key], 'type': 'key', 'target': [new_keys[new_key]]}
                    config['actions_player1'].append(key)
    # save
    user_config_file.write_text(json.dumps(config, indent=4))


def _list_values(by_names: dict[str, str], /) -> None:
    for key in sorted(by_names):
        print(key)


def main() -> None:
    parser = argparse.ArgumentParser(prog='batocera-joysticks-hotkeys')
    parser.add_argument('--values', action='store_true', help='list possible values. none and default can be used too.')
    parser.add_argument('--start', type=str, help='key for hotkey+start')
    parser.add_argument('--select', type=str, help='key for hotkey+select')
    parser.add_argument('--up', type=str, help='key for hotkey+up')
    parser.add_argument('--down', type=str, help='key for hotkey+down')
    parser.add_argument('--left', type=str, help='key for hotkey+left')
    parser.add_argument('--right', type=str, help='key for hotkey+right')
    parser.add_argument('--a', type=str, help='key for hotkey+a')
    parser.add_argument('--b', type=str, help='key for hotkey+b')
    parser.add_argument('--x', type=str, help='key for hotkey+x')
    parser.add_argument('--y', type=str, help='key for hotkey+y')
    parser.add_argument('--l', type=str, help='key for hotkey+l')
    parser.add_argument('--r', type=str, help='key for hotkey+r')
    parser.add_argument('--pageup', type=str, help='key for hotkey+l')
    parser.add_argument('--pagedown', type=str, help='key for hotkey+r')
    parser.add_argument('--l2', type=str, help='key for hotkey+l2')
    parser.add_argument('--r2', type=str, help='key for hotkey+r2')
    parser.add_argument('--l3', type=str, help='key for hotkey+l3')
    parser.add_argument('--r3', type=str, help='key for hotkey+r3')
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()
    new_keys: dict[str, str] = {}

    if args.start:
        new_keys['start'] = args.start
    if args.select:
        new_keys['select'] = args.select
    if args.up:
        new_keys['up'] = args.up
    if args.down:
        new_keys['down'] = args.down
    if args.left:
        new_keys['left'] = args.left
    if args.right:
        new_keys['right'] = args.right
    if args.a:
        new_keys['a'] = args.a
    if args.b:
        new_keys['b'] = args.b
    if args.x:
        new_keys['x'] = args.x
    if args.y:
        new_keys['y'] = args.y
    if args.l:
        new_keys['pageup'] = args.l
    if args.r:
        new_keys['pagedown'] = args.r
    if args.pageup:
        new_keys['pageup'] = args.pageup
    if args.pagedown:
        new_keys['pagedown'] = args.pagedown
    if args.l2:
        new_keys['l2'] = args.l2
    if args.r2:
        new_keys['r2'] = args.r2
    if args.l3:
        new_keys['l3'] = args.l3
    if args.r3:
        new_keys['r3'] = args.r3

    global gdebug
    gdebug = args.debug
    hotkeys_mapping = _read_hotkey_mapping(_HOTKEYGEN_MAPPING)

    if args.values:
        _list_values(hotkeys_mapping.by_names)
        exit(0)

    default_config = _read_config(_SYSTEM_HOTKEYS_FILE, _USER_HOTKEYS_FILE, True)
    config = _read_config(_SYSTEM_HOTKEYS_FILE, _USER_HOTKEYS_FILE)

    # convert new keys
    for k in new_keys:
        if new_keys[k] in hotkeys_mapping.by_names:
            new_keys[k] = hotkeys_mapping.by_names[new_keys[k]]

    if len(new_keys) == 0:
        _list_hotkeys(config, default_config, hotkeys_mapping)
    else:
        _update_hotkeys(config, new_keys, _USER_HOTKEYS_FILE, default_config)


if __name__ == '__main__':
    main()
