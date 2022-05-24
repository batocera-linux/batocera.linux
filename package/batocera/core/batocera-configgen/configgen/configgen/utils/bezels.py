import os
import batoceraFiles
import struct
from PIL import Image, ImageOps
from .logger import get_logger
from .videoMode import getGameSpecial

eslog = get_logger(__name__)

def getBezelInfos(rom, bezel, systemName, retroarch = False):
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
    gameSpecial = getGameSpecial(systemName, rom, retroarch)
    romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
    overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".info"
    overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".png"
    overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".lay"
    overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".zip"
    bezel_game = True
    if not os.path.exists(overlay_png_file):
        overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + systemName + "/" + romBase + ".info"
        overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + systemName + "/" + romBase + ".png"
        overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".lay"
        overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".zip"
        bezel_game = True
        if not os.path.exists(overlay_png_file):
            overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".info"
            overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".png"
            overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".lay"
            overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".zip"
            bezel_game = True
            if not os.path.exists(overlay_png_file):
                overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + romBase + ".info"
                overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + romBase + ".png"
                overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".lay"
                overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".zip"
                bezel_game = True
                if not os.path.exists(overlay_png_file):
                    if gameSpecial != 0:
                      overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".info"
                      overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".png"
                      overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".lay"
                      overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".zip"
                      bezel_game = False
                    if not os.path.exists(overlay_png_file):
                        overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".info"
                        overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".png"
                        overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".lay"
                        overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".zip"
                        bezel_game = False
                        if not os.path.exists(overlay_png_file):
                            if gameSpecial != 0:
                              overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".info"
                              overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".png"
                              overlay_layout_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".lay"
                              overlay_mamezip_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + "-" + str(gameSpecial) + ".zip"
                              bezel_game = False
                            if not os.path.exists(overlay_png_file):
                                overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".info"
                                overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".png"
                                overlay_layout_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".lay"
                                overlay_mamezip_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".zip"
                                bezel_game = False
                                if not os.path.exists(overlay_png_file):
                                    overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/default-" + str(gameSpecial) + ".info"
                                    overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/default-" + str(gameSpecial) + ".png"
                                    overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/default-" + str(gameSpecial) + ".lay"
                                    overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/default-" + str(gameSpecial) + ".zip"
                                    bezel_game = True
                                    if not os.path.exists(overlay_png_file):
                                      overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/default.info"
                                      overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/default.png"
                                      overlay_layout_file  = batoceraFiles.overlayUser + "/" + bezel + "/default.lay"
                                      overlay_mamezip_file  = batoceraFiles.overlayUser + "/" + bezel + "/default.zip"
                                      bezel_game = True
                                      if not os.path.exists(overlay_png_file):
                                          overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/default-" + str(gameSpecial) + ".info"
                                          overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default-" + str(gameSpecial) + ".png"
                                          overlay_layout_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default-" + str(gameSpecial) + ".lay"
                                          overlay_mamezip_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default-" + str(gameSpecial) + ".zip"
                                          bezel_game = True
                                          if not os.path.exists(overlay_png_file):
                                            overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/default.info"
                                            overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default.png"
                                            overlay_layout_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default.lay"
                                            overlay_mamezip_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default.zip"
                                            bezel_game = True
                                            if not os.path.exists(overlay_png_file):
                                              return None
    eslog.debug("Original bezel file used: {}".format(overlay_png_file))
    return { "png": overlay_png_file, "info": overlay_info_file, "layout": overlay_layout_file, "mamezip": overlay_mamezip_file, "specific_to_game": bezel_game }

# Much faster than PIL Image.size
def fast_image_size(image_file):
    if not os.path.exists(image_file):
        return -1, -1
    with open(image_file, 'rb') as fhandle:
        head = fhandle.read(32)
        if len(head) != 32:
           # corrupted header, or not a PNG
           return -1, -1
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
           # Not a PNG
           return -1, -1
        return struct.unpack('>ii', head[16:24]) #image width, height

def resizeImage(input_png, output_png, screen_width, screen_height, bezel_stretch=False):
    imgin = Image.open(input_png)
    eslog.debug("Resizing bezel: image mode {}".format(imgin.mode))
    if imgin.mode != "RGBA":
        alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
    else:
        imgout = imgin.resize((screen_width, screen_height), Image.BICUBIC)
        imgout.save(output_png, mode="RGBA", format="PNG")

def padImage(input_png, output_png, screen_width, screen_height, bezel_width, bezel_height, bezel_stretch=False):
  fillcolor = 'black'

  wratio = screen_width / float(bezel_width)
  hratio = screen_height / float(bezel_height)

  xoffset = screen_width  - bezel_width
  yoffset = screen_height - bezel_height

  borderw = 0
  borderh = 0
  if wratio > 1:
      borderw = xoffset // 2
  if hratio > 1:
      borderh = yoffset // 2
  imgin = Image.open(input_png)
  if imgin.mode != "RGBA":
      alphaPaste(input_png, output_png, imgin, fillcolor, (screen_width, screen_height), bezel_stretch)
  else:
      if bezel_stretch:
          imgout = ImageOps.fit(imgin, (screen_width, screen_height))
      else:
          imgout = ImageOps.pad(imgin, (screen_width, screen_height), color=fillcolor, centering=(0.5,0.5))
      imgout.save(output_png, mode="RGBA", format="PNG")

def tatooImage(input_png, output_png, system):
  if system.config['bezel.tattoo'] == 'system':
      try:
          tattoo_file = '/usr/share/batocera/controller-overlays/'+system.name+'.png'
          if not os.path.exists(tattoo_file):
              tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening controller overlay: {}".format(tattoo_file))
  elif system.config['bezel.tattoo'] == 'custom' and os.path.exists(system.config['bezel.tattoo_file']):
      try:
          tattoo_file = system.config['bezel.tattoo_file']
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening custom file: {}".format(tattoo_file))
  else:
      try:
          tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening custom file: {}".format(tattoo_file))
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

def alphaPaste(input_png, output_png, imgin, fillcolor, screensize, bezel_stretch):
  # screensize=(screen_width, screen_height)
  imgin = Image.open(input_png)
  # TheBezelProject have Palette + alpha, not RGBA. PIL can't convert from P+A to RGBA.
  # Even if it can load P+A, it can't save P+A as PNG. So we have to recreate a new image to adapt it.
  if not 'transparency' in imgin.info:
      raise Exception("no transparent pixels in the image, abort")
  alpha = imgin.split()[-1]  # alpha from original palette + alpha
  ix,iy = fast_image_size(input_png)
  imgnew = Image.new("RGBA", (ix,iy), (0,0,0,255))
  imgnew.paste(alpha, (0,0,ix,iy))
  if bezel_stretch:
      imgout = ImageOps.fit(imgnew, screensize)
  else:
      imgout = ImageOps.pad(imgnew, screensize, color=fillcolor, centering=(0.5,0.5))
  imgout.save(output_png, mode="RGBA", format="PNG")
