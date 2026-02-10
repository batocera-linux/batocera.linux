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
import gi
os.environ.setdefault("NO_AT_BRIDGE", "1")
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, Pango, GLib

WINDOW_TITLE_FLASH = "Batocera flash"
WINDOW_TITLE_OSD = "Batocera OSD"

def ensure_display():
    return bool(os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY"))

def gtk_init_check():
    try:
        ok, _ = Gtk.init_check(sys.argv)
        return bool(ok)
    except Exception:
        return False

def build_fullscreen_flash(color: str) -> Gtk.Window:
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_title(WINDOW_TITLE_FLASH)
    win.set_decorated(False)
    win.set_app_paintable(True)
    win.fullscreen()

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_hexpand(True)
    box.set_vexpand(True)
    win.add(box)

    css = Gtk.CssProvider()
    css.load_from_data(f"window, box {{ background-color: {color}; }}".encode("utf-8"))
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def close(_w, *_a):
        try: win.destroy()
        except Exception: pass
    win.connect("key-press-event", close)
    win.connect("button-press-event", close)
    return win

def get_primary_geometry():
    display = Gdk.Display.get_default()
    mon = None
    try: mon = display.get_primary_monitor()
    except Exception: mon = None
    if mon is None:
        try: mon = display.get_monitor(0)
        except Exception: mon = None
    if mon and hasattr(mon, "get_geometry"):
        g = mon.get_geometry()
        if g.height > g.width:
            (g.width, g.height) = (g.height, g.width) # some handhelds
        return g.x, g.y, g.width, g.height
    return (0, 0, 1280, 720)

def build_text_popup_top_center(text: str, text_color: str, font_pt: int) -> Gtk.Window:
    out_x, out_y, out_w, _ = get_primary_geometry()
    height_px = max(12, font_pt + 10)

    # Popup bypasses WM (override-redirect) — avoids fullscreen/decoration behavior
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_title(WINDOW_TITLE_OSD)
    win.set_decorated(False)
    win.set_app_paintable(True) # allow CSS color
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    root.set_size_request(out_w, height_px)
    root.set_hexpand(True); root.set_vexpand(True)
    root.set_margin_top(2); root.set_margin_bottom(2)
    root.set_margin_start(12); root.set_margin_end(12)
    win.add(root)

    css = Gtk.CssProvider()
    css.load_from_data(f"""
    box {{ background-color: #000000; }}
    label.overlay-text {{ color: {text_color}; }}
    """.encode("utf-8"))
    Gtk.StyleContext.add_provider_for_screen(win.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    label = Gtk.Label(label=text)
    label.set_justify(Gtk.Justification.CENTER)
    label.set_halign(Gtk.Align.CENTER)
    label.set_valign(Gtk.Align.CENTER)
    label.set_line_wrap(True)
    label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
    label.set_max_width_chars(256)
    label.get_style_context().add_class("overlay-text")

    attrs = Pango.AttrList()
    attrs.insert(Pango.attr_size_new(int(font_pt * Pango.SCALE)))
    label.set_attributes(attrs)

    root.pack_start(label, True, True, 0)

    # Place after map: compute window size then center horizontally
    def place_top_center(_w):
        if os.environ.get("WAYLAND_DISPLAY"):
            # Wayland/labwc: only size, don't move
            win.resize(out_w, height_px)
        else:
            # X11: manual positioning required
            width = out_w
            x = out_x + (out_w - width) // 2
            y = out_y + 2
            win.move(max(0, x), max(0, y))
            win.resize(width, height_px)

    win.connect("realize", place_top_center)

    def close(_w, *_a):
        try: win.destroy()
        except Exception: pass
    win.connect("key-press-event", close)
    win.connect("button-press-event", close)

    win._overlay_label = label
    return win

def animate_fade_out(widget: Gtk.Widget, duration_ms: int = 300, steps: int = 30):
    try: widget.set_opacity(1.0)
    except Exception: return
    step = 0
    interval = max(1, duration_ms // max(1, steps))
    def tick():
        nonlocal step
        step += 1
        opacity = max(0.0, 1.0 - (step / float(steps)))
        try:
            widget.set_opacity(opacity)
        except Exception:
            return False
        return step < steps
    GLib.timeout_add(interval, tick)

def flash(duration_seconds: float = 0.1, color: str = "#ffffff", text: str | None = None, font_pt: int = 36):
    if not ensure_display():
        raise RuntimeError("ERROR: No GUI display detected. Set DISPLAY (X11) or WAYLAND_DISPLAY (Wayland).")
    if not gtk_init_check():
        raise RuntimeError("ERROR: Gtk couldn't be initialized.")

    try: font_pt = int(font_pt)
    except Exception: font_pt = 36
    font_pt = max(6, min(200, font_pt))

    if text and text.strip():
        win = build_text_popup_top_center(text.strip(), color, font_pt)
    else:
        win = build_fullscreen_flash(color)

    win.show_all()

    # Ensure the popup maps before timing (important on X11)
    for _ in range(8):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        time.sleep(0.005)

    total_ms = max(300, int(duration_seconds * 1000))
    if text and text.strip():
        fade_ms = min(300, total_ms)
        def start_fade():
            label = getattr(win, "_overlay_label", None)
            if label is not None:
                animate_fade_out(label, duration_ms=fade_ms, steps=30)
            return False
        GLib.timeout_add(max(1, total_ms - fade_ms), start_fade)

    start = time.monotonic()
    while time.monotonic() - start < duration_seconds:
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        time.sleep(0.004)

    try: win.destroy()
    except Exception: pass

def unescape_cli_text(s: str) -> str:
    return (
        s.replace("\\\\", "\\")     # escaped backslash
         .replace("\\n", "\n")      # newline
         .replace("\\t", "\t")      # tab
         .replace("\\r", "\r")      # carriage return (rarely needed)
    )

def parse_args():
    duration = 0.1
    color = "#ffffff"
    text = None
    font_pt = 36
    if len(sys.argv) >= 2:
        if (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
            sys.stdout.write( """batocera-flash-screen duration color text font_size
 - duration in seconds (default: 0.1)
 - color can be "blue" or "#ffaacc" (default: white)
 - text is the string to display, if not provided the full screen flashes in color
 - font_size for text in pts (default: 36)
""")
            sys.exit(0)
        try: duration = float(sys.argv[1])
        except ValueError: pass
    if len(sys.argv) >= 3:
        color = sys.argv[2]
    if len(sys.argv) >= 4:
        # Allow escaped sequences in CLI to produce actual newlines
        text = unescape_cli_text(sys.argv[3])
    if len(sys.argv) >= 5:
        try: font_pt = int(sys.argv[4])
        except ValueError: pass
    return duration, color, text, font_pt

if __name__ == "__main__":
    dur, col, txt, fpt = parse_args()
    try:
        flash(dur, col, txt, fpt)
    except RuntimeError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)

