from __future__ import annotations

import ctypes.util
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, cast

from batocera_launch.dataclasses import cached_dataclass
from batocera_launch.functools import cached_property

if TYPE_CHECKING:
    from collections.abc import Generator


class _XSetWindowAttributes(ctypes.Structure):
    _fields_ = [
        ('background_pixmap', ctypes.c_ulong),
        ('background_pixel', ctypes.c_ulong),
        ('border_pixmap', ctypes.c_ulong),
        ('border_pixel', ctypes.c_ulong),
        ('bit_gravity', ctypes.c_int),
        ('win_gravity', ctypes.c_int),
        ('backing_store', ctypes.c_int),
        ('backing_planes', ctypes.c_ulong),
        ('backing_pixel', ctypes.c_ulong),
        ('save_under', ctypes.c_int),
        ('event_mask', ctypes.c_long),
        ('do_not_propagate_mask', ctypes.c_long),
        ('override_redirect', ctypes.c_int),
        ('colormap', ctypes.c_ulong),
        ('cursor', ctypes.c_ulong),
    ]


_libX11 = ctypes.cdll.LoadLibrary(cast('str', ctypes.util.find_library('X11')))
_libXfixes = ctypes.cdll.LoadLibrary(cast('str', ctypes.util.find_library('Xfixes')))

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
_libX11.XCreateWindow.argtypes = [
    _void_p,
    _ulong,
    _int_t,
    _int_t,
    _uint_t,
    _uint_t,
    _uint_t,
    _int_t,
    _uint_t,
    _void_p,
    _ulong,
    ctypes.POINTER(_XSetWindowAttributes),
]
_libX11.XMapRaised.argtypes = [_void_p, _ulong]
_libX11.XFlush.argtypes = [_void_p]
_libX11.XCloseDisplay.argtypes = [_void_p]

_libXfixes.XFixesCreateRegion.restype = _ulong
_libXfixes.XFixesCreateRegion.argtypes = [_void_p, _void_p, _int_t]
_libXfixes.XFixesSetWindowShapeRegion.argtypes = [_void_p, _ulong, _int_t, _int_t, _int_t, _ulong]
_libXfixes.XFixesDestroyRegion.argtypes = [_void_p, _ulong]


@cached_dataclass
class Display:
    display: ctypes._Pointer[Any]

    @cached_property
    def screen(self) -> int:
        return _libX11.XDefaultScreen(self.display)  # type: ignore[no-any-return]

    @cached_property
    def root_window(self) -> int:
        return _libX11.XRootWindow(self.display, self.screen)  # type: ignore[no-any-return]

    @cached_property
    def screen_width(self) -> int:
        return _libX11.XDisplayWidth(self.display, self.screen)  # type: ignore[no-any-return]

    @cached_property
    def screen_height(self) -> int:
        return _libX11.XDisplayHeight(self.display, self.screen)  # type: ignore[no-any-return]

    def draw_border(self, offset_x: int, offset_y: int, width: int, height: int, thickness: int, color: int, /) -> None:
        if thickness <= 0:
            return

        self.__create_click_through_rectangle(offset_x, offset_y, width, thickness, color)
        self.__create_click_through_rectangle(offset_x, offset_y + height - thickness, width, thickness, color)
        self.__create_click_through_rectangle(offset_x, offset_y + thickness, thickness, height - 2 * thickness, color)
        self.__create_click_through_rectangle(
            offset_x + width - thickness,
            offset_y + thickness,
            thickness,
            height - 2 * thickness,
            color,
        )

    def __create_click_through_rectangle(self, x: int, y: int, width: int, height: int, color: int, /) -> None:
        if width <= 0 or height <= 0:
            return

        CW_BACK_PIXEL = 1 << 1
        CW_OVERRIDE_REDIRECT = 1 << 9
        SHAPE_INPUT = 2

        attributes = _XSetWindowAttributes()
        attributes.background_pixel = color
        attributes.override_redirect = 1

        window = _libX11.XCreateWindow(
            self.display,
            self.root_window,
            x,
            y,
            width,
            height,
            0,
            0,
            1,
            None,
            CW_BACK_PIXEL | CW_OVERRIDE_REDIRECT,
            ctypes.byref(attributes),
        )

        empty_region: int = _libXfixes.XFixesCreateRegion(self.display, None, 0)
        _libXfixes.XFixesSetWindowShapeRegion(self.display, window, SHAPE_INPUT, 0, 0, empty_region)
        _libXfixes.XFixesDestroyRegion(self.display, empty_region)

        _libX11.XMapRaised(self.display, window)


@contextmanager
def open_display() -> Generator[Display]:
    x11_display = _libX11.XOpenDisplay(None)

    if not x11_display:
        raise Exception('Cannot open display')

    try:
        yield Display(display=x11_display)
    finally:
        _libX11.XFlush(x11_display)
