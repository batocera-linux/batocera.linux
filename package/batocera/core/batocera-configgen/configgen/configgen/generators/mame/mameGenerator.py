#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from utils.logger import get_logger
from os import path
from os import environ
import configparser
from xml.dom import minidom
import codecs
import shutil
import utils.bezels as bezelsUtil
import subprocess
from xml.dom import minidom
from PIL import Image, ImageOps
from . import mameControllers

eslog = get_logger(__name__)

class MameGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    def generate(self, system, rom, playersControllers, gameResolution):
        # Extract "<romfile.zip>"
        romBasename = path.basename(rom)
        romDirname  = path.dirname(rom)

        # Generate userdata folders if needed
        mamePaths = [ "system/configs/mame", "saves/mame", "saves/mame/nvram", "saves/mame/cfg", "saves/mame/input", "saves/mame/state", "saves/mame/diff", "saves/mame/comments", "bios/mame", "bios/mame/artwork", "cheats/mame", "saves/mame/plugins", "system/configs/mame/ctrlr", "system/configs/mame/ini", "bios/mame/artwork/crosshairs" ]
        for checkPath in mamePaths:
            if not os.path.exists("/userdata/" + checkPath + "/"):
                os.makedirs("/userdata/" + checkPath + "/")

        # Define systems that will use the MESS executable instead of MAME
        messSystems = [ "lcdgames", "gameandwatch", "cdi", "advision", "plugnplay", "megaduck", "crvision", "gamate", "pv1000", "gamecom" , "fm7", "xegs", "gamepock", "aarch", "atom", "apfm1000", "bbc", "camplynx", "adam", "arcadia", "supracan", "gmaster", "astrocde", "ti99", "tutor", "coco", "socrates", "macintosh" ]
        # If it needs a system name defined, use it here. Add a blank string if it does not (ie non-arcade, non-system ROMs)
        messSysName = [ "", "", "cdimono1", "advision", "", "megaduck", "crvision", "gamate", "pv1000", "gamecom", "fm7", "xegs", "gamepock", "aa310", "atom", "apfm1000", "bbcb", "lynx48k", "adam", "arcadia", "supracan", "gmaster", "astrocde", "ti99_4a", "tutor", "coco", "socrates", "maclc3" ]
        # For systems with a MAME system name, the type of ROM that needs to be passed on the command line (cart, tape, cdrm, etc)
        # If there are multiple ROM types (ie a computer w/disk & tape), select the default or primary type here.
        messRomType = [ "", "", "cdrm", "cart", "", "cart", "cart", "cart", "cart", "cart1", "flop1", "cart", "cart", "flop", "cass", "cart", "flop1", "cass", "cass1", "cart", "cart", "cart", "cart", "cart", "cart", "cart", "cart", "flop1" ]
        messAutoRun = [ "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 'mload""\\n', "", "", "", "", "", "", "", "", "", "" ]
        
        # Identify the current system, select MAME or MESS as needed.
        try:
            messMode = messSystems.index(system.name)
        except ValueError:
            messMode = -1
        if messMode == -1:
            commandArray =  [ "/usr/bin/mame/mame" ]
        else:
            commandArray =  [ "/usr/bin/mame/mess" ]
        
        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        commandArray += [ "-skip_gameinfo" ]
        if messMode == -1:
            commandArray += [ "-rompath",      romDirname ]
        else:
            commandArray += [ "-rompath",      romDirname + ";/userdata/bios/;/userdata/roms/mame/" ]

        # MAME various paths we can probably do better
        commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
        commandArray += [ "-fontpath",     "/usr/bin/mame/" ]               # Fonts can be left on ROM filesystem
        commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
        commandArray += [ "-pluginspath", "/usr/bin/mame/plugins/" ]
        commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
        commandArray += [ "-artpath",       "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/mame/artwork/;/userdata/decorations/" ] # first for systems ; second for overlays

        # Enable cheats
        commandArray += [ "-cheat" ]
        commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path containing the cheat.7z file

        # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
        commandArray += [ "-nvram_directory" ,    "/userdata/saves/mame/nvram/" ]

        # Set custom config path if option is selected or default path if not
        if system.isOptSet("customcfg"):
            customCfg = system.getOptBoolean("customcfg")
        else:
            customCfg = False

        if system.name == "mame":
            if customCfg:
                cfgPath = "/userdata/system/configs/mame/custom/"
            else:
                cfgPath = "/userdata/system/configs/mame/"
            if not os.path.exists("/userdata/system/configs/mame/"):
                os.makedirs("/userdata/system/configs/mame/")    
        else:
            if customCfg:
                cfgPath = "/userdata/system/configs/mame/" + messSysName[messMode]+ "/custom/"
            else:
                cfgPath = "/userdata/system/configs/mame/" + messSysName[messMode] + "/"
            if not os.path.exists("/userdata/system/configs/mame/" + messSysName[messMode] + "/"):
                os.makedirs("/userdata/system/configs/mame/" + messSysName[messMode] + "/")    
        if not os.path.exists(cfgPath):
            os.makedirs(cfgPath)

        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        if system.isOptSet("pergamecfg") and system.getOptBoolean("pergamecfg"):
            if not messMode == -1:
                if not messSysName[messMode] == "":
                    if not os.path.exists("/userdata/system/configs/mame/" + messSysName[messMode] + "/"):
                        os.makedirs("/userdata/system/configs/mame/" + messSysName[messMode]+ "/")
                    cfgPath = "/userdata/system/configs/mame/" + messSysName[messMode]+ "/" + romBasename + "/"
                    if not os.path.exists(cfgPath):
                        os.makedirs(cfgPath)
        commandArray += [ "-cfg_directory"   ,    cfgPath ]
        commandArray += [ "-input_directory" ,    "/userdata/saves/mame/input/" ]
        commandArray += [ "-state_directory" ,    "/userdata/saves/mame/state/" ]
        commandArray += [ "-snapshot_directory" , "/userdata/screenshots/" ]
        commandArray += [ "-diff_directory" ,     "/userdata/saves/mame/diff/" ]
        commandArray += [ "-comment_directory",   "/userdata/saves/mame/comments/" ]
        commandArray += [ "-homepath" ,           "/userdata/saves/mame/plugins/" ]
        commandArray += [ "-ctrlrpath" ,          "/userdata/system/configs/mame/ctrlr/" ]
        commandArray += [ "-inipath" ,            "/userdata/system/configs/mame/ini/" ]
        commandArray += [ "-crosshairpath" ,      "/userdata/bios/mame/artwork/crosshairs/" ]
        commandArray += [ "-pluginspath" ,        "/userdata/saves/mame/plugins/" ]

        # TODO These paths are not handled yet
        # TODO -swpath              path to loose software - might use if we want software list MESS support

        # BGFX video engine : https://docs.mamedev.org/advanced/bgfx.html
        if system.isOptSet("video") and system.config["video"] == "bgfx":
            commandArray += [ "-video", "bgfx" ]

            # BGFX backend
            if system.isOptSet("bgfxbackend") and system.config['bgfxbackend'] != 'automatic':
                commandArray += [ "-bgfx_backend", system.config['bgfxbackend'] ]
            else:
                commandArray += [ "-bgfx_backend", "auto" ]

            # BGFX shaders effects
            if system.isOptSet("bgfxshaders") and system.config['bgfxshaders'] != 'default':
                commandArray += [ "-bgfx_screen_chains", system.config['bgfxshaders'] ]
            else:
                commandArray += [ "-bgfx_screen_chains", "default" ]

        # Other video modes
        elif system.isOptSet("video") and system.config["video"] == "accel":
            commandArray += ["-video", "accel" ]
        else:
            commandArray += [ "-video", "opengl" ]

        # CRT / SwitchRes support
        if system.isOptSet("switchres") and system.getOptBoolean("switchres"):
            commandArray += [ "-modeline_generation" ]
            commandArray += [ "-changeres" ]
            commandArray += [ "-modesetting" ]
            commandArray += [ "-readconfig" ]
        else:
            commandArray += [ "-nomodeline_generation" ]
            commandArray += [ "-nochangeres" ]
            commandArray += [ "-noswitchres" ]

        # Rotation / TATE options
        if system.isOptSet("rotation") and system.config["rotation"] == "autoror":
            commandArray += [ "-autoror" ]
        if system.isOptSet("rotation") and system.config["rotation"] == "autorol":
            commandArray += [ "-autorol" ]
        
        # UI enable - for computer systems, the default sends all keys to the emulated system.
        # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
        # Hotkey + D-Pad Up will toggle this when in use (scroll lock key)
        if not (system.isOptSet("enableui") and not system.getOptBoolean("enableui")):
            commandArray += [ "-ui_active" ]
        
        # Finally we pass game name
        # MESS will use the full filename and pass the system & rom type parameters if needed.
        if messMode == -1:
            commandArray += [ romBasename ]
        else:
            if messSysName[messMode] == "":
                commandArray += [ romBasename ]
            else:
                # Alternate system for machines that have different configs (ie computers with different hardware)
                if system.isOptSet("altmodel"):
                    commandArray += [ system.config["altmodel"] ]
                else:
                    commandArray += [ messSysName[messMode] ]

                # Boot disk for Macintosh
                # Will use Floppy 1 or Hard Drive, depending on the disk.
                if system.name == "macintosh" and system.isOptSet("bootdisk"):
                    if system.config["bootdisk"] in [ "macos30", "macos608", "macos701", "macos75" ]:
                        bootType = "-flop1"                        
                        bootDisk = "/userdata/bios/" + system.config["bootdisk"] + ".img"
                    else:
                        bootType = "-hard"
                        bootDisk = "/userdata/bios/" + system.config["bootdisk"] + ".chd"
                    commandArray += [ bootType, bootDisk ]

                # Autostart computer games where applicable
                # Generic boot if only one type is available
                if messAutoRun[messMode] != "":
                    commandArray += [ "-autoboot_delay", "2", "-autoboot_command", messAutoRun[messMode] ]
                # bbc has different boots for floppy & cassette, no special boot for carts
                if system.name == "bbc":
                    if system.isOptSet("altromtype"):
                        if system.config["altromtype"] == "cass":
                            commandArray += [ '-autoboot_delay', '2', '-autoboot_command', '*tape\\nchain""\\n' ]
                        elif left(system.config["altromtype"], 4) == "flop":
                            commandArray += [ '-autoboot_delay',  '3',  '-autoboot_command', '*cat\\n*exec !boot\\n' ]
                    else:
                        commandArray += [ '-autoboot_delay',  '3',  '-autoboot_command', '*cat\\n*exec !boot\\n' ]
                # fm7 boots floppies, needs cassette loading
                if system.name == "fm7" and system.isOptSet("altromtype"):
                    if system.config["altromtype"] == "cass":
                        commandArray += [ '-autoboot_delay', '5', '-autoboot_command', 'LOADM”“,,R\\n' ]

                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                if system.name != "macintosh":
                    if system.isOptSet("altromtype"):
                        commandArray += [ "-" + system.config["altromtype"] ]
                    else:
                        commandArray += [ "-" + messRomType[messMode] ]
                else:
                    if system.isOptSet("bootdisk"):
                        if ((system.isOptSet("altromtype") and system.config["altromtype"] == "flop1") or not system.isOptSet("altromtype")) and system.config["bootdisk"] in [ "macos30", "macos608", "macos701", "macos75" ]:
                            commandArray += [ "-flop2" ]                            
                        elif system.isOptSet("altromtype"):
                            commandArray += [ "-" + system.config["altromtype"] ]
                        else:
                            commandArray += [ "-" + messRomType[messMode] ]
                    else:
                        if system.isOptSet("altromtype"):
                            commandArray += [ "-" + system.config["altromtype"] ]
                        else:
                            commandArray += [ "-" + messRomType[messMode] ]
                # Use the full filename for MESS ROMs
                commandArray += [ rom ]
        
        # Alternate D-Pad Mode
        if system.isOptSet("altdpad"):
            dpadMode = system.config["altdpad"]
        else:
            dpadMode = 0
        
        buttonLayout = getMameControlScheme(system, romBasename)
                
        if messMode == -1:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, "", dpadMode, buttonLayout, customCfg)
        else:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, messSysName[messMode], dpadMode, buttonLayout, customCfg)
        
        # bezels
        if 'bezel' not in system.config or system.config['bezel'] == '':
            bezelSet = None
        else:
            bezelSet = system.config['bezel']
        if system.isOptSet('forceNoBezel') and system.getOptBoolean('forceNoBezel'):
            bezelSet = None
        try:
            if messMode != -1:
                MameGenerator.writeBezelConfig(bezelSet, system, rom, messSysName[messMode])
            else:
                MameGenerator.writeBezelConfig(bezelSet, system, rom, "")
        except:
            MameGenerator.writeBezelConfig(None, system, rom, "")

        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.SAVES})

    @staticmethod
    def getRoot(config, name):
        xml_section = config.getElementsByTagName(name)

        if len(xml_section) == 0:
            xml_section = config.createElement(name)
            config.appendChild(xml_section)
        else:
            xml_section = xml_section[0]

        return xml_section

    @staticmethod
    def getSection(config, xml_root, name):
        xml_section = xml_root.getElementsByTagName(name)

        if len(xml_section) == 0:
            xml_section = config.createElement(name)
            xml_root.appendChild(xml_section)
        else:
            xml_section = xml_section[0]

        return xml_section

    @staticmethod
    def removeSection(config, xml_root, name):
        xml_section = xml_root.getElementsByTagName(name)

        for i in range(0, len(xml_section)):
            old = xml_root.removeChild(xml_section[i])
            old.unlink()

    @staticmethod
    def writeBezelConfig(bezelSet, system, rom, messSys):
        romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension

        if messSys == "":
            tmpZipDir = "/var/run/mame_artwork/" + romBase # ok, no need to zip, a folder is taken too
        else:
            tmpZipDir = "/var/run/mame_artwork/" + messSys # ok, no need to zip, a folder is taken too
        # clean, in case no bezel is set, and in case we want to recreate it
        if os.path.exists(tmpZipDir):
            shutil.rmtree(tmpZipDir)

        if bezelSet is None:
            return

        # let's generate the zip file
        os.makedirs(tmpZipDir)

        # bezels infos
        bz_infos = bezelsUtil.getBezelInfos(rom, bezelSet, system.name)
        if bz_infos is None:
            return

        # copy the png inside        
        if os.path.exists(bz_infos["layout"]):
            os.symlink(bz_infos["layout"], tmpZipDir + "/default.lay")
            pngFile = os.path.split(bz_infos["png"])[1]
            os.symlink(bz_infos["png"], tmpZipDir + "/" + pngFile)
        else:
            pngFile = "default.png"
            os.symlink(bz_infos["png"], tmpZipDir + "/default.png")
            if os.path.exists(bz_infos["info"]):
                bzInfoFile = open(bz_infos["info"], "r")
                bzInfoText = bzInfoFile.readlines()
                bz_alpha = 1.0 # Just in case it's not set in the info file
                for infoLine in bzInfoText:
                    if len(infoLine) > 7:
                        infoLineClean = (infoLine.replace('"', '')).rstrip(",\n").lstrip()
                        infoLineData = infoLineClean.split(":")
                        if infoLineData[0].lower() == "width":
                            img_width = int(infoLineData[1])
                        elif infoLineData[0].lower() == "height":
                            img_height = int(infoLineData[1])
                        elif infoLineData[0].lower() == "top":
                            bz_y = int(infoLineData[1])
                        elif infoLineData[0].lower() == "left":
                            bz_x = int(infoLineData[1])
                        elif infoLineData[0].lower() == "bottom":
                            bz_bottom = int(infoLineData[1])
                        elif infoLineData[0].lower() == "right":
                            bz_right = int(infoLineData[1])
                        elif infoLineData[0].lower() == "opacity":
                            bz_alpha = float(infoLineData[1])
                bzInfoFile.close()
                bz_width = img_width - bz_x - bz_right
                bz_height = img_height - bz_y - bz_bottom
            else:
                img_width, img_height = bezelsUtil.fast_image_size(bz_infos["png"])
                _, _, rotate = MameGenerator.getMameMachineSize(romBase, tmpZipDir)

                # assumes that all bezels are setup for 4:3H or 3:4V aspects
                if rotate == 270 or rotate == 90:
                    bz_width = int(img_height * (3 / 4))
                else:
                    bz_width = int(img_height * (4 / 3))
                bz_height = img_height
                bz_x = int((img_width - bz_width) / 2)
                bz_y = 0
                bz_alpha = 1.0

            f = open(tmpZipDir + "/default.lay", 'w')
            f.write("<mamelayout version=\"2\">\n")
            f.write("<element name=\"bezel\"><image file=\"default.png\" /></element>\n")
            f.write("<view name=\"bezel\">\n")
            f.write("<screen index=\"0\"><bounds x=\"" + str(bz_x) + "\" y=\"" + str(bz_y) + "\" width=\"" + str(bz_width) + "\" height=\"" + str(bz_height) + "\" /></screen>\n")
            f.write("<element ref=\"bezel\"><bounds x=\"0\" y=\"0\" width=\"" + str(img_width) + "\" height=\"" + str(img_height) + "\" alpha=\"" + str(bz_alpha) + "\" /></element>\n")
            f.write("</view>\n")
            f.write("</mamelayout>\n")
            f.close()

        if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
            if system.config['bezel.tattoo'] == 'system':
                try:
                    tattoo_file = '/usr/share/batocera/controller-overlays/'+system.name+'.png'
                    if not os.path.exists(tattoo_file):
                        tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
                    tattoo = Image.open(tattoo_file)
                except Exception as e:
                    eslog.error("Error opening controller overlay: {}".format(tattoo_file))
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
            output_png_file = "/tmp/bezel_tattooed.png"
            back = Image.open(tmpZipDir + "/" + pngFile)
            tattoo = tattoo.convert("RGBA")
            back = back.convert("RGBA")
            tw,th = bezelsUtil.fast_image_size(tattoo_file)
            tatwidth = int(240/1920 * img_width) # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
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
                back.paste(tattoo, (img_width-tatwidth,20), alphatat) # 20 pixels vertical margins (on 1080p)
            elif (corner.upper() == 'SE'):
                back.paste(tattoo, (img_width-tatwidth,img_height-tatheight-20), alphatat)
            elif (corner.upper() == 'SW'):
                back.paste(tattoo, (0,img_height-tatheight-20), alphatat)
            else: # default = NW
                back.paste(tattoo, (0,20), alphatat)
            imgnew = Image.new("RGBA", (img_width,img_height), (0,0,0,255))
            imgnew.paste(back, (0,0,img_width,img_height))
            imgnew.save(output_png_file, mode="RGBA", format="PNG")

            try:
                os.remove(tmpZipDir + "/" + pngFile)
            except:
                pass
            os.symlink(output_png_file, tmpZipDir + "/" + pngFile)

    @staticmethod
    def getMameMachineSize(machine, tmpdir):
        proc = subprocess.Popen(["/usr/bin/mame/mame", "-listxml", machine], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        exitcode = proc.returncode

        if exitcode != 0:
            raise Exception("mame -listxml " + machine + " failed")

        infofile = tmpdir + "/infos.xml"
        f = open(infofile, "w")
        f.write(out.decode())
        f.close()

        infos = minidom.parse(infofile)
        display = infos.getElementsByTagName('display')

        for element in display:
            iwidth  = element.getAttribute("width")
            iheight = element.getAttribute("height")
            irotate = element.getAttribute("rotate")
            return int(iwidth), int(iheight), int(irotate)

        raise Exception("display element not found")

def getMameControlScheme(system, romBasename):
    # Game list files
    mameCapcom = '/usr/lib/python3.9/site-packages/configgen/datainit/mame/mameCapcom.txt'
    mameKInstinct = '/usr/lib/python3.9/site-packages/configgen/datainit/mame/mameKInstinct.txt'
    mameMKombat = '/usr/lib/python3.9/site-packages/configgen/datainit/mame/mameMKombat.txt'
    mameNeogeo = '/usr/lib/python3.9/site-packages/configgen/datainit/mame/mameNeogeo.txt'
    mameTwinstick = '/usr/lib/python3.9/site-packages/configgen/datainit/mame/mameTwinstick.txt'
    mameRotatedstick = '/usr/lib/python3.9/site-packages/configgen/datainit/mame/mameRotatedstick.txt'

    # Controls for games with 5-6 buttons or other unusual controls
    if system.isOptSet("altlayout"):
        controllerType = system.config["altlayout"] # Option was manually selected
    else:
        controllerType = "auto"

    if controllerType in [ "default", "neomini", "neocd", "twinstick", "qbert" ]:
        return controllerType
    else:
        capcomList = set(open(mameCapcom).read().split())
        mkList = set(open(mameMKombat).read().split())
        kiList = set(open(mameKInstinct).read().split())
        neogeoList = set(open(mameNeogeo).read().split())
        twinstickList = set(open(mameTwinstick).read().split())
        qbertList = set(open(mameRotatedstick).read().split())
            
        romName = os.path.splitext(romBasename)[0]
        if romName in capcomList:
            if controllerType in [ "auto", "snes" ]:
                return "sfsnes"
            elif controllerType == "megadrive":
                return "megadrive"
            elif controllerType == "fightstick":
                return "sfstick"
        elif romName in mkList:
            if controllerType in [ "auto", "snes" ]:
                return "mksnes"
            elif controllerType == "megadrive":
                return "mkmegadrive"
            elif controllerType == "fightstick":
                return "mkstick"
        elif romName in kiList:
            if controllerType in [ "auto", "snes" ]:
                return "kisnes"
            elif controllerType == "megadrive":
                return "megadrive"
            elif controllerType == "fightstick":
                return "sfstick"
        elif romName in  neogeoList:
            return "neomini"
        elif romName in  twinstickList:
            return "twinstick"
        elif romName in  qbertList:
            return "qbert"
        else:
            if controllerType == "fightstick":
                return "fightstick"

    return "default"