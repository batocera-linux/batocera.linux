from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

from batocera_es_system.registry import Registry

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping


# numbers: 8, 10, 500+, 2.5, 100%, 3x, +50%
_number_pattern = re.compile(r'^(?:(?:[0-9]+(?:\.[0-9]+)?[+]?)|(?:[+-]?[0-9]+[%x]?))$')

# ratios and simple resolutions: 4:3, 4/3, 640x480
_ratio_pattern = re.compile(r'^[0-9]+[/:x][0-9]+$')

# complex resolutions: (2x 640x480, 4x (640x480), x4 640x480, 3x 1080p (1920x1584), 2x 720p, 7x 2880p 5K
_resolution_pattern = re.compile(r'^[xX]?[0-9]*[xX]?[ ]*\(?[0-9]+[x]?[0-9]+[pK]?\)?[ ]*\(?[0-9]+[x]?[0-9]+[pK]?\)?$')


def _iterate_strings(strings: Mapping[str, Iterable[str]], /) -> Iterator[tuple[str, str]]:
    for string, comments in strings.items():
        added_comments: list[str] = []
        for comment in sorted(comments):
            if comment not in added_comments:
                added_comments.append(comment)

            if len(added_comments) >= 5:
                added_comments.append('...')
                break

        yield string, ', '.join(added_comments)


def _iterate_translation_strings(translation_strings: Mapping[str, Iterable[str]], /) -> Iterator[tuple[str, str]]:
    for string, comments in _iterate_strings(translation_strings):
        # skip if string is an empty string or None
        if not string:
            continue

        if _number_pattern.match(string):
            continue

        if _ratio_pattern.match(string):
            continue

        if _resolution_pattern.match(string):
            continue

        yield string, comments


def _write_es_translations(translation_strings: Mapping[str, Iterable[str]], output_file: Path, /) -> None:
    if not translation_strings:
        return

    print('Generating ES translations...')
    with output_file.open('w') as file:
        file.write("// file generated automatically by batocera-finalize-es-data, don't modify it\n\n")

        for index, (string, comments) in enumerate(_iterate_translation_strings(translation_strings), start=1):
            file.write(f'/* TRANSLATION: {comments} */\n')
            file.write(
                f'#define fake_gettext_external_{index} pgettext("game_options", "{string.replace('"', r"\"")}")\n'
            )


def _write_es_keys_translations(parent_dir: Path, output_file: Path, /) -> None:
    print('Generating ES keys translations...')

    keys_strings: dict[str, set[str]] = defaultdict(set)

    for file in parent_dir.glob('**/*.keys'):
        print(f'... {file}')
        content: dict[str, list[dict[str, str]]] = json.loads(file.read_text())
        for actions in content.values():
            for action in actions:
                if 'description' in action:
                    keys_strings[action['description']].add(file.name)

    with output_file.open('w') as fd:
        fd.write("// file generated automatically by batocera-finalize-es-data, don't modify it\n\n")

        for index, (string, comments) in enumerate(_iterate_strings(keys_strings)):
            fd.write(f'/* TRANSLATION: {comments} */\n')
            fd.write(f'#define fake_gettext_external_{index} pgettext("keys_files", "{string.replace('"', r"\"")}")\n')


def build(
    registry: Registry,
    keys_dir: Path,
    locales_dir: Path,
    output_dir: Path,
    /,
) -> None:
    blacklisted_words: set[str] = set()

    with (locales_dir / 'blacklisted-words.txt').open() as f:
        for line in f:
            blacklisted_words.add(line.rstrip('\n'))

    translation_strings: dict[str, list[str]] = defaultdict(list)

    for emulator in registry:
        for string, comment in emulator.get_translation_data():
            if string not in blacklisted_words:
                core = comment.get('core', '')
                core = f'/{core}' if core and comment['emulator'] != core else ''
                translation_strings[string].append(f'{comment["emulator"]}{core}')

    _write_es_translations(translation_strings, output_dir / 'es_external_translations.h')
    _write_es_keys_translations(keys_dir, output_dir / 'es_keys_translations.h')


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--locales-dir', type=Path, required=True, help='Path to locales directory')
    parser.add_argument('--keys-dir', type=Path, required=True, help='Path to batocera-es-system keys directory')
    parser.add_argument('--output', type=Path, required=True, help='Path to build directory')
    parser.add_argument(
        'path_info_file', type=Path, help='Path to file containing paths of YAML files to load into the registry'
    )

    args = parser.parse_args()

    registry = Registry.load_path_file(args.path_info_file)

    build(registry, args.keys_dir, args.locales_dir, args.output)
