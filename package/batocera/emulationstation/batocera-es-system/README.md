## Directory navigation

 - `roms` Batocera's pre-bundled ROMs, and other necessary files for the ROMs directory.
 - `batocera-es-system.py` The Python script which generates `es_features.cfg` and `es_systems.cfg` based on the `es_features.yml` and `es_systems.yml` YML files.
 - `es_systems.yml` The systems that ES recognizes and shows on the system list when the user has installed the appropriate ROMs. Contains some metadata about the system, such as full name and manufacture date. This is the file you'd want to edit if you want to put a comment in the generated roms/<system>/_info.txt file.
 - `es_features.yml` The configuration file EmulationStation uses to show which options are available for each system (in “features”). Also includes the advanced per-system settings (in “cfeatures” as their own unique entries). Used in conjunction with the [config generators](https://github.com/batocera-linux/batocera.linux/tree/master/package/batocera/core/batocera-configgen/configgen/configgen/generators) to define new options. The user may override this with a custom file.
