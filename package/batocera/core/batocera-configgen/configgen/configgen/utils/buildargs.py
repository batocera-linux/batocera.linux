from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

"""Argument parsing helper functions for launching Build Engine source ports Eduke32 and Raze"""


@dataclass()
class ParseError:
    line_no: int
    message: str


@dataclass()
class Result:
    okay: bool
    message: str

    @staticmethod
    def success():
        return Result(True, "")

    @staticmethod
    def error(message: str):
        return Result(False, message)


@dataclass()
class BuildEngineArg:
    arg_key: str
    cli_opt: str
    only_one_allowed: bool


def parse_args(launch_args: list[str | Path], rom_path: Path) -> Result:
    # These arguments are all shared by EDuke32 and Raze, with noted differences
    build_args: dict[str, BuildEngineArg] = {e.arg_key: e for e in [
        BuildEngineArg("DIR", "-j", False),  # Adds directory to search list
        # The main game file to load: EDuke32 and Raze can load .grp, .zip, .ssi, .pk3, .pk4; Raze can also load .7z
        BuildEngineArg("FILE", "-gamegrp", True),
        # Add extra game file to load; this overrides files in virtual filesystem
        BuildEngineArg("FILE+", "-g", False),
        # Replace the main GAME.CON script module; surprisingly this can be a CON, DEF, or INI!
        BuildEngineArg("CON", "-x", True),
        BuildEngineArg("CON+", "-mx", False),  # Append CON after GAME.CON script module
        BuildEngineArg("DEF", "-h", True),  # Replace the main DEF module
        BuildEngineArg("DEF+", "-mh", False),  # Append DEF after main DEF module
        BuildEngineArg("MAP", "-map", True),  # Start specified MAP on launch
    ]}
    with rom_path.open("r") as file:
        lines = file.readlines()
    errors = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("#") or line.startswith("//"):
            continue
        split = line.split("=")
        key = None
        val = None
        if len(split) > 2:
            errors += [ParseError(i, f"found another '=', but there should only be one")]
            continue
        if len(split) == 2:
            key = split[0].strip().upper()
            val = split[1].strip()
        if not key or not val:
            errors += [ParseError(i, f"KEY and/or VAL is empty; are you missing a '='?")]
            continue
        if key not in build_args:
            errors += [ParseError(i, f"KEY '{key}' is not valid")]
            continue
        # Paths that begin with "/" denote absolute path from emulator roms directory e.g. /userdata/roms/raze
        # These paths are expected to exist on physical filesystem
        # Otherwise, no "/", they are expected to exist on the virtual filesystem
        val_path = (rom_path.parent / val[1:]) if val.startswith("/") else val
        build_arg = build_args[key]
        # We will check physical paths exist to be helpful, but virtual paths... who knows
        if isinstance(val_path, Path) and not val_path.exists():
            errors += [ParseError(i, f"{val_path} does not exist")]
            continue
        # Check obvious duplicates; there is never a reason the user would want to do this
        if build_arg.only_one_allowed and build_arg.cli_opt in launch_args:
            errors += [ParseError(i, f"found another '{build_arg.arg_key}', but there should only be one")]
            continue
        launch_args += [build_arg.cli_opt, val_path]
    if len(errors) > 0:
        message = f"{len(errors)} error(s) found in {rom_path}:\n"
        for error in errors:
            line = lines[error.line_no].replace("\n", "")
            message += f"line {error.line_no + 1}| {line}\t<-- {error.message}\n"
        return Result.error(message)
    return Result.success()
