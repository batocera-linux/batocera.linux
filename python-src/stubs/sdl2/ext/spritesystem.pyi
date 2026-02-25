from collections.abc import Callable, Iterable
from typing import Any

from sdl2.render import SDL_Renderer
from sdl2.surface import SDL_Surface
from sdl2.video import SDL_Window

from .ebs import System
from .renderer import Renderer
from .sprite import SoftwareSprite, Sprite, TextureSprite
from .window import Window

__all__ = [
    'SOFTWARE',
    'TEXTURE',
    'SoftwareSpriteRenderSystem',
    'SpriteFactory',
    'SpriteRenderSystem',
    'TextureSpriteRenderSystem',
]

TEXTURE: int
SOFTWARE: int

class SpriteFactory:
    default_args: dict[str, Any]
    def __init__(self, sprite_type: int = ..., **kwargs: Any) -> None: ...
    @property
    def sprite_type(self) -> int: ...
    def create_sprite_render_system(self, *args: Any, **kwargs: Any) -> SpriteRenderSystem: ...
    def from_image(self, img: Any) -> Sprite: ...
    def from_surface(self, tsurface: SDL_Surface, free: bool = False) -> Sprite: ...
    def from_object(self, obj: Any) -> Sprite: ...
    def from_color(
        self,
        color: Any,
        size: tuple[int, int],
        bpp: int = 32,
        masks: tuple[int, int, int, int] | None = None,
    ) -> Sprite: ...
    def from_text(self, text: str, **kwargs: Any) -> Sprite: ...
    def create_sprite(self, **kwargs: Any) -> Sprite: ...
    def create_software_sprite(
        self,
        size: tuple[int, int],
        bpp: int = 32,
        masks: tuple[int, int, int, int] | None = None,
    ) -> SoftwareSprite: ...
    def create_texture_sprite(
        self,
        renderer: Renderer | SDL_Renderer,
        size: tuple[int, int],
        pformat: int = ...,
        access: int = ...,
    ) -> TextureSprite: ...

class SpriteRenderSystem(System):
    componenttypes: tuple[type[object], ...]
    def __init__(self) -> None: ...
    def render(
        self,
        sprites: Sprite | Iterable[Sprite],
        x: int | None = None,
        y: int | None = None,
    ) -> None: ...
    def process(self, world: Any, components: Iterable[Sprite]) -> None: ...
    @property
    def sortfunc(self) -> Callable[[Sprite], Any]: ...
    @sortfunc.setter
    def sortfunc(self, value: Callable[[Sprite], Any]) -> None: ...

class SoftwareSpriteRenderSystem(SpriteRenderSystem):
    window: SDL_Window
    target: Window | SDL_Window
    surface: SDL_Surface
    componenttypes: tuple[type[object], ...]
    def __init__(self, window: Window | SDL_Window) -> None: ...
    def render(
        self,
        sprites: Sprite | Iterable[Sprite],
        x: int | None = None,
        y: int | None = None,
    ) -> None: ...

class TextureSpriteRenderSystem(SpriteRenderSystem):
    sdlrenderer: SDL_Renderer | None
    componenttypes: tuple[type[object], ...]
    def __init__(self, target: Window | SDL_Window | Renderer | SDL_Renderer) -> None: ...
    def __del__(self) -> None: ...
    def render(
        self,
        sprites: Sprite | Iterable[Sprite],
        x: int | None = None,
        y: int | None = None,
    ) -> None: ...
