from __future__ import annotations

import ctypes.util
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntFlag
from typing import TYPE_CHECKING, Any, cast

from batocera_common.dataclasses import cached_dataclass, cached_property

if TYPE_CHECKING:
    from collections.abc import Generator


class XSetWindowAttributes(ctypes.Structure):
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
    ctypes.POINTER(XSetWindowAttributes),
]
_libX11.XMapRaised.argtypes = [_void_p, _ulong]
_libX11.XFlush.argtypes = [_void_p]
_libX11.XCloseDisplay.argtypes = [_void_p]

_libXfixes.XFixesCreateRegion.restype = _ulong
_libXfixes.XFixesCreateRegion.argtypes = [_void_p, _void_p, _int_t]
_libXfixes.XFixesSetWindowShapeRegion.argtypes = [_void_p, _ulong, _int_t, _int_t, _int_t, _ulong]
_libXfixes.XFixesDestroyRegion.argtypes = [_void_p, _ulong]


class WindowAttributes(IntFlag):
    back_pixmap = 1 << 0
    back_pixel = 1 << 1
    border_pixmap = 1 << 2
    border_pixel = 1 << 3
    bit_gravity = 1 << 4
    win_gravity = 1 << 5
    backing_store = 1 << 6
    backing_planes = 1 << 7
    backing_pixel = 1 << 8
    ovrride_redirect = 1 << 9
    save_under = 1 << 10
    event_mask = 1 << 11
    dont_propagate = 1 << 12
    colormap = 1 << 13
    cursor = 1 << 14


class ShapeKind(IntFlag):
    bounding = 0
    clip = 1
    input = 2


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

    def create_window(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        /,
        *,
        border_width: int = 0,
        depth: int = 0,
        window_class: int = 1,
        attributes_mask: WindowAttributes | None = None,
        attributes: XSetWindowAttributes | None = None,
    ) -> Window:
        window = _libX11.XCreateWindow(
            self.display,
            self.root_window,
            x,
            y,
            width,
            height,
            border_width,
            depth,
            window_class,
            None,
            0 if attributes_mask is None else attributes_mask.real,
            None if attributes is None else ctypes.byref(attributes),
        )

        return Window(window=window, display=self)

    def create_empty_region(self) -> int:
        return _libXfixes.XFixesCreateRegion(self.display, None, 0)

    def destroy_region(self, region: int, /) -> None:
        _libXfixes.XFixesDestroyRegion(self.display, region)


@dataclass(slots=True)
class Window:
    window: ctypes._Pointer[Any]
    display: Display

    def set_window_shape_region(self, kind: ShapeKind, x: int, y: int, region: int, /) -> None:
        _libXfixes.XFixesSetWindowShapeRegion(self.display.display, self.window, kind.real, x, y, region)

    def map_raised(self) -> None:
        _libX11.XMapRaised(self.display.display, self.window)


@contextmanager
def open_display() -> Generator[Display]:
    x11_display = _libX11.XOpenDisplay(None)

    if not x11_display:
        raise Exception('Cannot open display')

    try:
        yield Display(display=x11_display)
    finally:
        _libX11.XFlush(x11_display)
