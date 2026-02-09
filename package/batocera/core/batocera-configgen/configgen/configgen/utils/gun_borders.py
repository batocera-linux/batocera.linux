from __future__ import annotations

import ctypes.util
import math
from typing import Final, cast


class _XSetWindowAttributes(ctypes.Structure):
    _fields_ = [
        ("background_pixmap", ctypes.c_ulong),
        ("background_pixel", ctypes.c_ulong),
        ("border_pixmap", ctypes.c_ulong),
        ("border_pixel", ctypes.c_ulong),
        ("bit_gravity", ctypes.c_int),
        ("win_gravity", ctypes.c_int),
        ("backing_store", ctypes.c_int),
        ("backing_planes", ctypes.c_ulong),
        ("backing_pixel", ctypes.c_ulong),
        ("save_under", ctypes.c_int),
        ("event_mask", ctypes.c_long),
        ("do_not_propagate_mask", ctypes.c_long),
        ("override_redirect", ctypes.c_int),
        ("colormap", ctypes.c_ulong),
        ("cursor", ctypes.c_ulong),
    ]

_libX11    = ctypes.cdll.LoadLibrary(cast('str', ctypes.util.find_library("X11")))
_libXfixes = ctypes.cdll.LoadLibrary(cast('str', ctypes.util.find_library("Xfixes")))

# X11 function signatures
_void_p = ctypes.c_void_p
_ulong = ctypes.c_ulong
_int_t = ctypes.c_int
_uint_t = ctypes.c_uint

_libX11.XOpenDisplay.restype = _void_p
_libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
_libX11.XDefaultScreen.restype = _int_t
_libX11.XDefaultScreen.argtypes = [_void_p]
_libX11.XRootWindow.restype = _ulong
_libX11.XRootWindow.argtypes = [_void_p, _int_t]
_libX11.XDisplayWidth.restype = _int_t
_libX11.XDisplayWidth.argtypes = [_void_p, _int_t]
_libX11.XDisplayHeight.restype = _int_t
_libX11.XDisplayHeight.argtypes = [_void_p, _int_t]
_libX11.XCreateWindow.restype = _ulong
_libX11.XCreateWindow.argtypes = [_void_p, _ulong, _int_t, _int_t, _uint_t, _uint_t, _uint_t, _int_t, _uint_t, _void_p, _ulong, ctypes.POINTER(_XSetWindowAttributes)]
_libX11.XMapRaised.argtypes = [_void_p, _ulong]
_libX11.XFlush.argtypes = [_void_p]
_libX11.XCloseDisplay.argtypes = [_void_p]

_libXfixes.XFixesCreateRegion.restype = _ulong
_libXfixes.XFixesCreateRegion.argtypes = [_void_p, _void_p, _int_t]
_libXfixes.XFixesSetWindowShapeRegion.argtypes = [_void_p, _ulong, _int_t, _int_t, _int_t, _ulong]
_libXfixes.XFixesDestroyRegion.argtypes = [_void_p, _ulong]

_BORDER_COLORS: Final = {
    "white": 0xFFFFFF,
    "red":   0xFF0000,
    "green": 0x00FF00,
    "blue":  0x0000FF,
}

_BORDER_PRESETS: Final = {
    "thin":   (1, 0),
    "medium": (2, 0),
    "big":    (2, 1),
}

def _create_click_through_rectangle(display: ctypes._Pointer, root_window: int, x: int, y: int, width: int, height: int, color: int, /) -> None:
    if width <= 0 or height <= 0:
        return

    CW_BACK_PIXEL = 1 << 1
    CW_OVERRIDE_REDIRECT = 1 << 9
    SHAPE_INPUT = 2

    attributes = _XSetWindowAttributes()
    attributes.background_pixel = color
    attributes.override_redirect = 1

    window = _libX11.XCreateWindow(
        display, root_window, x, y, width, height,
        0, 0, 1, None,
        CW_BACK_PIXEL | CW_OVERRIDE_REDIRECT,
        ctypes.byref(attributes)
    )

    empty_region: int = _libXfixes.XFixesCreateRegion(display, None, 0)
    _libXfixes.XFixesSetWindowShapeRegion(display, window, SHAPE_INPUT, 0, 0, empty_region)
    _libXfixes.XFixesDestroyRegion(display, empty_region)

    _libX11.XMapRaised(display, window)

def _draw_border_ring(display: ctypes._Pointer, root_window: int, offset_x: int, offset_y: int, width: int, height: int, thickness: int, color: int, /) -> None:
    if thickness <= 0:
        return

    _create_click_through_rectangle(display, root_window, offset_x, offset_y, width, thickness, color)
    _create_click_through_rectangle(display, root_window, offset_x, offset_y + height - thickness, width, thickness, color)
    _create_click_through_rectangle(display, root_window, offset_x, offset_y + thickness, thickness, height - 2 * thickness, color)
    _create_click_through_rectangle(display, root_window, offset_x + width - thickness, offset_y + thickness, thickness, height - 2 * thickness, color)

def draw_gun_borders(border_size: str, border_color: str, border_ratio: str | None, /) -> None:
    inner_percent, outer_percent = _BORDER_PRESETS.get(border_size, (2, 0))

    display = _libX11.XOpenDisplay(None)
    if not display:
        raise Exception("Cannot open display")

    screen: int        = _libX11.XDefaultScreen(display)
    root_window: int   = _libX11.XRootWindow(display, screen)
    screen_width: int  = _libX11.XDisplayWidth(display, screen)
    screen_height: int = _libX11.XDisplayHeight(display, screen)

    region_width = screen_width
    region_offset_x = 0

    if border_ratio == "4:3":
        region_width = min(int(screen_height / 3 * 4), screen_width)
        region_offset_x = (screen_width - region_width) // 2

    outer_thickness = math.ceil(screen_width * outer_percent / 100)
    inner_thickness = max(math.ceil(screen_width * inner_percent / 100), 1)

    # outer
    _draw_border_ring(display, root_window,
        region_offset_x, 0,
        region_width, screen_height,
        outer_thickness, 0x000000)

    # inner
    _draw_border_ring(display, root_window,
        region_offset_x + outer_thickness, outer_thickness,
        region_width - 2 * outer_thickness, screen_height - 2 * outer_thickness,
        inner_thickness, _BORDER_COLORS.get(border_color, 0xFFFFFF))

    _libX11.XFlush(display)

if __name__ == "__main__":
    import signal
    import sys

    border_size = "medium"
    border_color = "white"
    border_ratio = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("-s", "--size") and i + 1 < len(args):
            border_size = args[i + 1]
            i += 2
        elif args[i] in ("-c", "--color") and i + 1 < len(args):
            border_color = args[i + 1]
            i += 2
        elif args[i] in ("-r", "--ratio") and i + 1 < len(args):
            border_ratio = args[i + 1]
            i += 2
        else:
            i += 1

    draw_gun_borders(border_size, border_color, border_ratio)

    while True:
        signal.pause()
