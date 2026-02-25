from ctypes import _Pointer, c_int

__all__ = [
    'SDL_POWERSTATE_CHARGED',
    'SDL_POWERSTATE_CHARGING',
    'SDL_POWERSTATE_NO_BATTERY',
    'SDL_POWERSTATE_ON_BATTERY',
    'SDL_POWERSTATE_UNKNOWN',
    'SDL_GetPowerInfo',
    'SDL_PowerState',
]

SDL_PowerState = c_int
SDL_POWERSTATE_UNKNOWN: int
SDL_POWERSTATE_ON_BATTERY: int
SDL_POWERSTATE_NO_BATTERY: int
SDL_POWERSTATE_CHARGING: int
SDL_POWERSTATE_CHARGED: int

def SDL_GetPowerInfo(seconds: _Pointer[c_int], percent: _Pointer[c_int], /) -> int: ...
