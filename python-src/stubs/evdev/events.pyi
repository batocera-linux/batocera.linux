from typing import Final, Protocol

class InputEvent:
    sec: int
    usec: int
    type: int
    code: int
    value: int
    def __init__(self, sec: int, usec: int, type: int, code: int, value: int) -> None: ...
    def timestamp(self) -> float: ...

class HasEvent(Protocol):
    event: InputEvent

class KeyEvent:
    key_up: Final[int]
    key_down: Final[int]
    key_hold: Final[int]
    scancode: int
    keystate: int
    keycode: str | tuple[str, ...]
    event: InputEvent
    def __init__(self, event: InputEvent, allow_unknown: bool = False) -> None: ...

class RelEvent:
    event: InputEvent
    def __init__(self, event: InputEvent) -> None: ...

class AbsEvent:
    event: InputEvent
    def __init__(self, event: InputEvent) -> None: ...

class SynEvent:
    event: InputEvent
    def __init__(self, event: InputEvent) -> None: ...

event_factory: dict[int, type[KeyEvent | RelEvent | AbsEvent | SynEvent]]
