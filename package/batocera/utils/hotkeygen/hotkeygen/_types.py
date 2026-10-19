# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

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
