from ctypes import Structure, Union, _Pointer, c_int

from .pixels import SDL_Color
from .surface import SDL_Surface
from .video import SDL_Window

__all__ = [
    'SDL_INVALID_SHAPE_ARGUMENT',
    'SDL_NONSHAPEABLE_WINDOW',
    'SDL_SHAPEMODEALPHA',
    'SDL_WINDOW_LACKS_SHAPE',
    'SDL_CreateShapedWindow',
    'SDL_GetShapedWindowMode',
    'SDL_IsShapedWindow',
    'SDL_SetWindowShape',
    'SDL_WindowShapeMode',
    'SDL_WindowShapeParams',
    'ShapeModeBinarizeAlpha',
    'ShapeModeColorKey',
    'ShapeModeDefault',
    'ShapeModeReverseBinarizeAlpha',
    'WindowShapeMode',
]

SDL_NONSHAPEABLE_WINDOW: int
SDL_INVALID_SHAPE_ARGUMENT: int
SDL_WINDOW_LACKS_SHAPE: int
WindowShapeMode = c_int
ShapeModeDefault: int
ShapeModeBinarizeAlpha: int
ShapeModeReverseBinarizeAlpha: int
ShapeModeColorKey: int

def SDL_SHAPEMODEALPHA(mode: int) -> bool: ...

class SDL_WindowShapeParams(Union):
    binarizationCutoff: int
    colorKey: SDL_Color

class SDL_WindowShapeMode(Structure):
    mode: int
    parameters: SDL_WindowShapeParams

def SDL_CreateShapedWindow(
    title: bytes | None, x: int, y: int, w: int, h: int, flags: int, /
) -> _Pointer[SDL_Window]: ...
def SDL_IsShapedWindow(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_SetWindowShape(
    window: _Pointer[SDL_Window],
    shape: _Pointer[SDL_Surface],
    shape_mode: _Pointer[SDL_WindowShapeMode],
    /,
) -> int: ...
def SDL_GetShapedWindowMode(window: _Pointer[SDL_Window], shape_mode: _Pointer[SDL_WindowShapeMode], /) -> int: ...
