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
