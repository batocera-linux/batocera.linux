from __future__ import annotations

import logging
import struct
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PIL import Image, ImageDraw, ImageOps

from batocera_common.paths import BATOCERA_SHARE_DIR
from batocera_launch.exceptions import BatoceraException

if TYPE_CHECKING:
    from _typeshed import StrPath

    from PIL.ImageFile import ImageFile
    from qrcode.image.pil import PilImage

    from batocera_launch.config.config import SystemConfig

_logger = logging.getLogger(__name__)


# Much faster than PIL Image.size
def get_image_size(image_file: StrPath, /) -> tuple[int, int]:
    image_file = Path(image_file)

    if not image_file.exists():
        return -1, -1

    with image_file.open('rb') as fhandle:
        head = fhandle.read(32)

        if len(head) != 32:
            # corrupted header, or not a PNG
            return -1, -1

        if struct.unpack('>i', head[4:8])[0] != 0x0D0A1A0A:
            # Not a PNG
            return -1, -1

        return struct.unpack('>ii', head[16:24])  # image width, height


def create_transparent_image(path: StrPath, width: int, height: int, /) -> None:
    path = Path(path)
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(image)
    image.save(path, format='PNG', mode='RGBA')


def resize_image(
    input_path: StrPath, output_path: StrPath, width: int, height: int, /, *, stretch: bool = False
) -> None:
    input_image = Image.open(input_path)
    fillcolor = 'black'

    if input_image.mode != 'RGBA':
        _alpha_paste(input_path, output_path, fillcolor, (width, height), stretch)
    else:
        output_image = input_image.resize((width, height), Image.Resampling.BICUBIC)  # pyright: ignore[reportUnknownMemberType]
        output_image.save(output_path, mode='RGBA', format='PNG')


def pad_image(
    input_png: str | Path,
    output_png: str | Path,
    width: int,
    height: int,
    /,
    *,
    stretch: bool = False,
) -> None:
    input_image = Image.open(input_png)
    fill_color = 'black'

    _logger.debug('Padding bezel: image mode %s', input_image.mode)

    if input_image.mode != 'RGBA':
        _alpha_paste(input_png, output_png, fill_color, (width, height), stretch)
    else:
        if stretch:
            output_image = ImageOps.fit(input_image, (width, height))
        else:
            output_image = ImageOps.pad(input_image, (width, height), color=fill_color, centering=(0.5, 0.5))

        output_image.save(output_png, mode='RGBA', format='PNG')


def add_qr_code(input_png: StrPath, output_png: StrPath, code: str, corner: str, /) -> None:
    import qrcode

    url = f'https://retroachievements.org/game/{code}'

    box_size = 3
    border_size = 2

    qr = qrcode.QRCode(version=1, box_size=box_size, border=border_size)
    qr.add_data(url)
    qr.make()

    qr_image = cast('PilImage', qr.make_image(back_color=(120, 120, 120)))

    x = 29 * box_size + border_size * box_size * 2

    qr_image = cast('Image.Image', qr_image.convert('RGBA'))

    new_bezel = Image.open(input_png)
    new_bezel = new_bezel.convert('RGBA')

    width, height = get_image_size(input_png)

    if corner.upper() == 'NW':
        new_bezel.paste(qr_image, (0, 0, x, x))
    elif corner.upper() == 'SE':
        new_bezel.paste(qr_image, (width - x, height - x, width, height))
    elif corner.upper() == 'SW':
        new_bezel.paste(qr_image, (0, height - x, x, height))
    else:  # default = NE
        new_bezel.paste(qr_image, (width - x, 0, width, x))

    new_bezel.save(output_png)


def add_tattoo_image(input_path: StrPath, output_path: StrPath, config: SystemConfig, /) -> None:
    tattoo_file: ImageFile | None = None
    bezel_tattoo = config.get_str('bezel.tattoo')

    if bezel_tattoo == 'system':
        tattoo_path = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{config.system}.png'
        try:
            if not tattoo_path.exists():
                tattoo_path = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
            tattoo_file = Image.open(tattoo_path)
        except Exception:
            _logger.error('Error opening controller overlay: %s', tattoo_path)
    elif (
        bezel_tattoo == 'custom'
        and (bezel_tattoo_file := config.get('bezel.tattoo_file')) is not None
        and (tattoo_path := Path(bezel_tattoo_file)).exists()
    ):
        try:
            tattoo_file = Image.open(tattoo_path)
        except Exception:
            _logger.error('Error opening custom file: %s', tattoo_path)
    else:
        tattoo_path = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
        try:
            tattoo_file = Image.open(tattoo_path)
        except Exception:
            _logger.error('Error opening custom file: %s', tattoo_path)

    if tattoo_file is None:
        raise BatoceraException(f'Tattoo image could not be opened: {tattoo_path}')

    # Open the existing bezel...
    back_image = Image.open(input_path)
    # Convert it otherwise it implodes later on...
    back_image = back_image.convert('RGBA')

    tattoo_image = tattoo_file.convert('RGBA')

    # Quickly grab the sizes.
    width, height = get_image_size(input_path)
    tattoo_width, tattoo_height = get_image_size(tattoo_path)

    if not config.get_bool('bezel.resize_tattoo', True):
        # Maintain the image's original size.
        # Failsafe for if the image is too large.
        if tattoo_width > width or tattoo_height > height:
            # Limit width to that of the bezel and crop the rest.
            percent = float(width / tattoo_width)
            tattoo_height = int(float(tattoo_height) * percent)
            # Resize the tattoo to the calculated size.
            tattoo_image = tattoo_image.resize((width, tattoo_height), Image.Resampling.BICUBIC)  # pyright: ignore[reportUnknownMemberType]
    else:
        # Resize to be slightly smaller than the bezel's column.
        tattoo_width_tmp = int((225 / 1920) * width)
        percent = float(tattoo_width_tmp / tattoo_width)
        tattoo_height = int(float(tattoo_height) * percent)
        tattoo_image = tattoo_image.resize((tattoo_width_tmp, tattoo_height), Image.Resampling.BICUBIC)  # pyright: ignore[reportUnknownMemberType]
        tattoo_width = tattoo_width_tmp

    # Create a new blank canvas that is the same size as the bezel for later compositing (they are required to be the same size).
    tattoo_canvas = Image.new('RGBA', back_image.size)
    # Margin for the tattoo
    margin = int((20 / 1080) * height)

    corner = config.get('bezel.tattoo_corner', 'NW')
    if corner.upper() == 'NE':
        tattoo_canvas.paste(tattoo_image, (width - tattoo_width, margin))  # 20 pixels vertical margins (on 1080p)
    elif corner.upper() == 'SE':
        tattoo_canvas.paste(tattoo_image, (width - tattoo_width, height - tattoo_height - margin))
    elif corner.upper() == 'SW':
        tattoo_canvas.paste(tattoo_image, (0, height - tattoo_height - margin))
    else:  # default = NW
        tattoo_canvas.paste(tattoo_image, (0, margin))

    back_image = Image.alpha_composite(back_image, tattoo_canvas)

    new_image = Image.new('RGBA', (width, height), (0, 0, 0, 255))
    new_image.paste(back_image, (0, 0, width, height))
    new_image.save(output_path, mode='RGBA', format='PNG')


def _alpha_paste(
    input_png: StrPath, output_png: StrPath, fill_color: str, screen_size: tuple[int, int], bezel_stretch: bool, /
) -> None:
    input_image = Image.open(input_png)

    # TheBezelProject have Palette + alpha, not RGBA. PIL can't convert from P+A to RGBA.
    # Even if it can load P+A, it can't save P+A as PNG. So we have to recreate a new image to adapt it.
    if 'transparency' not in input_image.info:
        raise BatoceraException('No transparent pixels in the bezel image')

    screen_width, screen_height = screen_size

    alpha = input_image.split()[-1]  # alpha from original palette + alpha
    image_width, image_height = get_image_size(input_png)
    image_ratio = float(image_width) / float(image_height)
    screen_ratio = float(screen_width) / float(screen_height)

    if image_ratio - screen_ratio > 0.01:
        # cut off bezel sides for 16:10 screens
        new_x = int(image_width * screen_ratio / image_ratio)
        delta = int(image_width - new_x)
        border_x = delta // 2
        image_width = new_x
        alpha_new = alpha.crop((border_x, 0, new_x + border_x, image_height))
        alpha = alpha_new

    new_image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 255))
    new_image.paste(alpha, (0, 0, image_width, image_height))

    if bezel_stretch:
        output_image = ImageOps.fit(new_image, screen_size)
    else:
        output_image = ImageOps.pad(new_image, screen_size, color=fill_color, centering=(0.5, 0.5))

    output_image.save(output_png, mode='RGBA', format='PNG')
