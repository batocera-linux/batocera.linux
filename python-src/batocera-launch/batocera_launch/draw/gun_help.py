from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final, NotRequired, TypedDict, cast

from PIL import Image, ImageDraw, ImageFont

from batocera_common.paths import BATOCERA_SHARE_DIR

if TYPE_CHECKING:
    from collections.abc import Mapping

    from batocera_launch.devices.gun import Guns
    from batocera_launch.types import Resolution

_logger = logging.getLogger(__name__)

FONT_PATH: Final = Path('/usr/share/fonts/dejavu/DejaVuSans.ttf')
GUN_HELP_DIR: Final = Path('/var/run/batocera-overlays')
DEFAULT_GUN_HELP_PATH: Final = GUN_HELP_DIR / 'gun_help_default.png'
GUN_HELP_PATH: Final = GUN_HELP_DIR / 'gun_help.png'
GUNS_OVERLAYS_DIR: Final = BATOCERA_SHARE_DIR / 'guns-overlays'
IMG_RATIO: Final = 0.5  # ratio of the screen height


class _GunInfosTextDict(TypedDict):
    value: str
    x: float
    y: float
    line_color: str
    line: list[float]
    align: NotRequired[str]
    font_size_per_height: NotRequired[float]


class _GunInfosDict(TypedDict):
    texts: NotRequired[list[_GunInfosTextDict]]
    font_size_per_height: NotRequired[float]
    color: NotRequired[str]


def _png_to_png_with_texts(
    input_png_path: Path,
    output_png_path: Path,
    data: _GunInfosDict,
    /,
    *,
    font_path: Path,
    width: int | None = None,
    height: int | None = None,
) -> None:
    img_big = Image.open(input_png_path)
    ratio = img_big.width / img_big.height

    if width is None and height is None:
        raise ValueError('width or height must be provided')

    img_width: int = 0
    img_height: int = 0

    if width is None and height is not None:
        img_height = height
        img_width = int(height * ratio)

    if width is not None and height is None:
        img_width = width
        img_height = int(width * ratio)

    img = img_big.resize((img_width, img_height))  # pyright: ignore[reportUnknownMemberType]
    draw = ImageDraw.Draw(img)

    # font
    font: dict[float, ImageFont.FreeTypeFont] = {}
    if 'font_size_per_height' in data:
        font_size = int(data['font_size_per_height'] * img_height)
        font[font_size] = ImageFont.truetype(font_path, font_size)

    # lines
    if 'texts' in data:
        for text in data['texts']:
            if 'value' in text and text['value'] != '':
                line_color = 'black'
                line_size = 2
                if 'line_color' in text:
                    line_color = text['line_color']
                if 'line_size' in text:
                    line_size = text['line_size']
                if 'line' in text:
                    points: list[tuple[float, float]] = []
                    for i, v in enumerate(text['line']):
                        if i % 2 == 1:
                            points.append((text['line'][i - 1] * img_width, v * img_height))
                    draw.line(points, fill=line_color, width=line_size)

    # texts
    if 'texts' in data and 'font_size_per_height' in data:
        for text in data['texts']:
            if 'x' in text and 'y' in text and 'value' in text:
                # x, y
                x = round(text['x'] * img_width)
                y = round(text['y'] * img_height)

                # color
                color = 'black'
                if 'color' in data:
                    color = data['color']
                if 'color' in text:
                    color = text['color']

                # font
                font_size = int(data['font_size_per_height'] * img_height)
                if 'font_size_per_height' in text:
                    font_size = int(text['font_size_per_height'] * img_height)
                    if font_size not in font:
                        font[font_size] = ImageFont.truetype(font_path, font_size)

                # alignment
                text_width = draw.textlength(text['value'], font[font_size])
                align = 'left'
                if 'align' in text:
                    align = text['align']
                if align == 'center':
                    x = x - int(text_width / 2)
                if align == 'right':
                    x = x - text_width
                draw.text((x, y), text['value'], fill=color, font=font[font_size])

    # save
    img.save(output_png_path, 'PNG')


def _gun_help_replace(text: str, replacements: Mapping[str, str], /) -> str:
    result = text

    for replacement, value in replacements.items():
        result = result.replace(replacement, value)

    return result


def generate_gun_help(guns: Guns, metadata: Mapping[str, str], resolution: Resolution, /) -> Path | None:
    # default replacements
    replacements = {
        '<TRIGGER>': 'TRIGGER',
        '<ACTION>': 'ACTION',
        '<START>': 'START',
        '<SELECT>': 'SELECT',
        '<SUB1>': 'SUB1',
        '<SUB2>': 'SUB2',
        '<SUB3>': 'SUB3',
        '<UP>': 'UP',
        '<DOWN>': 'DOWN',
        '<LEFT>': 'LEFT',
        '<RIGHT>': 'RIGHT',
    }

    if not GUN_HELP_DIR.exists():
        GUN_HELP_DIR.mkdir(parents=True)

    # customize texts ?
    # use a gamesgunsbuttonsdb.xml to customize gun helps for each game
    customize_texts = any(key.startswith('gun_') for key in metadata)

    if customize_texts:
        for key in replacements:
            metadata_key = key[1:-1].lower()  # remove < and > and convert to lowercase
            replacements[key] = metadata.get(f'gun_{metadata_key}', '')

    if not customize_texts and DEFAULT_GUN_HELP_PATH.exists():
        shutil.copyfile(DEFAULT_GUN_HELP_PATH, GUN_HELP_PATH)
        _logger.info('using cache image : %s', DEFAULT_GUN_HELP_PATH)
        return GUN_HELP_PATH

    if GUN_HELP_PATH.exists():
        GUN_HELP_PATH.unlink()

    _logger.info('generating gun help image')

    # take the first gun
    gun_name = guns[0].name
    gun_overlay_png = GUNS_OVERLAYS_DIR / f'{gun_name}.png'

    if not gun_overlay_png.exists():
        _logger.info("image doesn't exist : %s", gun_overlay_png)
        return None

    gun_overlay_info = gun_overlay_png.with_suffix('.info')

    # try to open the help texts
    data: _GunInfosDict = {}
    if gun_overlay_info.exists():
        with gun_overlay_info.open(encoding='utf-8') as file:
            data = cast('_GunInfosDict', json.load(file))

    # replace data in texts
    if 'texts' in data:
        for text in data['texts']:
            text['value'] = _gun_help_replace(text['value'], replacements)

    img_height = int(resolution.height * IMG_RATIO)
    _logger.info('generating image %s', GUN_HELP_PATH)
    _png_to_png_with_texts(gun_overlay_png, GUN_HELP_PATH, data, font_path=FONT_PATH, height=img_height)

    return GUN_HELP_PATH
