from ctypes import _Pointer, c_int, c_void_p

from .stdinc import Uint8
from .surface import SDL_Surface
from .video import SDL_Window

__all__ = [
    'SDL_BUTTON',
    'SDL_BUTTON_LEFT',
    'SDL_BUTTON_LMASK',
    'SDL_BUTTON_MIDDLE',
    'SDL_BUTTON_MMASK',
    'SDL_BUTTON_RIGHT',
    'SDL_BUTTON_RMASK',
    'SDL_BUTTON_X1',
    'SDL_BUTTON_X1MASK',
    'SDL_BUTTON_X2',
    'SDL_BUTTON_X2MASK',
    'SDL_MOUSEWHEEL_FLIPPED',
    'SDL_MOUSEWHEEL_NORMAL',
    'SDL_NUM_SYSTEM_CURSORS',
    'SDL_SYSTEM_CURSOR_ARROW',
    'SDL_SYSTEM_CURSOR_CROSSHAIR',
    'SDL_SYSTEM_CURSOR_HAND',
    'SDL_SYSTEM_CURSOR_IBEAM',
    'SDL_SYSTEM_CURSOR_NO',
    'SDL_SYSTEM_CURSOR_SIZEALL',
    'SDL_SYSTEM_CURSOR_SIZENESW',
    'SDL_SYSTEM_CURSOR_SIZENS',
    'SDL_SYSTEM_CURSOR_SIZENWSE',
    'SDL_SYSTEM_CURSOR_SIZEWE',
    'SDL_SYSTEM_CURSOR_WAIT',
    'SDL_SYSTEM_CURSOR_WAITARROW',
    'SDL_CaptureMouse',
    'SDL_CreateColorCursor',
    'SDL_CreateCursor',
    'SDL_CreateSystemCursor',
    'SDL_Cursor',
    'SDL_FreeCursor',
    'SDL_GetCursor',
    'SDL_GetDefaultCursor',
    'SDL_GetGlobalMouseState',
    'SDL_GetMouseFocus',
    'SDL_GetMouseState',
    'SDL_GetRelativeMouseMode',
    'SDL_GetRelativeMouseState',
    'SDL_MouseWheelDirection',
    'SDL_SetCursor',
    'SDL_SetRelativeMouseMode',
    'SDL_ShowCursor',
    'SDL_SystemCursor',
    'SDL_WarpMouseGlobal',
    'SDL_WarpMouseInWindow',
]

SDL_SystemCursor = c_int
SDL_SYSTEM_CURSOR_ARROW: int
SDL_SYSTEM_CURSOR_IBEAM: int
SDL_SYSTEM_CURSOR_WAIT: int
SDL_SYSTEM_CURSOR_CROSSHAIR: int
SDL_SYSTEM_CURSOR_WAITARROW: int
SDL_SYSTEM_CURSOR_SIZENWSE: int
SDL_SYSTEM_CURSOR_SIZENESW: int
SDL_SYSTEM_CURSOR_SIZEWE: int
SDL_SYSTEM_CURSOR_SIZENS: int
SDL_SYSTEM_CURSOR_SIZEALL: int
SDL_SYSTEM_CURSOR_NO: int
SDL_SYSTEM_CURSOR_HAND: int
SDL_NUM_SYSTEM_CURSORS: int
SDL_MouseWheelDirection = c_int
SDL_MOUSEWHEEL_NORMAL: int
SDL_MOUSEWHEEL_FLIPPED: int

def SDL_BUTTON(X: int, /) -> int: ...

SDL_BUTTON_LEFT: int
SDL_BUTTON_MIDDLE: int
SDL_BUTTON_RIGHT: int
SDL_BUTTON_X1: int
SDL_BUTTON_X2: int
SDL_BUTTON_LMASK: int
SDL_BUTTON_MMASK: int
SDL_BUTTON_RMASK: int
SDL_BUTTON_X1MASK: int
SDL_BUTTON_X2MASK: int

class SDL_Cursor(c_void_p): ...

def SDL_GetMouseFocus() -> _Pointer[SDL_Window]: ...
def SDL_GetMouseState(x: _Pointer[c_int], y: _Pointer[c_int], /) -> int: ...
def SDL_GetRelativeMouseState(x: _Pointer[c_int], y: _Pointer[c_int], /) -> int: ...
def SDL_WarpMouseInWindow(window: _Pointer[SDL_Window], x: int, y: int, /) -> None: ...
def SDL_SetRelativeMouseMode(enabled: int, /) -> int: ...
def SDL_GetRelativeMouseMode() -> int: ...
def SDL_CreateCursor(
    data: _Pointer[Uint8], mask: _Pointer[Uint8], w: int, h: int, hot_x: int, hot_y: int, /
) -> _Pointer[SDL_Cursor]: ...
def SDL_CreateColorCursor(surface: _Pointer[SDL_Surface], hot_x: int, hot_y: int, /) -> _Pointer[SDL_Cursor]: ...
def SDL_CreateSystemCursor(id: int, /) -> _Pointer[SDL_Cursor]: ...
def SDL_SetCursor(cursor: _Pointer[SDL_Cursor], /) -> None: ...
def SDL_GetCursor() -> _Pointer[SDL_Cursor]: ...
def SDL_GetDefaultCursor() -> _Pointer[SDL_Cursor]: ...
def SDL_FreeCursor(cursor: _Pointer[SDL_Cursor], /) -> None: ...
def SDL_ShowCursor(toggle: int, /) -> int: ...
def SDL_WarpMouseGlobal(x: int, y: int, /) -> int: ...
def SDL_CaptureMouse(enabled: int, /) -> int: ...
def SDL_GetGlobalMouseState(x: _Pointer[c_int], y: _Pointer[c_int], /) -> int: ...
