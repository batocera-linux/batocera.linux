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

    from ..devices.gun import Guns
    from ..types import Resolution

_logger = logging.getLogger(__name__)

_FONT_PATH: Final = Path('/usr/share/fonts/dejavu/DejaVuSans.ttf')
_GUN_HELP_DIR: Final = Path('/var/run/batocera-overlays')
_GUN_HELP_CACHE_PATH: Final = _GUN_HELP_DIR / 'gun_help_default.png'
_GUN_HELP_PATH: Final = _GUN_HELP_DIR / 'gun_help.png'
_GUNS_OVERLAYS_DIR: Final = BATOCERA_SHARE_DIR / 'guns-overlays'
_IMG_RATIO: Final = 0.5  # ratio of the screen height

_DEFAULT_REPLACEMENTS: Final = {
    'TRIGGER': 'TRIGGER',
    'ACTION': 'ACTION',
    'START': 'START',
    'SELECT': 'SELECT',
    'SUB1': 'SUB1',
    'SUB2': 'SUB2',
    'SUB3': 'SUB3',
    'UP': 'UP',
    'DOWN': 'DOWN',
    'LEFT': 'LEFT',
    'RIGHT': 'RIGHT',
}


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
        font[font_size] = ImageFont.truetype(_FONT_PATH, font_size)

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
                        font[font_size] = ImageFont.truetype(_FONT_PATH, font_size)

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
        result = result.replace(f'<{replacement}>', value)

    return result


def generate_gun_help(use_guns: bool, guns: Guns, metadata: Mapping[str, str], resolution: Resolution, /) -> None:
    _GUN_HELP_DIR.mkdir(parents=True, exist_ok=True)

    customize_texts = any(key.startswith('gun_') for key in metadata)

    # if we use the image without any customization, copy the backup
    # cache file to the destination
    if (use_guns or guns) and not customize_texts and _GUN_HELP_CACHE_PATH.exists():
        shutil.copyfile(_GUN_HELP_CACHE_PATH, _GUN_HELP_PATH)
        _logger.info('using cache image: %s', _GUN_HELP_CACHE_PATH)
        return

    # remove any existing file
    if _GUN_HELP_PATH.exists():
        _GUN_HELP_PATH.unlink()

    # don't enable if not a gun game or no gun
    if not (use_guns and guns):
        _logger.info('not generating gun help image')
        return

    _logger.info('generating gun help image')

    # take the first gun
    gun_name = guns[0].name
    gun_overlay_png = _GUNS_OVERLAYS_DIR / f'{gun_name}.png'

    if not gun_overlay_png.exists():
        _logger.info("image doesn't exist: %s", gun_overlay_png)
        return

    gun_overlay_info = gun_overlay_png.with_suffix('.infos')

    # try to open the help texts
    data: _GunInfosDict = {}
    if gun_overlay_info.exists():
        with gun_overlay_info.open(encoding='utf-8') as file:
            data = cast('_GunInfosDict', json.load(file))

    # replace data in texts
    if 'texts' in data:
        # if we customize text, we reset replacements by the ones in the metadata (and
        # an empty string if it doesn't exist in the metadata)
        replacements = (
            {key: metadata.get(f'gun_{key.lower()}', '') for key in _DEFAULT_REPLACEMENTS}
            if customize_texts
            else _DEFAULT_REPLACEMENTS
        )

        for text in data['texts']:
            text['value'] = _gun_help_replace(text['value'], replacements)

    _logger.info('generating image: %s', _GUN_HELP_PATH)
    _png_to_png_with_texts(gun_overlay_png, _GUN_HELP_PATH, data, height=int(resolution.height * _IMG_RATIO))

    if not customize_texts:
        # cache the file since it hasn't been customized
        shutil.copyfile(_GUN_HELP_PATH, _GUN_HELP_CACHE_PATH)
        _logger.info('caching file to: %s', _GUN_HELP_CACHE_PATH)
