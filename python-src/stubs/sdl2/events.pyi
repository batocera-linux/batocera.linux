from ctypes import Array, Structure, Union, _CFuncPtr, _Pointer, c_char, c_float, c_int, c_uint8, c_void_p

from .keyboard import SDL_Keysym
from .syswm import SDL_SysWMmsg as SDL_SysWMmsg

__all__ = [
    'SDL_ADDEVENT',
    'SDL_APP_DIDENTERBACKGROUND',
    'SDL_APP_DIDENTERFOREGROUND',
    'SDL_APP_LOWMEMORY',
    'SDL_APP_TERMINATING',
    'SDL_APP_WILLENTERBACKGROUND',
    'SDL_APP_WILLENTERFOREGROUND',
    'SDL_AUDIODEVICEADDED',
    'SDL_AUDIODEVICEREMOVED',
    'SDL_CLIPBOARDUPDATE',
    'SDL_CONTROLLERAXISMOTION',
    'SDL_CONTROLLERBUTTONDOWN',
    'SDL_CONTROLLERBUTTONUP',
    'SDL_CONTROLLERDEVICEADDED',
    'SDL_CONTROLLERDEVICEREMAPPED',
    'SDL_CONTROLLERDEVICEREMOVED',
    'SDL_CONTROLLERSENSORUPDATE',
    'SDL_CONTROLLERSTEAMHANDLEUPDATED',
    'SDL_CONTROLLERTOUCHPADDOWN',
    'SDL_CONTROLLERTOUCHPADMOTION',
    'SDL_CONTROLLERTOUCHPADUP',
    'SDL_CONTROLLERUPDATECOMPLETE_RESERVED_FOR_SDL3',
    'SDL_DISABLE',
    'SDL_DISPLAYEVENT',
    'SDL_DOLLARGESTURE',
    'SDL_DOLLARRECORD',
    'SDL_DROPBEGIN',
    'SDL_DROPCOMPLETE',
    'SDL_DROPFILE',
    'SDL_DROPTEXT',
    'SDL_ENABLE',
    'SDL_FINGERDOWN',
    'SDL_FINGERMOTION',
    'SDL_FINGERUP',
    'SDL_FIRSTEVENT',
    'SDL_GETEVENT',
    'SDL_IGNORE',
    'SDL_JOYAXISMOTION',
    'SDL_JOYBALLMOTION',
    'SDL_JOYBATTERYUPDATED',
    'SDL_JOYBUTTONDOWN',
    'SDL_JOYBUTTONUP',
    'SDL_JOYDEVICEADDED',
    'SDL_JOYDEVICEREMOVED',
    'SDL_JOYHATMOTION',
    'SDL_KEYDOWN',
    'SDL_KEYMAPCHANGED',
    'SDL_KEYUP',
    'SDL_LASTEVENT',
    'SDL_LOCALECHANGED',
    'SDL_MOUSEBUTTONDOWN',
    'SDL_MOUSEBUTTONUP',
    'SDL_MOUSEMOTION',
    'SDL_MOUSEWHEEL',
    'SDL_MULTIGESTURE',
    'SDL_PEEKEVENT',
    'SDL_POLLSENTINEL',
    'SDL_PRESSED',
    'SDL_QUERY',
    'SDL_QUIT',
    'SDL_RELEASED',
    'SDL_RENDER_DEVICE_RESET',
    'SDL_RENDER_TARGETS_RESET',
    'SDL_SENSORUPDATE',
    'SDL_SYSWMEVENT',
    'SDL_TEXTEDITING',
    'SDL_TEXTEDITINGEVENT_TEXT_SIZE',
    'SDL_TEXTEDITING_EXT',
    'SDL_TEXTINPUT',
    'SDL_TEXTINPUTEVENT_TEXT_SIZE',
    'SDL_USEREVENT',
    'SDL_WINDOWEVENT',
    'SDL_AddEventWatch',
    'SDL_AudioDeviceEvent',
    'SDL_CommonEvent',
    'SDL_ControllerAxisEvent',
    'SDL_ControllerButtonEvent',
    'SDL_ControllerDeviceEvent',
    'SDL_ControllerSensorEvent',
    'SDL_ControllerTouchpadEvent',
    'SDL_DelEventWatch',
    'SDL_DisplayEvent',
    'SDL_DollarGestureEvent',
    'SDL_DropEvent',
    'SDL_Event',
    'SDL_EventFilter',
    'SDL_EventState',
    'SDL_EventType',
    'SDL_FilterEvents',
    'SDL_FlushEvent',
    'SDL_FlushEvents',
    'SDL_GetEventFilter',
    'SDL_GetEventState',
    'SDL_HasEvent',
    'SDL_HasEvents',
    'SDL_JoyAxisEvent',
    'SDL_JoyBallEvent',
    'SDL_JoyBatteryEvent',
    'SDL_JoyButtonEvent',
    'SDL_JoyDeviceEvent',
    'SDL_JoyHatEvent',
    'SDL_KeyboardEvent',
    'SDL_MouseButtonEvent',
    'SDL_MouseMotionEvent',
    'SDL_MouseWheelEvent',
    'SDL_MultiGestureEvent',
    'SDL_OSEvent',
    'SDL_PeepEvents',
    'SDL_PollEvent',
    'SDL_PumpEvents',
    'SDL_PushEvent',
    'SDL_QuitEvent',
    'SDL_QuitRequested',
    'SDL_RegisterEvents',
    'SDL_SensorEvent',
    'SDL_SetEventFilter',
    'SDL_SysWMEvent',
    'SDL_SysWMmsg',
    'SDL_TextEditingEvent',
    'SDL_TextEditingExtEvent',
    'SDL_TextInputEvent',
    'SDL_TouchFingerEvent',
    'SDL_UserEvent',
    'SDL_WaitEvent',
    'SDL_WaitEventTimeout',
    'SDL_WindowEvent',
    'SDL_eventaction',
]

SDL_RELEASED: int
SDL_PRESSED: int
SDL_EventType = c_int
SDL_FIRSTEVENT: int
SDL_QUIT: int
SDL_APP_TERMINATING: int
SDL_APP_LOWMEMORY: int
SDL_APP_WILLENTERBACKGROUND: int
SDL_APP_DIDENTERBACKGROUND: int
SDL_APP_WILLENTERFOREGROUND: int
SDL_APP_DIDENTERFOREGROUND: int
SDL_LOCALECHANGED: int
SDL_DISPLAYEVENT: int
SDL_WINDOWEVENT: int
SDL_SYSWMEVENT: int
SDL_KEYDOWN: int
SDL_KEYUP: int
SDL_TEXTEDITING: int
SDL_TEXTINPUT: int
SDL_KEYMAPCHANGED: int
SDL_TEXTEDITING_EXT: int
SDL_MOUSEMOTION: int
SDL_MOUSEBUTTONDOWN: int
SDL_MOUSEBUTTONUP: int
SDL_MOUSEWHEEL: int
SDL_JOYAXISMOTION: int
SDL_JOYBALLMOTION: int
SDL_JOYHATMOTION: int
SDL_JOYBUTTONDOWN: int
SDL_JOYBUTTONUP: int
SDL_JOYDEVICEADDED: int
SDL_JOYDEVICEREMOVED: int
SDL_JOYBATTERYUPDATED: int
SDL_CONTROLLERAXISMOTION: int
SDL_CONTROLLERBUTTONDOWN: int
SDL_CONTROLLERBUTTONUP: int
SDL_CONTROLLERDEVICEADDED: int
SDL_CONTROLLERDEVICEREMOVED: int
SDL_CONTROLLERDEVICEREMAPPED: int
SDL_CONTROLLERTOUCHPADDOWN: int
SDL_CONTROLLERTOUCHPADMOTION: int
SDL_CONTROLLERTOUCHPADUP: int
SDL_CONTROLLERSENSORUPDATE: int
SDL_CONTROLLERUPDATECOMPLETE_RESERVED_FOR_SDL3: int
SDL_CONTROLLERSTEAMHANDLEUPDATED: int
SDL_FINGERDOWN: int
SDL_FINGERUP: int
SDL_FINGERMOTION: int
SDL_DOLLARGESTURE: int
SDL_DOLLARRECORD: int
SDL_MULTIGESTURE: int
SDL_CLIPBOARDUPDATE: int
SDL_DROPFILE: int
SDL_DROPTEXT: int
SDL_DROPBEGIN: int
SDL_DROPCOMPLETE: int
SDL_AUDIODEVICEADDED: int
SDL_AUDIODEVICEREMOVED: int
SDL_SENSORUPDATE: int
SDL_RENDER_TARGETS_RESET: int
SDL_RENDER_DEVICE_RESET: int
SDL_POLLSENTINEL: int
SDL_USEREVENT: int
SDL_LASTEVENT: int
SDL_eventaction = c_int
SDL_ADDEVENT: int
SDL_PEEKEVENT: int
SDL_GETEVENT: int
SDL_TEXTEDITINGEVENT_TEXT_SIZE: int
SDL_TEXTINPUTEVENT_TEXT_SIZE: int
SDL_QUERY: int
SDL_IGNORE: int
SDL_DISABLE: int
SDL_ENABLE: int

class SDL_CommonEvent(Structure):
    type: int
    timestamp: int

class SDL_DisplayEvent(Structure):
    type: int
    timestamp: int
    display: int
    event: int
    padding1: int
    padding2: int
    padding3: int
    data1: int

class SDL_WindowEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    event: int
    padding1: int
    padding2: int
    padding3: int
    data1: int
    data2: int

class SDL_KeyboardEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    state: int
    repeat: int
    padding2: int
    padding3: int
    keysym: SDL_Keysym

class SDL_TextEditingEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    text: Array[c_char]
    start: int
    length: int

class SDL_TextEditingExtEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    text: bytes | None
    start: int
    length: int

class SDL_TextInputEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    text: Array[c_char]

class SDL_MouseMotionEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    which: int
    state: int
    x: int
    y: int
    xrel: int
    yrel: int

class SDL_MouseButtonEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    which: int
    button: int
    state: int
    clicks: int
    padding1: int
    x: int
    y: int

class SDL_MouseWheelEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    which: int
    x: int
    y: int
    direction: int
    preciseX: float
    preciseY: float
    mouseX: int
    mouseY: int

class SDL_JoyAxisEvent(Structure):
    type: int
    timestamp: int
    which: int
    axis: int
    padding1: int
    padding2: int
    padding3: int
    value: int
    padding4: int

class SDL_JoyBallEvent(Structure):
    type: int
    timestamp: int
    which: int
    ball: int
    padding1: int
    padding2: int
    padding3: int
    xrel: int
    yrel: int

class SDL_JoyHatEvent(Structure):
    type: int
    timestamp: int
    which: int
    hat: int
    value: int
    padding1: int
    padding2: int

class SDL_JoyButtonEvent(Structure):
    type: int
    timestamp: int
    which: int
    button: int
    state: int
    padding1: int
    padding2: int

class SDL_JoyDeviceEvent(Structure):
    type: int
    timestamp: int
    which: int

class SDL_JoyBatteryEvent(Structure):
    type: int
    timestamp: int
    which: int
    level: int

class SDL_ControllerAxisEvent(Structure):
    type: int
    timestamp: int
    which: int
    axis: int
    padding1: int
    padding2: int
    padding3: int
    value: int
    padding4: int

class SDL_ControllerButtonEvent(Structure):
    type: int
    timestamp: int
    which: int
    button: int
    state: int
    padding1: int
    padding2: int

class SDL_ControllerDeviceEvent(Structure):
    type: int
    timestamp: int
    which: int

class SDL_ControllerTouchpadEvent(Structure):
    type: int
    timestamp: int
    which: int
    touchpad: int
    finger: int
    x: float
    y: float
    pressure: float

class SDL_ControllerSensorEvent(Structure):
    type: int
    timestamp: int
    which: int
    sensor: int
    data: Array[c_float]
    timestamp_us: int

class SDL_AudioDeviceEvent(Structure):
    type: int
    timestamp: int
    which: int
    iscapture: int
    padding1: int
    padding2: int
    padding3: int

class SDL_TouchFingerEvent(Structure):
    type: int
    timestamp: int
    touchId: int
    fingerId: int
    x: float
    y: float
    dx: float
    dy: float
    pressure: float
    windowID: int

class SDL_MultiGestureEvent(Structure):
    type: int
    timestamp: int
    touchId: int
    dTheta: float
    dDist: float
    x: float
    y: float
    numFingers: int
    padding: int

class SDL_DollarGestureEvent(Structure):
    type: int
    timestamp: int
    touchId: int
    gestureId: int
    numFingers: int
    error: float
    x: float
    y: float

class SDL_DropEvent(Structure):
    type: int
    timestamp: int
    file: bytes | None
    windowID: int

class SDL_SensorEvent(Structure):
    type: int
    timestamp: int
    which: int
    data: Array[c_float]
    timestamp_us: int

class SDL_QuitEvent(Structure):
    type: int
    timestamp: int

class SDL_OSEvent(Structure):
    type: int
    timestamp: int

class SDL_UserEvent(Structure):
    type: int
    timestamp: int
    windowID: int
    code: int
    data1: int | None
    data2: int | None

class SDL_SysWMEvent(Structure):
    type: int
    timestamp: int
    msg: _Pointer[SDL_SysWMmsg]

class SDL_Event(Union):
    type: int
    common: SDL_CommonEvent
    display: SDL_DisplayEvent
    window: SDL_WindowEvent
    key: SDL_KeyboardEvent
    edit: SDL_TextEditingEvent
    editExt: SDL_TextEditingExtEvent
    text: SDL_TextInputEvent
    motion: SDL_MouseMotionEvent
    button: SDL_MouseButtonEvent
    wheel: SDL_MouseWheelEvent
    jaxis: SDL_JoyAxisEvent
    jball: SDL_JoyBallEvent
    jhat: SDL_JoyHatEvent
    jbutton: SDL_JoyButtonEvent
    jdevice: SDL_JoyDeviceEvent
    jbattery: SDL_JoyBatteryEvent
    caxis: SDL_ControllerAxisEvent
    cbutton: SDL_ControllerButtonEvent
    cdevice: SDL_ControllerDeviceEvent
    ctouchpad: SDL_ControllerTouchpadEvent
    csensor: SDL_ControllerSensorEvent
    adevice: SDL_AudioDeviceEvent
    sensor: SDL_SensorEvent
    quit: SDL_QuitEvent
    user: SDL_UserEvent
    syswm: SDL_SysWMEvent
    tfinger: SDL_TouchFingerEvent
    mgesture: SDL_MultiGestureEvent
    dgesture: SDL_DollarGestureEvent
    drop: SDL_DropEvent
    padding: Array[c_uint8]

SDL_EventFilter: type[_CFuncPtr]

def SDL_PumpEvents() -> None: ...
def SDL_PeepEvents(events: _Pointer[SDL_Event], numevents: int, action: int, minType: int, maxType: int, /) -> int: ...
def SDL_HasEvent(type: int, /) -> int: ...
def SDL_HasEvents(minType: int, maxType: int, /) -> int: ...
def SDL_FlushEvent(type: int, /) -> None: ...
def SDL_FlushEvents(minType: int, maxType: int, /) -> None: ...
def SDL_PollEvent(event: _Pointer[SDL_Event], /) -> int: ...
def SDL_WaitEvent(event: _Pointer[SDL_Event], /) -> int: ...
def SDL_WaitEventTimeout(event: _Pointer[SDL_Event], timeout: int, /) -> int: ...
def SDL_PushEvent(event: _Pointer[SDL_Event], /) -> int: ...
def SDL_SetEventFilter(filter: _CFuncPtr, userdata: c_void_p | int | None, /) -> None: ...
def SDL_GetEventFilter(filter: _Pointer[_CFuncPtr], userdata: _Pointer[c_void_p], /) -> int: ...
def SDL_AddEventWatch(filter: _CFuncPtr, userdata: c_void_p | int | None, /) -> None: ...
def SDL_DelEventWatch(filter: _CFuncPtr, userdata: c_void_p | int | None, /) -> None: ...
def SDL_FilterEvents(filter: _CFuncPtr, userdata: c_void_p | int | None, /) -> None: ...
def SDL_EventState(type: int, state: int, /) -> int: ...
def SDL_GetEventState(type: int, /) -> int: ...
def SDL_RegisterEvents(numevents: int, /) -> int: ...
def SDL_QuitRequested() -> bool: ...
