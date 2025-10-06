#!/usr/bin/env python3
#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025 lbrpdx for the Batocera team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
import os
import sys
import time
os.environ.setdefault("NO_AT_BRIDGE", "1")
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

def ensure_display():
    # Ensures we're running inside a GUI session (Wayland or X11).
    # Wayland compositors set WAYLAND_DISPLAY; X11 sets DISPLAY
    if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY"):
        return True
    return False

def gtk_init_check():
    try:
        # Gtk.init_check returns (initialized: bool, argv: list) in PyGObject
        ok, _ = Gtk.init_check(sys.argv)
        return bool(ok)
    except Exception:
        return False

def flash(duration_seconds: float = 0.1, color: str = "#ffffff"):
    # Show a fullscreen window filled with `color` for `duration_seconds`
    if not ensure_display():
        raise RuntimeError(
                "ERROR: No GUI display detected. Set DISPLAY (X11) or WAYLAND_DISPLAY (Wayland)."
        )

    if not gtk_init_check():
        raise RuntimeError(
                "ERROR: Gtk couldn't be initialized."
        )

    # Create the fullscreen borderless window
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_title("Screenshot taken")
    win.set_decorated(False)
    win.set_app_paintable(True)
    win.fullscreen()
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_hexpand(True)
    box.set_vexpand(True)
    win.add(box)
    css = Gtk.CssProvider()
    css.load_from_data(f"""
    window, box {{
        background-color: {color};
    }}
    """.encode("utf-8"))
    screen = Gdk.Screen.get_default()
    Gtk.StyleContext.add_provider_for_screen(
        screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    # Close on any key or mouse to avoid getting stuck
    def close(_w, *_a):
        Gtk.main_quit()
    win.connect("key-press-event", close)
    win.connect("button-press-event", close)
    win.show_all()
    start = time.monotonic()
    while time.monotonic() - start < duration_seconds:
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        time.sleep(0.004)
    Gtk.main_quit()

def parse_args():
    # Arguments: duration and color
    duration = 0.1
    color = "#ffffff"
    if len(sys.argv) >= 2:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            pass
    if len(sys.argv) >= 3:
        color = sys.argv[2]
    return duration, color

if __name__ == "__main__":
    dur, col = parse_args()
    try:
        flash(dur, col)
    except RuntimeError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)

