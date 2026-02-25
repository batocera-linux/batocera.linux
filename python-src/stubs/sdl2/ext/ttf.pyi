from ctypes import _Pointer
from typing import Any

from sdl2.pixels import SDL_Color
from sdl2.rwops import SDL_RWops
from sdl2.sdlttf import TTF_Font
from sdl2.surface import SDL_Surface

from .color import Color

__all__ = ['FontManager', 'FontTTF']

class FontTTF:
    def __init__(
        self,
        font: str | SDL_RWops,
        size: int | str,
        color: Color | tuple[int, int, int] | tuple[int, int, int, int] | None,
        index: int = 0,
        height_chars: str | None = None,
    ) -> None: ...
    def get_ttf_font(self, style: str = 'default') -> TTF_Font: ...
    def add_style(
        self,
        name: str,
        size: int | str,
        color: Color | tuple[int, int, int] | tuple[int, int, int, int] | None,
        bg_color: Color | tuple[int, int, int] | tuple[int, int, int, int] | None = None,
    ) -> None: ...
    def render_text(
        self,
        text: str,
        style: str = 'default',
        line_h: int | str | None = None,
        width: int | None = None,
        align: str = 'left',
    ) -> SDL_Surface: ...
    def close(self) -> None: ...
    def contains(self, c: str) -> bool: ...
    @property
    def family_name(self) -> str | None: ...
    @property
    def style_name(self) -> str | None: ...
    @property
    def is_fixed_width(self) -> bool: ...

class FontManager:
    fonts: dict[str, dict[int, _Pointer[TTF_Font]]]
    aliases: dict[str, str]
    size: int
    def __init__(
        self,
        font_path: str,
        alias: str | None = None,
        size: int = 16,
        color: Color = ...,
        bg_color: Color = ...,
        index: int = 0,
    ) -> None: ...
    def __del__(self) -> None: ...
    def close(self) -> None: ...
    def add(
        self,
        font_path: str,
        alias: str | None = None,
        size: int | None = None,
        index: int = 0,
    ) -> _Pointer[TTF_Font] | None: ...
    @property
    def color(self) -> Color: ...
    @color.setter
    def color(self, value: Color | tuple[int, int, int] | tuple[int, int, int, int]) -> None: ...
    @property
    def bg_color(self) -> Color: ...
    @bg_color.setter
    def bg_color(self, value: Color | tuple[int, int, int] | tuple[int, int, int, int]) -> None: ...
    @property
    def default_font(self) -> str | None: ...
    @default_font.setter
    def default_font(self, value: str) -> None: ...
    def render(
        self,
        text: str,
        alias: str | None = None,
        size: int | None = None,
        width: int | None = None,
        color: Color | SDL_Color | None = None,
        bg_color: Color | SDL_Color | None = None,
        **kwargs: Any,
    ) -> SDL_Surface: ...
