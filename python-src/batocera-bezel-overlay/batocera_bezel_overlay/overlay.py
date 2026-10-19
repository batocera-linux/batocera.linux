# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import logging
import sys
from typing import ClassVar, Literal

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


def create_overlay(kind: Literal['x11', 'wayland'], image_path: str, dimensions: tuple[int, int], /) -> Overlay:
    match kind:
        case 'x11':
            from batocera_bezel_overlay.x11_overlay import X11Overlay

            return X11Overlay(image_path, dimensions)
        case 'wayland':
            from batocera_bezel_overlay.wayland_overlay import WaylandOverlay

            return WaylandOverlay(image_path, dimensions)
        case _:
            raise ValueError(f'Unsupported overlay kind: {kind}')
