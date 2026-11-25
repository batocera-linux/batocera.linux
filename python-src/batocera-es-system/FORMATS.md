# batocera-es-system input formats

Build entry point: `batocera_es_system.build_es_data`. It loads a registry of
emulator/core YAML files, then writes:

- `es_systems.cfg` — from `es_systems.yml` plus registry metadata
- `es_features.cfg` — from registry features
- `es_savestates.cfg` and `savestates.json` — from registry `savestates`
- `roms/<system>/_info.txt` — comments from `es_systems.yml`, extension lists
  from registry metadata
- translation sources — from feature prompts/choices and key descriptions

## `es_systems.yml`

Path (in-tree):
`package/batocera/emulationstation/batocera-es-system/es_systems.yml`

Top-level map of system id → system metadata. This is the EmulationStation
system catalog (name, manufacturer, release, hardware, path, platform, theme,
group, comments). It does **not** list which emulators/cores belong to a
system; that comes from `*.emulator.yml` / `*.core.yml`.

Common keys:

| Key | Role |
| --- | --- |
| `name` | Display name |
| `manufacturer` / `release` / `hardware` | Catalog fields |
| `path` | ROM folder under `/userdata/roms` (defaults to the system id) |
| `platform` | ES platform string (defaults to the system id) |
| `theme` / `group` | Theme and grouping |
| `force` | Include the system even with no registered emulator/core |
| `file_extensions` | Fallback when a forced system has no registry metadata |
| `comment_en` / `comment_fr` / … | Appended into `_info.txt` |

A system is emitted into `es_systems.cfg` only if it has at least one
emulator/core from the registry, or `force: true`.

System `<extension>` is the **union** of every core’s resolved
`file_extensions` for that system. Per-core
`incompatible_extensions` is that union minus the core’s own set.

## Emulator and core YAML

Discovered from a path list written at build time (`info_files.txt`). Files are
YAML 1.2 and classified by filename:

| Pattern | Kind |
| --- | --- |
| `<name>.emulator.yml` | Base emulator definition |
| `<prefix>.<name>.emulator.yml` | Overlay merged onto that emulator |
| `<name>.<emulator>.core.yml` | Base core definition |
| `<prefix>.<name>.<emulator>.core.yml` | Overlay merged onto that core |

Special emulator names:

- `_shared` → `sharedFeatures` in `es_features.cfg` (shared feature catalog)
- `_global` → `globalFeatures` in `es_features.cfg`
- `_emulators` → overlays only (`<prefix>._emulators.emulator.yml`): their
  `shared_features` are added to every emulator except those in `exclude`, after
  its POWER OPTIONS features (or first when it has none), and to `_global`

Overlays (extra path segments before the base name) are applied with
`extend()` after the base file loads: lists append, `custom_features` merge
(with optional `before:` insertion), `keys` replace, `systems` merge by name,
and `file_extensions` replace (see below).

Examples in-tree:

- `package/batocera/emulationstation/batocera-es-system/_shared.emulator.yml`
- `package/batocera/emulationstation/batocera-es-system/hud._shared.emulator.yml`
- `package/batocera/emulators/mame/mame.emulator.yml`
- `package/batocera/emulators/mame/sega-arcade.mame.emulator.yml`
- `package/batocera/emulators/retroarch/libretro/libretro-mame/mame.libretro.core.yml`

### Shared keys (emulator, core, and system entries)

| Key | Role |
| --- | --- |
| `features` | Built-in ES feature flags (comma-joined in XML) |
| `shared_features` | References into `_shared` custom features |
| `custom_features` | Advanced options (`prompt`, `choices` or `preset`, …) |
| `keys` | Hotkey actions for translations / key config |
| `file_extensions` | ROM extensions this level supports |
| `systems` | Systems this emulator/core provides |

A system entry may be a bare name string, or a map with `name` plus any of the
shared keys. Emulator system entries may also set `as_emulator` / `as_core`
and `disabled`.

`es_features.yml` is **not** read by the builder. Features come only from these
emulator/core files (and their overlays).

### `file_extensions` resolution

Resolved **emulator → core → system**:

1. Bare list — replace the parent list
2. Omitted — inherit the parent list
3. Map with `values` / `add` / `remove`:
   - start from `values` if present, else the parent list
   - `values` may itself be a nested map (YAML anchors are common)
   - apply `remove`, then `add` (deduped, stable order)
   - remove-then-re-add works

When an overlay supplies a map with only `add`/`remove` (no `values`), the
previous level’s extensions become the implied `values`.

Standalone emulators (no cores) resolve system extensions against the
emulator. Cores resolve system → core → emulator.

### `savestates` (emulator files only)

One map per emulator; an overlay replaces it whole. It is written to
`es_savestates.cfg` for ES and to `savestates.json`, which batocera-launch's
save state manager reads at `/usr/share/batocera/launch/savestates.json`.

ES keys, emitted in this order when present: `directory`, `file`, `image`,
`nofileextension`, `firstslot`, `autosave`, `autosave_file`, `autosave_image`,
`incremental` (see ES's `es_savestates.cfg`).

Launcher keys:

| Key | Role |
| --- | --- |
| `slots` | `[first, last]` numbered slots the emulator has |
| `keys` | `quick_save` / `quick_load` (its quick slot, listed as the autosave), `save_slot` / `load_slot` per slot, `save` / `restore` for its current slot or its own choice, or MAME's `save_menu` / `load_menu` / `slot`; `{slot}` is substituted |
| `boot` | starting from a state: `args` (`{file}` substituted), `copy` into the current slot, `send: load\|restore` after `delay` s |
| `mirror` | serial-named states: `native_dir`, `glob`, `pattern` (groups `serial`, `slot`), `slot_name`, `auto_name` or `auto_slot`, `placement`, `fresh`, `screenshot` |
| `archive` | rom extensions; inside a zip or 7z the emulator names states after that rom, which the manager mirrors |
| `migrate` | `from`/`to` names in the ES directory, moved at launch when the target is free |

The pad's `save_state` / `restore_state` use the quick slot when there is one; otherwise, like
`batocera-savestate save`, a save always makes a new numbered state and a load takes the newest.

## Outputs worth knowing

| Output | Source |
| --- | --- |
| `es_systems.cfg` | `es_systems.yml` + registry system/core metadata |
| `es_features.cfg` | Registry `features` / `shared_features` / `custom_features` |
| `es_savestates.cfg`, `savestates.json` | Registry `savestates` |
| `roms/<system>/_info.txt` | Comments from `es_systems.yml`; per-core extension lists from metadata |

Defaults for which emulator/core is marked `default="true"` come from
batocera-launch’s staged defaults directory passed to the build.
