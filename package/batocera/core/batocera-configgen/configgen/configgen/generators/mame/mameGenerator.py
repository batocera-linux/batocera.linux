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

    def generate(self, system, rom, playersControllers, gameResolution):

        # Extract "<romfile.zip>"
        romBasename = path.basename(rom)
        romDirname  = path.dirname(rom)

        # Generate userdata folders if needed
        if not os.path.exists("/userdata/system/configs/mame/"):
            os.makedirs("/userdata/system/configs/mame/")
        if not os.path.exists("/userdata/saves/mame/"):
            os.makedirs("/userdata/saves/mame/")
        if not os.path.exists("/userdata/saves/mame/nvram/"):
            os.makedirs("/userdata/saves/mame/nvram")
        if not os.path.exists("/userdata/saves/mame/cfg/"):
            os.makedirs("/userdata/saves/mame/cfg/")
        if not os.path.exists("/userdata/saves/mame/input/"):
            os.makedirs("/userdata/saves/mame/input/")
        if not os.path.exists("/userdata/saves/mame/state/"):
            os.makedirs("/userdata/saves/mame/state/")
        if not os.path.exists("/userdata/saves/mame/diff/"):
            os.makedirs("/userdata/saves/mame/diff/")
        if not os.path.exists("/userdata/saves/mame/comments/"):
            os.makedirs("/userdata/saves/mame/comments/")

        # Define systems that will use the MESS executable instead of MAME
        messSystems = [ "lcdgames", "gameandwatch", "cdi", "advision", "tvgames", "megaduck", "crvision", "gamate", "pv1000", "gamecom" , "fm7", "xegs", "gamepock", "aarch", "atom", "apfm1000", "bbc", "camplynx", "adam", "arcadia", "supracan", "gmaster", "astrocde", "ti99", "tutor", "coco", "socrates" ]
        # If it needs a system name defined, use it here. Add a blank string if it does not (ie non-arcade, non-system ROMs)
        messSysName = [ "", "", "cdimono1", "advision", "", "megaduck", "crvision", "gamate", "pv1000", "gamecom", "fm7", "xegs", "gamepock", "aa310", "atom", "apfm1000", "bbcb", "lynx48k", "adam", "arcadia", "supracan", "gmaster", "astrocde", "ti99_4a", "tutor", "coco", "socrates" ]
        # For systems with a MAME system name, the type of ROM that needs to be passed on the command line (cart, tape, cdrm, etc)
        # If there are multiple ROM types (ie a computer w/disk & tape), select the default or primary type here.
        messRomType = [ "", "", "cdrm", "cart", "", "cart", "cart", "cart", "cart", "cart1", "flop1", "cart", "cart", "flop", "cass", "cart", "flop1", "cass", "cass1", "cart", "cart", "cart", "cart", "cart", "cart", "cart", "cart" ]
        messAutoRun = [ "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", 'mload""\\n', "", "", "", "", "", "", "", "", "" ]
        
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
        commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path or cheat.7z file ?
        commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
        commandArray += [ "-artpath",       "/userdata/decorations/;/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/mame/artwork/" ] # first for systems ; second for overlays

        # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
        commandArray += [ "-nvram_directory" ,    "/userdata/saves/mame/nvram/" ]
        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        cfgPath = "/userdata/system/configs/mame/"
        if system.isOptSet("pergamecfg") and system.getOptBoolean("pergamecfg"):
            if not messMode == -1:
                if not messSysName[messMode] == "":
                    if not os.path.exists("/userdata/system/configs/mame/" + messSysName[messMode] + "/"):
                        os.makedirs("/userdata/system/configs/mame/" + messSysName[messMode] + "/")
                    cfgPath = "/userdata/system/configs/mame/" + messSysName[messMode] + "/" + romBasename + "/"
                    if not os.path.exists(cfgPath):
                        os.makedirs(cfgPath)
        commandArray += [ "-cfg_directory"   ,    cfgPath ]
        commandArray += [ "-input_directory" ,    "/userdata/saves/mame/input/" ]
        commandArray += [ "-state_directory" ,    "/userdata/saves/mame/state/" ]
        commandArray += [ "-snapshot_directory" , "/userdata/screenshots/" ]
        commandArray += [ "-diff_directory" ,     "/userdata/saves/mame/diff/" ]
        commandArray += [ "-comment_directory",   "/userdata/saves/mame/comments/" ]

        # TODO These paths are not handled yet
        # TODO -homepath            path to base folder for plugin data (read/write)
        # TODO -ctrlrpath           path to controller definitions
        # TODO -inipath             path to ini files
        # TODO -crosshairpath       path to crosshair files
        # TODO -pluginspath         path to plugin files
        # TODO -swpath              path to loose software

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
                if system.name == "fm7" and system.isOptSet("altromtype") and system.config["altromtype"] == "cass":
                    commandArray += [ '-autoboot_delay', '5', '-autoboot_command', 'LOADM”“,,R\\n' ]
                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
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
        
        # Controls for games with 5-6 buttons
        if system.isOptSet("altlayout"):
            buttonLayout = system.config["altlayout"] # Option was manually selected
        else:
            romName = os.path.splitext(romBasename)[0]
            if romName in [ "ts2", "ts2ja", "ts2j", "ts2ua", "ts2u", "kikaioh", "dstlka", "dstlk", "dstlkh", "dstlkur1", "dstlku", "hsf2a", "hsf2j1", "hsf2j", 
                "hsf2", "jojojr2", "jojojr1", "jojoj", "jojobanr1", "jojobajr1", "jojoban", "jojobaj", "jojobaner1", "jojobar1", "jojobane", "jojoba", "jojonr2", 
                "jojoar2", "jojonr1", "jojoar1", "jojon", "jojoa", "jojor2", "jojor1", "jojo", "jojour2", "jojour1", "jojou", "msha", "mshbr1", "mshb", "msh", "mshh", 
                "mshjr1", "mshj", "mshu", "mshvsfa1", "mshvsfa", "mshvsfb1", "mshvsfb", "mshvsf", "mshvsfh", "mshvsfj2", "mshvsfj1", "mshvsfj", "mshvsfu1", "mshvsfu", 
                "mvscar1", "mvsca", "mvscb", "mvscr1", "mvsc", "mvsch", "mvscjr1", "mvscj", "mvscjsing", "mvscur1", "mvscu", "nwarra", "nwarrb", "nwarr", "nwarrh", 
                "nwarru", "plsmaswda", "plsmaswd", "redearthr1", "redearth", "ringdesta", "ringdestb", "ringdest", "ringdesth", "rvschoola", "rvschool", "rvschoolu", 
                "jgakuen1", "jgakuen", "stargld2", "stargladj", "starglad", "sfa2", "sfa2ur1", "sfa2u", "sfa3b", "sfa3", "sfa3hr1", "sfa3h", "sfa3us", "sfa3ur1", 
                "sfa3u", "sfar3", "sfar2", "sfar1", "sfa", "sfau", "sfexa", "sfex", "sfexj", "sfexu", "sfexpj1", "sfexpj", "sfexpu1", "sfexp", "sfex2a", "sfex2", 
                "sfex2h", "sfex2j", "sfex2u1", "sfex2u", "sfex2pa", "sfex2p", "sfex2ph", "sfex2pj", "sfex2pu", "sf2ja", "sf2jc", "sf2jf", "sf2jh", "sf2j", "sf2j17", 
                "sf2jl", "sf2ua", "sf2ub", "sf2ue", "sf2uc", "sf2ud", "sf2uf", "sf2ug", "sf2uh", "sf2ui", "sf2uk", "sf2um", "sf2em", "sf2en", "sf2ea", "sf2eb", "sf2ee", 
                "sf2ed", "sf2ef", "sf2", "sf2hfj", "sf2ceja", "sf2cejb", "sf2cejc", "sf2cet", "sf2ceua", "sf2ceub", "sf2ceuc", "sf2ceea", "sf2ce", "sf2hfu", "sf2hf", 
                "sfiii2n", "sfiii2j", "sfiii2", "sfiii3r1", "sfiii3", "sfiii3nr1", "sfiii3jr1", "sfiii3n", "sfiii3j", "sfiii3ur1", "sfiii3u", "sfiiin", "sfiiina", 
                "sfiiia", "sfiii", "sfiiih", "sfiiij", "sfiiiu", "sfzar1", "sfza", "sfzbr1", "sfzb", "sfzhr1", "sfzh", "sfzjr2", "sfzjr1", "sfzj", "sfz2a", "sfz2br1", 
                "sfz2b", "sfz2h", "sfz2jr1", "sfz2j", "sfz2n", "sfz2alr1", "sfz2al", "sfz2alb", "sfz2alh", "sfz2alj", "sfz3ar1", "sfz3a", "sfz3jr2", "sfz3jr1", "sfz3j", 
                "smbombr1", "smbomb", "ssf2ta", "ssf2th", "ssf2tur1", "ssf2tu", "ssf2t", "ssf2xjr1r", "ssf2xjr1", "ssf2xj", "ssf2ar1", "ssf2a", "ssf2h", "ssf2jr2", 
                "ssf2jr1", "ssf2j", "ssf2u", "ssf2r1", "ssf2", "ssf2tba", "ssf2tbh", "ssf2tbj1", "ssf2tbj", "ssf2tbu", "ssf2tbr1", "ssf2tb", "techromna", "techromn", 
                "techromnu", "vhunt2r1", "vhunt2", "vhuntjr2", "vhuntjr1s", "vhuntjr1", "vhuntj", "vsav2", "vsava", "vsavb", "vsav", "vsavh", "vsavj", "vsavu", "vampjr1", 
                "vampja", "vampj", "warzardr1", "warzard", "xmvsfar3", "xmvsfar2", "xmvsfar1", "xmvsfa", "xmvsfb", "xmvsfr1", "xmvsf", "xmvsfh", "xmvsfjr3", "xmvsfjr2", 
                "xmvsfjr1", "xmvsfj", "xmvsfur2", "xmvsfur1", "xmvsfu", "xmcotaar2", "xmcotaar1", "xmcotaa", "xmcotab", "xmcotar1", "xmcota", "xmcotahr1", "xmcotah", 
                "xmcotajr", "xmcotaj3", "xmcotaj2", "xmcotaj1", "xmcotaj", "xmcotau" ]:
                buttonLayout = 1 # Capcom 6 button
            elif romName in [ "mknifty666", "mknifty", "mkprot4", "mkprot8", "mkprot9", "mkrep", "mkla1", "mkla2", "mkla3", "mkla4", "mkr4", "mk", "mkyturboe",
                "mkyturbo", "mktturbo", "mkyawdim", "mkyawdim2", "mkyawdim3", "mkyawdim4", "mk3p40", "mk3r10", "mk3r20", "mk3", "mk4b", "mk4a", "mk4", "mk2r11", "mk2r14",
                "mk2r20", "mk2r21", "mk2r30", "mk2r31e", "mk2", "mk2r32e", "mk2r42", "mk2r91", "mk2chal", "umk3r10", "umk3r11", "umk3" ]:
                buttonLayout = 2 # Mortal Kombat 5/6 button
            elif romName in [ "kinst", "kinst2", "kinst2uk" ]:
                buttonLayout = 3 # Killer Inistinct 6 button
            else:
                buttonLayout = 0 # Default layout if it's not a recognized game
        
        if messMode == -1:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, "", dpadMode, buttonLayout)
        else:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, messSysName[messMode], dpadMode, buttonLayout)
        
        # bezels
        if 'bezel' not in system.config or system.config['bezel'] == '':
            bezel = None
        else:
            bezel = system.config['bezel']
        if system.isOptSet('forceNoBezel') and system.getOptBoolean('forceNoBezel'):
            bezel = None
        try:
            MameGenerator.writeBezelConfig(bezel, system, rom)
        except:
            MameGenerator.writeBezelConfig(None, system, rom)

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
    def writeBezelConfig(bezel, system, rom):
        romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension

        tmpZipDir = "/var/run/mame_artwork/" + romBase # ok, no need to zip, a folder is taken too
        # clean, in case no bezel is set, and in case we want to recreate it
        if os.path.exists(tmpZipDir):
            shutil.rmtree(tmpZipDir)

        if bezel is None:
            return

        # let's generate the zip file
        os.makedirs(tmpZipDir)

        # bezels infos
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name)
        if bz_infos is None:
            return

        # copy the png inside
        os.symlink(bz_infos["png"], tmpZipDir + "/default.png")

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
            back = Image.open(tmpZipDir + "/default.png")
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
                os.remove(tmpZipDir + "/default.png")
            except:
                pass
            os.symlink(output_png_file, tmpZipDir + "/default.png")

        f = open(tmpZipDir + "/default.lay", 'w')
        f.write("<mamelayout version=\"2\">")
        f.write("<element name=\"bezel\"><image file=\"default.png\" /></element>")
        f.write("<view name=\"bezel\">")
        f.write("<screen index=\"0\"><bounds x=\"" + str(bz_x) + "\" y=\"" + str(bz_y) + "\" width=\"" + str(bz_width) + "\" height=\"" + str(bz_height) + "\" /></screen>")
        f.write("<bezel element=\"bezel\"><bounds x=\"0\" y=\"0\" width=\"" + str(img_width) + "\" height=\"" + str(img_height) + "\" /></bezel>")
        f.write("</view>")
        f.write("</mamelayout>")
        f.close()

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
