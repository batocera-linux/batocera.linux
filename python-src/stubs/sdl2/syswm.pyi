from ctypes import Array, Structure, Union, _Pointer, c_int, c_void_p

from .stdinc import Uint8
from .version import SDL_version
from .video import SDL_Window

__all__ = [
    'SDL_SYSWM_ANDROID',
    'SDL_SYSWM_COCOA',
    'SDL_SYSWM_DIRECTFB',
    'SDL_SYSWM_HAIKU',
    'SDL_SYSWM_KMSDRM',
    'SDL_SYSWM_MIR',
    'SDL_SYSWM_OS2',
    'SDL_SYSWM_RISCOS',
    'SDL_SYSWM_TYPE',
    'SDL_SYSWM_UIKIT',
    'SDL_SYSWM_UNKNOWN',
    'SDL_SYSWM_VIVANTE',
    'SDL_SYSWM_WAYLAND',
    'SDL_SYSWM_WINDOWS',
    'SDL_SYSWM_WINRT',
    'SDL_SYSWM_X11',
    'SDL_GetWindowWMInfo',
    'SDL_SysWMinfo',
    'SDL_SysWMmsg',
]

SDL_SYSWM_TYPE = c_int
SDL_SYSWM_UNKNOWN: int
SDL_SYSWM_WINDOWS: int
SDL_SYSWM_X11: int
SDL_SYSWM_DIRECTFB: int
SDL_SYSWM_COCOA: int
SDL_SYSWM_UIKIT: int
SDL_SYSWM_WAYLAND: int
SDL_SYSWM_MIR: int
SDL_SYSWM_WINRT: int
SDL_SYSWM_ANDROID: int
SDL_SYSWM_VIVANTE: int
SDL_SYSWM_OS2: int
SDL_SYSWM_HAIKU: int
SDL_SYSWM_KMSDRM: int
SDL_SYSWM_RISCOS: int
HWND = c_void_p
HDC = c_void_p
HINSTANCE = c_void_p
UINT = c_int
WPARAM = c_int
LPARAM = c_int

class _winmsg(Structure):
    hwnd: int | None
    msg: int
    wParam: int
    lParam: int

class _x11msg(Structure):
    event: int | None

class _dfbmsg(Structure):
    event: int | None

class _cocoamsg(Structure):
    dummy: int

class _uikitmsg(Structure):
    dummy: int

class _vivantemsg(Structure):
    dummy: int

BOOL = c_int
ULONG = c_int
MPARAM = c_int

class _os2msg(Structure):
    fFrame: int
    hwnd: int
    msg: int
    mp1: int
    mp2: int

class _msg(Union):
    win: _winmsg
    x11: _x11msg
    dfb: _dfbmsg
    cocoa: _cocoamsg
    uikit: _uikitmsg
    vivante: _vivantemsg
    os2: _os2msg
    dummy: int

class SDL_SysWMmsg(Structure):
    version: SDL_version
    subsystem: int
    msg: _msg

class _wininfo(Structure):
    window: int | None
    hdc: int | None
    hinstance: int | None

class _winrtinfo(Structure):
    window: int | None

class _x11info(Structure):
    display: int | None
    window: int

class _dfbinfo(Structure):
    dfb: int | None
    window: int | None
    surface: int | None

class _cocoainfo(Structure):
    window: int | None

class _uikitinfo(Structure):
    window: int | None
    framebuffer: int
    colorbuffer: int
    resolveFramebuffer: int

class _wl(Structure):
    display: int | None
    surface: int | None
    shell_surface: int | None
    egl_window: int | None
    xdg_surface: int | None
    xdg_toplevel: int | None
    xdg_popup: int | None
    xdg_positioner: int | None

class _mir(Structure):
    connection: int | None
    surface: int | None

class _android(Structure):
    window: int | None
    surface: int | None

class _os2(Structure):
    hwnd: int | None
    hwndFrame: int | None

class _vivante(Structure):
    display: int | None
    window: int | None

class _kmsdrm(Structure):
    dev_index: int
    drm_fd: int
    gbm_dev: int | None

class _info(Union):
    win: _wininfo
    winrt: _winrtinfo
    x11: _x11info
    dfb: _dfbinfo
    cocoa: _cocoainfo
    uikit: _uikitinfo
    wl: _wl
    mir: _mir
    android: _android
    os2: _os2
    vivante: _vivante
    kmsdrm: _kmsdrm
    dummy: Array[Uint8]

class SDL_SysWMinfo(Structure):
    version: SDL_version
    subsystem: int
    info: _info

def SDL_GetWindowWMInfo(window: _Pointer[SDL_Window], info: _Pointer[SDL_SysWMinfo], /) -> int: ...
