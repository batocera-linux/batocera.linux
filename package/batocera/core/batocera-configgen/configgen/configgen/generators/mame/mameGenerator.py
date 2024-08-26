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
import xml.etree.ElementTree as ET
import codecs
import shutil
import utils.bezels as bezelsUtil
import subprocess
from xml.dom import minidom
from PIL import Image, ImageOps
from . import mameControllers
from pathlib import Path
import csv
import controllersConfig
import utils.videoMode as videoMode

eslog = get_logger(__name__)

class MameGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Extract "<romfile.zip>"
        romBasename = path.basename(rom)
        romDirname  = path.dirname(rom)
        (romName, romExt) = os.path.splitext(romBasename)

        softDir = "/var/run/mame_software/"
        softList = ""
        messModel = ""
        specialController = "none"
        subdirSoftList = [ "mac_hdd", "bbc_hdd", "cdi", "archimedes_hdd", "fmtowns_cd" ]

        # Generate userdata folders if needed
        mamePaths = [ "system/configs/mame", "saves/mame", "saves/mame/nvram", "saves/mame/cfg", "saves/mame/input", "saves/mame/state", "saves/mame/diff", "saves/mame/comments", "bios/mame", "bios/mame/artwork", "cheats/mame", "saves/mame/plugins", "system/configs/mame/ctrlr", "system/configs/mame/ini", "bios/mame/artwork/crosshairs" ]
        for checkPath in mamePaths:
            if not os.path.exists("/userdata/" + checkPath + "/"):
                os.makedirs("/userdata/" + checkPath + "/")

        messDataFile = '/usr/share/batocera/configgen/data/mame/messSystems.csv'
        openFile = open(messDataFile, 'r')
        messSystems = []
        messSysName = []
        messRomType = []
        messAutoRun = []
        with openFile:
            messDataList = csv.reader(openFile, delimiter=';', quotechar="'")
            for row in messDataList:
                messSystems.append(row[0])
                messSysName.append(row[1])
                messRomType.append(row[2])
                messAutoRun.append(row[3])
        
        # Identify the current system
        try:
            messMode = messSystems.index(system.name)
        except ValueError:
            messMode = -1

        if system.isOptSet("softList") and system.config["softList"] != "none":
            softList = system.config["softList"]
        else:
            softList = ""

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if system.name == 'fmtowns' and softList == '':
            romParentPath = path.basename(romDirname)
            if os.path.exists('/userdata/roms/fmtowns/{}.zip'.format(romParentPath)):
                softList = 'fmtowns_cd'

        commandArray =  [ "/usr/bin/mame/mame" ]
        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        commandArray += [ "-skip_gameinfo" ]
        if messMode == -1:
            commandArray += [ "-rompath", f"{romDirname};/userdata/bios/mame/;/userdata/bios/" ]
        else:
            if softList in subdirSoftList:
                commandArray += [ "-rompath", f"{romDirname};/userdata/bios/mame/;/userdata/bios/;/userdata/roms/mame/;/var/run/mame_software/" ]
            else:
                commandArray += [ "-rompath", f"{romDirname};/userdata/bios/mame/;/userdata/bios/;/userdata/roms/mame/" ]
        
        # MAME various paths we can probably do better
        commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
        commandArray += [ "-fontpath",     "/usr/bin/mame/" ]               # Fonts can be left on ROM filesystem
        commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
        commandArray += [ "-pluginspath", "/usr/bin/mame/plugins/;/userdata/saves/mame/plugins" ]
        commandArray += [ "-samplepath",   "/userdata/bios/mame/samples/" ] # Current batocera storage location for MAME samples
        commandArray += [ "-artpath",       "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/mame/artwork/;/userdata/decorations/" ] # first for systems ; second for overlays

        # Enable cheats
        commandArray += [ "-cheat" ]
        commandArray += [ "-cheatpath",    "/userdata/cheats/mame/" ]       # Should this point to path containing the cheat.7z file

        # logs
        commandArray += [ "-verbose" ]

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
        commandArray += [ "-inipath" ,            "/userdata/system/configs/mame/;/userdata/system/configs/mame/ini/" ]
        commandArray += [ "-crosshairpath" ,      "/userdata/bios/mame/artwork/crosshairs/" ]
        if softList != "":
            commandArray += [ "-swpath" ,        softDir ]
            commandArray += [ "-hashpath" ,      softDir + "hash/" ]

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
            commandArray += [ "-resolution", "{}x{}".format(gameResolution["width"], gameResolution["height"]) ]

        # Refresh rate options to help with screen tearing
        # syncrefresh is unlisted, it requires specific display timings and 99.9% of users will get unplayable games.
        # Leaving it so it can be set manually, for CRT or other arcade-specific display users.
        if system.isOptSet("vsync") and system.getOptBoolean("vsync"):
            commandArray += [ "-waitvsync" ]
        if system.isOptSet("syncrefresh") and system.getOptBoolean("syncrefresh"):
            commandArray += [ "-syncrefresh" ]

        # Rotation / TATE options
        if system.isOptSet("rotation") and system.config["rotation"] == "autoror":
            commandArray += [ "-autoror" ]
        if system.isOptSet("rotation") and system.config["rotation"] == "autorol":
            commandArray += [ "-autorol" ]

        # Artwork crop
        if system.isOptSet("artworkcrop") and system.getOptBoolean("artworkcrop"):
            commandArray += [ "-artwork_crop" ]

        # UI enable - for computer systems, the default sends all keys to the emulated system.
        # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
        # Hotkey + D-Pad Up will toggle this when in use (scroll lock key)
        if not (system.isOptSet("enableui") and not system.getOptBoolean("enableui")):
            commandArray += [ "-ui_active" ]

        # Load selected plugins
        pluginsToLoad = []
        if not (system.isOptSet("hiscoreplugin") and system.getOptBoolean("hiscoreplugin") == False):
            pluginsToLoad += [ "hiscore" ]
        if system.isOptSet("coindropplugin") and system.getOptBoolean("coindropplugin"):
            pluginsToLoad += [ "coindrop" ]
        if system.isOptSet("dataplugin") and system.getOptBoolean("dataplugin"):
            pluginsToLoad += [ "data" ]
        if len(pluginsToLoad) > 0:
            commandArray += [ "-plugins", "-plugin", ",".join(pluginsToLoad) ]

        # Mouse
        useMouse = False
        if (system.isOptSet('use_mouse') and system.getOptBoolean('use_mouse')) or not (messSysName[messMode] == "" or messMode == -1):
            useMouse = True
            commandArray += [ "-dial_device", "mouse" ]
            commandArray += [ "-trackball_device", "mouse" ]
            commandArray += [ "-paddle_device", "mouse" ]
            commandArray += [ "-positional_device", "mouse" ]
            commandArray += [ "-mouse_device", "mouse" ]
            commandArray += [ "-ui_mouse" ]
            if not (system.isOptSet('use_guns') and system.getOptBoolean('use_guns')):
                commandArray += [ "-lightgun_device", "mouse" ]
                commandArray += [ "-adstick_device", "mouse" ]
        else:
            commandArray += [ "-dial_device", "joystick" ]
            commandArray += [ "-trackball_device", "joystick" ]
            commandArray += [ "-paddle_device", "joystick" ]
            commandArray += [ "-positional_device", "joystick" ]
            commandArray += [ "-mouse_device", "joystick" ]
            if not (system.isOptSet('use_guns') and system.getOptBoolean('use_guns')):
                commandArray += [ "-lightgun_device", "joystick" ]
                commandArray += [ "-adstick_device", "joystick" ]
        # Multimouse option currently hidden in ES, SDL only detects one mouse.
        # Leaving code intact for testing & possible ManyMouse integration
        multiMouse = False
        if system.isOptSet('multimouse') and system.getOptBoolean('multimouse'):
            multiMouse = True
            commandArray += [ "-multimouse" ]

        # guns
        useGuns = False
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
            useGuns = True
            commandArray += [ "-lightgunprovider", "udev" ]
            commandArray += [ "-lightgun_device", "lightgun" ]
            commandArray += [ "-adstick_device", "lightgun" ]
        if system.isOptSet('offscreenreload') and system.getOptBoolean('offscreenreload'):
            commandArray += [ "-offscreen_reload" ]

        # wheels
        useWheels = False
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels'):
            useWheels = True

        if system.isOptSet('multiscreens') and system.getOptBoolean('multiscreens'):
            screens = videoMode.getScreensInfos(system.config)
            if len(screens) > 1:
                commandArray += [ "-numscreens", str(len(screens)) ]

        # Finally we pass game name
        # MESS will use the full filename and pass the system & rom type parameters if needed.
        if messSysName[messMode] == "" or messMode == -1:
            commandArray += [ romBasename ]
        else:
            messModel = messSysName[messMode]
            # Alternate system for machines that have different configs (ie computers with different hardware)
            if system.isOptSet("altmodel"):
                messModel = system.config["altmodel"]
            commandArray += [ messModel ]

            #TI-99 32k RAM expansion & speech modules - enabled by default
            if system.name == "ti99":
                commandArray += [ "-ioport", "peb" ]
                if not system.isOptSet("ti99_32kram") or (system.isOptSet("ti99_32kram") and system.getOptBoolean("ti99_32kram")):
                    commandArray += ["-ioport:peb:slot2", "32kmem"]
                if not system.isOptSet("ti99_speech") or (system.isOptSet("ti99_speech") and system.getOptBoolean("ti99_speech")):
                    commandArray += ["-ioport:peb:slot3", "speech"]

            #Laser 310 Memory Expansion & Joystick
            if system.name == "laser310":
                commandArray += ['-io', 'joystick']
                if not system.isOptSet('memslot'):
                    laser310mem = 'laser_64k'
                else:
                    laser310mem = system.config['memslot']
                commandArray += ["-mem", laser310mem]

            # BBC Joystick
            if system.name == "bbc":
                if system.isOptSet('sticktype') and system.config['sticktype'] != 'none':
                    commandArray += ["-analogue", system.config['sticktype']]
                    specialController = system.config['sticktype']

            # Apple II
            if system.name == "apple2":
                commandArray += ["-sl7", "cffa202"]
                if system.isOptSet('gameio') and system.config['gameio'] != 'none':
                    if system.config['gameio'] == 'joyport' and messModel != 'apple2p':
                        eslog.debug("Joyport joystick is only compatible with Apple II Plus")
                    else:
                        commandArray += ["-gameio", system.config['gameio']]
                        specialController = system.config['gameio']

            # RAM size (Mac excluded, special handling below)
            if system.name != "macintosh" and system.isOptSet("ramsize"):
                commandArray += [ '-ramsize', str(system.config["ramsize"]) + 'M' ]

            # Mac RAM & Image Reader (if applicable)
            if system.name == "macintosh":
                if system.isOptSet("ramsize"):
                    ramSize = int(system.config["ramsize"])
                    if messModel in [ 'maciix', 'maclc3' ]:
                        if messModel == 'maclc3' and ramSize == 2:
                            ramSize = 4
                        if messModel == 'maclc3' and ramSize > 80:
                            ramSize = 80
                        if messModel == 'maciix' and ramSize == 16:
                            ramSize = 32
                        if messModel == 'maciix' and ramSize == 48:
                            ramSize = 64
                        commandArray += [ '-ramsize', str(ramSize) + 'M' ]
                    if messModel == 'maciix':
                        imageSlot = 'nba'
                        if system.isOptSet('imagereader'):
                            if system.config["imagereader"] == "disabled":
                                imageSlot = ''
                            else:
                                imageSlot = system.config["imagereader"]
                        if imageSlot != "":
                            commandArray += [ "-" + imageSlot, 'image' ]

            if softList == "":
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

                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                # Only one drive on FMTMarty
                if system.name != "macintosh":
                    if system.isOptSet("altromtype"):
                        if messModel == "fmtmarty" and system.config["altromtype"] == "flop1":
                            commandArray += [ "-flop" ]
                        else:
                            commandArray += [ "-" + system.config["altromtype"] ]
                    elif system.name == "adam":
                        # add some logic based on the rom extension
                        rom_extension = os.path.splitext(rom)[1].lower()
                        if rom_extension == ".ddp":
                            commandArray += [ "-cass1" ]
                        elif rom_extension == ".dsk":
                            commandArray += [ "-flop1" ]
                        else:
                            commandArray += [ "-cart1" ]
                    elif system.name == "coco":
                        if romExt.casefold() == ".cas":
                            commandArray += [ "-cass" ]
                        elif romExt.casefold() == ".dsk":
                            commandArray += [ "-flop1" ]
                        else:
                            commandArray += [ "-cart" ]
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
            else:
                # Prepare software lists
                if softList != "":
                    if not os.path.exists(softDir):
                        os.makedirs(softDir)
                    for fileName in os.listdir(softDir):
                        checkFile = os.path.join(softDir, fileName)
                        if os.path.islink(checkFile):
                            os.unlink(checkFile)
                        if os.path.isdir(checkFile):
                            shutil.rmtree(checkFile)
                    if not os.path.exists(softDir + "hash/"):
                        os.makedirs(softDir + "hash/")
                    # Clear existing hashfile links
                    for hashFile in os.listdir(softDir + "hash/"):
                        if hashFile.endswith('.xml'):
                            os.unlink(softDir + "hash/" + hashFile)
                    os.symlink("/usr/bin/mame/hash/" + softList + ".xml", softDir + "hash/" + softList + ".xml")
                    if softList in subdirSoftList:
                        romPath = Path(romDirname)
                        os.symlink(str(romPath.parents[0]), softDir + softList, True)
                        commandArray += [ path.basename(romDirname) ]
                    else:
                        os.symlink(romDirname, softDir + softList, True)
                        commandArray += [ os.path.splitext(romBasename)[0] ]

            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually or FM Towns Marty.
            if system.isOptSet('addblankdisk') and system.getOptBoolean('addblankdisk'):
                if system.name == 'fmtowns':
                    blankDisk = '/usr/share/mame/blank.fmtowns'
                    targetFolder = '/userdata/saves/mame/{}'.format(system.name)
                    targetDisk = '{}/{}.fmtowns'.format(targetFolder, os.path.splitext(romBasename)[0])
                # Add elif statements here for other systems if enabled
                if not os.path.exists(targetFolder):
                    os.makedirs(targetFolder)
                if not os.path.exists(targetDisk):
                    shutil.copy2(blankDisk, targetDisk)
                # Add other single floppy systems to this if statement
                if messModel == "fmtmarty":
                    commandArray += [ '-flop', targetDisk ]
                elif (system.isOptSet('altromtype') and system.config['altromtype'] == 'flop2'):
                    commandArray += [ '-flop1', targetDisk ]
                else:
                    commandArray += [ '-flop2', targetDisk ]

            autoRunCmd = ""
            autoRunDelay = 0
            # Autostart computer games where applicable
            # bbc has different boots for floppy & cassette, no special boot for carts
            if system.name == "bbc":
                if system.isOptSet("altromtype") or softList != "":
                    if (system.isOptSet('altromtype') and system.config["altromtype"] == "cass") or softList.endswith("cass"):
                        autoRunCmd = '*tape\\nchain""\\n'
                        autoRunDelay = 2
                    elif (system.isOptSet('altromtype') and system.config["altromtype"].startswith("flop")) or softList.endswith("flop"):
                        autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                        autoRunDelay = 3
                else:
                    autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                    autoRunDelay = 3
            # fm7 boots floppies, needs cassette loading
            elif system.name == "fm7":
                if system.isOptSet("altromtype") or softList != "":
                    if (system.isOptSet('altromtype') and system.config["altromtype"] == "cass") or softList.endswith("cass"):
                        autoRunCmd = 'LOADM”“,,R\\n'
                        autoRunDelay = 5
            elif system.name == "coco":
                romType = 'cart'
                autoRunDelay = 2

                # if using software list, use "usage" for autoRunCmd (if provided)
                if softList != "":
                    softListFile = '/usr/bin/mame/hash/{}.xml'.format(softList)
                    if os.path.exists(softListFile):
                        softwarelist = ET.parse(softListFile)
                        for software in softwarelist.findall('software'):
                            if software.attrib != {}:
                                if software.get('name') == romName:
                                    for info in software.iter('info'):
                                        if info.get('name') == 'usage':
                                            autoRunCmd = info.get('value') + '\\n'

                # if still undefined, default autoRunCmd based on media type
                if autoRunCmd == "":
                    if (system.isOptSet('altromtype') and system.config["altromtype"] == "cass") or (softList != "" and softList.endswith("cass")) or romExt.casefold() == ".cas":
                        romType = 'cass'
                        if romName.casefold().endswith(".bas"):
                            autoRunCmd = 'CLOAD:RUN\\n'
                        else:
                            autoRunCmd = 'CLOADM:EXEC\\n'
                    if (system.isOptSet('altromtype') and system.config["altromtype"] == "flop1") or (softList != "" and softList.endswith("flop")) or romExt.casefold() == ".dsk":
                        romType = 'flop'
                        if romName.casefold().endswith(".bas"):
                            autoRunCmd = 'RUN \"{}\"\\n'.format(romName)
                        else:
                            autoRunCmd = 'LOADM \"{}\":EXEC\\n'.format(romName)

                # check for a user override
                autoRunFile = 'system/configs/mame/autoload/{}_{}_autoload.csv'.format(system.name, romType)
                if os.path.exists(autoRunFile):
                    openARFile = open(autoRunFile, 'r')
                    with openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row and not row[0].startswith('#'):
                                if row[0].casefold() == romName.casefold():
                                    autoRunCmd = row[1] + "\\n"
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = '/usr/share/batocera/configgen/data/mame/{}_autoload.csv'.format(softList)
                if os.path.exists(autoRunFile):
                    openARFile = open(autoRunFile, 'r')
                    with openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row[0].casefold() == os.path.splitext(romBasename)[0].casefold():
                                autoRunCmd = row[1] + "\\n"
                                autoRunDelay = 3
            if autoRunCmd != "":
                if autoRunCmd.startswith("'"):
                    autoRunCmd.replace("'", "")
                commandArray += [ "-autoboot_delay", str(autoRunDelay), "-autoboot_command", autoRunCmd ]

        # bezels
        if 'bezel' not in system.config.keys() or system.config['bezel'] == '':
            bezelSet = None
        else:
            bezelSet = system.config['bezel']
        if system.isOptSet('forceNoBezel') and system.getOptBoolean('forceNoBezel'):
            bezelSet = None
        try:
            if messMode != -1:
                MameGenerator.writeBezelConfig(bezelSet, system, rom, messSysName[messMode], gameResolution, controllersConfig.gunsBordersSizeName(guns, system.config))
            else:
                MameGenerator.writeBezelConfig(bezelSet, system, rom, "", gameResolution, controllersConfig.gunsBordersSizeName(guns, system.config))
        except:
            MameGenerator.writeBezelConfig(None, system, rom, "", gameResolution, controllersConfig.gunsBordersSizeName(guns, system.config))

        buttonLayout = getMameControlScheme(system, romBasename)

        if messMode == -1:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, "", buttonLayout, customCfg, specialController, bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)
        else:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, messModel, buttonLayout, customCfg, specialController, bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)

        # Change directory to MAME folder (allows data plugin to load properly)
        os.chdir('/usr/bin/mame')
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
    def writeBezelConfig(bezelSet, system, rom, messSys, gameResolution, gunsBordersSize):
        romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension

        if messSys == "":
            tmpZipDir = "/var/run/mame_artwork/" + romBase # ok, no need to zip, a folder is taken too
        else:
            tmpZipDir = "/var/run/mame_artwork/" + messSys # ok, no need to zip, a folder is taken too
        # clean, in case no bezel is set, and in case we want to recreate it
        if os.path.exists(tmpZipDir):
            shutil.rmtree(tmpZipDir)

        if bezelSet is None and gunsBordersSize is None:
            return

        # let's generate the zip file
        os.makedirs(tmpZipDir)

        # bezels infos
        if bezelSet is None:
            if gunsBordersSize is not None:
                bz_infos = None
            else:
                return
        else:
            bz_infos = bezelsUtil.getBezelInfos(rom, bezelSet, system.name, 'mame')
            if bz_infos is None:
                if gunsBordersSize is None:
                    return

        # create an empty bezel
        if bz_infos is None:
            overlay_png_file = "/tmp/bezel_transmame_black.png"
            bezelsUtil.createTransparentBezel(overlay_png_file, gameResolution["width"], gameResolution["height"])
            bz_infos = { "png": overlay_png_file }

        # copy the png inside
        if "mamezip" in bz_infos and os.path.exists(bz_infos["mamezip"]):
            if messSys == "":
                artFile = "/var/run/mame_artwork/" + romBase + ".zip"
            else:
                artFile = "/var/run/mame_artwork/" + messSys + ".zip"
            if os.path.exists(artFile):
                if os.islink(artFile):
                    os.unlink(artFile)
                else:
                    os.remove(artFile)
            os.symlink(bz_infos["mamezip"], artFile)
            # hum, not nice if guns need borders
            return
        elif "layout" in bz_infos and os.path.exists(bz_infos["layout"]):
            os.symlink(bz_infos["layout"], tmpZipDir + "/default.lay")
            pngFile = os.path.split(bz_infos["png"])[1]
            os.symlink(bz_infos["png"], tmpZipDir + "/" + pngFile)
        else:
            pngFile = "default.png"
            os.symlink(bz_infos["png"], tmpZipDir + "/default.png")
            if "info" in bz_infos and os.path.exists(bz_infos["info"]):
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
                    eslog.error(f"Error opening controller overlay: {tattoo_file}")
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

        # borders for guns
        if gunsBordersSize is not None:
            output_png_file = "/tmp/bezel_gunborders.png"
            innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
            borderSize = bezelsUtil.gunBorderImage(tmpZipDir + "/" + pngFile, output_png_file, None, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
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
    mameCapcom = '/usr/share/batocera/configgen/data/mame/mameCapcom.txt'
    mameKInstinct = '/usr/share/batocera/configgen/data/mame/mameKInstinct.txt'
    mameMKombat = '/usr/share/batocera/configgen/data/mame/mameMKombat.txt'
    mameNeogeo = '/usr/share/batocera/configgen/data/mame/mameNeogeo.txt'
    mameTwinstick = '/usr/share/batocera/configgen/data/mame/mameTwinstick.txt'
    mameRotatedstick = '/usr/share/batocera/configgen/data/mame/mameRotatedstick.txt'

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
            if controllerType == "megadrive":
                return "mddefault"

    return "default"
