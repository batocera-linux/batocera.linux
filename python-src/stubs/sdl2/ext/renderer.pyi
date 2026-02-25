from collections.abc import Sequence
from typing import Any

from sdl2.rect import SDL_FPoint, SDL_FRect, SDL_Point, SDL_Rect
from sdl2.render import SDL_Renderer, SDL_Texture
from sdl2.surface import SDL_Surface

from .color import Color
from .compat import deprecated
from .sprite import SoftwareSprite, TextureSprite
from .window import Window

__all__ = ['Renderer', 'Texture', 'set_texture_scale_quality']

type _PointLike = SDL_Point | SDL_FPoint | tuple[float, float] | Sequence[float]
type _RectLike = SDL_Rect | SDL_FRect | tuple[float, float, float, float] | Sequence[float]
type _ColorLike = Color | tuple[int, int, int] | tuple[int, int, int, int] | int

def set_texture_scale_quality(method: str) -> None: ...

class Texture:
    def __init__(
        self,
        renderer: Renderer | Any,
        surface: SDL_Surface | SoftwareSprite | Any,
    ) -> None: ...
    def __del__(self) -> None: ...
    @property
    def tx(self) -> SDL_Texture: ...
    @property
    def size(self) -> tuple[int, int]: ...
    def destroy(self) -> None: ...
    @property
    def scale_mode(self) -> str: ...
    def set_scale_mode(self, mode: str) -> None: ...

class Renderer:
    rendertarget: Any
    def __init__(
        self,
        target: Window | Any,
        backend: int | str = -1,
        logical_size: tuple[int, int] | None = None,
        flags: int = ...,
    ) -> None: ...
    def __del__(self) -> None: ...
    @property
    def sdlrenderer(self) -> SDL_Renderer: ...
    @property
    @deprecated
    def renderer(self) -> SDL_Renderer: ...
    @property
    def logical_size(self) -> tuple[int, int]: ...
    @logical_size.setter
    def logical_size(self, size: tuple[int, int]) -> None: ...
    @property
    def color(self) -> Color: ...
    @color.setter
    def color(self, value: _ColorLike) -> None: ...
    @property
    def blendmode(self) -> int: ...
    @blendmode.setter
    def blendmode(self, value: int) -> None: ...
    @property
    def scale(self) -> tuple[float, float]: ...
    @scale.setter
    def scale(self, value: tuple[float, float]) -> None: ...
    def destroy(self) -> None: ...
    def reset_logical_size(self) -> None: ...
    def clear(self, color: _ColorLike | None = None) -> None: ...
    def copy(
        self,
        src: Texture | TextureSprite | SDL_Texture,
        srcrect: _RectLike | None = None,
        dstrect: _RectLike | _PointLike | None = None,
        angle: float = 0,
        center: _PointLike | None = None,
        flip: int = ...,
    ) -> None: ...
    def blit(
        self,
        src: Texture | TextureSprite | SDL_Texture,
        srcrect: _RectLike | None = None,
        dstrect: _RectLike | _PointLike | None = None,
        angle: float = 0,
        center: _PointLike | None = None,
        flip: int = ...,
    ) -> None: ...
    def rcopy(
        self,
        src: Texture | TextureSprite | SDL_Texture,
        loc: _PointLike,
        size: tuple[int, int] | None = None,
        align: tuple[float, float] = (0.0, 0.0),
        srcrect: _RectLike | None = None,
    ) -> None: ...
    def present(self) -> None: ...
    def draw_line(
        self,
        points: Sequence[_PointLike] | Sequence[float],
        color: _ColorLike | None = None,
    ) -> None: ...
    def draw_point(
        self,
        points: Sequence[_PointLike] | Sequence[float],
        color: _ColorLike | None = None,
    ) -> None: ...
    def draw_rect(
        self,
        rects: _RectLike | Sequence[_RectLike],
        color: _ColorLike | None = None,
    ) -> None: ...
    def fill(
        self,
        rects: _RectLike | Sequence[_RectLike],
        color: _ColorLike | None = None,
    ) -> None: ...
