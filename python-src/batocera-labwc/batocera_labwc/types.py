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

from typing import Literal, NotRequired, TypedDict

type Output = Literal['primary', 'secondary', 'primary|secondary', 'secondary|primary']


class MoveToOutputAction(TypedDict):
    name: Literal['MoveToOutput']
    output: Output
    remove_if_missing: NotRequired[bool]


class FocusOutputAction(TypedDict):
    name: Literal['FocusOutput']
    output: Output
    remove_if_missing: NotRequired[bool]


class ToggleFullscreenAction(TypedDict):
    name: Literal['ToggleFullscreen']
    value: NotRequired[bool]


class SpanOutputsAction(TypedDict):
    name: Literal['SpanOutputs']


class LabWCRule(TypedDict):
    identifier: NotRequired[str]
    title: NotRequired[str]
    actions: list[MoveToOutputAction | FocusOutputAction | ToggleFullscreenAction | SpanOutputsAction]
