from __future__ import annotations

import importlib
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from ._generate_proxies import generate_proxies

_GENERATE_PROXIES_COMMAND = 'generate-proxies'


def _generate_proxies(args: Namespace, /) -> None:
    module = importlib.import_module(args.module)
    output_file = args.output_file or (Path(cast('str', module.__file__)).parent / 'proxies.py')

    output_file.write_text(generate_proxies(module, output_file, _GENERATE_PROXIES_COMMAND, args.output_file))


parser = ArgumentParser()
subparsers = parser.add_subparsers(required=True)

generate_proxies_parser = subparsers.add_parser(_GENERATE_PROXIES_COMMAND)
generate_proxies_parser.add_argument(
    'module',
    type=str,
    help='The module to generate client proxies for (e.g. "hotkeygen.dbus.interfaces").',
)
generate_proxies_parser.add_argument(
    'output_file',
    type=Path,
    nargs='?',
    help='The file to write the generated client proxy code to (defaults to `proxies.py` as a sibling of the module argument).',
)
generate_proxies_parser.set_defaults(command_handler=_generate_proxies)

args = parser.parse_args()
args.command_handler(args)
