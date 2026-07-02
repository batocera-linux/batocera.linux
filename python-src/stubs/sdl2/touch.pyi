from ctypes import Structure, _Pointer, c_int

from .stdinc import Sint64

__all__ = [
    'SDL_MOUSE_TOUCHID',
    'SDL_TOUCH_DEVICE_DIRECT',
    'SDL_TOUCH_DEVICE_INDIRECT_ABSOLUTE',
    'SDL_TOUCH_DEVICE_INDIRECT_RELATIVE',
    'SDL_TOUCH_DEVICE_INVALID',
    'SDL_TOUCH_MOUSEID',
    'SDL_Finger',
    'SDL_FingerID',
    'SDL_GetNumTouchDevices',
    'SDL_GetNumTouchFingers',
    'SDL_GetTouchDevice',
    'SDL_GetTouchDeviceType',
    'SDL_GetTouchFinger',
    'SDL_GetTouchName',
    'SDL_TouchDeviceType',
    'SDL_TouchID',
]

SDL_TouchDeviceType = c_int
SDL_TOUCH_DEVICE_INVALID: tuple[int]
SDL_TOUCH_DEVICE_DIRECT: int
SDL_TOUCH_DEVICE_INDIRECT_ABSOLUTE: int
SDL_TOUCH_DEVICE_INDIRECT_RELATIVE: int
SDL_TOUCH_MOUSEID: int
SDL_MOUSE_TOUCHID: int
SDL_TouchID = Sint64
SDL_FingerID = Sint64

class SDL_Finger(Structure):
    id: int
    x: float
    y: float
    pressure: float

def SDL_GetNumTouchDevices() -> int: ...
def SDL_GetTouchDevice(index: int, /) -> int: ...
def SDL_GetTouchName(index: int, /) -> bytes | None: ...
def SDL_GetTouchDeviceType(touchID: int, /) -> int: ...
def SDL_GetNumTouchFingers(touchID: int, /) -> int: ...
def SDL_GetTouchFinger(touchID: int, index: int, /) -> _Pointer[SDL_Finger]: ...
