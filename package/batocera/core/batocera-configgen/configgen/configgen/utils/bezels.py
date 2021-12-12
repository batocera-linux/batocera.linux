import os
import batoceraFiles
import struct
from PIL import Image, ImageOps

def getBezelInfos(rom, bezel, systemName):
    # by order choose :
    # rom name in the system subfolder of the user directory (gb/mario.png)
    # rom name in the system subfolder of the system directory (gb/mario.png)
    # rom name in the user directory (mario.png)
    # rom name in the system directory (mario.png)
    # system name in the user directory (gb.png)
    # system name in the system directory (gb.png)
    # default name (default.png)
    # else return
    romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
    overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".info"
    overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".png"
    bezel_game = True
    if not os.path.exists(overlay_png_file):
        overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + systemName + "/" + romBase + ".info"
        overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + systemName + "/" + romBase + ".png"
        bezel_game = True
        if not os.path.exists(overlay_png_file):
            overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".info"
            overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".png"
            bezel_game = True
            if not os.path.exists(overlay_png_file):
                overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + romBase + ".info"
                overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + romBase + ".png"
                bezel_game = True
                if not os.path.exists(overlay_png_file):
                    overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".info"
                    overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".png"
                    bezel_game = False
                    if not os.path.exists(overlay_png_file):
                        overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".info"
                        overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".png"
                        bezel_game = False
                        if not os.path.exists(overlay_png_file):
                            overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/default.info"
                            overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/default.png"
                            bezel_game = True
                            if not os.path.exists(overlay_png_file):
                                overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/default.info"
                                overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default.png"
                                bezel_game = True
                                if not os.path.exists(overlay_png_file):
                                    return None
    return { "png": overlay_png_file, "info": overlay_info_file, "specific_to_game": bezel_game }

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

def resizeImage(input_png, output_png, screen_width, screen_height):
    imgin = Image.open(input_png)
    if imgin.mode != "RGBA":
        # TheBezelProject have Palette + alpha, not RGBA. PIL can't convert from P+A to RGBA.
        # Even if it can load P+A, it can't save P+A as PNG. So we have to recreate a new image to adapt it.
        if not 'transparency' in imgin.info:
            raise Exception("no transparent layer for the viewport, abort")
        alpha = imgin.split()[-1]  # alpha from original palette + alpha
        ix,iy = fast_image_size(input_png)
        imgnew = Image.new("RGBA", (ix,iy), (0,0,0,255))
        imgnew.paste(alpha, (0,0,ix,iy))
        imgout = imgin.resize((screen_width, screen_height), Image.ANTIALIAS)
        imgout.save(output_png, mode="RGBA", format="PNG")
    else:
        imgout = imgin.resize((screen_width, screen_height), Image.ANTIALIAS)
        imgout.save(output_png, mode="RGBA", format="PNG")

def padImage(input_png, output_png, screen_width, screen_height, bezel_width, bezel_height):
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
      # TheBezelProject have Palette + alpha, not RGBA. PIL can't convert from P+A to RGBA.
      # Even if it can load P+A, it can't save P+A as PNG. So we have to recreate a new image to adapt it.
      if not 'transparency' in imgin.info:
          raise Exception("no transparent layer for the viewport, abort")
      alpha = imgin.split()[-1]  # alpha from original palette + alpha
      ix,iy = fast_image_size(input_png)
      imgnew = Image.new("RGBA", (ix,iy), (0,0,0,255))
      imgnew.paste(alpha, (0,0,ix,iy))
      imgout = ImageOps.expand(imgnew, border=(borderw, borderh, xoffset-borderw, yoffset-borderh), fill=fillcolor)
      imgout.save(output_png, mode="RGBA", format="PNG")
  else:
      imgout = ImageOps.expand(imgin, border=(borderw, borderh, xoffset-borderw, yoffset-borderh), fill=fillcolor)
      imgout.save(output_png, mode="RGBA", format="PNG")

def tatooImageAdapt(input_png, output_png, system):
  if system.config['bezel.tattoo'] == 'system':
      try:
          tattoo_file = '/usr/share/batocera/controller-overlays/'+system.name+'.png'
          if not os.path.exists(tattoo_file):
              tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening controller overlay: {}".format('tattoo_file'))
  elif system.config['bezel.tattoo'] == 'custom' and os.path.exists(system.config['bezel.tattoo_file']):
      try:
          tattoo_file = system.config['bezel.tattoo_file']
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening custom file: {}".format('tattoo_file'))
  else:
      try:
          tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening custom file: {}".format('tattoo_file'))
  back = Image.open(input_png)
  tattoo = tattoo.convert("RGBA")
  back = back.convert("RGBA")
  w,h = fast_image_size(input_png)
  tw,th = fast_image_size(tattoo_file)
  tatwidth = int(225/1920 * w)
  pcent = float(tatwidth / tw)
  tatheight = int(float(th) * pcent)
  tattoo = tattoo.resize((tatwidth,tatheight), Image.ANTIALIAS)
  alpha = back.split()[-1]
  alphatat = tattoo.split()[-1]
  if system.isOptSet('bezel.tattoo_corner'):
      corner = system.config['bezel.tattoo_corner']
  else:
      corner = 'NW'
  if (corner.upper() == 'NE'):
      back.paste(tattoo, (w-tatwidth,20), alphatat) # 20 pixels vertical margins (on 1080p)
  elif (corner.upper() == 'SE'):
      back.paste(tattoo, (w-tatwidth,h-tatheight-20), alphatat)
  elif (corner.upper() == 'SW'):
      back.paste(tattoo, (0,h-tatheight-20), alphatat)
  else: # default = NW
      back.paste(tattoo, (0,20), alphatat)
  imgnew = Image.new("RGBA", (w,h), (0,0,0,255))
  imgnew.paste(back, (0,0,w,h))
  imgnew.save(output_png, mode="RGBA", format="PNG")

def tatooImage(input_png, system):
  if system.config['bezel.tattoo'] == 'system':
      try:
          tattoo_file = '/usr/share/batocera/controller-overlays/'+system.name+'.png'
          if not os.path.exists(tattoo_file):
              tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening controller overlay: {}".format('tattoo_file'))
  elif system.config['bezel.tattoo'] == 'custom' and os.path.exists(system.config['bezel.tattoo_file']):
      try:
          tattoo_file = system.config['bezel.tattoo_file']
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening custom file: {}".format('tattoo_file'))
  else:
      try:
          tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
          tattoo = Image.open(tattoo_file)
      except:
          eslog.error("Error opening custom file: {}".format('tattoo_file'))
  back = Image.open(input_png)
  tattoo = tattoo.convert("RGBA")
  back = back.convert("RGBA")
  w,h = fast_image_size(input_png)
  tw,th = fast_image_size(tattoo_file)
  tatwidth = int(225/1920 * w)
  pcent = float(tatwidth / tw)
  tatheight = int(float(th) * pcent)
  tattoo = tattoo.resize((tatwidth,tatheight), Image.ANTIALIAS)
  alpha = back.split()[-1]
  alphatat = tattoo.split()[-1]
  if system.isOptSet('bezel.tattoo_corner'):
      corner = system.config['bezel.tattoo_corner']
  else:
      corner = 'NW'
  if (corner.upper() == 'NE'):
      back.paste(tattoo, (w-tatwidth,20), alphatat) # 20 pixels vertical margins (on 1080p)
  elif (corner.upper() == 'SE'):
      back.paste(tattoo, (w-tatwidth,h-tatheight-20), alphatat)
  elif (corner.upper() == 'SW'):
      back.paste(tattoo, (0,h-tatheight-20), alphatat)
  else: # default = NW
      back.paste(tattoo, (0,20), alphatat)
  imgnew = Image.new("RGBA", (w,h), (0,0,0,255))
  imgnew.paste(back, (0,0,w,h))
  imgnew.save(input_png, mode="RGBA", format="PNG")
