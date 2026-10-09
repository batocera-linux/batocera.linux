from __future__ import annotations

import logging
import sys
from typing import ClassVar

import gi

from batocera_bezel_overlay.overlay import Overlay

try:
    gi.require_version('Gtk', '3.0')

    from gi.repository import Gtk
except (ImportError, ValueError) as exc:
    print('Error: Dependencies not met.', exc)
    sys.exit(1)


_log = logging.getLogger(__name__)


class X11Overlay(Overlay):
    """Specialized Overlay for X11/Openbox environments."""

    __gtype_name__ = 'X11Overlay'

    window_type: ClassVar[Gtk.WindowType] = Gtk.WindowType.POPUP

    def setup(self, dimensions: tuple[int, int], /) -> None:
        """Configure override-redirect parameters on X11."""
        _log.debug('Initializing X11/Openbox window attributes...')

        self.move(0, 0)
        self.resize(*dimensions)
