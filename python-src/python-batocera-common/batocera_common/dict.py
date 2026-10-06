from __future__ import annotations

from collections.abc import Mapping
from typing import Any


# adapted from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def merge(destination: dict[str, Any], source: Mapping[str, Any]) -> None:
    """Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param destination: dict onto which the merge is executed
    :param source: dict merged into destination
    :return: None
    """
    for key, value in source.items():
        if key in destination and isinstance(destination[key], dict) and isinstance(value, Mapping):
            merge(destination[key], value)  # pyright: ignore[reportUnknownArgumentType]
        else:
            destination[key] = value
