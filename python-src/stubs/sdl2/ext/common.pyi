from collections.abc import Iterable

from sdl2.events import SDL_Event

from .window import Window

__all__ = ['TestEventProcessor', 'get_events', 'init', 'quit', 'quit_requested']

def init(
    video: bool = True,
    audio: bool = False,
    timer: bool = False,
    joystick: bool = False,
    controller: bool = False,
    haptic: bool = False,
    sensor: bool = False,
    events: bool = True,
) -> None: ...
def quit() -> None: ...
def get_events() -> list[SDL_Event]: ...
def quit_requested(events: SDL_Event | Iterable[SDL_Event]) -> bool: ...

class TestEventProcessor:
    def run(self, window: Window) -> None: ...
