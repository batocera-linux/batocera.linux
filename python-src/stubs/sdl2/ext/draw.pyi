from collections.abc import Sequence
from ctypes import _Pointer
from typing import Any

from sdl2.pixels import SDL_PixelFormat
from sdl2.rect import SDL_Rect
from sdl2.surface import SDL_Surface

from .sprite import SoftwareSprite

__all__ = ['fill', 'line', 'prepare_color']

type _Target = SDL_Surface | SoftwareSprite | _Pointer[SDL_Surface]
type _Area = SDL_Rect | tuple[int, int, int, int]

def prepare_color(
    color: Any,
    target: SDL_PixelFormat | _Target,
) -> int: ...
def fill(
    target: _Target,
    color: Any,
    area: _Area | Sequence[_Area] | None = None,
) -> None: ...
def line(
    target: _Target,
    color: Any,
    dline: Sequence[int] | Sequence[Sequence[int]],
    width: int = 1,
) -> None: ...
