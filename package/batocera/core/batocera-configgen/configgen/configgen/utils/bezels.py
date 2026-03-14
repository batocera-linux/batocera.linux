from __future__ import annotations

import json
import logging
import shutil
import struct
from pathlib import Path
from typing import TYPE_CHECKING, NotRequired, TypedDict, cast

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps

from ..batoceraPaths import BATOCERA_SHARE_DIR, ES_GUNS_ART_METADATA, SYSTEM_DECORATIONS, USER_DECORATIONS
from ..exceptions import BatoceraException
from . import metadata
from .videoMode import getAltDecoration

if TYPE_CHECKING:
    from collections.abc import Mapping

    from PIL.ImageFile import ImageFile
    from qrcode.image.pil import PilImage

    from configgen.gun import Guns
    from configgen.types import Resolution

    from ..config import SystemConfig
    from ..Emulator import Emulator

_logger = logging.getLogger(__name__)

class BezelInfos(TypedDict):
    png: Path
    info: Path
    layout: Path
    mamezip: Path
    specific_to_game: bool


def getBezelInfos(rom: str | Path, bezel: str, systemName: str, emulator: str) -> BezelInfos | None:
    # by order choose :
    # rom name in the system subfolder of the user directory (gb/mario.png)
    # rom name in the system subfolder of the system directory (gb/mario.png)
    # rom name in the user directory (mario.png)
    # rom name in the system directory (mario.png)
    # system name with special graphic in the user directory (gb-90.png)
    # system name in the user directory (gb.png)
    # system name with special graphic in the system directory (gb-90.png)
    # system name in the system directory (gb.png)
    # default name (default.png)
    # else return
    # mamezip files are for MAME-specific advanced artwork (bezels with overlays and backdrops, animated LEDs, etc)
    altDecoration = getAltDecoration(systemName, rom, emulator)
    romBase = Path(rom).stem # filename without extension
    overlay_info_file = USER_DECORATIONS / bezel / "games" / systemName / f"{romBase}.info"
    overlay_png_file  = USER_DECORATIONS / bezel / "games" / systemName / f"{romBase}.png"
    overlay_layout_file  = USER_DECORATIONS / bezel / "games" / systemName / f"{romBase}.lay"
    overlay_mamezip_file  = USER_DECORATIONS / bezel / "games" / systemName / f"{romBase}.zip"
    bezel_game = True
    if not overlay_png_file.exists():
        overlay_info_file = SYSTEM_DECORATIONS / bezel / "games" / systemName / f"{romBase}.info"
        overlay_png_file  = SYSTEM_DECORATIONS / bezel / "games" / systemName / f"{romBase}.png"
        overlay_layout_file  = USER_DECORATIONS / bezel / "games" / systemName / f"{romBase}.lay"
        overlay_mamezip_file  = USER_DECORATIONS / bezel / "games" / systemName / f"{romBase}.zip"
        bezel_game = True
        if not overlay_png_file.exists():
            overlay_info_file = USER_DECORATIONS / bezel / "games" / f"{romBase}.info"
            overlay_png_file  = USER_DECORATIONS / bezel / "games" / f"{romBase}.png"
            overlay_layout_file  = USER_DECORATIONS / bezel / "games" / f"{romBase}.lay"
            overlay_mamezip_file  = USER_DECORATIONS / bezel / "games" / f"{romBase}.zip"
            bezel_game = True
            if not overlay_png_file.exists():
                overlay_info_file = SYSTEM_DECORATIONS / bezel / "games" / f"{romBase}.info"
                overlay_png_file  = SYSTEM_DECORATIONS / bezel / "games" / f"{romBase}.png"
                overlay_layout_file  = USER_DECORATIONS / bezel / "games" / f"{romBase}.lay"
                overlay_mamezip_file  = USER_DECORATIONS / bezel / "games" / f"{romBase}.zip"
                bezel_game = True
                if not overlay_png_file.exists():
                    if altDecoration != "0":
                        overlay_info_file = USER_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.info"
                        overlay_png_file  = USER_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.png"
                        overlay_layout_file  = USER_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.lay"
                        overlay_mamezip_file  = USER_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.zip"
                        bezel_game = False
                    if not overlay_png_file.exists():
                        overlay_info_file = USER_DECORATIONS / bezel / "systems" / f"{systemName}.info"
                        overlay_png_file  = USER_DECORATIONS / bezel / "systems" / f"{systemName}.png"
                        overlay_layout_file  = USER_DECORATIONS / bezel / "systems" / f"{systemName}.lay"
                        overlay_mamezip_file  = USER_DECORATIONS / bezel / "systems" / f"{systemName}.zip"
                        bezel_game = False
                        if not overlay_png_file.exists():
                            if altDecoration != "0":
                                overlay_info_file = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.info"
                                overlay_png_file  = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.png"
                                overlay_layout_file  = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.lay"
                                overlay_mamezip_file  = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}-{altDecoration!s}.zip"
                                bezel_game = False
                            if not overlay_png_file.exists():
                                overlay_info_file = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}.info"
                                overlay_png_file  = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}.png"
                                overlay_layout_file  = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}.lay"
                                overlay_mamezip_file  = SYSTEM_DECORATIONS / bezel / "systems" / f"{systemName}.zip"
                                bezel_game = False
                                if not overlay_png_file.exists():
                                    overlay_info_file = USER_DECORATIONS / bezel / f"default-{altDecoration!s}.info"
                                    overlay_png_file  = USER_DECORATIONS / bezel / f"default-{altDecoration!s}.png"
                                    overlay_layout_file  = USER_DECORATIONS / bezel / f"default-{altDecoration!s}.lay"
                                    overlay_mamezip_file  = USER_DECORATIONS / bezel / f"default-{altDecoration!s}.zip"
                                    bezel_game = True
                                    if not overlay_png_file.exists():
                                        overlay_info_file = USER_DECORATIONS / bezel / "default.info"
                                        overlay_png_file  = USER_DECORATIONS / bezel / "default.png"
                                        overlay_layout_file  = USER_DECORATIONS / bezel / "default.lay"
                                        overlay_mamezip_file  = USER_DECORATIONS / bezel / "default.zip"
                                        bezel_game = True
                                        if not overlay_png_file.exists():
                                            overlay_info_file = SYSTEM_DECORATIONS / bezel / f"default-{altDecoration!s}.info"
                                            overlay_png_file  = SYSTEM_DECORATIONS / bezel / f"default-{altDecoration!s}.png"
                                            overlay_layout_file  = SYSTEM_DECORATIONS / bezel / f"default-{altDecoration!s}.lay"
                                            overlay_mamezip_file  = SYSTEM_DECORATIONS / bezel / f"default-{altDecoration!s}.zip"
                                            bezel_game = True
                                            if not overlay_png_file.exists():
                                                overlay_info_file = SYSTEM_DECORATIONS / bezel / "default.info"
                                                overlay_png_file  = SYSTEM_DECORATIONS / bezel / "default.png"
                                                overlay_layout_file  = SYSTEM_DECORATIONS / bezel / "default.lay"
                                                overlay_mamezip_file  = SYSTEM_DECORATIONS / bezel / "default.zip"
                                                bezel_game = True
                                                if not overlay_png_file.exists():
                                                    return None
    _logger.debug("Original bezel file used: %s", overlay_png_file)
    return { "png": overlay_png_file, "info": overlay_info_file, "layout": overlay_layout_file, "mamezip": overlay_mamezip_file, "specific_to_game": bezel_game }

# Much faster than PIL Image.size
def fast_image_size(image_file: str | Path) -> tuple[int, int]:
    image_file = Path(image_file)
    if not image_file.exists():
        return -1, -1
    with image_file.open('rb') as fhandle:
        head = fhandle.read(32)
        if len(head) != 32:
            # corrupted header, or not a PNG
            return -1, -1
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
            # Not a PNG
            return -1, -1
        return struct.unpack('>ii', head[16:24]) #image width, height

def resizeImage(input_png: str | Path, output_png: str | Path, screen_width: int, screen_height: int, bezel_stretch: bool = False) -> None:
    imgin = Image.open(input_png)
    fillcolor = 'black'
    _logger.debug("Resizing bezel: image mode %s", imgin.mode)
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        imgout = imgin.resize((screen_width, screen_height), Image.Resampling.BICUBIC)
        imgout.save(output_png, mode="RGBA", format="PNG")

def padImage(input_png: str | Path, output_png: str | Path, screen_width: int, screen_height: int, bezel_width: int, bezel_height: int, bezel_stretch: bool = False) -> None:
    imgin = Image.open(input_png)
    fillcolor = 'black'
    _logger.debug("Padding bezel: image mode %s", imgin.mode)
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        if bezel_stretch:
            imgout = ImageOps.fit(imgin, (screen_width, screen_height))
        else:
            imgout = ImageOps.pad(imgin, (screen_width, screen_height), color=fillcolor, centering=(0.5,0.5))
        imgout.save(output_png, mode="RGBA", format="PNG")

def addQRCode(input_png: str | Path, output_png: str | Path, code: str, system: Emulator):
    url = f"https://retroachievements.org/game/{code}"

    bxsize = 3
    bdsize = 2
    qr = qrcode.QRCode(version=1, box_size=bxsize, border=bdsize)
    qr.add_data(url)
    qr.make()
    qrimg = cast('PilImage', qr.make_image(back_color = (120, 120, 120)))

    x = 29 * bxsize + bdsize * bxsize * 2

    w,h = fast_image_size(input_png)
    newBezel = Image.open(input_png)
    qrimg    = cast('Image.Image', qrimg.convert("RGBA"))
    newBezel = newBezel.convert("RGBA")

    corner = system.config.get('bezel.qrcode_corner', 'NE')
    if (corner.upper() == 'NW'):
        newBezel.paste(qrimg, (0, 0, x, x))
    elif (corner.upper() == 'SE'):
        newBezel.paste(qrimg, (w-x, h-x, w, h))
    elif (corner.upper() == 'SW'):
        newBezel.paste(qrimg, (0, h-x, x, h))
    else: # default = NE
        newBezel.paste(qrimg, (w-x, 0, w, x))
    newBezel.save(output_png)

def tatooImage(input_png: Path, output_png: Path, system: Emulator) -> None:
    tattoo_file: ImageFile | None = None

    if system.config['bezel.tattoo'] == 'system':
        tattoo_path = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{system.name}.png'
        try:
            if not tattoo_path.exists():
                tattoo_path = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
            tattoo_file = Image.open(tattoo_path)
        except Exception:
            _logger.error("Error opening controller overlay: %s", tattoo_path)
    elif system.config['bezel.tattoo'] == 'custom' and (tattoo_path := Path(system.config['bezel.tattoo_file'])).exists():
        try:
            tattoo_file = Image.open(tattoo_path)
        except Exception:
            _logger.error("Error opening custom file: %s", tattoo_path)
    else:
        tattoo_path = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
        try:
            tattoo_file = Image.open(tattoo_path)
        except Exception:
            _logger.error("Error opening custom file: %s", tattoo_path)

    if tattoo_file is None:
        raise BatoceraException(f'Tattoo image could not be opened: {tattoo_path}')

    # Open the existing bezel...
    back = Image.open(input_png)
    # Convert it otherwise it implodes later on...
    back = back.convert("RGBA")
    tattoo = tattoo_file.convert("RGBA")
    # Quickly grab the sizes.
    w,h = fast_image_size(input_png)
    tw,th = fast_image_size(tattoo_path)
    if not system.config.get_bool("bezel.resize_tattoo", True):
        # Maintain the image's original size.
        # Failsafe for if the image is too large.
        if tw > w or th > h:
            # Limit width to that of the bezel and crop the rest.
            pcent = float(w / tw)
            th = int(float(th) * pcent)
            # Resize the tattoo to the calculated size.
            tattoo = tattoo.resize((w,th), Image.Resampling.BICUBIC)
    else:
        # Resize to be slightly smaller than the bezel's column.
        twtemp = int((225/1920) * w)
        pcent = float(twtemp / tw)
        th = int(float(th) * pcent)
        tattoo = tattoo.resize((twtemp,th), Image.Resampling.BICUBIC)
        tw = twtemp
    # Create a new blank canvas that is the same size as the bezel for later compositing (they are required to be the same size).
    tattooCanvas = Image.new("RGBA", back.size)
    # Margin for the tattoo
    margin = int((20 / 1080) * h)
    corner = system.config.get('bezel.tattoo_corner', 'NW')
    if (corner.upper() == 'NE'):
        tattooCanvas.paste(tattoo, (w-tw,margin)) # 20 pixels vertical margins (on 1080p)
    elif (corner.upper() == 'SE'):
        tattooCanvas.paste(tattoo, (w-tw,h-th-margin))
    elif (corner.upper() == 'SW'):
        tattooCanvas.paste(tattoo, (0,h-th-margin))
    else: # default = NW
        tattooCanvas.paste(tattoo, (0,margin))
    back = Image.alpha_composite(back, tattooCanvas)

    imgnew = Image.new("RGBA", (w,h), (0,0,0,255))
    imgnew.paste(back, (0,0,w,h))
    imgnew.save(output_png, mode="RGBA", format="PNG")

def alphaPaste(input_png: str | Path, output_png: str | Path, imgin: ImageFile, fillcolor: str, screensize: tuple[int, int], bezel_stretch: bool) -> None:
    # screensize=(screen_width, screen_height)
    imgin = Image.open(input_png)
    # TheBezelProject have Palette + alpha, not RGBA. PIL can't convert from P+A to RGBA.
    # Even if it can load P+A, it can't save P+A as PNG. So we have to recreate a new image to adapt it.
    if 'transparency' not in imgin.info:
        raise BatoceraException("No transparent pixels in the bezel image")
    alpha = imgin.split()[-1]  # alpha from original palette + alpha
    ix,iy = fast_image_size(input_png)
    sx,sy = screensize
    i_ratio = (float(ix) / float(iy))
    s_ratio = (float(sx) / float(sy))

    if (i_ratio - s_ratio > 0.01):
        # cut off bezel sides for 16:10 screens
        new_x = int(ix*s_ratio/i_ratio)
        delta = int(ix-new_x)
        borderx = delta//2
        ix = new_x
        alpha_new = alpha.crop((borderx, 0, new_x+borderx, iy))
        alpha = alpha_new

    imgnew = Image.new("RGBA", (ix,iy), (0,0,0,255))
    imgnew.paste(alpha, (0,0,ix,iy))
    if bezel_stretch:
        imgout = ImageOps.fit(imgnew, screensize)
    else:
        imgout = ImageOps.pad(imgnew, screensize, color=fillcolor, centering=(0.5,0.5))
    imgout.save(output_png, mode="RGBA", format="PNG")

def gunBordersSize(bordersSize: str | None) -> tuple[int, int]:
    if bordersSize == "thin":
        return 1, 0
    if bordersSize == "medium":
        return 2, 0
    if bordersSize == "big":
        return 2, 1
    return 0, 0

def gunBorderImage(input_png: str | Path, output_png: str | Path, aspect_ratio: str | None, innerBorderSizePer: int = 2, outerBorderSizePer: int = 3, innerBorderColor: str = "#ffffff", outerBorderColor: str = "#000000") -> int:
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

    from PIL import ImageDraw
    w,h = fast_image_size(input_png)

    # Calculate new width for 4:3 aspect ratio if a widescreen resolution
    if abs(w / h - 4 / 3) < 0.01:
        new_w = w
    elif aspect_ratio == "4:3":
        new_w = int((4 / 3) * h)
    else:
        new_w = w

    # Calculate offset for centering the border image
    offset_x = (w - new_w) // 2

    # outer border
    outerBorderSize = w * outerBorderSizePer // 100 # use only h to have homogen border size
    if outerBorderSize < 1: # minimal size
        outerBorderSize = 0
    outerShapes = [
        [(offset_x, 0), (offset_x + new_w, outerBorderSize)],
        [(offset_x + new_w - outerBorderSize, 0), (offset_x + new_w, h)],
        [(offset_x, h - outerBorderSize), (offset_x + new_w, h)],
        [(offset_x, 0), (offset_x + outerBorderSize, h)]
    ]

    # inner border
    innerBorderSize = w * innerBorderSizePer // 100 # use only h to have homogen border size
    if innerBorderSize < 1: # minimal size
        innerBorderSize = 1
    innerShapes = [
        [(offset_x + outerBorderSize, outerBorderSize), (offset_x + new_w - outerBorderSize, outerBorderSize + innerBorderSize)],
        [(offset_x + new_w - outerBorderSize - innerBorderSize, outerBorderSize), (offset_x + new_w - outerBorderSize, h - outerBorderSize)],
        [(offset_x + outerBorderSize, h - outerBorderSize - innerBorderSize), (offset_x + new_w - outerBorderSize, h - outerBorderSize)],
        [(offset_x + outerBorderSize, outerBorderSize), (offset_x + outerBorderSize + innerBorderSize, h - outerBorderSize)]
    ]

    back = Image.open(input_png)
    imgnew = Image.new("RGBA", (w,h), (0,0,0,255))
    imgnew.paste(back, (0,0,w,h))
    imgnewdraw = ImageDraw.Draw(imgnew)
    for shape in outerShapes:
        imgnewdraw.rectangle(shape, fill=outerBorderColor)
    for shape in innerShapes:
        imgnewdraw.rectangle(shape, fill=innerBorderColor)
    imgnew.save(output_png, mode="RGBA", format="PNG")

    return outerBorderSize + innerBorderSize

def gunsBorderSize(w: int, h: int, innerBorderSizePer: int = 2, outerBorderSizePer: int = 3) -> int:
    return (w * (innerBorderSizePer + outerBorderSizePer)) // 100

def gunsBordersColorFomConfig(config: SystemConfig) -> str:
    if "controllers.guns.borderscolor" in config:
        if config["controllers.guns.borderscolor"] == "red":
            return "#ff0000"
        if config["controllers.guns.borderscolor"] == "green":
            return "#00ff00"
        if config["controllers.guns.borderscolor"] == "blue":
            return "#0000ff"
        if config["controllers.guns.borderscolor"] == "white":
            return "#ffffff"
    return "#ffffff"

def createTransparentBezel(output_png: Path, width: int, height: int) -> None:
    from PIL import ImageDraw
    imgnew = Image.new("RGBA", (width,height), (0,0,0,0))
    ImageDraw.Draw(imgnew)
    imgnew.save(output_png, mode="RGBA", format="PNG")

class _GunInfosTextDict(TypedDict):
    value: str
    x: float
    y: float
    line_color: str
    line: list[str]
    align: NotRequired[str]
    font_size_per_height: NotRequired[float]

class _GunInfosDict(TypedDict):
    texts: NotRequired[list[_GunInfosTextDict]]
    font_size_per_height: NotRequired[float]
    color: NotRequired[str]

def png_to_png_with_texts(
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
        raise ValueError("width or height must be provided")

    img_width: int = 0
    img_height: int = 0

    if width is None and height is not None:
        img_height = height
        img_width = int(height * ratio)

    if width is not None and height is None:
        img_width = width
        img_height = int(width * ratio)

    img = img_big.resize((img_width, img_height))
    draw = ImageDraw.Draw(img)

    # font
    font = {}
    if "font_size_per_height" in data:
        font_size = int(data["font_size_per_height"]*img_height)
        font[font_size] = ImageFont.truetype(font_path, font_size)

    # lines
    if "texts" in data:
        for text in data["texts"]:
            if "value" in text and text["value"] != "":
                line_color = "black"
                line_size  = 2
                if "line_color" in text:
                    line_color = text["line_color"]
                if "line_size" in text:
                    line_size = text["line_size"]
                if "line" in text:
                    points = []
                    for i, v in enumerate(text["line"]):
                        if i % 2 == 1:
                            points.append((text["line"][i-1] * img_width, v * img_height))
                    draw.line(points, fill=line_color, width=line_size)

    # texts
    if "texts" in data and "font_size_per_height" in data:
        for text in data["texts"]:
            if "x" in text and "y" in text and "value" in text:
                # x, y
                x = round(text["x"]*img_width)
                y = round(text["y"]*img_height)

                # color
                color = "black"
                if "color" in data:
                    color = data["color"]
                if "color" in text:
                    color = text["color"]

                # font
                font_size = int(data["font_size_per_height"]*img_height)
                if "font_size_per_height" in text:
                    font_size = int(text["font_size_per_height"]*img_height)
                    if font_size not in font:
                        font[font_size] = ImageFont.truetype(font_path, font_size)

                # alignment
                text_width = draw.textlength(text["value"], font[font_size])
                align = "left"
                if "align" in text:
                    align = text["align"]
                if align == "center":
                    x = x-int(text_width/2)
                if align == "right":
                    x = x-text_width
                draw.text((x, y), text["value"], fill=color, font=font[font_size])

    # save
    img.save(output_png_path, "PNG")

def gun_help_replace(text: str, replacements: Mapping[str, str]) -> str:
    res = text
    for r in replacements:
        res = res.replace(r, replacements[r])
    return res

def generate_gun_help(
    system: str,
    rom: Path,
    use_guns: bool,
    guns: Guns,
    gun_help_dir: Path,
    gun_help_filename: str,
    gameResolution: Resolution,
    /,
) -> None:
    ttf = Path("/usr/share/fonts/dejavu/DejaVuSans.ttf")
    img_ratio = 0.5 # ratio of the screen height
    default_gun_help_path = gun_help_dir / "gun_help_default.png" # cache file for next game run
    target_path = gun_help_dir / gun_help_filename

    # default replacements
    replacements = {
        "<TRIGGER>": "TRIGGER",
        "<ACTION>":  "ACTION",
        "<START>":   "START",
        "<SELECT>":  "SELECT",
        "<SUB1>":    "SUB1",
        "<SUB2>":    "SUB2",
        "<SUB3>":    "SUB3",
        "<UP>":      "UP",
        "<DOWN>":    "DOWN",
        "<LEFT>":    "LEFT",
        "<RIGHT>":   "RIGHT",
    }

    if not gun_help_dir.exists():
        gun_help_dir.mkdir(parents=True)

    # customize texts ?
    # use a gamesgunsbuttonsdb.xml to customize gun helps for each game
    customize_texts = False

    # search specific metadata
    md = {}
    if ES_GUNS_ART_METADATA.exists():
        md = metadata.get_games_meta_data(ES_GUNS_ART_METADATA, system, rom)
        for key in md:
            if key.startswith("gun_"):
                customize_texts = True
        # if we customize text, we reset replacements by only the one in metadata
        if customize_texts:
            for key in replacements:
                rkey = key[1:-1].lower() # remove the first, last char and lowercase
                if "gun_"+rkey in md:
                    replacements[key] = md["gun_"+rkey]
                else:
                    replacements[key] = "" # we replace by an empty string
    else:
        _logger.info("gun help: metadata file not found : %s", ES_GUNS_ART_METADATA)

    # if we use the image without any customization, copy the backup
    # we did of it to the destination
    if (use_guns or guns) and not customize_texts and default_gun_help_path.exists():
        shutil.copyfile(default_gun_help_path, target_path)
        _logger.info("gun help: using cache image : %s", default_gun_help_path)
        return

    # remove any existing file
    if target_path.exists():
        target_path.unlink()

    # don't enable if not a gun game or no gun
    if not(use_guns and guns):
        _logger.info("gun help: not generating gun help image")
        return

    _logger.info("gun help: generating gun help image")

    # take the first gun
    gun_name = guns[0].name
    GUN_HELP_DIR = Path("/usr/share/batocera/guns-overlays")
    GUN_HELP_PNG = GUN_HELP_DIR / Path(gun_name + ".png")
    GUN_HELP_INFO = GUN_HELP_DIR / Path(gun_name + ".infos")

    if not GUN_HELP_PNG.exists():
        _logger.info("gun help: image doesn't exist : %s", GUN_HELP_PNG)
        return

    # try to open the help texts
    data: _GunInfosDict = {}
    if GUN_HELP_INFO.exists():
        with GUN_HELP_INFO.open(encoding="utf-8") as file:
            data = cast('_GunInfosDict', json.load(file))

    # replace data in texts
    if "texts" in data:
        for n, _ in enumerate(data["texts"]):
            data["texts"][n]["value"] = gun_help_replace(data["texts"][n]["value"], replacements)

    img_height = int(gameResolution["height"] * img_ratio)
    _logger.info("gun help: generating image %s", target_path)
    png_to_png_with_texts(GUN_HELP_PNG, target_path, data, font_path=ttf, height=img_height)

    # save the default help as a cache
    if not customize_texts:
        shutil.copyfile(target_path, default_gun_help_path)
        _logger.info("gun help: caching file to : %s", default_gun_help_path)
