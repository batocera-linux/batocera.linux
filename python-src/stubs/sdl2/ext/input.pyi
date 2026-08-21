from collections.abc import Iterable

from sdl2.events import SDL_Event

__all__ = [
    'get_clicks',
    'get_key_state',
    'get_text_input',
    'key_pressed',
    'mouse_clicked',
    'start_text_input',
    'stop_text_input',
    'text_input_enabled',
]

def key_pressed(
    events: SDL_Event | Iterable[SDL_Event],
    key: int | str | None = None,
    mod: int | str | Iterable[int | str] | None = None,
    released: bool = False,
) -> bool: ...
def get_key_state(key: int | str) -> int: ...
def mouse_clicked(
    events: SDL_Event | Iterable[SDL_Event],
    button: int | str | None = None,
    released: bool = False,
) -> bool: ...
def get_clicks(
    events: SDL_Event | Iterable[SDL_Event],
    button: int | str | None = None,
    released: bool = False,
) -> list[tuple[int, int]]: ...
def start_text_input() -> None: ...
def stop_text_input() -> None: ...
def text_input_enabled() -> bool: ...
def get_text_input(events: SDL_Event | Iterable[SDL_Event]) -> str: ...
