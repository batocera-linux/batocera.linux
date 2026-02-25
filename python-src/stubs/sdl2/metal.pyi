from ctypes import _Pointer, c_int, c_void_p

from .video import SDL_Window

__all__ = [
    'SDL_MetalView',
    'SDL_Metal_CreateView',
    'SDL_Metal_DestroyView',
    'SDL_Metal_GetDrawableSize',
    'SDL_Metal_GetLayer',
]

class SDL_MetalView(c_void_p): ...

def SDL_Metal_CreateView(window: _Pointer[SDL_Window], /) -> SDL_MetalView: ...
def SDL_Metal_DestroyView(view: SDL_MetalView, /) -> None: ...
def SDL_Metal_GetLayer(view: SDL_MetalView, /) -> int | None: ...
def SDL_Metal_GetDrawableSize(
    window: _Pointer[SDL_Window],
    w: _Pointer[c_int],
    h: _Pointer[c_int],
    /,
) -> None: ...
