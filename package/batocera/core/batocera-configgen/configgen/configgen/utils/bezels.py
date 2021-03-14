import os
import batoceraFiles
import struct

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
