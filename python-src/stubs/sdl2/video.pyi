from ctypes import Structure, _CFuncPtr, _Pointer, c_float, c_int, c_size_t, c_void_p, py_object

from .rect import SDL_Point, SDL_Rect
from .stdinc import Uint16
from .surface import SDL_Surface

__all__ = [
    'SDL_DISPLAYEVENT_CONNECTED',
    'SDL_DISPLAYEVENT_DISCONNECTED',
    'SDL_DISPLAYEVENT_MOVED',
    'SDL_DISPLAYEVENT_NONE',
    'SDL_DISPLAYEVENT_ORIENTATION',
    'SDL_FLASH_BRIEFLY',
    'SDL_FLASH_CANCEL',
    'SDL_FLASH_UNTIL_FOCUSED',
    'SDL_GL_ACCELERATED_VISUAL',
    'SDL_GL_ACCUM_ALPHA_SIZE',
    'SDL_GL_ACCUM_BLUE_SIZE',
    'SDL_GL_ACCUM_GREEN_SIZE',
    'SDL_GL_ACCUM_RED_SIZE',
    'SDL_GL_ALPHA_SIZE',
    'SDL_GL_BLUE_SIZE',
    'SDL_GL_BUFFER_SIZE',
    'SDL_GL_CONTEXT_DEBUG_FLAG',
    'SDL_GL_CONTEXT_EGL',
    'SDL_GL_CONTEXT_FLAGS',
    'SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG',
    'SDL_GL_CONTEXT_MAJOR_VERSION',
    'SDL_GL_CONTEXT_MINOR_VERSION',
    'SDL_GL_CONTEXT_NO_ERROR',
    'SDL_GL_CONTEXT_PROFILE_COMPATIBILITY',
    'SDL_GL_CONTEXT_PROFILE_CORE',
    'SDL_GL_CONTEXT_PROFILE_ES',
    'SDL_GL_CONTEXT_PROFILE_MASK',
    'SDL_GL_CONTEXT_RELEASE_BEHAVIOR',
    'SDL_GL_CONTEXT_RELEASE_BEHAVIOR_FLUSH',
    'SDL_GL_CONTEXT_RELEASE_BEHAVIOR_NONE',
    'SDL_GL_CONTEXT_RESET_ISOLATION_FLAG',
    'SDL_GL_CONTEXT_RESET_LOSE_CONTEXT',
    'SDL_GL_CONTEXT_RESET_NOTIFICATION',
    'SDL_GL_CONTEXT_RESET_NO_NOTIFICATION',
    'SDL_GL_CONTEXT_ROBUST_ACCESS_FLAG',
    'SDL_GL_DEPTH_SIZE',
    'SDL_GL_DOUBLEBUFFER',
    'SDL_GL_FLOATBUFFERS',
    'SDL_GL_FRAMEBUFFER_SRGB_CAPABLE',
    'SDL_GL_GREEN_SIZE',
    'SDL_GL_MULTISAMPLEBUFFERS',
    'SDL_GL_MULTISAMPLESAMPLES',
    'SDL_GL_RED_SIZE',
    'SDL_GL_RETAINED_BACKING',
    'SDL_GL_SHARE_WITH_CURRENT_CONTEXT',
    'SDL_GL_STENCIL_SIZE',
    'SDL_GL_STEREO',
    'SDL_HITTEST_DRAGGABLE',
    'SDL_HITTEST_NORMAL',
    'SDL_HITTEST_RESIZE_BOTTOM',
    'SDL_HITTEST_RESIZE_BOTTOMLEFT',
    'SDL_HITTEST_RESIZE_BOTTOMRIGHT',
    'SDL_HITTEST_RESIZE_LEFT',
    'SDL_HITTEST_RESIZE_RIGHT',
    'SDL_HITTEST_RESIZE_TOP',
    'SDL_HITTEST_RESIZE_TOPLEFT',
    'SDL_HITTEST_RESIZE_TOPRIGHT',
    'SDL_ORIENTATION_LANDSCAPE',
    'SDL_ORIENTATION_LANDSCAPE_FLIPPED',
    'SDL_ORIENTATION_PORTRAIT',
    'SDL_ORIENTATION_PORTRAIT_FLIPPED',
    'SDL_ORIENTATION_UNKNOWN',
    'SDL_WINDOWEVENT_CLOSE',
    'SDL_WINDOWEVENT_DISPLAY_CHANGED',
    'SDL_WINDOWEVENT_ENTER',
    'SDL_WINDOWEVENT_EXPOSED',
    'SDL_WINDOWEVENT_FOCUS_GAINED',
    'SDL_WINDOWEVENT_FOCUS_LOST',
    'SDL_WINDOWEVENT_HIDDEN',
    'SDL_WINDOWEVENT_HIT_TEST',
    'SDL_WINDOWEVENT_ICCPROF_CHANGED',
    'SDL_WINDOWEVENT_LEAVE',
    'SDL_WINDOWEVENT_MAXIMIZED',
    'SDL_WINDOWEVENT_MINIMIZED',
    'SDL_WINDOWEVENT_MOVED',
    'SDL_WINDOWEVENT_NONE',
    'SDL_WINDOWEVENT_RESIZED',
    'SDL_WINDOWEVENT_RESTORED',
    'SDL_WINDOWEVENT_SHOWN',
    'SDL_WINDOWEVENT_SIZE_CHANGED',
    'SDL_WINDOWEVENT_TAKE_FOCUS',
    'SDL_WINDOWPOS_CENTERED',
    'SDL_WINDOWPOS_CENTERED_DISPLAY',
    'SDL_WINDOWPOS_CENTERED_MASK',
    'SDL_WINDOWPOS_ISCENTERED',
    'SDL_WINDOWPOS_ISUNDEFINED',
    'SDL_WINDOWPOS_UNDEFINED',
    'SDL_WINDOWPOS_UNDEFINED_DISPLAY',
    'SDL_WINDOWPOS_UNDEFINED_MASK',
    'SDL_WINDOW_ALLOW_HIGHDPI',
    'SDL_WINDOW_ALWAYS_ON_TOP',
    'SDL_WINDOW_BORDERLESS',
    'SDL_WINDOW_FOREIGN',
    'SDL_WINDOW_FULLSCREEN',
    'SDL_WINDOW_FULLSCREEN_DESKTOP',
    'SDL_WINDOW_HIDDEN',
    'SDL_WINDOW_INPUT_FOCUS',
    'SDL_WINDOW_INPUT_FOCUS',
    'SDL_WINDOW_INPUT_GRABBED',
    'SDL_WINDOW_KEYBOARD_GRABBED',
    'SDL_WINDOW_MAXIMIZED',
    'SDL_WINDOW_METAL',
    'SDL_WINDOW_MINIMIZED',
    'SDL_WINDOW_MOUSE_CAPTURE',
    'SDL_WINDOW_MOUSE_FOCUS',
    'SDL_WINDOW_MOUSE_GRABBED',
    'SDL_WINDOW_OPENGL',
    'SDL_WINDOW_POPUP_MENU',
    'SDL_WINDOW_RESIZABLE',
    'SDL_WINDOW_SHOWN',
    'SDL_WINDOW_SKIP_TASKBAR',
    'SDL_WINDOW_TOOLTIP',
    'SDL_WINDOW_UTILITY',
    'SDL_WINDOW_VULKAN',
    'SDL_CreateWindow',
    'SDL_CreateWindowFrom',
    'SDL_DestroyWindow',
    'SDL_DestroyWindowSurface',
    'SDL_DisableScreenSaver',
    'SDL_DisplayEventID',
    'SDL_DisplayMode',
    'SDL_DisplayOrientation',
    'SDL_EnableScreenSaver',
    'SDL_FlashOperation',
    'SDL_FlashWindow',
    'SDL_GLContext',
    'SDL_GLContextResetNotification',
    'SDL_GL_CreateContext',
    'SDL_GL_DeleteContext',
    'SDL_GL_ExtensionSupported',
    'SDL_GL_GetAttribute',
    'SDL_GL_GetCurrentContext',
    'SDL_GL_GetCurrentWindow',
    'SDL_GL_GetDrawableSize',
    'SDL_GL_GetProcAddress',
    'SDL_GL_GetSwapInterval',
    'SDL_GL_LoadLibrary',
    'SDL_GL_MakeCurrent',
    'SDL_GL_ResetAttributes',
    'SDL_GL_SetAttribute',
    'SDL_GL_SetSwapInterval',
    'SDL_GL_SwapWindow',
    'SDL_GL_UnloadLibrary',
    'SDL_GLattr',
    'SDL_GLcontextFlag',
    'SDL_GLcontextReleaseFlag',
    'SDL_GLprofile',
    'SDL_GetClosestDisplayMode',
    'SDL_GetCurrentDisplayMode',
    'SDL_GetCurrentVideoDriver',
    'SDL_GetDesktopDisplayMode',
    'SDL_GetDisplayBounds',
    'SDL_GetDisplayDPI',
    'SDL_GetDisplayMode',
    'SDL_GetDisplayName',
    'SDL_GetDisplayOrientation',
    'SDL_GetDisplayUsableBounds',
    'SDL_GetGrabbedWindow',
    'SDL_GetNumDisplayModes',
    'SDL_GetNumVideoDisplays',
    'SDL_GetNumVideoDrivers',
    'SDL_GetPointDisplayIndex',
    'SDL_GetRectDisplayIndex',
    'SDL_GetVideoDriver',
    'SDL_GetWindowBordersSize',
    'SDL_GetWindowBrightness',
    'SDL_GetWindowData',
    'SDL_GetWindowDisplayIndex',
    'SDL_GetWindowDisplayMode',
    'SDL_GetWindowFlags',
    'SDL_GetWindowFromID',
    'SDL_GetWindowGammaRamp',
    'SDL_GetWindowGrab',
    'SDL_GetWindowICCProfile',
    'SDL_GetWindowID',
    'SDL_GetWindowKeyboardGrab',
    'SDL_GetWindowMaximumSize',
    'SDL_GetWindowMinimumSize',
    'SDL_GetWindowMouseGrab',
    'SDL_GetWindowMouseRect',
    'SDL_GetWindowOpacity',
    'SDL_GetWindowPixelFormat',
    'SDL_GetWindowPosition',
    'SDL_GetWindowSize',
    'SDL_GetWindowSizeInPixels',
    'SDL_GetWindowSurface',
    'SDL_GetWindowTitle',
    'SDL_HasWindowSurface',
    'SDL_HideWindow',
    'SDL_HitTest',
    'SDL_HitTestResult',
    'SDL_IsScreenSaverEnabled',
    'SDL_MaximizeWindow',
    'SDL_MinimizeWindow',
    'SDL_RaiseWindow',
    'SDL_RestoreWindow',
    'SDL_SetWindowAlwaysOnTop',
    'SDL_SetWindowBordered',
    'SDL_SetWindowBrightness',
    'SDL_SetWindowData',
    'SDL_SetWindowDisplayMode',
    'SDL_SetWindowFullscreen',
    'SDL_SetWindowGammaRamp',
    'SDL_SetWindowGrab',
    'SDL_SetWindowHitTest',
    'SDL_SetWindowIcon',
    'SDL_SetWindowInputFocus',
    'SDL_SetWindowKeyboardGrab',
    'SDL_SetWindowMaximumSize',
    'SDL_SetWindowMinimumSize',
    'SDL_SetWindowModalFor',
    'SDL_SetWindowMouseGrab',
    'SDL_SetWindowMouseRect',
    'SDL_SetWindowOpacity',
    'SDL_SetWindowPosition',
    'SDL_SetWindowResizable',
    'SDL_SetWindowSize',
    'SDL_SetWindowTitle',
    'SDL_ShowWindow',
    'SDL_UpdateWindowSurface',
    'SDL_UpdateWindowSurfaceRects',
    'SDL_VideoInit',
    'SDL_VideoQuit',
    'SDL_Window',
    'SDL_WindowEventID',
    'SDL_WindowFlags',
]

SDL_WindowFlags = c_int
SDL_WINDOW_FULLSCREEN: int
SDL_WINDOW_OPENGL: int
SDL_WINDOW_SHOWN: int
SDL_WINDOW_HIDDEN: int
SDL_WINDOW_BORDERLESS: int
SDL_WINDOW_RESIZABLE: int
SDL_WINDOW_MINIMIZED: int
SDL_WINDOW_MAXIMIZED: int
SDL_WINDOW_MOUSE_GRABBED: int
SDL_WINDOW_INPUT_GRABBED = SDL_WINDOW_MOUSE_GRABBED
SDL_WINDOW_INPUT_FOCUS: int
SDL_WINDOW_MOUSE_FOCUS: int
SDL_WINDOW_FULLSCREEN_DESKTOP: int
SDL_WINDOW_FOREIGN: int
SDL_WINDOW_ALLOW_HIGHDPI: int
SDL_WINDOW_MOUSE_CAPTURE: int
SDL_WINDOW_ALWAYS_ON_TOP: int
SDL_WINDOW_SKIP_TASKBAR: int
SDL_WINDOW_UTILITY: int
SDL_WINDOW_TOOLTIP: int
SDL_WINDOW_POPUP_MENU: int
SDL_WINDOW_KEYBOARD_GRABBED: int
SDL_WINDOW_VULKAN: int
SDL_WINDOW_METAL: int
SDL_WindowEventID = c_int
SDL_WINDOWEVENT_NONE: int
SDL_WINDOWEVENT_SHOWN: int
SDL_WINDOWEVENT_HIDDEN: int
SDL_WINDOWEVENT_EXPOSED: int
SDL_WINDOWEVENT_MOVED: int
SDL_WINDOWEVENT_RESIZED: int
SDL_WINDOWEVENT_SIZE_CHANGED: int
SDL_WINDOWEVENT_MINIMIZED: int
SDL_WINDOWEVENT_MAXIMIZED: int
SDL_WINDOWEVENT_RESTORED: int
SDL_WINDOWEVENT_ENTER: int
SDL_WINDOWEVENT_LEAVE: int
SDL_WINDOWEVENT_FOCUS_GAINED: int
SDL_WINDOWEVENT_FOCUS_LOST: int
SDL_WINDOWEVENT_CLOSE: int
SDL_WINDOWEVENT_TAKE_FOCUS: int
SDL_WINDOWEVENT_HIT_TEST: int
SDL_WINDOWEVENT_ICCPROF_CHANGED: int
SDL_WINDOWEVENT_DISPLAY_CHANGED: int
SDL_DisplayEventID = c_int
SDL_DISPLAYEVENT_NONE: int
SDL_DISPLAYEVENT_ORIENTATION: int
SDL_DISPLAYEVENT_CONNECTED: int
SDL_DISPLAYEVENT_DISCONNECTED: int
SDL_DISPLAYEVENT_MOVED: int
SDL_DisplayOrientation = c_int
SDL_ORIENTATION_UNKNOWN: int
SDL_ORIENTATION_LANDSCAPE: int
SDL_ORIENTATION_LANDSCAPE_FLIPPED: int
SDL_ORIENTATION_PORTRAIT: int
SDL_ORIENTATION_PORTRAIT_FLIPPED: int
SDL_FlashOperation = c_int
SDL_FLASH_CANCEL: int
SDL_FLASH_BRIEFLY: int
SDL_FLASH_UNTIL_FOCUSED: int
SDL_GLattr = c_int
SDL_GL_RED_SIZE: int
SDL_GL_GREEN_SIZE: int
SDL_GL_BLUE_SIZE: int
SDL_GL_ALPHA_SIZE: int
SDL_GL_BUFFER_SIZE: int
SDL_GL_DOUBLEBUFFER: int
SDL_GL_DEPTH_SIZE: int
SDL_GL_STENCIL_SIZE: int
SDL_GL_ACCUM_RED_SIZE: int
SDL_GL_ACCUM_GREEN_SIZE: int
SDL_GL_ACCUM_BLUE_SIZE: int
SDL_GL_ACCUM_ALPHA_SIZE: int
SDL_GL_STEREO: int
SDL_GL_MULTISAMPLEBUFFERS: int
SDL_GL_MULTISAMPLESAMPLES: int
SDL_GL_ACCELERATED_VISUAL: int
SDL_GL_RETAINED_BACKING: int
SDL_GL_CONTEXT_MAJOR_VERSION: int
SDL_GL_CONTEXT_MINOR_VERSION: int
SDL_GL_CONTEXT_EGL: int
SDL_GL_CONTEXT_FLAGS: int
SDL_GL_CONTEXT_PROFILE_MASK: int
SDL_GL_SHARE_WITH_CURRENT_CONTEXT: int
SDL_GL_FRAMEBUFFER_SRGB_CAPABLE: int
SDL_GL_CONTEXT_RELEASE_BEHAVIOR: int
SDL_GL_CONTEXT_RESET_NOTIFICATION: int
SDL_GL_CONTEXT_NO_ERROR: int
SDL_GL_FLOATBUFFERS: int
SDL_GLprofile = c_int
SDL_GL_CONTEXT_PROFILE_CORE: int
SDL_GL_CONTEXT_PROFILE_COMPATIBILITY: int
SDL_GL_CONTEXT_PROFILE_ES: int
SDL_GLcontextFlag = c_int
SDL_GL_CONTEXT_DEBUG_FLAG: int
SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG: int
SDL_GL_CONTEXT_ROBUST_ACCESS_FLAG: int
SDL_GL_CONTEXT_RESET_ISOLATION_FLAG: int
SDL_GLcontextReleaseFlag = c_int
SDL_GL_CONTEXT_RELEASE_BEHAVIOR_NONE: int
SDL_GL_CONTEXT_RELEASE_BEHAVIOR_FLUSH: int
SDL_GLContextResetNotification = c_int
SDL_GL_CONTEXT_RESET_NO_NOTIFICATION: int
SDL_GL_CONTEXT_RESET_LOSE_CONTEXT: int
SDL_HitTestResult = c_int
SDL_HITTEST_NORMAL: int
SDL_HITTEST_DRAGGABLE: int
SDL_HITTEST_RESIZE_TOPLEFT: int
SDL_HITTEST_RESIZE_TOP: int
SDL_HITTEST_RESIZE_TOPRIGHT: int
SDL_HITTEST_RESIZE_RIGHT: int
SDL_HITTEST_RESIZE_BOTTOMRIGHT: int
SDL_HITTEST_RESIZE_BOTTOM: int
SDL_HITTEST_RESIZE_BOTTOMLEFT: int
SDL_HITTEST_RESIZE_LEFT: int
SDL_WINDOWPOS_UNDEFINED_MASK: int

def SDL_WINDOWPOS_UNDEFINED_DISPLAY(x: int, /) -> int: ...

SDL_WINDOWPOS_UNDEFINED: int

def SDL_WINDOWPOS_ISUNDEFINED(x: int, /) -> bool: ...

SDL_WINDOWPOS_CENTERED_MASK: int

def SDL_WINDOWPOS_CENTERED_DISPLAY(x: int, /) -> int: ...

SDL_WINDOWPOS_CENTERED: int

def SDL_WINDOWPOS_ISCENTERED(x: int, /) -> bool: ...

SDL_GLContext = c_void_p

class SDL_Window(c_void_p): ...

class SDL_DisplayMode(Structure):
    format: int
    w: int
    h: int
    refresh_rate: int
    driverdata: int | None
    def __init__(self, format_: int = 0, w: int = 0, h: int = 0, refresh_rate: int = 0) -> None: ...
    def __eq__(self, mode: object) -> bool: ...
    def __ne__(self, mode: object) -> bool: ...

SDL_HitTest: type[_CFuncPtr]

def SDL_GetNumVideoDrivers() -> int: ...
def SDL_GetVideoDriver(index: int, /) -> bytes | None: ...
def SDL_VideoInit(driver_name: bytes | None, /) -> int: ...
def SDL_VideoQuit() -> None: ...
def SDL_GetCurrentVideoDriver() -> bytes | None: ...
def SDL_GetNumVideoDisplays() -> int: ...
def SDL_GetDisplayName(displayIndex: int, /) -> bytes | None: ...
def SDL_GetDisplayBounds(displayIndex: int, rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_GetDisplayUsableBounds(displayIndex: int, rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_GetDisplayDPI(
    displayIndex: int, ddpi: _Pointer[c_float], hdpi: _Pointer[c_float], vdpi: _Pointer[c_float], /
) -> int: ...
def SDL_GetDisplayOrientation(displayIndex: int, /) -> int: ...
def SDL_GetNumDisplayModes(displayIndex: int, /) -> int: ...
def SDL_GetDisplayMode(displayIndex: int, modeIndex: int, mode: _Pointer[SDL_DisplayMode], /) -> int: ...
def SDL_GetDesktopDisplayMode(displayIndex: int, mode: _Pointer[SDL_DisplayMode], /) -> int: ...
def SDL_GetCurrentDisplayMode(displayIndex: int, mode: _Pointer[SDL_DisplayMode], /) -> int: ...
def SDL_GetClosestDisplayMode(
    displayIndex: int, mode: _Pointer[SDL_DisplayMode], closest: _Pointer[SDL_DisplayMode], /
) -> _Pointer[SDL_DisplayMode]: ...
def SDL_GetPointDisplayIndex(point: _Pointer[SDL_Point], /) -> int: ...
def SDL_GetRectDisplayIndex(rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_GetWindowDisplayIndex(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_SetWindowDisplayMode(window: _Pointer[SDL_Window], mode: _Pointer[SDL_DisplayMode], /) -> int: ...
def SDL_GetWindowDisplayMode(window: _Pointer[SDL_Window], mode: _Pointer[SDL_DisplayMode], /) -> int: ...
def SDL_GetWindowICCProfile(window: _Pointer[SDL_Window], size: _Pointer[c_size_t], /) -> int | None: ...
def SDL_GetWindowPixelFormat(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_CreateWindow(title: bytes | None, x: int, y: int, w: int, h: int, flags: int, /) -> _Pointer[SDL_Window]: ...
def SDL_CreateWindowFrom(data: c_void_p | int | None, /) -> _Pointer[SDL_Window]: ...
def SDL_GetWindowID(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_GetWindowFromID(id: int, /) -> _Pointer[SDL_Window]: ...
def SDL_GetWindowFlags(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_SetWindowTitle(window: _Pointer[SDL_Window], title: bytes | None, /) -> None: ...
def SDL_GetWindowTitle(window: _Pointer[SDL_Window], /) -> bytes | None: ...
def SDL_SetWindowIcon(window: _Pointer[SDL_Window], icon: _Pointer[SDL_Surface], /) -> None: ...
def SDL_SetWindowData(
    window: _Pointer[SDL_Window], name: bytes | None, userdata: _Pointer[py_object], /
) -> _Pointer[py_object]: ...
def SDL_GetWindowData(window: _Pointer[SDL_Window], name: bytes | None, /) -> _Pointer[py_object]: ...
def SDL_SetWindowPosition(window: _Pointer[SDL_Window], x: int, y: int, /) -> None: ...
def SDL_GetWindowPosition(window: _Pointer[SDL_Window], x: _Pointer[c_int], y: _Pointer[c_int], /) -> None: ...
def SDL_SetWindowSize(window: _Pointer[SDL_Window], w: int, h: int, /) -> None: ...
def SDL_GetWindowSize(window: _Pointer[SDL_Window], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
def SDL_GetWindowBordersSize(
    window: _Pointer[SDL_Window],
    top: _Pointer[c_int],
    left: _Pointer[c_int],
    bottom: _Pointer[c_int],
    right: _Pointer[c_int],
    /,
) -> int: ...
def SDL_GetWindowSizeInPixels(window: _Pointer[SDL_Window], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
def SDL_SetWindowMinimumSize(window: _Pointer[SDL_Window], min_w: int, min_h: int, /) -> None: ...
def SDL_GetWindowMinimumSize(window: _Pointer[SDL_Window], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
def SDL_SetWindowMaximumSize(window: _Pointer[SDL_Window], max_w: int, max_h: int, /) -> None: ...
def SDL_GetWindowMaximumSize(window: _Pointer[SDL_Window], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
def SDL_SetWindowBordered(window: _Pointer[SDL_Window], bordered: int, /) -> None: ...
def SDL_SetWindowResizable(window: _Pointer[SDL_Window], resizable: int, /) -> None: ...
def SDL_SetWindowAlwaysOnTop(window: _Pointer[SDL_Window], on_top: int, /) -> None: ...
def SDL_ShowWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_HideWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_RaiseWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_MaximizeWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_MinimizeWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_RestoreWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_SetWindowFullscreen(window: _Pointer[SDL_Window], flags: int, /) -> int: ...
def SDL_HasWindowSurface(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_GetWindowSurface(window: _Pointer[SDL_Window], /) -> _Pointer[SDL_Surface]: ...
def SDL_UpdateWindowSurface(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_UpdateWindowSurfaceRects(window: _Pointer[SDL_Window], rects: _Pointer[SDL_Rect], numrects: int, /) -> int: ...
def SDL_DestroyWindowSurface(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_SetWindowGrab(window: _Pointer[SDL_Window], grabbed: int, /) -> None: ...
def SDL_SetWindowKeyboardGrab(window: _Pointer[SDL_Window], grabbed: int, /) -> None: ...
def SDL_SetWindowMouseGrab(window: _Pointer[SDL_Window], grabbed: int, /) -> None: ...
def SDL_GetWindowGrab(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_GetWindowKeyboardGrab(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_GetWindowMouseGrab(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_GetGrabbedWindow() -> _Pointer[SDL_Window]: ...
def SDL_SetWindowMouseRect(window: _Pointer[SDL_Window], rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_GetWindowMouseRect(window: _Pointer[SDL_Window], /) -> _Pointer[SDL_Rect]: ...
def SDL_SetWindowBrightness(window: _Pointer[SDL_Window], brightness: float, /) -> int: ...
def SDL_GetWindowBrightness(window: _Pointer[SDL_Window], /) -> float: ...
def SDL_GetWindowOpacity(window: _Pointer[SDL_Window], out_opacity: _Pointer[c_float], /) -> int: ...
def SDL_SetWindowOpacity(window: _Pointer[SDL_Window], opacity: float, /) -> int: ...
def SDL_SetWindowModalFor(modal_window: _Pointer[SDL_Window], parent_window: _Pointer[SDL_Window], /) -> int: ...
def SDL_SetWindowInputFocus(window: _Pointer[SDL_Window], /) -> int: ...
def SDL_SetWindowGammaRamp(
    window: _Pointer[SDL_Window],
    red: _Pointer[Uint16],
    green: _Pointer[Uint16],
    blue: _Pointer[Uint16],
    /,
) -> int: ...
def SDL_GetWindowGammaRamp(
    window: _Pointer[SDL_Window],
    red: _Pointer[Uint16],
    green: _Pointer[Uint16],
    blue: _Pointer[Uint16],
    /,
) -> int: ...
def SDL_SetWindowHitTest(
    window: _Pointer[SDL_Window], callback: _CFuncPtr, callback_data: c_void_p | int | None, /
) -> int: ...
def SDL_FlashWindow(window: _Pointer[SDL_Window], operation: int, /) -> int: ...
def SDL_DestroyWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_IsScreenSaverEnabled() -> int: ...
def SDL_EnableScreenSaver() -> None: ...
def SDL_DisableScreenSaver() -> None: ...
def SDL_GL_LoadLibrary(path: bytes | None, /) -> int: ...
def SDL_GL_GetProcAddress(proc: bytes | None, /) -> int | None: ...
def SDL_GL_UnloadLibrary() -> None: ...
def SDL_GL_ExtensionSupported(extension: bytes | None, /) -> int: ...
def SDL_GL_ResetAttributes() -> None: ...
def SDL_GL_SetAttribute(attr: int, value: int, /) -> int: ...
def SDL_GL_GetAttribute(attr: int, value: _Pointer[c_int], /) -> int: ...
def SDL_GL_CreateContext(window: _Pointer[SDL_Window], /) -> int | None: ...
def SDL_GL_MakeCurrent(window: _Pointer[SDL_Window], context: c_void_p | int | None, /) -> int: ...
def SDL_GL_GetCurrentWindow() -> _Pointer[SDL_Window]: ...
def SDL_GL_GetCurrentContext() -> int | None: ...
def SDL_GL_GetDrawableSize(window: _Pointer[SDL_Window], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
def SDL_GL_SetSwapInterval(interval: int, /) -> int: ...
def SDL_GL_GetSwapInterval() -> int: ...
def SDL_GL_SwapWindow(window: _Pointer[SDL_Window], /) -> None: ...
def SDL_GL_DeleteContext(context: c_void_p | int | None, /) -> None: ...
