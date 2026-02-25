from ctypes import Array, Structure, _CFuncPtr, _Pointer, c_char, c_int, c_void_p

from .stdinc import Sint16, Sint32, Uint8, Uint16

__all__ = [
    'SDL_HAT_CENTERED',
    'SDL_HAT_DOWN',
    'SDL_HAT_LEFT',
    'SDL_HAT_LEFTDOWN',
    'SDL_HAT_LEFTUP',
    'SDL_HAT_RIGHT',
    'SDL_HAT_RIGHTDOWN',
    'SDL_HAT_RIGHTUP',
    'SDL_HAT_UP',
    'SDL_IPHONE_MAX_GFORCE',
    'SDL_JOYSTICK_POWER_EMPTY',
    'SDL_JOYSTICK_POWER_FULL',
    'SDL_JOYSTICK_POWER_LOW',
    'SDL_JOYSTICK_POWER_MAX',
    'SDL_JOYSTICK_POWER_MEDIUM',
    'SDL_JOYSTICK_POWER_UNKNOWN',
    'SDL_JOYSTICK_POWER_WIRED',
    'SDL_JOYSTICK_TYPE_ARCADE_PAD',
    'SDL_JOYSTICK_TYPE_ARCADE_STICK',
    'SDL_JOYSTICK_TYPE_DANCE_PAD',
    'SDL_JOYSTICK_TYPE_DRUM_KIT',
    'SDL_JOYSTICK_TYPE_FLIGHT_STICK',
    'SDL_JOYSTICK_TYPE_GAMECONTROLLER',
    'SDL_JOYSTICK_TYPE_GUITAR',
    'SDL_JOYSTICK_TYPE_THROTTLE',
    'SDL_JOYSTICK_TYPE_UNKNOWN',
    'SDL_JOYSTICK_TYPE_WHEEL',
    'SDL_VIRTUAL_JOYSTICK_DESC_VERSION',
    'SDL_GetJoystickGUIDInfo',
    'SDL_Joystick',
    'SDL_JoystickAttachVirtual',
    'SDL_JoystickAttachVirtualEx',
    'SDL_JoystickClose',
    'SDL_JoystickCurrentPowerLevel',
    'SDL_JoystickDetachVirtual',
    'SDL_JoystickEventState',
    'SDL_JoystickFromInstanceID',
    'SDL_JoystickFromPlayerIndex',
    'SDL_JoystickGUID',
    'SDL_JoystickGetAttached',
    'SDL_JoystickGetAxis',
    'SDL_JoystickGetAxisInitialState',
    'SDL_JoystickGetBall',
    'SDL_JoystickGetButton',
    'SDL_JoystickGetDeviceGUID',
    'SDL_JoystickGetDeviceInstanceID',
    'SDL_JoystickGetDevicePlayerIndex',
    'SDL_JoystickGetDeviceProduct',
    'SDL_JoystickGetDeviceProductVersion',
    'SDL_JoystickGetDeviceType',
    'SDL_JoystickGetDeviceVendor',
    'SDL_JoystickGetFirmwareVersion',
    'SDL_JoystickGetGUID',
    'SDL_JoystickGetGUIDFromString',
    'SDL_JoystickGetGUIDString',
    'SDL_JoystickGetHat',
    'SDL_JoystickGetPlayerIndex',
    'SDL_JoystickGetProduct',
    'SDL_JoystickGetProductVersion',
    'SDL_JoystickGetSerial',
    'SDL_JoystickGetType',
    'SDL_JoystickGetVendor',
    'SDL_JoystickHasLED',
    'SDL_JoystickHasRumble',
    'SDL_JoystickHasRumbleTriggers',
    'SDL_JoystickID',
    'SDL_JoystickInstanceID',
    'SDL_JoystickIsVirtual',
    'SDL_JoystickName',
    'SDL_JoystickNameForIndex',
    'SDL_JoystickNumAxes',
    'SDL_JoystickNumBalls',
    'SDL_JoystickNumButtons',
    'SDL_JoystickNumHats',
    'SDL_JoystickOpen',
    'SDL_JoystickPath',
    'SDL_JoystickPathForIndex',
    'SDL_JoystickPowerLevel',
    'SDL_JoystickRumble',
    'SDL_JoystickRumbleTriggers',
    'SDL_JoystickSendEffect',
    'SDL_JoystickSetLED',
    'SDL_JoystickSetPlayerIndex',
    'SDL_JoystickSetVirtualAxis',
    'SDL_JoystickSetVirtualButton',
    'SDL_JoystickSetVirtualHat',
    'SDL_JoystickType',
    'SDL_JoystickUpdate',
    'SDL_LockJoysticks',
    'SDL_NumJoysticks',
    'SDL_UnlockJoysticks',
    'SDL_VirtualJoystickDesc',
]

SDL_JoystickPowerLevel = c_int
SDL_JOYSTICK_POWER_UNKNOWN: int
SDL_JOYSTICK_POWER_EMPTY: int
SDL_JOYSTICK_POWER_LOW: int
SDL_JOYSTICK_POWER_MEDIUM: int
SDL_JOYSTICK_POWER_FULL: int
SDL_JOYSTICK_POWER_WIRED: int
SDL_JOYSTICK_POWER_MAX: int
SDL_JoystickType = c_int
SDL_JOYSTICK_TYPE_UNKNOWN: int
SDL_JOYSTICK_TYPE_GAMECONTROLLER: int
SDL_JOYSTICK_TYPE_WHEEL: int
SDL_JOYSTICK_TYPE_ARCADE_STICK: int
SDL_JOYSTICK_TYPE_FLIGHT_STICK: int
SDL_JOYSTICK_TYPE_DANCE_PAD: int
SDL_JOYSTICK_TYPE_GUITAR: int
SDL_JOYSTICK_TYPE_DRUM_KIT: int
SDL_JOYSTICK_TYPE_ARCADE_PAD: int
SDL_JOYSTICK_TYPE_THROTTLE: int
SDL_IPHONE_MAX_GFORCE: float
SDL_HAT_CENTERED: int
SDL_HAT_UP: int
SDL_HAT_RIGHT: int
SDL_HAT_DOWN: int
SDL_HAT_LEFT: int
SDL_HAT_RIGHTUP: int
SDL_HAT_RIGHTDOWN: int
SDL_HAT_LEFTUP: int
SDL_HAT_LEFTDOWN: int
SDL_VIRTUAL_JOYSTICK_DESC_VERSION: int
SDL_JoystickID = Sint32

class SDL_JoystickGUID(Structure):
    data: Array[Uint8]

class SDL_Joystick(c_void_p): ...

class SDL_VirtualJoystickDesc(Structure):
    version: int
    type: int
    naxes: int
    nbuttons: int
    nhats: int
    vendor_id: int
    product_id: int
    padding: int
    button_mask: int
    axis_mask: int
    name: bytes | None
    userdata: int | None
    Update: _CFuncPtr
    SetPlayerIndex: _CFuncPtr
    Rumble: _CFuncPtr
    RumbleTriggers: _CFuncPtr
    SetLED: _CFuncPtr
    SendEffect: _CFuncPtr

def SDL_LockJoysticks() -> None: ...
def SDL_UnlockJoysticks() -> None: ...
def SDL_NumJoysticks() -> int: ...
def SDL_JoystickNameForIndex(device_index: int, /) -> bytes | None: ...
def SDL_JoystickPathForIndex(device_index: int, /) -> bytes | None: ...
def SDL_JoystickGetDevicePlayerIndex(device_index: int, /) -> int: ...
def SDL_JoystickGetDeviceGUID(device_index: int, /) -> SDL_JoystickGUID: ...
def SDL_JoystickGetDeviceVendor(device_index: int, /) -> int: ...
def SDL_JoystickGetDeviceProduct(device_index: int, /) -> int: ...
def SDL_JoystickGetDeviceProductVersion(device_index: int, /) -> int: ...
def SDL_JoystickGetDeviceType(device_index: int, /) -> int: ...
def SDL_JoystickGetDeviceInstanceID(device_index: int, /) -> int: ...
def SDL_JoystickOpen(device_index: int, /) -> _Pointer[SDL_Joystick]: ...
def SDL_JoystickFromInstanceID(instance_id: int, /) -> _Pointer[SDL_Joystick]: ...
def SDL_JoystickFromPlayerIndex(player_index: int, /) -> _Pointer[SDL_Joystick]: ...
def SDL_JoystickAttachVirtual(type: int, naxes: int, nbuttons: int, nhats: int, /) -> int: ...
def SDL_JoystickAttachVirtualEx(desc: _Pointer[SDL_VirtualJoystickDesc], /) -> int: ...
def SDL_JoystickDetachVirtual(device_index: int, /) -> int: ...
def SDL_JoystickIsVirtual(device_index: int, /) -> int: ...
def SDL_JoystickSetVirtualAxis(joystick: _Pointer[SDL_Joystick], axis: int, value: int, /) -> int: ...
def SDL_JoystickSetVirtualButton(joystick: _Pointer[SDL_Joystick], button: int, value: int, /) -> int: ...
def SDL_JoystickSetVirtualHat(joystick: _Pointer[SDL_Joystick], hat: int, value: int, /) -> int: ...
def SDL_JoystickName(joystick: _Pointer[SDL_Joystick], /) -> bytes | None: ...
def SDL_JoystickPath(joystick: _Pointer[SDL_Joystick], /) -> bytes | None: ...
def SDL_JoystickGetPlayerIndex(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickSetPlayerIndex(joystick: _Pointer[SDL_Joystick], player_index: int, /) -> None: ...
def SDL_JoystickGetGUID(joystick: _Pointer[SDL_Joystick], /) -> SDL_JoystickGUID: ...
def SDL_JoystickGetVendor(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickGetProduct(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickGetProductVersion(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickGetFirmwareVersion(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickGetSerial(joystick: _Pointer[SDL_Joystick], /) -> bytes | None: ...
def SDL_JoystickGetType(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickGetGUIDString(guid: SDL_JoystickGUID, pszGUID: Array[c_char], cbGUID: int, /) -> None: ...
def SDL_JoystickGetGUIDFromString(pchGUID: bytes | None, /) -> SDL_JoystickGUID: ...
def SDL_GetJoystickGUIDInfo(
    guid: SDL_JoystickGUID,
    vendor: _Pointer[Uint16],
    product: _Pointer[Uint16],
    version: _Pointer[Uint16],
    crc16: _Pointer[Uint16],
    /,
) -> None: ...
def SDL_JoystickGetAttached(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickInstanceID(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickNumAxes(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickNumBalls(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickNumHats(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickNumButtons(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickUpdate() -> None: ...
def SDL_JoystickEventState(state: int, /) -> int: ...
def SDL_JoystickGetAxis(joystick: _Pointer[SDL_Joystick], axis: int, /) -> int: ...
def SDL_JoystickGetAxisInitialState(joystick: _Pointer[SDL_Joystick], axis: int, state: _Pointer[Sint16], /) -> int: ...
def SDL_JoystickGetHat(joystick: _Pointer[SDL_Joystick], hat: int, /) -> int: ...
def SDL_JoystickGetBall(
    joystick: _Pointer[SDL_Joystick], ball: int, dx: _Pointer[c_int], dy: _Pointer[c_int], /
) -> int: ...
def SDL_JoystickGetButton(joystick: _Pointer[SDL_Joystick], button: int, /) -> int: ...
def SDL_JoystickRumble(
    joystick: _Pointer[SDL_Joystick],
    low_frequency_rumble: int,
    high_frequency_rumble: int,
    duration_ms: int,
    /,
) -> int: ...
def SDL_JoystickRumbleTriggers(
    joystick: _Pointer[SDL_Joystick],
    left_rumble: int,
    right_rumble: int,
    duration_ms: int,
    /,
) -> int: ...
def SDL_JoystickHasLED(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickHasRumble(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickHasRumbleTriggers(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_JoystickSetLED(joystick: _Pointer[SDL_Joystick], red: int, green: int, blue: int, /) -> int: ...
def SDL_JoystickSendEffect(joystick: _Pointer[SDL_Joystick], data: c_void_p | int | None, size: int, /) -> int: ...
def SDL_JoystickClose(joystick: _Pointer[SDL_Joystick], /) -> None: ...
def SDL_JoystickCurrentPowerLevel(joystick: _Pointer[SDL_Joystick], /) -> int: ...
