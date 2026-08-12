from __future__ import annotations

from typing import TYPE_CHECKING

import gi

if TYPE_CHECKING:
    from batocera_bezel_overlay import _layer_shell as GtkLayerShell
else:
    gi.require_version('GtkLayerShell', '0.1')

    from gi.repository import GtkLayerShell as GtkLayerShell  # pyright: ignore
