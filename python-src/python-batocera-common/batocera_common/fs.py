from __future__ import annotations

import filecmp
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


type Difference = tuple[None, Path] | tuple[Path, None] | tuple[Path, Path]


def _dircmp_differences(comparison: filecmp.dircmp[str], /) -> Iterator[Difference]:
    left = Path(comparison.left)
    right = Path(comparison.right)

    yield from ((left / name, None) for name in comparison.left_only)
    yield from ((None, right / name) for name in comparison.right_only)
    yield from (
        (left / name, right / name) for name in comparison.diff_files + comparison.funny_files + comparison.common_funny
    )

    for sub in comparison.subdirs.values():
        yield from _dircmp_differences(sub)


@dataclass(slots=True)
class directory_differences:
    left: Path
    right: Path

    _differences: tuple[Difference, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        comparison = filecmp.dircmp(self.left, self.right, shallow=False)
        self._differences = tuple(_dircmp_differences(comparison))

    def __bool__(self) -> bool:
        return bool(self._differences)

    def report(self) -> str:
        if not self._differences:
            return 'Directories are identical'

        left_only: list[Path] = []
        right_only: list[Path] = []
        different: list[Path] = []

        for difference in self._differences:
            if difference[0] is not None:
                if difference[1] is None:
                    left_only.append(difference[0])
                else:
                    different.append(difference[0])
            else:
                right_only.append(difference[1])

        report: list[str] = []

        if left_only:
            report.append(f'Missing in {self.right}:')
            report.extend(f'  {path.relative_to(self.left)}' for path in left_only)

        if right_only:
            report.append(f'Extra in {self.right}:')
            report.extend(f'  {path.relative_to(self.right)}' for path in right_only)

        if different:
            report.append('Different files:')
            report.extend(f'  {path.relative_to(self.left)}' for path in different)

        return '\n'.join(report)
