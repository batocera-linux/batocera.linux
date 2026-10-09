from __future__ import annotations

import ctypes
import logging
import sys
from typing import Any, ClassVar, cast

import gi

from batocera_bezel_overlay.overlay import Overlay

try:
    gi.require_version('Gtk', '3.0')

    from gi.repository import GLib, Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)

_log = logging.getLogger(__name__)


class WaylandOverlay(Overlay):
    """Specialized Overlay for Wayland environments using GtkLayerShell."""

    __gtype_name__ = 'WaylandOverlay'

    window_type: ClassVar[Gtk.WindowType] = Gtk.WindowType.TOPLEVEL

    def _apply_input_passthrough(self) -> bool:
        """Make the mapped layer surface ignore pointer and touch input."""
        # Buildroot disables PyCairo support in python-gobject, so Cairo regions
        # cannot be passed through GI. Call the native GDK/Cairo APIs directly.
        try:
            gdk_window = self.get_window()
            if gdk_window is None:
                _log.error('Wayland input pass-through: no Gdk.Window available')
                return False

            capsule = cast('Any', gdk_window).__gpointer__

            pyapi = ctypes.pythonapi
            pyapi.PyCapsule_GetName.argtypes = [ctypes.py_object]
            pyapi.PyCapsule_GetName.restype = ctypes.c_char_p
            pyapi.PyCapsule_GetPointer.argtypes = [
                ctypes.py_object,
                ctypes.c_char_p,
            ]
            pyapi.PyCapsule_GetPointer.restype = ctypes.c_void_p

            capsule_name = pyapi.PyCapsule_GetName(capsule)
            gdk_ptr = pyapi.PyCapsule_GetPointer(capsule, capsule_name)

            libcairo = ctypes.CDLL('libcairo.so.2')
            libgdk = ctypes.CDLL('libgdk-3.so.0')

            libcairo.cairo_region_create.argtypes = []
            libcairo.cairo_region_create.restype = ctypes.c_void_p
            libcairo.cairo_region_destroy.argtypes = [ctypes.c_void_p]
            libcairo.cairo_region_destroy.restype = None

            libgdk.gdk_window_input_shape_combine_region.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int,
                ctypes.c_int,
            ]
            libgdk.gdk_window_input_shape_combine_region.restype = None

            libgdk.gdk_window_invalidate_rect.argtypes = [
                ctypes.c_void_p,
                ctypes.c_void_p,
                ctypes.c_int,
            ]
            libgdk.gdk_window_invalidate_rect.restype = None

            region = libcairo.cairo_region_create()
            try:
                libgdk.gdk_window_input_shape_combine_region(
                    gdk_ptr,
                    region,
                    0,
                    0,
                )
                libgdk.gdk_window_invalidate_rect(
                    gdk_ptr,
                    None,
                    0,
                )
            finally:
                libcairo.cairo_region_destroy(region)

            _log.debug('Wayland input pass-through configured successfully.')
        except Exception:
            _log.exception('Failed to configure Wayland input pass-through')

        # GLib.idle_add expects False to remove the callback.
        return False

    def do_map(self) -> None:
        Gtk.Window.do_map(self)

        # GtkLayerShell configures the wl_surface during mapping. Applying the
        # empty input region afterwards prevents it from being overwritten.
        GLib.idle_add(self._apply_input_passthrough)

    def setup(self, dimensions: tuple[int, int], /) -> None:
        """Bind window overlay parameters using GtkLayerShell on Wayland."""

        try:
            from batocera_bezel_overlay.layer_shell import GtkLayerShell

            _log.debug('Initializing Wayland Layer Shell layers...')

            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
            GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)

            # Stretch overlay across physical screen edges
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        except ValueError, ImportError:
            _log.exception(
                'Wayland GtkLayerShell initialization failed. Falling back to standard positioning.',
            )
            self.resize(*dimensions)
