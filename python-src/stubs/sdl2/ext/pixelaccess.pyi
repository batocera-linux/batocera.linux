from ctypes import _Pointer
from typing import Any, Self

from sdl2.surface import SDL_Surface

from .array import MemoryView
from .sprite import SoftwareSprite

__all__ = ['PixelView', 'SurfaceArray', 'pixels2d', 'pixels3d', 'surface_to_ndarray']

class PixelView(MemoryView):
    def __init__(self, source: SDL_Surface | SoftwareSprite | _Pointer[SDL_Surface]) -> None: ...

def pixels2d(source: SDL_Surface | SoftwareSprite, transpose: bool = True) -> Any: ...
def pixels3d(source: SDL_Surface | SoftwareSprite, transpose: bool = True) -> Any: ...
def surface_to_ndarray(source: SDL_Surface | SoftwareSprite, ndim: int = 3) -> Any: ...

class SurfaceArray:
    def __new__(
        cls,
        shape: Any,
        dtype: Any = ...,
        buffer_: Any = None,
        offset: int = 0,
        strides: Any = None,
        order: Any = None,
        source: Any = None,
        surface: Any = None,
    ) -> Self: ...
    def __array_finalize__(self, sfarray: Any) -> None: ...
