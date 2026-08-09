#!/usr/bin/env python3
from __future__ import annotations

import os
import sys

# Force GDK backend selection before initializing GTK/GDK modules
session_type = os.environ.get("XDG_SESSION_TYPE", "x11").lower()
if "wayland" in session_type:
    os.environ["GDK_BACKEND"] = "wayland"
else:
    os.environ["GDK_BACKEND"] = "x11"

# We use '# noqa: E402' because these imports must happen after setting GDK_BACKEND
import gi  # noqa: E402  # type: ignore  # pyright: ignore[reportMissingImports]

gi.require_version('Gtk', '3.0')
from gi.repository import GdkPixbuf, Gtk  # noqa: E402  # type: ignore  # pyright: ignore[reportMissingImports]


class StandaloneBezelOverlay(Gtk.Window):
    def __init__(self, image_path: str, width: int, height: int):
        # Force POPUP type on X11 to set override_redirect=True and bypass Openbox's fullscreen layering.
        # Use TOPLEVEL on Wayland since GtkLayerShell handles Wayland's layer stacking natively.
        if "wayland" in session_type:
            super().__init__(type=Gtk.WindowType.TOPLEVEL)
        else:
            super().__init__(type=Gtk.WindowType.POPUP)

        self.image_path = image_path
        self.target_width = width
        self.target_height = height

        # Standard transparent borderless window configurations
        self.set_title("Batocera Bezel Overlay")
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        # Configure the screen for alpha channel (transparency)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        # Use native CSS to force the main GTK window background to be completely transparent
        try:
            css_provider = Gtk.CssProvider()
            css_provider.load_from_data(b"window { background-color: transparent; background-image: none; box-shadow: none; border: none; }")
            self.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except Exception as css_err:
            print(f"Failed to apply transparency CSS: {css_err}", file=sys.stderr)

        # Scale the PNG natively with GdkPixbuf and load it into a Gtk.Image widget
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                image_path,
                width=self.target_width,
                height=self.target_height,
                preserve_aspect_ratio=False
            )
            image_widget = Gtk.Image.new_from_pixbuf(pixbuf)
            self.add(image_widget)
        except Exception as e:
            print(f"Failed to load image via GdkPixbuf: {e}", file=sys.stderr)
            sys.exit(1)

        # Connect realize signal to apply Gdk.Window level click-through when ready
        self.connect("realize", self.on_realize)

        # Adjust positioning based on active display server
        if "wayland" in session_type:
            self.setup_wayland()
        else:
            self.setup_x11()

        self.show_all()

    def on_realize(self, widget):
        print("Window realized. Configuring native input pass-through...", file=sys.stderr)
        gdk_window = self.get_window()
        if gdk_window:
            try:
                gdk_window.set_pass_through(True)
                print("Native Gdk.Window input pass-through configured successfully.", file=sys.stderr)
            except Exception as e:
                print(f"Failed to set Gdk.Window pass-through: {e}", file=sys.stderr)

    def setup_x11(self):
        """Configure override-redirect parameters on X11."""
        print("Initializing X11/Openbox window attributes...", file=sys.stderr)
        self.move(0, 0)
        self.resize(self.target_width, self.target_height)

    def setup_wayland(self):
        """Bind window overlay parameters using GtkLayerShell on Wayland."""
        try:
            gi.require_version('GtkLayerShell', '0.1')
            from gi.repository import GtkLayerShell  # type: ignore  # pyright: ignore[reportMissingImports]

            print("Initializing Wayland Layer Shell layers...", file=sys.stderr)
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
            GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)

            # Stretch overlay across physical screen edges
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        except (ValueError, ImportError) as e:
            print(f"Wayland GtkLayerShell initialization failed: {e}. Falling back to standard positioning.", file=sys.stderr)
            self.resize(self.target_width, self.target_height)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: bezelOverlay.py <image_path> <width> <height>")
        sys.exit(1)

    Gtk.init(sys.argv)
    overlay = StandaloneBezelOverlay(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    Gtk.main()
