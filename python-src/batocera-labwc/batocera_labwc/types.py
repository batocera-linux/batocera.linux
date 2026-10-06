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
