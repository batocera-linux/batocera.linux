#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from batocera_common.paths import BATOCERA_SHARE_DIR

from .config import RC_XML, LabWCConfig
from .outputs import layout_box
from .types import LabWCRule, Output


def _load_rules(key: str, /) -> list[LabWCRule]:
    rules_file = BATOCERA_SHARE_DIR / 'labwc' / f'{key}.labwc-rules.yml'

    if not rules_file.exists():
        return []

    from batocera_common.yaml import safe_load_yaml12

    return safe_load_yaml12(rules_file, list[LabWCRule]) or []


def _get_output(output: Output, primary: str, secondary: str, /) -> str:
    match output:
        case 'primary':
            return primary
        case 'secondary':
            return secondary
        case 'primary|secondary':
            return primary or secondary
        case 'secondary|primary':  # pragma: no branch
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
                case 'SpanOutputs':  # pragma: no branch
                    # labwc shrinks a new window to one output, so size it over the whole layout afterwards
                    window_rule.span(layout_box((primary, secondary)) if primary and secondary else None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-path', type=Path, default=RC_XML, help='path to rc.xml', metavar='PATH')
    parser.add_argument('--reconfigure', action='store_true', help='reload configuration in LabWC')
    parser.add_argument('--primary', type=str, help='primary output screen')
    parser.add_argument('--secondary', type=str, help='secondary output screen')
    parser.add_argument('--touchscreen', type=str, help='touchscreen device')
    parser.add_argument(
        '--touchscreen-map',
        nargs=3,
        action='append',
        metavar=('DEVICE', 'OUTPUT', 'ROTATION'),
        help='map a touchscreen device to an output, rotation 0-3 (repeatable)',
    )
    parser.add_argument(
        'rule_set',
        type=str,
        nargs='?',
        metavar='RULE-SET',
        help='rule set to apply (default: _global)',
    )

    args = parser.parse_args()

    if (
        args.rule_set is None
        and args.reconfigure
        and args.primary is None
        and args.secondary is None
        and args.touchscreen is None
        and args.touchscreen_map is None
    ):
        LabWCConfig.reconfigure()
        return

    config = LabWCConfig(args.config_path)

    if args.primary is not None and args.secondary is not None:
        rules = _load_rules('_global' if args.rule_set is None else args.rule_set)
        _apply_rules(config, rules, args.primary, args.secondary)

    if args.touchscreen is not None:
        config.set_touchscreen(name=args.touchscreen or None, map_to_output_name=args.primary or None)
    elif args.touchscreen_map is not None:
        config.set_touchscreens(
            [
                (name, output, int(rotation) if rotation.isdigit() else 0)
                for name, output, rotation in args.touchscreen_map
                if name and output
            ]
        )

    config.save()

    if args.reconfigure:
        config.reconfigure()


if __name__ == '__main__':
    main()
