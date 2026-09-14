## Directory navigation

 - `roms` Batocera's pre-bundled ROMs, and other necessary files for the ROMs directory.
 - `es_systems.yml` The systems that ES recognizes and shows on the system list when the user has installed the appropriate ROMs. Contains catalog metadata (full name, manufacturer, comments for generated `roms/<system>/_info.txt`, and so on). Emulator/core membership and ROM extensions come from `*.emulator.yml` / `*.core.yml` files under `package/batocera/`.
 - `_shared.emulator.yml` / `_global.emulator.yml` Shared and global EmulationStation feature definitions (with overlays such as `hud._shared.emulator.yml`).

Input formats and how the builder parses them are documented in
[`python-src/batocera-es-system/FORMATS.md`](../../../../python-src/batocera-es-system/FORMATS.md).
