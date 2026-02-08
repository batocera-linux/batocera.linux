#!/usr/bin/env python3
#
# batocera-borders - X11 border overlay for Sinden lightgun calibration
#

import ctypes
import ctypes.util
import math

class GunBorders:

    BORDER_COLORS = {
        "white": 0xFFFFFF,
        "red":   0xFF0000,
        "green": 0x00FF00,
        "blue":  0x0000FF,
    }

    BORDER_PRESETS = {
        "thin":   (1, 0),
        "medium": (2, 0),
        "big":    (2, 1),
    }

    class XSetWindowAttributes(ctypes.Structure):
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
        
    libX11    = ctypes.cdll.LoadLibrary(ctypes.util.find_library("X11"))
    libXfixes = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Xfixes"))

    # X11 function signatures
    void_p = ctypes.c_void_p
    ulong = ctypes.c_ulong
    int_t = ctypes.c_int
    uint_t = ctypes.c_uint

    libX11.XOpenDisplay.restype = void_p
    libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    libX11.XDefaultScreen.restype = int_t
    libX11.XDefaultScreen.argtypes = [void_p]
    libX11.XRootWindow.restype = ulong
    libX11.XRootWindow.argtypes = [void_p, int_t]
    libX11.XDisplayWidth.restype = int_t
    libX11.XDisplayWidth.argtypes = [void_p, int_t]
    libX11.XDisplayHeight.restype = int_t
    libX11.XDisplayHeight.argtypes = [void_p, int_t]
    libX11.XCreateWindow.restype = ulong
    libX11.XCreateWindow.argtypes = [void_p, ulong, int_t, int_t, uint_t, uint_t, uint_t, int_t, uint_t, void_p, ulong, ctypes.POINTER(XSetWindowAttributes)]
    libX11.XMapRaised.argtypes = [void_p, ulong]
    libX11.XFlush.argtypes = [void_p]
    libX11.XCloseDisplay.argtypes = [void_p]

    libXfixes.XFixesCreateRegion.restype = ulong
    libXfixes.XFixesCreateRegion.argtypes = [void_p, void_p, int_t]
    libXfixes.XFixesSetWindowShapeRegion.argtypes = [void_p, ulong, int_t, int_t, int_t, ulong]
    libXfixes.XFixesDestroyRegion.argtypes = [void_p, ulong]

    @staticmethod
    def create_click_through_rectangle(display, root_window, x, y, width, height, color):
        if width <= 0 or height <= 0:
            return

        CW_BACK_PIXEL = 1 << 1
        CW_OVERRIDE_REDIRECT = 1 << 9
        SHAPE_INPUT = 2
    
        attributes = GunBorders.XSetWindowAttributes()
        attributes.background_pixel = color
        attributes.override_redirect = 1
    
        window = GunBorders.libX11.XCreateWindow(
            display, root_window, x, y, width, height,
            0, 0, 1, None,
            CW_BACK_PIXEL | CW_OVERRIDE_REDIRECT,
            ctypes.byref(attributes)
        )
    
        empty_region = GunBorders.libXfixes.XFixesCreateRegion(display, None, 0)
        GunBorders.libXfixes.XFixesSetWindowShapeRegion(display, window, SHAPE_INPUT, 0, 0, empty_region)
        GunBorders.libXfixes.XFixesDestroyRegion(display, empty_region)
    
        GunBorders.libX11.XMapRaised(display, window)

    @staticmethod
    def draw_border_ring(display, root_window, offset_x, offset_y, width, height, thickness, color):
        if thickness <= 0:
            return
        GunBorders.create_click_through_rectangle(display, root_window, offset_x, offset_y, width, thickness, color)
        GunBorders.create_click_through_rectangle(display, root_window, offset_x, offset_y + height - thickness, width, thickness, color)
        GunBorders.create_click_through_rectangle(display, root_window, offset_x, offset_y + thickness, thickness, height - 2 * thickness, color)
        GunBorders.create_click_through_rectangle(display, root_window, offset_x + width - thickness, offset_y + thickness, thickness, height - 2 * thickness, color)

    @staticmethod
    def draw_borders(border_size, border_color, border_ratio):
        inner_percent, outer_percent = GunBorders.BORDER_PRESETS.get(border_size, (2, 0))
    
        display = GunBorders.libX11.XOpenDisplay(None)
        if not display:
            raise Exception("Cannot open display")
    
        screen        = GunBorders.libX11.XDefaultScreen(display)
        root_window   = GunBorders.libX11.XRootWindow(display, screen)
        screen_width  = GunBorders.libX11.XDisplayWidth(display, screen)
        screen_height = GunBorders.libX11.XDisplayHeight(display, screen)
    
        region_width = screen_width
        region_offset_x = 0
    
        if border_ratio == "4:3":
            region_width = min(int(screen_height / 3 * 4), screen_width)
            region_offset_x = (screen_width - region_width) // 2
    
        outer_thickness = math.ceil(screen_width * outer_percent / 100)
        inner_thickness = max(math.ceil(screen_width * inner_percent / 100), 1)
    
        # outer
        GunBorders.draw_border_ring(display, root_window,
            region_offset_x, 0,
            region_width, screen_height,
            outer_thickness, 0x000000)
    
        # inner
        GunBorders.draw_border_ring(display, root_window,
            region_offset_x + outer_thickness, outer_thickness,
            region_width - 2 * outer_thickness, screen_height - 2 * outer_thickness,
            inner_thickness, GunBorders.BORDER_COLORS.get(border_color, 0xFFFFFF))
    
        GunBorders.libX11.XFlush(display)

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
    
    GunBorders.draw_borders(border_size, border_color, border_ratio)
    while True:
        signal.pause()
