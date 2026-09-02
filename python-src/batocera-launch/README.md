# batocera-launch

Game/emulator launcher for Batocera. It replaces the old launch path in
`batocera-configgen` (`emulatorlauncher.py` + per-emulator `Generator`
classes) with an async `Emulator` base class that owns ROM preparation,
controllers, guns, wheels, resolution, bezels, HUD, hotkeys, and process
execution.

CLI entry points: `batocera-launch` and `emulatorlauncher` (same main).

For porting a configgen generator into an `Emulator` subclass, see
[MIGRATION.md](MIGRATION.md).

## Layout

| Path | Role |
|---|---|
| `batocera_launch/emulator.py` | `Emulator` base class and entry-point loader |
| `batocera_launch/rom.py` | `Rom` helper (squashfs mount, source vs prepared path) |
| `batocera_launch/command.py` | `Command` to run the emulator process |
| `batocera_launch/emulators/` | In-tree emulator subclasses |
| `batocera_launch/cli/` | Argument parsing and main |
| `batocera_launch/config/` | System config, LabWC, libretro helpers, … |
| `batocera_launch/devices/` | Controllers, guns, wheels, video, mouse, … |
| `resources/` | Default options, scripts, and data installed on target |
| `tests/` | pytest suite |
| `batocera-launch.mk` | Buildroot package; excludes unused in-tree emulators |

Related packages live beside this one as `python-src/batocera-launch-<name>/`
(e.g. flycast, rpcs3).

## How emulator classes are loaded

`Emulator.create()` resolves the class via the
[`entry_points`](https://docs.python.org/3/library/importlib.metadata.html#entry-points)
group `batocera_launch.emulators` (`Emulator._load_class`):

1. Look up an entry point named like `system_config.emulator`.
2. If found, load and use that class.
3. Otherwise load the special `configgen` entry point
   (`configgen.launch:GeneratorEmulator`), which wraps a legacy `Generator`.
4. If `configgen` is also missing, raise `UnknownEmulator`.

Setting `configgen=1` in batocera.conf forces the entire legacy
`configgen.emulatorlauncher` path instead of batocera-launch.

## In-tree vs separate packages

Because discovery uses entry points, an emulator class may ship in this
package or in its own `batocera-launch-*` distribution. The loader only
matches the emulator id; Buildroot can install heavy or optional emulators
without growing the core package for every port.

In-tree modules register in this package’s `pyproject.toml` and are omitted
from images that lack the binary via `BATOCERA_LAUNCH_LOCAL_PYTHON_EXCLUSIONS`
in `batocera-launch.mk`. Separate packages provide their own `pyproject.toml`,
`Config.in`, and `.mk`, and are `select`ed from the emulator’s Buildroot
config.

When to inline vs split is covered in [MIGRATION.md](MIGRATION.md).

## Development

From this directory (or via the workspace `uv` env):

```bash
pytest
ruff check . --fix && ruff format .
pyright
```

Python style matches the repo root: 3.14, `from __future__ import annotations`,
strict ruff/pyright.
