from ctypes import _Pointer

from sdl2.rect import SDL_Rect
from sdl2.surface import SDL_Surface

from .sprite import SoftwareSprite

__all__ = ['BitmapFont']

class BitmapFont:
    DEFAULTMAP: list[str]
    surface: SDL_Surface
    mapping: list[str]
    size: tuple[int, int]
    offsets: dict[str, SDL_Rect]
    def __init__(
        self,
        font_img: str | SoftwareSprite | SDL_Surface | _Pointer[SDL_Surface],
        size: tuple[int, int] | None = None,
        mapping: list[str] | None = None,
    ) -> None: ...
    def remap(self, c: str, x: int, y: int, w: int, h: int) -> None: ...
    def render(self, text: str, bpp: int | None = None) -> SoftwareSprite: ...
    def render_text(self, text: str, line_h: int | None = None, as_argb: bool = True) -> SDL_Surface: ...
    def render_on(
        self,
        target: SDL_Surface | SoftwareSprite | _Pointer[SDL_Surface],
        text: str,
        offset: tuple[int, int] = (0, 0),
        line_h: int | None = None,
    ) -> tuple[int, int, int, int]: ...
    def contains(self, c: str) -> bool: ...
    def can_render(self, text: str) -> bool: ...
