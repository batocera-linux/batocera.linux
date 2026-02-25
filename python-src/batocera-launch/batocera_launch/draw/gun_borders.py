from __future__ import annotations

import math
from typing import TYPE_CHECKING, Final

from batocera_launch.draw.pil import get_image_size

if TYPE_CHECKING:
    from pathlib import Path

_BORDER_COLOR_VALUES: Final = {
    'white': 0xFFFFFF,
    'red': 0xFF0000,
    'green': 0x00FF00,
    'blue': 0x0000FF,
}

_BORDER_COLOR_RGB: Final = {
    'white': '#ffffff',
    'red': '#ff0000',
    'green': '#00ff00',
    'blue': '#0000ff',
    'black': '#000000',
}

_BORDER_PRESETS: Final = {
    'thin': (1, 0),
    'medium': (2, 0),
    'big': (2, 1),
}


def create_gun_border_image(
    input_png: Path,
    output_path: Path,
    border_size: str,
    border_ratio: str | None,
    /,
    *,
    inner_color: str = 'white',
    outer_color: str = 'black',
) -> None:
    # good default border that works in most circumstances is:
    #
    # 2% of the screen width in white.  Surrounded by 3% screen width of
    # black.  I have attached an example.  The black helps the lightgun detect
    # the border against a bright background behind the tv.
    #
    # The ideal solution is to draw the games inside the border rather than
    # overlap.  Then you can see the whole game.  The lightgun thinks that the
    # outer edge of the border is the edge of the game screen.  So you have to
    # make some adjustments in the lightgun settings to keep it aligned.  This
    # is why normally the border overlaps as it means that people do not need
    # to calculate an adjustment and is therefore easier.
    #
    # If all the games are drawn with the border this way then the settings
    # are static and the adjustment only needs to be calculated once.

    from PIL import Image, ImageDraw

    w, h = get_image_size(input_png)
    inner_percent, outer_percent = _BORDER_PRESETS.get(border_size, (0, 0))

    # Calculate new width for 4:3 aspect ratio if a widescreen resolution
    if abs(w / h - 4 / 3) < 0.01:
        new_w = w
    elif border_ratio == '4:3':
        new_w = int((4 / 3) * h)
    else:
        new_w = w

    # Calculate offset for centering the border image
    offset_x = (w - new_w) // 2

    # outer border
    outer_border_size = w * outer_percent // 100  # use only h to have homogen border size
    if outer_border_size < 1:  # minimal size
        outer_border_size = 0
    outer_shapes = [
        [(offset_x, 0), (offset_x + new_w, outer_border_size)],
        [(offset_x + new_w - outer_border_size, 0), (offset_x + new_w, h)],
        [(offset_x, h - outer_border_size), (offset_x + new_w, h)],
        [(offset_x, 0), (offset_x + outer_border_size, h)],
    ]

    # inner border
    inner_border_size = w * inner_percent // 100  # use only h to have homogen border size
    if inner_border_size < 1:  # minimal size
        inner_border_size = 1
    inner_shapes = [
        [
            (offset_x + outer_border_size, outer_border_size),
            (offset_x + new_w - outer_border_size, outer_border_size + inner_border_size),
        ],
        [
            (offset_x + new_w - outer_border_size - inner_border_size, outer_border_size),
            (offset_x + new_w - outer_border_size, h - outer_border_size),
        ],
        [
            (offset_x + outer_border_size, h - outer_border_size - inner_border_size),
            (offset_x + new_w - outer_border_size, h - outer_border_size),
        ],
        [
            (offset_x + outer_border_size, outer_border_size),
            (offset_x + outer_border_size + inner_border_size, h - outer_border_size),
        ],
    ]

    back = Image.open(input_png)

    new_image = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    new_image.paste(back, (0, 0, w, h))

    new_image_draw = ImageDraw.Draw(new_image)

    for shape in outer_shapes:
        new_image_draw.rectangle(shape, fill=_BORDER_COLOR_RGB.get(outer_color, _BORDER_COLOR_RGB['black']))

    for shape in inner_shapes:
        new_image_draw.rectangle(shape, fill=_BORDER_COLOR_RGB.get(inner_color, _BORDER_COLOR_RGB['white']))

    new_image.save(output_path, mode='RGBA', format='PNG')


def draw_gun_borders(border_size: str, border_color: str, border_ratio: str | None, /) -> None:
    from batocera_launch.draw.x11 import open_display

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
            _BORDER_COLOR_VALUES.get(border_color, 0xFFFFFF),
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
