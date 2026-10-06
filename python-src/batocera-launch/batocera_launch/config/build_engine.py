from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from ..exceptions import InvalidConfiguration

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class _BuildEngineArg:
    key: str
    option: str
    only_one: bool = False


# Shared by EDuke32 and Raze (with noted differences).
_BUILD_ENGINE_ARGS: Final = {
    arg.key: arg
    for arg in (
        _BuildEngineArg('DIR', '-j'),  # Adds directory to search list
        # Main game file: EDuke32/Raze load .grp/.zip/.ssi/.pk3/.pk4; Raze also .7z
        _BuildEngineArg('FILE', '-gamegrp', only_one=True),
        _BuildEngineArg('FILE+', '-g'),  # Extra game file; overrides virtual FS entries
        # Replace main GAME.CON script module (may be CON, DEF, or INI)
        _BuildEngineArg('CON', '-x', only_one=True),
        _BuildEngineArg('CON+', '-mx'),  # Append CON after GAME.CON
        _BuildEngineArg('DEF', '-h', only_one=True),  # Replace main DEF module
        _BuildEngineArg('DEF+', '-mh'),  # Append DEF after main DEF module
        _BuildEngineArg('MAP', '-map', only_one=True),  # Start specified MAP on launch
    )
}


def parse_build_engine_args(
    rom_path: Path,
    /,
    *,
    existing: Iterable[str | Path] | None = None,
) -> list[str | Path]:
    """Parse Build Engine launcher arguments from a ROM script (EDuke32 / Raze).

    Lines are ``KEY=value``. A leading ``/`` on the value means a path relative to the
    ROM's parent directory (physical filesystem); otherwise the value is kept as a
    virtual-filesystem path.

    Args:
        rom_path: Path to the launcher script.
        existing: CLI args already present; used to enforce single-use options.

    Returns:
        Alternating option/value pairs suitable for extending a command line.

    Raises:
        InvalidConfiguration: If the script contains one or more parse errors.
    """
    lines = rom_path.read_text().splitlines()
    args: list[str | Path] = []
    seen_options: set[str] = set() if existing is None else {arg for arg in existing if isinstance(arg, str)}
    errors: list[tuple[int, str]] = []

    for line_no, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line or line.startswith(('#', '//')):
            continue

        parts = line.split('=')
        if len(parts) > 2:
            errors.append((line_no, "found another '=', but there should only be one"))
            continue
        if len(parts) < 2:
            errors.append((line_no, "KEY and/or VAL is empty; are you missing a '='?"))
            continue

        key = parts[0].strip().upper()
        value_str = parts[1].strip()
        if not key or not value_str:
            errors.append((line_no, "KEY and/or VAL is empty; are you missing a '='?"))
            continue

        build_arg = _BUILD_ENGINE_ARGS.get(key)
        if build_arg is None:
            errors.append((line_no, f"KEY '{key}' is not valid"))
            continue

        # "/" denotes a path under the ROM directory; otherwise treat as virtual FS.
        value: str | Path
        if value_str.startswith('/'):
            value = rom_path.parent / value_str[1:]
            if not value.exists():
                errors.append((line_no, f'{value} does not exist'))
                continue
        else:
            value = value_str

        if build_arg.only_one and build_arg.option in seen_options:
            errors.append((line_no, f"found another '{build_arg.key}', but there should only be one"))
            continue

        args.extend((build_arg.option, value))
        seen_options.add(build_arg.option)

    if errors:
        message = f'{len(errors)} error(s) found in {rom_path}:\n'
        message += ''.join(f'line {line_no + 1}| {lines[line_no]}\t<-- {error}\n' for line_no, error in errors)
        raise InvalidConfiguration(message)

    return args
