from __future__ import annotations

from typing import TYPE_CHECKING, ReadOnly, TypedDict

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


type KeysDict = dict[str, list[int] | int | str]


class HotkeysContext(TypedDict):
    name: str
    keys: KeysDict


type KeysMapping = Mapping[str, Sequence[str]]  # Sequence[str] covers both str and list[str]


class HotkeysContextMapping(TypedDict):
    name: ReadOnly[str]
    keys: ReadOnly[KeysMapping]


class PersistedHotkeysContext(TypedDict):
    context: HotkeysContextMapping
    include_common: bool
