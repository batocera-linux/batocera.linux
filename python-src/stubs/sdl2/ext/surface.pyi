from collections.abc import Sequence

from sdl2.rect import SDL_Rect
from sdl2.surface import SDL_Surface

__all__ = ['subsurface']

def subsurface(surface: SDL_Surface, area: SDL_Rect | Sequence[int]) -> SDL_Surface: ...
