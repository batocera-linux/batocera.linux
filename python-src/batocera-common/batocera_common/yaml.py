from __future__ import annotations

from typing import TYPE_CHECKING
from typing_extensions import TypeForm

if TYPE_CHECKING:
    from pathlib import Path


def safe_load_yaml12[T](file: Path, type: TypeForm[T], /) -> T | None:
    import ruamel.yaml

    yml = ruamel.yaml.YAML(typ='safe', pure=True)
    with file.open() as f:
        return yml.load(f)  # pyright: ignore


def safe_dump_yaml12(
    data: object,
    file: Path,
    /,
    *,
    flow_style: bool | None = False,
    sort_mapping: bool | None = False,
    mapping_indent: int | None = 2,
    sequence_indent: int | None = 4,
    sequence_dash_offset: int | None = 2,
    explicit_start: bool | None = None,
    explicit_end: bool | None = None,
) -> None:
    import ruamel.yaml

    yml = ruamel.yaml.YAML(typ='safe', pure=True)
    yml.indent(mapping=mapping_indent, sequence=sequence_indent, offset=sequence_dash_offset)

    if flow_style is not None:
        yml.default_flow_style = flow_style
    if sort_mapping is not None:
        yml.sort_base_mapping_type_on_output = sort_mapping  # pyright: ignore
    if explicit_start is not None:
        yml.explicit_start = explicit_start
    if explicit_end is not None:
        yml.explicit_end = explicit_end

    yml.dump(data, file)  # pyright: ignore


def safe_load_yaml[T](file: Path, type: TypeForm[T], /) -> T | None:
    import yaml as pyyaml

    return pyyaml.safe_load(file.read_text())
