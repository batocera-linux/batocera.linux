#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

from batocera_common.paths import BATOCERA_SHARE_DIR

from .config import RC_XML, LabWCConfig

type Output = Literal['primary', 'secondary', 'primary|secondary', 'secondary|primary']


class MoveToOutputAction(TypedDict):
    name: Literal['MoveToOutput']
    output: Output
    remove_if_missing: NotRequired[bool]


class FocusOutputAction(TypedDict):
    name: Literal['FocusOutput']
    output: Output
    remove_if_missing: NotRequired[bool]


class ToggleFullscreenAction(TypedDict):
    name: Literal['ToggleFullscreen']
    value: NotRequired[bool]


class LabWCRule(TypedDict):
    identifier: NotRequired[str]
    title: NotRequired[str]
    actions: list[MoveToOutputAction | FocusOutputAction | ToggleFullscreenAction]


def _get_rules(key: str, /) -> list[LabWCRule]:
    from batocera_common.yaml import safe_load_yaml12

    rules_map = safe_load_yaml12(BATOCERA_SHARE_DIR / 'labwc' / 'labwc-rules.yml', dict[str, list[LabWCRule]]) or {}

    return rules_map.get(key) or []


def _get_output(output: Output, primary: str, secondary: str, /) -> str:
    match output:
        case 'primary':
            return primary
        case 'secondary':
            return secondary
        case 'primary|secondary':
            return primary or secondary
        case 'secondary|primary':
            return secondary or primary


def _apply_rules(config: LabWCConfig, rules: list[LabWCRule], primary: str, secondary: str, /) -> None:
    for rule in rules:
        identifier = rule.get('identifier')
        title = rule.get('title')

        if identifier is None and title is None:
            raise ValueError("Each rule must have at least an 'identifier' or a 'title'.")

        for action in rule['actions']:
            window_rule = config.window_rule(identifier=identifier, title=title)

            match action['name']:
                case 'MoveToOutput':
                    output = _get_output(action['output'], primary, secondary)
                    if action.get('remove_if_missing', False):
                        window_rule.move_to_output(output or None)
                    elif output:
                        window_rule.move_to_output(output)
                case 'FocusOutput':
                    output = _get_output(action['output'], primary, secondary)
                    if action.get('remove_if_missing', False):
                        window_rule.focus_output(output or None)
                    elif output:
                        window_rule.focus_output(output)
                case 'ToggleFullscreen':
                    window_rule.toggle_fullscreen(action.get('value', True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=Path, default=RC_XML, help='path to rc.xml', metavar='PATH')
    parser.add_argument('--reconfigure', action='store_true', help='reload configuration in LabWC')
    parser.add_argument('--primary', type=str, help='primary output screen')
    parser.add_argument('--secondary', type=str, help='secondary output screen')
    parser.add_argument('--touchscreen', type=str, help='touchscreen device')
    parser.add_argument(
        'rule_set',
        type=str,
        default='main',
        nargs='?',
        metavar='RULE-SET',
        help='rule set to apply (default: main)',
    )

    args = parser.parse_args()

    if (
        args.rule_set == 'main'
        and args.reconfigure
        and args.primary is None
        and args.secondary is None
        and args.touchscreen is None
    ):
        LabWCConfig.reconfigure()
        return

    config = LabWCConfig(args.config_path)

    if args.primary is not None and args.secondary is not None:
        rules = _get_rules(args.rule_set)
        _apply_rules(config, rules, args.primary, args.secondary)

    if args.touchscreen is not None:
        config.set_touchscreen(name=args.touchscreen or None, map_to_output_name=args.primary or None)

    config.save()

    if args.reconfigure:
        config.reconfigure()


if __name__ == '__main__':
    main()
