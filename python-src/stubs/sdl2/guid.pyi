from ctypes import _Pointer, c_char

from .joystick import SDL_JoystickGUID

__all__ = ['SDL_GUID', 'SDL_GUIDFromString', 'SDL_GUIDToString']

SDL_GUID = SDL_JoystickGUID

def SDL_GUIDToString(guid: SDL_GUID, pszGUID: _Pointer[c_char] | bytes, cbGUID: int, /) -> None: ...
def SDL_GUIDFromString(pchGUID: bytes | None, /) -> SDL_GUID: ...
