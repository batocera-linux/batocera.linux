from ctypes import Array, Structure, _Pointer, c_int

from .video import SDL_Window

__all__ = [
    'SDL_MESSAGEBOX_BUTTONS_LEFT_TO_RIGHT',
    'SDL_MESSAGEBOX_BUTTONS_RIGHT_TO_LEFT',
    'SDL_MESSAGEBOX_BUTTON_ESCAPEKEY_DEFAULT',
    'SDL_MESSAGEBOX_BUTTON_RETURNKEY_DEFAULT',
    'SDL_MESSAGEBOX_COLOR_BACKGROUND',
    'SDL_MESSAGEBOX_COLOR_BUTTON_BACKGROUND',
    'SDL_MESSAGEBOX_COLOR_BUTTON_BORDER',
    'SDL_MESSAGEBOX_COLOR_BUTTON_SELECTED',
    'SDL_MESSAGEBOX_COLOR_MAX',
    'SDL_MESSAGEBOX_COLOR_TEXT',
    'SDL_MESSAGEBOX_ERROR',
    'SDL_MESSAGEBOX_INFORMATION',
    'SDL_MESSAGEBOX_WARNING',
    'SDL_MessageBoxButtonData',
    'SDL_MessageBoxButtonFlags',
    'SDL_MessageBoxColor',
    'SDL_MessageBoxColorScheme',
    'SDL_MessageBoxColorType',
    'SDL_MessageBoxData',
    'SDL_MessageBoxFlags',
    'SDL_ShowMessageBox',
    'SDL_ShowSimpleMessageBox',
]

SDL_MessageBoxFlags = c_int
SDL_MESSAGEBOX_ERROR: int
SDL_MESSAGEBOX_WARNING: int
SDL_MESSAGEBOX_INFORMATION: int
SDL_MESSAGEBOX_BUTTONS_LEFT_TO_RIGHT: int
SDL_MESSAGEBOX_BUTTONS_RIGHT_TO_LEFT: int
SDL_MessageBoxButtonFlags = c_int
SDL_MESSAGEBOX_BUTTON_RETURNKEY_DEFAULT: int
SDL_MESSAGEBOX_BUTTON_ESCAPEKEY_DEFAULT: int
SDL_MessageBoxColorType = c_int
SDL_MESSAGEBOX_COLOR_BACKGROUND: int
SDL_MESSAGEBOX_COLOR_TEXT: int
SDL_MESSAGEBOX_COLOR_BUTTON_BORDER: int
SDL_MESSAGEBOX_COLOR_BUTTON_BACKGROUND: int
SDL_MESSAGEBOX_COLOR_BUTTON_SELECTED: int
SDL_MESSAGEBOX_COLOR_MAX: int

class SDL_MessageBoxButtonData(Structure):
    flags: int
    buttonid: int
    text: bytes | None

class SDL_MessageBoxColor(Structure):
    r: int
    g: int
    b: int

class SDL_MessageBoxColorScheme(Structure):
    colors: Array[SDL_MessageBoxColor]

class SDL_MessageBoxData(Structure):
    flags: int
    window: _Pointer[SDL_Window]
    title: bytes | None
    message: bytes | None
    numbuttons: int
    buttons: _Pointer[SDL_MessageBoxButtonData]
    colorScheme: _Pointer[SDL_MessageBoxColorScheme]

def SDL_ShowMessageBox(messageboxdata: _Pointer[SDL_MessageBoxData], buttonid: _Pointer[c_int], /) -> int: ...
def SDL_ShowSimpleMessageBox(
    flags: int, title: bytes | None, message: bytes | None, window: _Pointer[SDL_Window], /
) -> int: ...
