from __future__ import annotations

import logging
import struct
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from PIL import Image, ImageOps

from ..batoceraPaths import BATOCERA_SHARE_DIR, SYSTEM_DECORATIONS, USER_DECORATIONS
from .videoMode import getAltDecoration

if TYPE_CHECKING:
    from collections.abc import Mapping

    from PIL.ImageFile import ImageFile

    from ..Emulator import Emulator

eslog = logging.getLogger(__name__)

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
                    if altDecoration != 0:
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
                            if altDecoration != 0:
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
    eslog.debug(f"Original bezel file used: {overlay_png_file!s}")
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
    eslog.debug(f"Resizing bezel: image mode {imgin.mode}")
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        imgout = imgin.resize((screen_width, screen_height), Image.BICUBIC)
        imgout.save(output_png, mode="RGBA", format="PNG")

def padImage(input_png: str | Path, output_png: str | Path, screen_width: int, screen_height: int, bezel_width: int, bezel_height: int, bezel_stretch: bool = False) -> None:
    imgin = Image.open(input_png)
    fillcolor = 'black'
    eslog.debug(f"Padding bezel: image mode {imgin.mode}")
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        if bezel_stretch:
          imgout = ImageOps.fit(imgin, (screen_width, screen_height))
        else:
          imgout = ImageOps.pad(imgin, (screen_width, screen_height), color=fillcolor, centering=(0.5,0.5))
        imgout.save(output_png, mode="RGBA", format="PNG")

def tatooImage(input_png: str | Path, output_png: str | Path, system: Emulator) -> None:
  if system.config['bezel.tattoo'] == 'system':
      try:
          tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{system.name}.png'
          if not tattoo_file.exists():
              tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error(f"Error opening controller overlay: {tattoo_file}")
  elif system.config['bezel.tattoo'] == 'custom' and (tattoo_file := Path(system.config['bezel.tattoo_file'])).exists():
      try:
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error(f"Error opening custom file: {tattoo_file}")
  else:
      try:
          tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error(f"Error opening custom file: {tattoo_file}")
  # Open the existing bezel...
  back = Image.open(input_png)
  # Convert it otherwise it implodes later on...
  back = back.convert("RGBA")
  tattoo = tattoo.convert("RGBA")
  # Quickly grab the sizes.
  w,h = fast_image_size(input_png)
  tw,th = fast_image_size(tattoo_file)
  if "bezel.resize_tattoo" in system.config and system.config['bezel.resize_tattoo'] == 0:
      # Maintain the image's original size.
      # Failsafe for if the image is too large.
      if tw > w or th > h:
          # Limit width to that of the bezel and crop the rest.
          pcent = float(w / tw)
          th = int(float(th) * pcent)
          # Resize the tattoo to the calculated size.
          tattoo = tattoo.resize((w,th), Image.BICUBIC)
  else:
      # Resize to be slightly smaller than the bezel's column.
      twtemp = int((225/1920) * w)
      pcent = float(twtemp / tw)
      th = int(float(th) * pcent)
      tattoo = tattoo.resize((twtemp,th), Image.BICUBIC)
      tw = twtemp
  # Create a new blank canvas that is the same size as the bezel for later compositing (they are required to be the same size).
  tattooCanvas = Image.new("RGBA", back.size)
  # Margin for the tattoo
  margin = int((20 / 1080) * h)
  if system.isOptSet('bezel.tattoo_corner'):
      corner = system.config['bezel.tattoo_corner']
  else:
      corner = 'NW'
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
  if not 'transparency' in imgin.info:
      raise Exception("no transparent pixels in the image, abort")
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

def gunBordersSize(bordersSize: str) -> tuple[int, int]:
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

def gunsBordersColorFomConfig(config: Mapping[str, object]) -> str:
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
    imgnewdraw = ImageDraw.Draw(imgnew)
    imgnew.save(output_png, mode="RGBA", format="PNG")
