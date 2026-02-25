import abc
from collections.abc import Sequence
from ctypes import _Pointer

from sdl2.rect import SDL_Point, SDL_Rect
from sdl2.render import SDL_Texture
from sdl2.surface import SDL_Surface

__all__ = ['SoftwareSprite', 'Sprite', 'TextureSprite']

class Sprite(metaclass=abc.ABCMeta):
    x: int
    y: int
    depth: int
    def __init__(self) -> None: ...
    @property
    def position(self) -> tuple[int, int]: ...
    @position.setter
    def position(self, value: tuple[int, int]) -> None: ...
    @property
    @abc.abstractmethod
    def size(self) -> tuple[int, int]: ...
    @property
    def area(self) -> tuple[int, int, int, int]: ...

class SoftwareSprite(Sprite):
    free: bool
    surface: SDL_Surface | None
    def __init__(self, imgsurface: SDL_Surface | _Pointer[SDL_Surface], free: bool) -> None: ...
    def __del__(self) -> None: ...
    @property
    def size(self) -> tuple[int, int]: ...
    def subsprite(self, area: SDL_Rect | Sequence[int]) -> SoftwareSprite: ...

class TextureSprite(Sprite):
    texture: SDL_Texture | None
    free: bool
    angle: float
    flip: int
    def __init__(self, texture: SDL_Texture, free: bool = True) -> None: ...
    def __del__(self) -> None: ...
    @property
    def center(self) -> SDL_Point | None: ...
    @center.setter
    def center(self, value: tuple[int, int] | None) -> None: ...
    @property
    def size(self) -> tuple[int, int]: ...
