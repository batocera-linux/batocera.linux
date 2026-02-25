from __future__ import annotations

import math
from typing import Final

from batocera_launch.draw.x11 import open_display

_BORDER_COLORS: Final = {
    'white': 0xFFFFFF,
    'red': 0xFF0000,
    'green': 0x00FF00,
    'blue': 0x0000FF,
}

_BORDER_PRESETS: Final = {
    'thin': (1, 0),
    'medium': (2, 0),
    'big': (2, 1),
}


def draw_gun_borders(border_size: str, border_color: str, border_ratio: str | None, /) -> None:
    inner_percent, outer_percent = _BORDER_PRESETS.get(border_size, (2, 0))

    with open_display() as display:
        screen_width = display.screen_width
        screen_height = display.screen_height

        region_width = screen_width
        region_offset_x = 0

        if border_ratio == '4:3':
            region_width = min(int(screen_height / 3 * 4), screen_width)
            region_offset_x = (screen_width - region_width) // 2

        outer_thickness = math.ceil(screen_width * outer_percent / 100)
        inner_thickness = max(math.ceil(screen_width * inner_percent / 100), 1)

        # outer
        display.draw_border(region_offset_x, 0, region_width, screen_height, outer_thickness, 0x000000)

        # inner
        display.draw_border(
            region_offset_x + outer_thickness,
            outer_thickness,
            region_width - 2 * outer_thickness,
            screen_height - 2 * outer_thickness,
            inner_thickness,
            _BORDER_COLORS.get(border_color, 0xFFFFFF),
        )


if __name__ == '__main__':
    import signal
    import sys

    border_size = 'medium'
    border_color = 'white'
    border_ratio = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ('-s', '--size') and i + 1 < len(args):
            border_size = args[i + 1]
            i += 2
        elif args[i] in ('-c', '--color') and i + 1 < len(args):
            border_color = args[i + 1]
            i += 2
        elif args[i] in ('-r', '--ratio') and i + 1 < len(args):
            border_ratio = args[i + 1]
            i += 2
        else:
            i += 1

    draw_gun_borders(border_size, border_color, border_ratio)

    while True:
        signal.pause()
