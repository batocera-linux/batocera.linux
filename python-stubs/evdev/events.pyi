from typing import ClassVar

class InputEvent:
    sec: float
    usec: int
    type: int
    code: int
    value: object

    def timestamp(self) -> float: ...

class KeyEvent:
    key_up: ClassVar[int]
    key_down: ClassVar[int]
    key_hold: ClassVar[int]
    scancode: int
    keystate: int
    keycode: str
    event: InputEvent
    def __init__(self, event: InputEvent, allow_unknown: bool = ...) -> None: ...

class RelEvent:
    event: InputEvent
    def __init__(self, event: InputEvent) -> None: ...

class AbsEvent:
    event: InputEvent
    def __init__(self, event: InputEvent) -> None: ...

class SynEvent:
    event: InputEvent
    def __init__(self, event: InputEvent) -> None: ...
