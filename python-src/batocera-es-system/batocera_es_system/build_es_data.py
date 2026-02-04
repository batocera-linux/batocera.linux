from __future__ import annotations

import argparse
from pathlib import Path

from batocera_es_system.es_features import build as _build_es_features
from batocera_es_system.es_systems import build as _build_es_systems
from batocera_es_system.registry import (
    Registry,
)
from batocera_es_system.roms import build as _build_roms_dir
from batocera_es_system.shared import ConfiggenDefaults
from batocera_es_system.translations import build as _build_translations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--es-systems-yml', type=Path, help='es_systems.yml definition file')
    parser.add_argument('--locales-dir', type=Path, required=True, help='Path to locales directory')
    parser.add_argument('--roms-dir', type=Path, required=True, help='Path to roms directory')
    parser.add_argument('--configgen', type=Path, required=True, help='Path to batocera-configgen staging directory')
    parser.add_argument('--keys-dir', type=Path, required=True, help='Path to batocera-es-system keys directory')
    parser.add_argument('--output', type=Path, required=True, help='Path to build directory')
    parser.add_argument('--arch', help='Target architecture', default=None)
    parser.add_argument(
        'info_path_file',
        type=Path,
        help='Path to file containing paths of YAML files to load into the registry',
    )

    args = parser.parse_args()

    registry = Registry.load_path_file(args.info_path_file)

    configgen_defaults = ConfiggenDefaults.for_directory(args.configgen)
    systems_data = _build_es_systems(
        registry.get_systems_metadata(configgen_defaults),
        args.es_systems_yml,
        args.output,
    )
    _build_es_features(registry, args.output)
    _build_translations(registry, args.keys_dir, args.locales_dir, args.output)
    _build_roms_dir(systems_data, args.roms_dir, args.output)
