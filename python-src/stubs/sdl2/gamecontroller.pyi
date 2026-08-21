from ctypes import Structure, Union, _Pointer, c_float, c_int, c_void_p

from .joystick import SDL_Joystick, SDL_JoystickGUID
from .rwops import SDL_RWops
from .stdinc import Uint8, Uint64

__all__ = [
    'SDL_CONTROLLER_AXIS_INVALID',
    'SDL_CONTROLLER_AXIS_LEFTX',
    'SDL_CONTROLLER_AXIS_LEFTY',
    'SDL_CONTROLLER_AXIS_MAX',
    'SDL_CONTROLLER_AXIS_RIGHTX',
    'SDL_CONTROLLER_AXIS_RIGHTY',
    'SDL_CONTROLLER_AXIS_TRIGGERLEFT',
    'SDL_CONTROLLER_AXIS_TRIGGERRIGHT',
    'SDL_CONTROLLER_BINDTYPE_AXIS',
    'SDL_CONTROLLER_BINDTYPE_BUTTON',
    'SDL_CONTROLLER_BINDTYPE_HAT',
    'SDL_CONTROLLER_BINDTYPE_NONE',
    'SDL_CONTROLLER_BUTTON_A',
    'SDL_CONTROLLER_BUTTON_B',
    'SDL_CONTROLLER_BUTTON_BACK',
    'SDL_CONTROLLER_BUTTON_DPAD_DOWN',
    'SDL_CONTROLLER_BUTTON_DPAD_LEFT',
    'SDL_CONTROLLER_BUTTON_DPAD_RIGHT',
    'SDL_CONTROLLER_BUTTON_DPAD_UP',
    'SDL_CONTROLLER_BUTTON_GUIDE',
    'SDL_CONTROLLER_BUTTON_INVALID',
    'SDL_CONTROLLER_BUTTON_LEFTSHOULDER',
    'SDL_CONTROLLER_BUTTON_LEFTSTICK',
    'SDL_CONTROLLER_BUTTON_MAX',
    'SDL_CONTROLLER_BUTTON_MISC1',
    'SDL_CONTROLLER_BUTTON_PADDLE1',
    'SDL_CONTROLLER_BUTTON_PADDLE2',
    'SDL_CONTROLLER_BUTTON_PADDLE3',
    'SDL_CONTROLLER_BUTTON_PADDLE4',
    'SDL_CONTROLLER_BUTTON_RIGHTSHOULDER',
    'SDL_CONTROLLER_BUTTON_RIGHTSTICK',
    'SDL_CONTROLLER_BUTTON_START',
    'SDL_CONTROLLER_BUTTON_TOUCHPAD',
    'SDL_CONTROLLER_BUTTON_X',
    'SDL_CONTROLLER_BUTTON_Y',
    'SDL_CONTROLLER_TYPE_AMAZON_LUNA',
    'SDL_CONTROLLER_TYPE_GOOGLE_STADIA',
    'SDL_CONTROLLER_TYPE_MAX',
    'SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_LEFT',
    'SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_PAIR',
    'SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT',
    'SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_PRO',
    'SDL_CONTROLLER_TYPE_NVIDIA_SHIELD',
    'SDL_CONTROLLER_TYPE_PS3',
    'SDL_CONTROLLER_TYPE_PS4',
    'SDL_CONTROLLER_TYPE_PS5',
    'SDL_CONTROLLER_TYPE_UNKNOWN',
    'SDL_CONTROLLER_TYPE_VIRTUAL',
    'SDL_CONTROLLER_TYPE_XBOX360',
    'SDL_CONTROLLER_TYPE_XBOXONE',
    'SDL_GameController',
    'SDL_GameControllerAddMapping',
    'SDL_GameControllerAddMappingsFromFile',
    'SDL_GameControllerAddMappingsFromRW',
    'SDL_GameControllerAxis',
    'SDL_GameControllerBindType',
    'SDL_GameControllerButton',
    'SDL_GameControllerButtonBind',
    'SDL_GameControllerClose',
    'SDL_GameControllerEventState',
    'SDL_GameControllerFromInstanceID',
    'SDL_GameControllerFromPlayerIndex',
    'SDL_GameControllerGetAppleSFSymbolsNameForAxis',
    'SDL_GameControllerGetAppleSFSymbolsNameForButton',
    'SDL_GameControllerGetAttached',
    'SDL_GameControllerGetAxis',
    'SDL_GameControllerGetAxisFromString',
    'SDL_GameControllerGetBindForAxis',
    'SDL_GameControllerGetBindForButton',
    'SDL_GameControllerGetButton',
    'SDL_GameControllerGetButtonFromString',
    'SDL_GameControllerGetFirmwareVersion',
    'SDL_GameControllerGetJoystick',
    'SDL_GameControllerGetNumTouchpadFingers',
    'SDL_GameControllerGetNumTouchpads',
    'SDL_GameControllerGetPlayerIndex',
    'SDL_GameControllerGetProduct',
    'SDL_GameControllerGetProductVersion',
    'SDL_GameControllerGetSensorData',
    'SDL_GameControllerGetSensorDataRate',
    'SDL_GameControllerGetSensorDataWithTimestamp',
    'SDL_GameControllerGetSerial',
    'SDL_GameControllerGetSteamHandle',
    'SDL_GameControllerGetStringForAxis',
    'SDL_GameControllerGetStringForButton',
    'SDL_GameControllerGetTouchpadFinger',
    'SDL_GameControllerGetType',
    'SDL_GameControllerGetVendor',
    'SDL_GameControllerHasAxis',
    'SDL_GameControllerHasButton',
    'SDL_GameControllerHasLED',
    'SDL_GameControllerHasRumble',
    'SDL_GameControllerHasRumbleTriggers',
    'SDL_GameControllerHasSensor',
    'SDL_GameControllerIsSensorEnabled',
    'SDL_GameControllerMapping',
    'SDL_GameControllerMappingForDeviceIndex',
    'SDL_GameControllerMappingForGUID',
    'SDL_GameControllerMappingForIndex',
    'SDL_GameControllerName',
    'SDL_GameControllerNameForIndex',
    'SDL_GameControllerNumMappings',
    'SDL_GameControllerOpen',
    'SDL_GameControllerPath',
    'SDL_GameControllerPathForIndex',
    'SDL_GameControllerRumble',
    'SDL_GameControllerRumbleTriggers',
    'SDL_GameControllerSendEffect',
    'SDL_GameControllerSetLED',
    'SDL_GameControllerSetPlayerIndex',
    'SDL_GameControllerSetSensorEnabled',
    'SDL_GameControllerType',
    'SDL_GameControllerTypeForIndex',
    'SDL_GameControllerUpdate',
    'SDL_IsGameController',
]

SDL_GameControllerBindType = c_int
SDL_CONTROLLER_BINDTYPE_NONE: int
SDL_CONTROLLER_BINDTYPE_BUTTON: int
SDL_CONTROLLER_BINDTYPE_AXIS: int
SDL_CONTROLLER_BINDTYPE_HAT: int
SDL_GameControllerType = c_int
SDL_CONTROLLER_TYPE_UNKNOWN: int
SDL_CONTROLLER_TYPE_XBOX360: int
SDL_CONTROLLER_TYPE_XBOXONE: int
SDL_CONTROLLER_TYPE_PS3: int
SDL_CONTROLLER_TYPE_PS4: int
SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_PRO: int
SDL_CONTROLLER_TYPE_VIRTUAL: int
SDL_CONTROLLER_TYPE_PS5: int
SDL_CONTROLLER_TYPE_AMAZON_LUNA: int
SDL_CONTROLLER_TYPE_GOOGLE_STADIA: int
SDL_CONTROLLER_TYPE_NVIDIA_SHIELD: int
SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_LEFT: int
SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_RIGHT: int
SDL_CONTROLLER_TYPE_NINTENDO_SWITCH_JOYCON_PAIR: int
SDL_CONTROLLER_TYPE_MAX: int
SDL_GameControllerAxis = c_int
SDL_CONTROLLER_AXIS_INVALID: int
SDL_CONTROLLER_AXIS_LEFTX: int
SDL_CONTROLLER_AXIS_LEFTY: int
SDL_CONTROLLER_AXIS_RIGHTX: int
SDL_CONTROLLER_AXIS_RIGHTY: int
SDL_CONTROLLER_AXIS_TRIGGERLEFT: int
SDL_CONTROLLER_AXIS_TRIGGERRIGHT: int
SDL_CONTROLLER_AXIS_MAX: int
SDL_GameControllerButton = c_int
SDL_CONTROLLER_BUTTON_INVALID: int
SDL_CONTROLLER_BUTTON_A: int
SDL_CONTROLLER_BUTTON_B: int
SDL_CONTROLLER_BUTTON_X: int
SDL_CONTROLLER_BUTTON_Y: int
SDL_CONTROLLER_BUTTON_BACK: int
SDL_CONTROLLER_BUTTON_GUIDE: int
SDL_CONTROLLER_BUTTON_START: int
SDL_CONTROLLER_BUTTON_LEFTSTICK: int
SDL_CONTROLLER_BUTTON_RIGHTSTICK: int
SDL_CONTROLLER_BUTTON_LEFTSHOULDER: int
SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: int
SDL_CONTROLLER_BUTTON_DPAD_UP: int
SDL_CONTROLLER_BUTTON_DPAD_DOWN: int
SDL_CONTROLLER_BUTTON_DPAD_LEFT: int
SDL_CONTROLLER_BUTTON_DPAD_RIGHT: int
SDL_CONTROLLER_BUTTON_MISC1: int
SDL_CONTROLLER_BUTTON_PADDLE1: int
SDL_CONTROLLER_BUTTON_PADDLE2: int
SDL_CONTROLLER_BUTTON_PADDLE3: int
SDL_CONTROLLER_BUTTON_PADDLE4: int
SDL_CONTROLLER_BUTTON_TOUCHPAD: int
SDL_CONTROLLER_BUTTON_MAX: int

class _gchat(Structure):
    hat: int
    hat_mask: int

class _gcvalue(Union):
    button: int
    axis: int
    hat: _gchat

class SDL_GameControllerButtonBind(Structure):
    bindType: int
    value: _gcvalue

class SDL_GameController(c_void_p): ...

def SDL_GameControllerAddMappingsFromRW(rw: _Pointer[SDL_RWops], freerw: int, /) -> int: ...
def SDL_GameControllerAddMappingsFromFile(fname: bytes | None) -> int: ...
def SDL_GameControllerAddMapping(mappingString: bytes | None, /) -> int: ...
def SDL_GameControllerNumMappings() -> int: ...
def SDL_GameControllerMappingForIndex(mapping_index: int, /) -> bytes | None: ...
def SDL_GameControllerMappingForGUID(guid: SDL_JoystickGUID, /) -> bytes | None: ...
def SDL_GameControllerMapping(gamecontroller: _Pointer[SDL_GameController], /) -> bytes | None: ...
def SDL_IsGameController(joystick_index: int, /) -> int: ...
def SDL_GameControllerNameForIndex(joystick_index: int, /) -> bytes | None: ...
def SDL_GameControllerPathForIndex(joystick_index: int, /) -> bytes | None: ...
def SDL_GameControllerTypeForIndex(joystick_index: int, /) -> int: ...
def SDL_GameControllerMappingForDeviceIndex(joystick_index: int, /) -> bytes | None: ...
def SDL_GameControllerOpen(joystick_index: int, /) -> _Pointer[SDL_GameController]: ...
def SDL_GameControllerFromInstanceID(joyid: int, /) -> _Pointer[SDL_GameController]: ...
def SDL_GameControllerFromPlayerIndex(player_index: int, /) -> _Pointer[SDL_GameController]: ...
def SDL_GameControllerName(gamecontroller: _Pointer[SDL_GameController], /) -> bytes | None: ...
def SDL_GameControllerPath(gamecontroller: _Pointer[SDL_GameController], /) -> bytes | None: ...
def SDL_GameControllerGetType(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetPlayerIndex(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerSetPlayerIndex(gamecontroller: _Pointer[SDL_GameController], player_index: int, /) -> None: ...
def SDL_GameControllerGetVendor(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetProduct(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetProductVersion(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetFirmwareVersion(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetSerial(gamecontroller: _Pointer[SDL_GameController], /) -> bytes | None: ...
def SDL_GameControllerGetSteamHandle(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetAttached(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetJoystick(gamecontroller: _Pointer[SDL_GameController], /) -> _Pointer[SDL_Joystick]: ...
def SDL_GameControllerEventState(state: int, /) -> int: ...
def SDL_GameControllerUpdate() -> None: ...
def SDL_GameControllerGetAxisFromString(pchString: bytes | None, /) -> int: ...
def SDL_GameControllerGetStringForAxis(axis: int, /) -> bytes | None: ...
def SDL_GameControllerGetBindForAxis(
    gamecontroller: _Pointer[SDL_GameController], axis: int, /
) -> SDL_GameControllerButtonBind: ...
def SDL_GameControllerHasAxis(gamecontroller: _Pointer[SDL_GameController], axis: int, /) -> int: ...
def SDL_GameControllerGetAxis(gamecontroller: _Pointer[SDL_GameController], axis: int, /) -> int: ...
def SDL_GameControllerGetButtonFromString(pchString: bytes | None, /) -> int: ...
def SDL_GameControllerGetStringForButton(button: int, /) -> bytes | None: ...
def SDL_GameControllerGetBindForButton(
    gamecontroller: _Pointer[SDL_GameController], button: int, /
) -> SDL_GameControllerButtonBind: ...
def SDL_GameControllerHasButton(gamecontroller: _Pointer[SDL_GameController], button: int, /) -> int: ...
def SDL_GameControllerGetButton(gamecontroller: _Pointer[SDL_GameController], button: int, /) -> int: ...
def SDL_GameControllerGetNumTouchpads(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerGetNumTouchpadFingers(gamecontroller: _Pointer[SDL_GameController], touchpad: int, /) -> int: ...
def SDL_GameControllerGetTouchpadFinger(
    gamecontroller: _Pointer[SDL_GameController],
    touchpad: int,
    finger: int,
    state: _Pointer[Uint8],
    x: _Pointer[c_float],
    y: _Pointer[c_float],
    pressure: _Pointer[c_float],
    /,
) -> int: ...
def SDL_GameControllerHasSensor(gamecontroller: _Pointer[SDL_GameController], type: int, /) -> int: ...
def SDL_GameControllerSetSensorEnabled(
    gamecontroller: _Pointer[SDL_GameController], type: int, enabled: int, /
) -> int: ...
def SDL_GameControllerIsSensorEnabled(gamecontroller: _Pointer[SDL_GameController], type: int, /) -> int: ...
def SDL_GameControllerGetSensorDataRate(gamecontroller: _Pointer[SDL_GameController], type: int, /) -> float: ...
def SDL_GameControllerGetSensorData(
    gamecontroller: _Pointer[SDL_GameController],
    type: int,
    data: _Pointer[c_float],
    num_values: int,
    /,
) -> int: ...
def SDL_GameControllerGetSensorDataWithTimestamp(
    gamecontroller: _Pointer[SDL_GameController],
    type: int,
    timestamp: _Pointer[Uint64],
    data: _Pointer[c_float],
    num_values: int,
    /,
) -> int: ...
def SDL_GameControllerRumble(
    gamecontroller: _Pointer[SDL_GameController],
    low_frequency_rumble: int,
    high_frequency_rumble: int,
    duration_ms: int,
    /,
) -> int: ...
def SDL_GameControllerRumbleTriggers(
    gamecontroller: _Pointer[SDL_GameController],
    left_rumble: int,
    right_rumble: int,
    duration_ms: int,
    /,
) -> int: ...
def SDL_GameControllerHasLED(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerHasRumble(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerHasRumbleTriggers(gamecontroller: _Pointer[SDL_GameController], /) -> int: ...
def SDL_GameControllerSetLED(
    gamecontroller: _Pointer[SDL_GameController], red: int, green: int, blue: int, /
) -> int: ...
def SDL_GameControllerSendEffect(
    gamecontroller: _Pointer[SDL_GameController], data: c_void_p | int | None, size: int, /
) -> int: ...
def SDL_GameControllerClose(gamecontroller: _Pointer[SDL_GameController], /) -> None: ...
def SDL_GameControllerGetAppleSFSymbolsNameForButton(
    gamecontroller: _Pointer[SDL_GameController], button: int, /
) -> bytes | None: ...
def SDL_GameControllerGetAppleSFSymbolsNameForAxis(
    gamecontroller: _Pointer[SDL_GameController], axis: int, /
) -> bytes | None: ...
