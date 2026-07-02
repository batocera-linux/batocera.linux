from ctypes import _Pointer

from .rwops import SDL_RWops
from .stdinc import Sint64

__all__ = [
    'SDL_GestureID',
    'SDL_LoadDollarTemplates',
    'SDL_RecordGesture',
    'SDL_SaveAllDollarTemplates',
    'SDL_SaveDollarTemplate',
]

SDL_GestureID = Sint64

def SDL_RecordGesture(touchId: int, /) -> int: ...
def SDL_SaveAllDollarTemplates(dst: _Pointer[SDL_RWops], /) -> int: ...
def SDL_SaveDollarTemplate(gestureId: int, dst: _Pointer[SDL_RWops], /) -> int: ...
def SDL_LoadDollarTemplates(touchId: int, src: _Pointer[SDL_RWops], /) -> int: ...
