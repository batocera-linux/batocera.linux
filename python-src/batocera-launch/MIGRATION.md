# Migrating configgen generators to batocera-launch

This guide is for porting remaining `configgen` generators
(`package/batocera/core/batocera-configgen/configgen/configgen/generators/`)
into `batocera-launch` emulator subclasses.

Package overview, entry-point loading, and in-tree vs separate-package layout
are in [README.md](README.md). Read that first if you are new to
`batocera-launch`.

## Goals of the migration

- Replace the procedural launch pipeline in `emulatorlauncher.py` with an
  async context-managed `Emulator` that owns preparation (ROM mount, controllers,
  guns, wheels, resolution, mouse, bezels, HUD, hotkeys, SDL).
- Discover emulator classes via the `batocera_launch.emulators` entry-point
  group instead of deriving a class name from the emulator id and maintaining
  a hard-coded list of exceptions (`importer.py`).
- Collapse `generate(...)` plus optional hook methods into properties and a
  single `configure()` method that returns a `Command`.
- Prefer instance helpers (`config_dir`, `saves_dir`, `roms_dir`, `self.rom`,
  `self.resolution`, `self.controllers`) over module-level path constants and
  long parameter lists.
- Keep comments that document *why* from the old generator.

## Choosing where to put the port

**Default: inline** into `batocera_launch/emulators/<name>.py` and register the
entry point in this package’s `pyproject.toml`.

Use a separate `python-src/batocera-launch-<name>/` package when the port has:

- Multiple Python modules (controllers, paths, helpers)
- Extra Python dependencies beyond `batocera-common` / `batocera-launch`
- Shared base classes used by more than one emulator entry point
  (e.g. fallout1/fallout2)
- A large, self-contained engine of its own (libretro, mame, rpcs3, dolphin,
  pcsx2, …)

Existing packages today include: `cdogs`, `cgenius`, `drastic`, `fallout`,
`flycast`, `kodi`, `openjazz`, `openjk`, `openjkdf2`, `openmohaa`, `rpcs3`.

Thin launchers (command + env/SDL, or a single-file INI/JSON writer comparable
to GSplus / NanoBoyAdvance / Sonic Retro) should be inlined even if they are
more than a few dozen lines.

## Hook mapping

| configgen `Generator` hook | batocera-launch `Emulator` replacement | Notes |
|---|---|---|
| `generate(system, rom, playersControllers, metadata, guns, wheels, gameResolution) -> Command` | `async def configure(self) -> Command` | Only abstract method besides hotkeys. Access state via `self.*` (see below). |
| `getHotkeysContext()` | `@cached_property def hotkeygen_context(self) -> HotkeysContext` | Required. Same dict shape: `{'name': ..., 'keys': {...}}`. |
| `getMouseMode(config, rom)` | `@property def needs_mouse(self) -> bool` | Default `False`. May depend on `self.config` / `self.rom`. |
| `executionDirectory(config, rom)` | `@property def execution_path(self) -> Path \| None` | Default `None`. Base class `chdir`s here before run. |
| `getResolutionMode(config)` | `@property def target_video_mode(self) -> str` | Default `self.config.video_mode` (from `videomode`). |
| `writesToRom(config)` | `@property def needs_overlayfs(self) -> bool` | When `True`, squashfs ROMs get a writable overlay under `SAVES / system / rom.stem`. |
| `supportsInternalBezels()` | `@property def handles_bezels(self) -> bool` | Skips mangohud/external bezel overlay. |
| `hasInternalMangoHUDCall()` | `@property def handles_hud(self) -> bool` | Skips prepending `mangohud` to the command. |
| `getInGameRatio(config, gameResolution, rom)` | `@cached_property def in_game_ratio(self) -> float` | Default `4/3`. Use `self.resolution` if needed. |
| Manual `SDL_GAMECONTROLLERCONFIG=generate_sdl_game_controller_config(...)` in `Command` env | `needs_sdl_game_controller_config = True` (class var) | Base class injects the env var after `configure()`. |
| Manual `write_sdl_controller_db(...)` | `needs_sdl_controller_db = True` (+ optional `sdl_controller_db_path` override) | Base class writes the DB before `configure()`. |
| LabWC / window-manager setup scattered in `generate` | `async def prepare_labwc(self) -> None` | Called when `LABWC_PID` is in the environment. Prefer `LabWCConfig`. |
| Special decoration IDs (MAME-style) | mixin `SpecialDecorationsMixin` | Overrides `decoration_id` from ROM stem metadata. |

### `generate()` argument → `self` attribute

| Old argument | New access |
|---|---|
| `system` (configgen `Emulator`) | `self` / `self.config` / `self.name` / `self.core` / `self.system` |
| `rom` | `self.rom` (`Rom`, subclass of `Path`) |
| `playersControllers` | `self.controllers` |
| `metadata` | `self.metadata` |
| `guns` | `self.guns` |
| `wheels` | `self.wheels` |
| `gameResolution["width"]` / `["height"]` | `self.resolution.width` / `.height` (`Resolution` dataclass) |

`system.config[...]` becomes `self.config.get` / `get_str` / `get_bool`. Prefer
typed helpers (`self.config.show_fps`, `self.config.use_guns`,
`self.config.video_mode`, `self.config.get_str('system.language')`) when they
exist.

## The `Rom` class vs `original_rom` / `rom`

In configgen's `emulatorlauncher.py`:

1. `original_rom = args.rom` — the path EmulationStation passed in.
2. If the suffix is `.squashfs`, the archive is mounted and `rom` becomes the
   mount point; otherwise `rom == original_rom`.
3. `generate(...)` receives the *mounted* `rom`.
4. Evmapy / system identity often still key off `original_rom` (stem, path).
5. When `writesToRom` is true and the ROM is squashfs, an overlayfs is mounted
   on `rom` with upperdir `SAVES / system / original_rom.stem`.

In batocera-launch, `Rom.prepare()` runs inside `Emulator.__aenter__` and
produces a single `Rom` instance assigned to `self.rom`:

| Concept | configgen | batocera-launch |
|---|---|---|
| Path ES passed in | `original_rom` | `self.rom.source` |
| Path used as the game file/dir (after squashfs mount, if any) | `rom` | `self.rom` itself (`Path` value) |
| Mounted squashfs path only | `rom` when squashfs | `self.rom.prepared` (`None` if not squashfs) |
| Stable game id (stem of source) | `original_rom.stem` | `self.rom.id` |
| Short id (alphanumeric stem, parens/brackets stripped) | ad-hoc helpers | `self.rom.short_id` |

`Rom` subclasses `pathlib.Path`, so existing path operations (`suffix`,
`parent`, `read_text()`, `is_dir()`, `/`, …) work on the *prepared* location.
Path-returning methods (`parent`, `with_suffix`, …) return plain `Path`, not
`Rom`.

**Rules of thumb when porting:**

- Use `self.rom` wherever the old code used `rom` (file contents, parent dir,
  “is this a directory game”, launch argv).
- Use `self.rom.id` (or `.source`) when the old code used `original_rom.stem`
  or needed an identity that must not change when a squashfs is mounted.
  Example: CatacombGL matches version keywords with `self.rom.id.lower()`.
- Evmapy already uses `self.rom.source` internally; emulator code rarely needs
  to touch that.
- Overlayfs is automatic via `needs_overlayfs`; do not reimplement
  `mount_overlayfs` / `writesToRom` logic in `configure()`.

## Common replacements

| configgen | batocera-launch |
|---|---|
| `from ...batoceraPaths import CONFIGS, SAVES, ROMS, mkdir_if_not_exists` | `from batocera_common.paths import CONFIGS, SAVES, ROMS` and `path.mkdir(parents=True, exist_ok=True)` — or use `self.config_dir` / `self.saves_dir` / `self.roms_dir` |
| `UnixSettings(path, separator=' ')` + `save(k, v)` + `write()` | `KeyValueConfig(path, separator=' ')` from `batocera_common.key_value_config`: assign with `config[k] = v`, then `config.write()` |
| `CaseSensitiveConfigParser` / raw ini | Same parsers live in `batocera_common.configparser` |
| `Command(array=[...], env={...})` | `Command([...], env={...})` — field is `args`, not `array`. Prefer `command.update_env(...)` when the base class also mutates env. |
| `generate_sdl_game_controller_config(playersControllers)` in env | Class var `needs_sdl_game_controller_config = True` |
| `subprocess` / `batocera-settings-get` for language | `self.config.get_str('system.language', 'en_US')` |
| `system.config.show_fps` | `self.config.show_fps` |
| `os.chdir(...)` inside generate | Override `execution_path` |
| Module-level `_CONFIG_DIR = CONFIGS / 'foo'` | Override `@cached_property def config_dir` (and `saves_dir` / `roms_dir`) when the path differs from defaults (`CONFIGS / self.name`, `SAVES / self.system`, `ROMS / self.system`) |
| Shared build-engine argv parsing (`utils/buildargs.py`) | `from batocera_launch import parse_build_engine_args` |
| Directory with data files next to the generator | Inline as a package directory under `emulators/` (see `xash3d_fwgs/`) and load via `importlib.resources`; rsync exclusions for directories need a trailing `/` |

Default directories on `Emulator`:

- `config_dir` → `CONFIGS / self.name` (emulator name)
- `saves_dir` → `SAVES / self.system`
- `roms_dir` → `ROMS / self.system`
- `bios_dir` → `BIOS / self.system`

Override these when the binary expects a mixed-case or otherwise non-default
path (GSplus → `CONFIGS / 'GSplus'`, Azahar → `CONFIGS / 'azahar-emu'`,
IOQuake3 → shared `CONFIGS / 'ioquake3'`, etc.). Prefer instance properties
over module-level path constants so cores that share a class can diverge cleanly.

## Porting checklist (inline)

1. Read the configgen generator (and any sibling `*Config.py` / controllers
   modules). Note hooks: mouse, chdir, overlayfs, bezels, HUD, ratio, SDL.
2. Look up the emulator key in
   `configgen/generators/importer.py` (`_GENERATOR_MAP` or the default
   `{emulator}` name). That string is the entry-point name.
3. Add `batocera_launch/emulators/<module>.py`:
   - `@cached_dataclass class <Name>(Emulator):`
   - `needs_sdl_game_controller_config` / other class vars as needed
   - `@cached_property hotkeygen_context`
   - hook property overrides
   - `async def configure(self) -> Command`
4. Register in `python-src/batocera-launch/pyproject.toml` under
   `[project.entry-points."batocera_launch.emulators"]`:
   ```toml
   myemu = 'batocera_launch.emulators.myemu:MyEmu'
   ```
5. Exclude the module from images that lack the binary in
   `python-src/batocera-launch/batocera-launch.mk`:
   ```make
   $(if $(BR2_PACKAGE_MYEMU),,myemu.py) \
   ```
   For a directory module, use a trailing slash: `xash3d_fwgs/`.
6. Port comments that explain non-obvious behavior.
7. Run `ruff check` / `ruff format` and `pyright` on the new module.
8. Remove the generator from the [todo list](#todo-remaining-generators) below.

Until the entry point is registered, launches for that emulator id still use
the `configgen` adapter (see
[README.md](README.md#how-emulator-classes-are-loaded)).

### Minimal skeleton

```python
from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext


@cached_dataclass
class MyEmu(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'myemu',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        # write configs using self.config / self.rom / self.resolution / self.controllers
        return Command(['myemu', self.rom])
```

## Porting checklist (separate package)

Use when the port fails the “inline” heuristic above.

1. Create `python-src/batocera-launch-<name>/` with:
   - `pyproject.toml` (depends on `batocera-common`, `batocera-launch`; entry
     point under `batocera_launch.emulators`)
   - `Config.in` (`BR2_PACKAGE_BATOCERA_LAUNCH_<NAME>`)
   - `batocera-launch-<name>.mk` (`local-python-package`, hatch setup)
   - Python package `batocera_launch_<name>/` exporting the emulator class
2. `source` the new `Config.in` from the root `Config.in` (near the other
   `batocera-launch-*` entries).
3. In the emulator/port Buildroot `Config.in`,
   `select BR2_PACKAGE_BATOCERA_LAUNCH_<NAME>`.
4. Same code-port rules as inline (hooks, `Rom`, `KeyValueConfig`, …).
5. Remove the generator from the [todo list](#todo-remaining-generators) below.

Example entry point:

```toml
[project.entry-points."batocera_launch.emulators"]
flycast = 'batocera_launch_flycast:Flycast'
```

## Idioms from existing ports

- **Do not** put SDL controller env in the returned `Command` when
  `needs_sdl_game_controller_config` is set; the base class adds it.
- Prefer `self.rom.read_text().strip()` over manual `open`/`read` for one-line
  ROM sidecar files (Flatpak, Steam, IOQuake3).
- `configure()` is `async` even when it does no awaits — keep the signature.
- Use `@cached_property` for values derived once per launch (`hotkeygen_context`,
  path overrides, `in_game_ratio` when expensive). Use `@property` for cheap
  flags (`needs_mouse`, `needs_overlayfs`, `execution_path`).
- When two entry points share one class (e.g. `sonic2013` / `soniccd` →
  `SonicRetro`, `ioquake3` / `vkquake3` → `IOQuake3`), register both keys and
  branch on `self.name` / `self.core` only when necessary; prefer shared
  `config_dir` overrides so both see the same files.
- Move logic that lived in shell wrappers (`batocera-ikemen`, etc.) into the
  emulator class when porting.
- Restore meaningful comments from the generator and any sibling config module
  onto the corresponding lines in the new file.

## Todo: remaining generators

Generators below still only exist under
`package/batocera/core/batocera-configgen/configgen/configgen/generators/`
and have no matching `batocera_launch.emulators` entry point. They load through
the `configgen` adapter (see
[README.md](README.md#how-emulator-classes-are-loaded)).

Check off and remove an item when its port is registered. Where the entry-point
name differs from the generator directory, it is noted in parentheses
(from `importer.py`).

Large multi-module generators (dolphin, pcsx2, libretro, mame, linuxloader, …)
should become packages; smaller single-module ones should be inlined unless
they pull unusual dependencies.

- [ ] `bigpemu`
- [ ] `citron`
- [ ] `demul`
- [ ] `dolphin`
- [ ] `duckstation`
- [ ] `duckstation_legacy` (emulator `duckstation`, core `duckstation-legacy`)
- [ ] `fsuae`
- [ ] `gzdoom`
- [ ] `hypseus_singe` (`hypseus-singe`)
- [ ] `libretro`
- [ ] `linuxloader`
- [ ] `mame`
- [ ] `melonds`
- [ ] `model2emu`
- [ ] `moonlight`
- [ ] `mugen`
- [ ] `mupen` (`mupen64plus`)
- [ ] `openbor`
- [ ] `openmsx`
- [ ] `pcsx2`
- [ ] `pcsx2x6`
- [ ] `play`
- [ ] `ppsspp`
- [ ] `shadps4`
- [ ] `supermodel`
- [ ] `vice`
- [ ] `vita3k`
- [ ] `vpinball`
- [ ] `wine`
- [ ] `xemu`
- [ ] `xenia` (`xenia-canary`)
- [ ] `xenia_edge` (`xenia-edge`)
- [ ] `ymir`

## Reference files

| Role | Path |
|---|---|
| New base class | `batocera_launch/emulator.py` |
| ROM helper | `batocera_launch/rom.py` |
| Command | `batocera_launch/command.py` |
| Legacy adapter | `configgen/launch.py` (`GeneratorEmulator`) |
| Old hooks | `configgen/generators/Generator.py` |
| Old importer keys | `configgen/generators/importer.py` |
| Build exclusions | `batocera-launch.mk` (`BATOCERA_LAUNCH_LOCAL_PYTHON_EXCLUSIONS`) |
| Example thin port | `emulators/abuse.py`, `emulators/corsixth.py` |
| Example path overrides + KeyValueConfig | `emulators/gsplus.py` |
| Example overlayfs | `emulators/dosbox_staging.py` |
| Example LabWC | `emulators/azahar.py` |
| Example package | `python-src/batocera-launch-flycast/` |
