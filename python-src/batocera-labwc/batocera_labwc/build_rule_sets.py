from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict

from batocera_common.yaml import safe_dump_yaml12, safe_load_yaml12

if TYPE_CHECKING:
    from .types import LabWCRule


class LabWCEmulatorInfo(TypedDict):
    window_rules: NotRequired[list[LabWCRule]]


class EmulatorInfo(TypedDict):
    labwc: NotRequired[LabWCEmulatorInfo]


def _main(info_path_file: Path, destination_dir: Path, /) -> None:
    info_files = (
        Path(str_path)
        for str_path in info_path_file.read_text().strip().split()
        if (info_file := Path(str_path))
        and info_file.name.endswith(('.emulator.yml', '.emulator.yaml'))
        and (parts := info_file.stem.split('.'))
        and len(parts) == 2
        and parts[-1] == 'emulator'
    )

    for info_file in info_files:
        emulator_info = safe_load_yaml12(info_file, EmulatorInfo) or {}

        if 'labwc' in emulator_info and 'window_rules' in emulator_info['labwc']:
            safe_dump_yaml12(
                emulator_info['labwc']['window_rules'],
                destination_dir / f'{info_file.stem.removesuffix(".emulator")}.labwc-rules.yml',
            )


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        'info_path_file',
        type=Path,
        help='Path to file containing paths of YAML files to build labwc rule sets from',
    )
    parser.add_argument(
        'destination_dir',
        type=Path,
        help='Path to directory where the built rule sets will be written',
    )

    args = parser.parse_args()

    _main(args.info_path_file, args.destination_dir)


if __name__ == '__main__':
    main()
