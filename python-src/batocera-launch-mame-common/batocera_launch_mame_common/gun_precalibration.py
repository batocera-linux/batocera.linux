from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Rom


def precalibrate_mame_guns(rom: Rom, precalibration_dir: Path, target_dir: Path, /) -> None:
    src = precalibration_dir / 'nvram' / rom.stem
    dest = target_dir / 'nvram' / rom.stem

    if src.is_dir() and not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        src.copy(dest, preserve_metadata=True)

    src_diff = precalibration_dir / 'diff'
    dest_diff = target_dir / 'diff'
    starts_with = f'{rom.stem}_'

    for src_diff_file in src_diff.iterdir():
        dest_diff_file = dest_diff / src_diff_file.name

        if src_diff_file.name.startswith(starts_with) and not dest_diff_file.exists():
            dest_diff_file.parent.mkdir(parents=True, exist_ok=True)
            src_diff_file.copy(dest_diff_file)
