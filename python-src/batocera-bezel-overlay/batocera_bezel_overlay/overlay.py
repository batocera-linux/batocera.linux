from __future__ import annotations

import logging
import sys
from typing import ClassVar

import gi

try:
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('Gtk', '3.0')

    from gi.repository import GdkPixbuf, Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


_log = logging.getLogger(__name__)


class Overlay(Gtk.Window):
    __gtype_name__ = 'Overlay'

    window_type: ClassVar[Gtk.WindowType]

    def __init__(self, image_path: str, dimensions: tuple[int, int], /) -> None:
        # Force POPUP type on X11 to set override_redirect=True and bypass Openbox's fullscreen layering.
        # Use TOPLEVEL on Wayland since GtkLayerShell handles Wayland's layer stacking natively.

        super().__init__(
            type=self.window_type,
            # Standard transparent borderless window configurations
            title='Batocera Bezel Overlay',
            decorated=False,
            skip_taskbar_hint=True,
            skip_pager_hint=True,
        )

        self.set_keep_above(True)

        # Configure the screen for alpha channel (transparency)
        if visual := self.get_screen().get_rgba_visual():
            self.set_visual(visual)

        # Use native CSS to force the main GTK window background to be completely transparent
        try:
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(
                b'window { background-color: transparent; background-image: none; box-shadow: none; border: none; }'
            )
            self.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except Exception:
            _log.exception('Failed to apply transparency CSS')

        try:
            # Scale the PNG natively with GdkPixbuf
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(image_path, *dimensions, preserve_aspect_ratio=False)
        except Exception as e:
            _log.exception('Failed to load image via GdkPixbuf')
            raise e

        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.add(image)

        self.setup(dimensions)
        self.show_all()

    def setup(self, dimensions: tuple[int, int], /) -> None:
        raise NotImplementedError('Subclasses must implement setup()')

    def do_realize(self) -> None:
        # Apply Gdk.Window level click-through when ready
        Gtk.Window.do_realize(self)

        _log.debug('Window realized. Configuring native input pass-through...')
        if gdk_window := self.get_window():
            try:
                gdk_window.set_pass_through(True)
                _log.debug('Native Gdk.Window input pass-through configured successfully.')
            except Exception:
                _log.exception('Failed to set Gdk.Window pass-through')


class X11Overlay(Overlay):
    """Specialized Overlay for X11/Openbox environments."""

    __gtype_name__ = 'X11Overlay'

    window_type: ClassVar[Gtk.WindowType] = Gtk.WindowType.POPUP

    def setup(self, dimensions: tuple[int, int], /) -> None:
        """Configure override-redirect parameters on X11."""
        _log.debug('Initializing X11/Openbox window attributes...')

        self.move(0, 0)
        self.resize(*dimensions)


class WaylandOverlay(Overlay):
    """Specialized Overlay for Wayland environments using GtkLayerShell."""

    __gtype_name__ = 'WaylandOverlay'

    window_type: ClassVar[Gtk.WindowType] = Gtk.WindowType.TOPLEVEL

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
