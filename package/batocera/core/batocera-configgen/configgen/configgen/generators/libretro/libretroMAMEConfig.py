#!/usr/bin/env python
from PIL import Image, ImageOps
from pathlib import Path
from settings.unixSettings import UnixSettings
from utils.logger import get_logger
from xml.dom import minidom
import xml.etree.ElementTree as ET
import Command
import batoceraFiles
import codecs
import configparser
import csv
import os
import shutil
import subprocess
import sys
import zipfile

# Define RetroPad inputs for mapping
retroPad = {
    "joystick1up":      "YAXIS_UP_SWITCH",
    "joystick1down":    "YAXIS_DOWN_SWITCH",
    "joystick1left":    "XAXIS_LEFT_SWITCH",
    "joystick1right":   "XAXIS_RIGHT_SWITCH",
    "up":               "HAT{0}UP",
    "down":             "HAT{0}DOWN",
    "left":             "HAT{0}LEFT",
    "right":            "HAT{0}RIGHT",
    "joystick2up":      "RYAXIS_NEG_SWITCH",
    "joystick2down":    "RYAXIS_POS_SWITCH",
    "joystick2left":    "RXAXIS_NEG_SWITCH",
    "joystick2right":   "RXAXIS_POS_SWITCH",
    "a":                "BUTTON1",
    "b":                "BUTTON2",
    "x":                "BUTTON3",
    "y":                "BUTTON4",
    "pageup":           "BUTTON5",
    "pagedown":         "BUTTON6",
    "l2":               "RZAXIS_POS_SWITCH",
    "r2":               "ZAXIS_POS_SWITCH",
    "l3":               "BUTTON12",
    "r3":               "BUTTON11",
    "select":           "SELECT",
    "start":            "START"
}

def generateMAMEConfigs(playersControllers, system, rom, guns):
    # Generate command line for MAME/MESS/MAMEVirtual
    commandLine = []
    romBasename = os.path.basename(rom)
    romDirname  = os.path.dirname(rom)
    (romDrivername, romExt) = os.path.splitext(romBasename)
    specialController = 'none'

    if system.config['core'] in [ 'mame', 'mess', 'mamevirtual' ]:
        corePath = 'lr-' + system.config['core']
    else:
        corePath = system.config['core']

    if system.name in [ 'mame', 'neogeo', 'lcdgames', 'plugnplay', 'vis' ]:
        # Set up command line for basic systems
        # ie. no media, softlists, etc.
        if system.getOptBoolean("customcfg"):
            cfgPath = "/userdata/system/configs/{}/custom/".format(corePath)
        else:
            cfgPath = "/userdata/saves/mame/mame/cfg/"
        if not os.path.exists(cfgPath):
            os.makedirs(cfgPath)
        if system.name == 'vis':
            commandLine += [ 'vis', '-cdrom', f'"{rom}"' ]
        else:
            commandLine += [ romDrivername ]
        commandLine += [ '-cfg_directory', cfgPath ]
        commandLine += [ '-rompath', f'"{romDirname};/userdata/bios/mame/;/userdata/bios/"' ]
        pluginsToLoad = []
        if not (system.isOptSet("hiscoreplugin") and system.getOptBoolean("hiscoreplugin") == False):
            pluginsToLoad += [ "hiscore" ]
        if system.isOptSet("coindropplugin") and system.getOptBoolean("coindropplugin"):
            pluginsToLoad += [ "coindrop" ]
        if len(pluginsToLoad) > 0:
            commandLine += [ "-plugins", "-plugin", ",".join(pluginsToLoad) ]
        messMode = -1
        messModel = ''
    else:
        # Set up command line for MESS or MAMEVirtual
        softDir = "/var/run/mame_software/"
        subdirSoftList = [ "mac_hdd", "bbc_hdd", "cdi", "archimedes_hdd", "fmtowns_cd" ]
        if system.isOptSet("softList") and system.config["softList"] != "none":
            softList = system.config["softList"]
        else:
            softList = ""

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if system.name == 'fmtowns' and softList == '':
            romParentPath = os.path.basename(romDirname)
            if os.path.exists('/userdata/roms/fmtowns/{}.zip'.format(romParentPath)):
                softList = 'fmtowns_cd'

        # Determine MESS system name (if needed)
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
        messMode = messSystems.index(system.name)

        # Alternate system for machines that have different configs (ie computers with different hardware)
        messModel = messSysName[messMode]
        if system.isOptSet("altmodel"):
            messModel = system.config["altmodel"]
        commandLine += [ messModel ]

        if messSysName[messMode] == "":
            # Command line for non-arcade, non-system ROMs (lcdgames, plugnplay)
            if system.getOptBoolean("customcfg"):
                cfgPath = "/userdata/system/configs/{}/custom/".format(corePath)
            else:
                cfgPath = "/userdata/saves/mame/mame/cfg/"
            if not os.path.exists(cfgPath):
                os.makedirs(cfgPath)
            commandLine += [ romDrivername ]
            commandLine += [ '-cfg_directory', cfgPath ]
            commandLine += [ '-rompath', f'"{romDirname};/userdata/bios/"' ]
        else:
            # Command line for MESS consoles/computers
            # TI-99 32k RAM expansion & speech modules
            # Don't enable 32k by default
            if system.name == "ti99":
                commandLine += [ "-ioport", "peb" ]
                if system.isOptSet("ti99_32kram") and system.getOptBoolean("ti99_32kram"):
                    commandLine += ["-ioport:peb:slot2", "32kmem"]
                if not system.isOptSet("ti99_speech") or (system.isOptSet("ti99_speech") and system.getOptBoolean("ti99_speech")):
                    commandLine += ["-ioport:peb:slot3", "speech"]

            #Laser 310 Memory Expansion & joystick
            if system.name == "laser310":
                commandLine += ['-io', 'joystick']
                if not system.isOptSet('memslot'):
                    laser310mem = 'laser_64k'
                else:
                    laser310mem = system.config['memslot']
                commandLine += ["-mem", laser310mem]

            # BBC Joystick
            if system.name == "bbc":
                if system.isOptSet('sticktype') and system.config['sticktype'] != 'none':
                    commandLine += ["-analogue", system.config['sticktype']]
                    specialController = system.config['sticktype']

            # Apple II
            if system.name == "apple2":
                commandLine += ["-sl7", "cffa202"]
                if system.isOptSet('gameio') and system.config['gameio'] != 'none':
                    if system.config['gameio'] == 'joyport' and messModel != 'apple2p':
                        eslog.debug("Joyport is only compatible with Apple II +")
                    else:
                        commandLine += ["-gameio", system.config['gameio']]
                        specialController = system.config['gameio']

            # RAM size (Mac excluded, special handling below)
            if system.name != "macintosh" and system.isOptSet("ramsize"):
                commandLine += [ '-ramsize', str(system.config["ramsize"]) + 'M' ]

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
                        commandLine += [ '-ramsize', str(ramSize) + 'M' ]
                    if messModel == 'maciix':
                        imageSlot = 'nba'
                        if system.isOptSet('imagereader'):
                            if system.config["imagereader"] == "disabled":
                                imageSlot = ''
                            else:
                                imageSlot = system.config["imagereader"]
                        if imageSlot != "":
                            commandLine += [ "-" + imageSlot, 'image' ]

            if softList != "":
                # Software list ROM commands
                prepSoftwareList(subdirSoftList, softList, softDir, "/userdata/bios/mame/hash", romDirname)
                if softList in subdirSoftList:
                    commandLine += [ os.path.basename(romDirname) ]
                else:
                    commandLine += [ romDrivername ]
                commandLine += [ "-rompath", f'"{softDir};/userdata/bios/"' ]
                commandLine += [ "-swpath", softDir ]
                commandLine += [ "-verbose" ]
            else:
                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                if system.name != "macintosh":
                    if system.isOptSet("altromtype"):
                        if system.config["altromtype"] == "flop1" and messModel == "fmtmarty":
                            commandLine += [ "-flop" ]
                        else:
                            commandLine += [ "-" + system.config["altromtype"] ]
                    elif system.name == "adam":
                        # add some logic based on the extension
                        rom_extension = os.path.splitext(rom)[1].lower()
                        if rom_extension == ".ddp":
                            commandLine += [ "-cass1" ]
                        elif rom_extension == ".dsk":
                            commandLine += [ "-flop1" ]
                        else:
                            commandLine += [ "-cart1" ]
                    elif system.name == "coco":
                        if romExt.casefold() == ".cas":
                            commandLine += [ "-cass" ]
                        elif romExt.casefold() == ".dsk":
                            commandLine += [ "-flop1" ]
                        else:
                            commandLine += [ "-cart" ]
                    # try to choose the right floppy for Apple2gs
                    elif system.name == "apple2gs":
                        rom_extension = os.path.splitext(rom)[1].lower()
                        if rom_extension == ".zip":
                            with zipfile.ZipFile(rom, 'r') as zip_file:
                                file_list = zip_file.namelist()
                                # assume only one file in zip
                                if len(file_list) == 1:
                                    filename = file_list[0]
                                    rom_extension = os.path.splitext(filename)[1].lower()
                        if rom_extension in [".2mg", ".2img", ".img", ".image"]:
                            commandLine += [ "-flop3" ]
                        else:
                            commandLine += [ "-flop1" ]
                    else:
                        commandLine += [ "-" + messRomType[messMode] ]
                else:
                    if system.isOptSet("bootdisk"):
                        if ((system.isOptSet("altromtype") and system.config["altromtype"] == "flop1") or not system.isOptSet("altromtype")) and system.config["bootdisk"] in [ "macos30", "macos608", "macos701", "macos75" ]:
                            commandLine += [ "-flop2" ]
                        elif system.isOptSet("altromtype"):
                            commandLine += [ "-" + system.config["altromtype"] ]
                        else:
                            commandLine += [ "-" + messRomType[messMode] ]
                    else:
                        if system.isOptSet("altromtype"):
                            commandLine += [ "-" + system.config["altromtype"] ]
                        else:
                            commandLine += [ "-" + messRomType[messMode] ]
                # Use the full filename for MESS non-softlist ROMs
                commandLine += [ f'"{rom}"' ]
                commandLine += [ "-rompath", f'"{romDirname};/userdata/bios/"' ]

                # Boot disk for Macintosh
                # Will use Floppy 1 or Hard Drive, depending on the disk.
                if system.name == "macintosh" and system.isOptSet("bootdisk"):
                    if system.config["bootdisk"] in [ "macos30", "macos608", "macos701", "macos75" ]:
                        bootType = "-flop1"
                        bootDisk = '"/userdata/bios/' + system.config["bootdisk"] + '.img"'
                    else:
                        bootType = "-hard"
                        bootDisk = '"/userdata/bios/' + system.config["bootdisk"] + '.chd"'
                    commandLine += [ bootType, bootDisk ]

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
                        commandLine += [ '-flop', targetDisk ]
                    elif (system.isOptSet('altromtype') and system.config['altromtype'] == 'flop2'):
                        commandLine += [ '-flop1', targetDisk ]
                    else:
                        commandLine += [ '-flop2', targetDisk ]

            # UI enable - for computer systems, the default sends all keys to the emulated system.
            # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
            if not (system.isOptSet("enableui") and not system.getOptBoolean("enableui")):
                commandLine += [ "-ui_active" ]

            # MESS config folder
            if system.getOptBoolean("customcfg"):
                cfgPath = "/userdata/system/configs/{}/{}/custom/".format(corePath, messSysName[messMode])
            else:
                cfgPath = "/userdata/saves/mame/mame/cfg/{}/".format(messSysName[messMode])
            if system.getOptBoolean("pergamecfg"):
                cfgPath = "/userdata/system/configs/{}/{}/{}/".format(corePath, messSysName[messMode], romBasename)
            if not os.path.exists(cfgPath):
                os.makedirs(cfgPath)
            commandLine += [ '-cfg_directory', cfgPath ]

            # Autostart via ini file
            # Init variables, delete old ini if it exists, prepare ini path
            # lr-mame does NOT support multiple ini paths
            autoRunCmd = ""
            autoRunDelay = 0
            if not os.path.exists('/userdata/saves/mame/mame/ini/'):
                     os.makedirs('/userdata/saves/mame/mame/ini/')
            if os.path.exists('/userdata/saves/mame/mame/ini/batocera.ini'):
                os.remove('/userdata/saves/mame/mame/ini/batocera.ini')
            # bbc has different boots for floppy & cassette, no special boot for carts
            if system.name == "bbc":
                if system.isOptSet("altromtype") or softList != "":
                    if (system.isOptSet("altromtype") and system.config["altromtype"] == "cass") or softList[-4:] == "cass":
                        autoRunCmd = '*tape\\nchain""\\n'
                        autoRunDelay = 2
                    elif (system.isOptSet("altromtype") and system.config["altromtype"].startswith("flop")) or "flop" in softList:
                        autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                        autoRunDelay = 3
                else:
                    autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                    autoRunDelay = 3
            # fm7 boots floppies, needs cassette loading
            elif system.name == "fm7":
                if system.isOptSet("altromtype") or softList != "":
                    if (system.isOptSet("altromtype") and system.config["altromtype"] == "cass") or softList[-4:] == "cass":
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
                                if software.get('name') == romDrivername:
                                    for info in software.iter('info'):
                                        if info.get('name') == 'usage':
                                            autoRunCmd = info.get('value') + '\\n'

                # if still undefined, default autoRunCmd based on media type
                if autoRunCmd == "":
                    if (system.isOptSet('altromtype') and system.config["altromtype"] == "cass") or (softList != "" and softList.endswith("cass")) or romExt.casefold() == ".cas":
                        romType = 'cass'
                        if romDrivername.casefold().endswith(".bas"):
                            autoRunCmd = 'CLOAD:RUN\\n'
                        else:
                            autoRunCmd = 'CLOADM:EXEC\\n'
                    if (system.isOptSet('altromtype') and system.config["altromtype"] == "flop1") or (softList != "" and softList.endswith("flop")) or romExt.casefold() == ".dsk":
                        romType = 'flop'
                        if romDrivername.casefold().endswith(".bas"):
                            autoRunCmd = 'RUN \"{}\"\\n'.format(romDrivername)
                        else:
                            autoRunCmd = 'LOADM \"{}\":EXEC\\n'.format(romDrivername)

                # check for a user override
                autoRunFile = 'system/configs/mame/autoload/{}_{}_autoload.csv'.format(system.name, romType)
                if os.path.exists(autoRunFile):
                    openARFile = open(autoRunFile, 'r')
                    with openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row and not row[0].startswith('#'):
                                if row[0].casefold() == romDrivername.casefold():
                                    autoRunCmd = row[1] + "\\n"
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = '/usr/share/batocera/configgen/data/mame/' + softList + '_autoload.csv'
                if os.path.exists(autoRunFile):
                    openARFile = open(autoRunFile, 'r')
                    with openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row[0].casefold() == os.path.splitext(romBasename)[0].casefold():
                                autoRunCmd = row[1] + "\\n"
                                autoRunDelay = 3
            commandLine += [ '-inipath', '/userdata/saves/mame/mame/ini/' ]
            if autoRunCmd != "":
                if autoRunCmd.startswith("'"):
                    autoRunCmd.replace("'", "")
                iniFile = open('/userdata/saves/mame/mame/ini/batocera.ini', "w")
                iniFile.write('autoboot_command          ' + autoRunCmd + "\n")
                iniFile.write('autoboot_delay            ' + str(autoRunDelay))
                iniFile.close()
            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually.
            if system.isOptSet('addblankdisk') and system.getOptBoolean('addblankdisk'):
                if not os.path.exists('/userdata/saves/lr-mess/{}/{}.dsk'.format(system.name, os.path.splitext(romBasename)[0])):
                    os.makedirs('/userdata/saves/lr-mess/{}/'.format(system.name))
                    shutil.copy2('/usr/share/mame/blank.dsk', '/userdata/saves/lr-mess/{}/{}.dsk'.format(system.name, os.path.splitext(romBasename)[0]))
                if system.isOptSet('altromtype') and system.config['altromtype'] == 'flop2':
                    commandLine += [ '-flop1', '/userdata/saves/lr-mess/{}/{}.dsk'.format(system.name, os.path.splitext(romBasename)[0]) ]
                else:
                    commandLine += [ '-flop2', '/userdata/saves/lr-mess/{}/{}.dsk'.format(system.name, os.path.splitext(romBasename)[0]) ]

    # Lightgun reload option
    if system.isOptSet('offscreenreload') and system.getOptBoolean('offscreenreload'):
        commandLine += [ "-offscreen_reload" ]

    # Art paths - lr-mame displays artwork in the game area and not in the bezel area, so using regular MAME artwork + shaders is not recommended.
    # By default, will ignore standalone MAME's art paths.
    if system.config['core'] != 'same_cdi':
        if not (system.isOptSet("sharemameart") and not system.getOptBoolean('sharemameart')):
            artPath = "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/lr-mame/artwork/;/userdata/bios/mame/artwork/;/userdata/decorations/"
        else:
            artPath = "/var/run/mame_artwork/;/usr/bin/mame/artwork/;/userdata/bios/lr-mame/artwork/"
        if not system.name == "ti99":
            commandLine += [ '-artpath', artPath ]

    # Artwork crop - default to On for lr-mame
    # Exceptions for PDP-1 (status lights) and VGM Player (indicators)
    if not system.isOptSet("artworkcrop"):
        if not system.name in [ 'pdp1', 'vgmplay', 'ti99' ]:
            commandLine += [ "-artwork_crop" ]
    else:
        if system.getOptBoolean("artworkcrop"):
            commandLine += [ "-artwork_crop" ]

    # Share plugins & samples with standalone MAME (except TI99)
    if not system.name == "ti99":
        commandLine += [ "-pluginspath", "/usr/bin/mame/plugins/;/userdata/saves/mame/plugins" ]
        commandLine += [ "-homepath" , "/userdata/saves/mame/plugins/" ]
        commandLine += [ "-samplepath", "/userdata/bios/mame/samples/" ]
    if not os.path.exists("/userdata/saves/mame/plugins/"):
        os.makedirs("/userdata/saves/mame/plugins/")
    if not os.path.exists("/userdata/bios/mame/samples/"):
        os.makedirs("/userdata/bios/mame/samples/")

    # Delete old cmd files & prepare path
    cmdPath = "/var/run/cmdfiles/"
    if not os.path.exists(cmdPath):
        os.makedirs(cmdPath)
    cmdFileList = os.listdir(cmdPath)
    for file in cmdFileList:
        if file.endswith(".cmd"):
            os.remove(os.path.join(cmdPath, file))

    # Write command line file
    cmdFilename = "{}{}.cmd".format(cmdPath, romDrivername)
    cmdFile = open(cmdFilename, "w")
    cmdFile.write(' '.join(commandLine))
    cmdFile.close()

    # Call Controller Config
    if messMode == -1:
        generateMAMEPadConfig(cfgPath, playersControllers, system, "", romBasename, specialController, guns)
    else:
        generateMAMEPadConfig(cfgPath, playersControllers, system, messModel, romBasename, specialController, guns)

def prepSoftwareList(subdirSoftList, softList, softDir, hashDir, romDirname):
    if not os.path.exists(softDir):
        os.makedirs(softDir)
    # Check for/remove existing symlinks, remove hashfile folder
    for fileName in os.listdir(softDir):
        checkFile = os.path.join(softDir, fileName)
        if os.path.islink(checkFile):
            os.unlink(checkFile)
        if os.path.isdir(checkFile):
            shutil.rmtree(checkFile)
    # Prepare hashfile path
    if not os.path.exists(hashDir):
        os.makedirs(hashDir)
    # Remove existing xml files
    hashFiles = os.listdir(hashDir)
    for file in hashFiles:
        if file.endswith(".xml"):
            os.remove(os.path.join(hashDir, file))
    # Copy hashfile
    shutil.copy2("/usr/bin/mame/hash/" + softList + ".xml", hashDir + "/" + softList + ".xml")
    # Link ROM's parent folder if needed, ROM's folder otherwise
    if softList in subdirSoftList:
        romPath = Path(romDirname)
        os.symlink(str(romPath.parents[0]), softDir + softList, True)
    else:
        os.symlink(romDirname, softDir + softList, True)

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

    return "default"

def generateMAMEPadConfig(cfgPath, playersControllers, system, messSysName, romBasename, specialController, guns):
    # config file
    config = minidom.Document()
    configFile = cfgPath + "default.cfg"
    if os.path.exists(configFile):
        try:
            config = minidom.parse(configFile)
        except:
            pass # reinit the file

    if system.isOptSet('customcfg'):
        customCfg = system.getOptBoolean('customcfg')
    else:
        customCfg = False
    # Don't overwrite if using custom configs
    if os.path.exists(configFile) and customCfg:
        overwriteMAME = False
    else:
        overwriteMAME = True

    # Get controller scheme
    altButtons = getMameControlScheme(system, romBasename)

    # Load standard controls from csv
    controlFile = '/usr/share/batocera/configgen/data/mame/mameControls.csv'
    openFile = open(controlFile, 'r')
    controlDict = {}
    with openFile:
        controlList = csv.reader(openFile)
        for row in controlList:
            if not row[0] in controlDict.keys():
                controlDict[row[0]] = {}
            controlDict[row[0]][row[1]] = row[2]

    # Common controls
    mappings = {}
    for controlDef in controlDict['default'].keys():
        mappings[controlDef] = controlDict['default'][controlDef]

    # Buttons that change based on game/setting
    if altButtons in controlDict:
        for controlDef in controlDict[altButtons].keys():
            mappings.update({controlDef: controlDict[altButtons][controlDef]})

    xml_mameconfig = getRoot(config, "mameconfig")
    xml_mameconfig.setAttribute("version", "10") # otherwise, config of pad won't work at first run (batocera v33)
    xml_system = getSection(config, xml_mameconfig, "system")
    xml_system.setAttribute("name", "default")

    removeSection(config, xml_system, "input")
    xml_input = config.createElement("input")
    xml_system.appendChild(xml_input)

    messControlDict = {}
    if messSysName in [ "bbcb", "bbcm", "bbcm512", "bbcmc" ]:
        if specialController == 'none':
            useControls = "bbc"
        else:
            useControls = f"bbc-{specialController}"
    elif messSysName in [ "apple2p", "apple2e", "apple2ee" ]:
        if specialController == 'none':
            useControls = "apple2"
        else:
            useControls = f"apple2-{specialController}"
    else:
        useControls = messSysName

    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    specialControlList = [ "cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb", "bbcm", "bbcm512", "bbcmc", "xegs", \
        "socrates", "vgmplay", "pdp1", "vc4000", "fmtmarty", "gp32", "apple2p", "apple2e", "apple2ee" ]
    if messSysName in specialControlList:
        # Load mess controls from csv
        messControlFile = '/usr/share/batocera/configgen/data/mame/messControls.csv'
        openMessFile = open(messControlFile, 'r')
        with openMessFile:
            controlList = csv.reader(openMessFile, delimiter=';')
            for row in controlList:
                if not row[0] in messControlDict.keys():
                    messControlDict[row[0]] = {}
                messControlDict[row[0]][row[1]] = {}
                currentEntry = messControlDict[row[0]][row[1]]
                currentEntry['type'] = row[2]
                currentEntry['player'] = int(row[3])
                currentEntry['tag'] = row[4]
                currentEntry['key'] = row[5]
                if currentEntry['type'] in [ 'special', 'main' ]:
                    currentEntry['mapping'] = row[6]
                    currentEntry['useMapping'] = row[7]
                    currentEntry['reversed'] = row[8]
                    currentEntry['mask'] = row[9]
                    currentEntry['default'] = row[10]
                elif currentEntry['type'] == 'analog':
                    currentEntry['incMapping'] = row[6]
                    currentEntry['decMapping'] = row[7]
                    currentEntry['useMapping1'] = row[8]
                    currentEntry['useMapping2'] = row[9]
                    currentEntry['reversed'] = row[10]
                    currentEntry['mask'] = row[11]
                    currentEntry['default'] = row[12]
                    currentEntry['delta'] = row[13]
                    currentEntry['axis'] = row[14]
                if currentEntry['type'] == 'combo':
                    currentEntry['kbMapping'] = row[6]
                    currentEntry['mapping'] = row[7]
                    currentEntry['useMapping'] = row[8]
                    currentEntry['reversed'] = row[9]
                    currentEntry['mask'] = row[10]
                    currentEntry['default'] = row[11]
                if currentEntry['reversed'] == 'False':
                    currentEntry['reversed'] == False
                else:
                    currentEntry['reversed'] == True

        config_alt = minidom.Document()
        configFile_alt = cfgPath + messSysName + ".cfg"
        if os.path.exists(configFile_alt):
            try:
                config_alt = minidom.parse(configFile_alt)
            except:
                pass # reinit the file

        perGameCfg = system.getOptBoolean('pergamecfg')
        if os.path.exists(configFile_alt) and (customCfg or perGameCfg):
            overwriteSystem = False
        else:
            overwriteSystem = True

        xml_mameconfig_alt = getRoot(config_alt, "mameconfig")
        xml_mameconfig_alt.setAttribute("version", "10")
        xml_system_alt = getSection(config_alt, xml_mameconfig_alt, "system")
        xml_system_alt.setAttribute("name", messSysName)

        removeSection(config_alt, xml_system_alt, "input")
        xml_input_alt = config_alt.createElement("input")
        xml_system_alt.appendChild(xml_input_alt)

        # Hide the LCD display on CD-i
        if useControls == "cdimono1":
            removeSection(config_alt, xml_system_alt, "video")
            xml_video_alt = config_alt.createElement("video")
            xml_system_alt.appendChild(xml_video_alt)

            xml_screencfg_alt = config_alt.createElement("target")
            xml_screencfg_alt.setAttribute("index", "0")
            xml_screencfg_alt.setAttribute("view", "Main Screen Standard (4:3)")
            xml_video_alt.appendChild(xml_screencfg_alt)

        # If using BBC keyboard controls, enable keyboard to gamepad
        if useControls == 'bbc':
            xml_kbenable_alt = config_alt.createElement("keyboard")
            xml_kbenable_alt.setAttribute("tag", ":")
            xml_kbenable_alt.setAttribute("enabled", "1")
            xml_input_alt.appendChild(xml_kbenable_alt)

    # Don't configure pads if guns are present and "use_guns" is on
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
        return

    # Fill in controls on cfg files
    nplayer = 1
    maxplayers = len(playersControllers)
    for playercontroller, pad in sorted(playersControllers.items()):
        mappings_use = mappings
        if "joystick1up" not in pad.inputs:
            mappings_use["JOYSTICK_UP"] = "up"
            mappings_use["JOYSTICK_DOWN"] = "down"
            mappings_use["JOYSTICK_LEFT"] = "left"
            mappings_use["JOYSTICK_RIGHT"] = "right"

        for mapping in mappings_use:
            if mappings_use[mapping] in pad.inputs:
                if mapping in [ 'START', 'COIN' ]:
                    xml_input.appendChild(generateSpecialPortElement(pad, config, 'standard', nplayer, pad.index, mapping + str(nplayer), mappings_use[mapping], retroPad[mappings_use[mapping]], False, "", ""))
                else:
                    xml_input.appendChild(generatePortElement(pad, config, nplayer, pad.index, mapping, mappings_use[mapping], retroPad[mappings_use[mapping]], False, altButtons))
            else:
                rmapping = reverseMapping(mappings_use[mapping])
                if rmapping in retroPad:
                        xml_input.appendChild(generatePortElement(pad, config, nplayer, pad.index, mapping, mappings_use[mapping], retroPad[rmapping], True, altButtons))

        #UI Mappings
        if nplayer == 1:
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_DOWN", "DOWN", mappings_use["JOYSTICK_DOWN"], retroPad[mappings_use["JOYSTICK_DOWN"]], False, "", ""))      # Down
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_LEFT", "LEFT", mappings_use["JOYSTICK_LEFT"], retroPad[mappings_use["JOYSTICK_LEFT"]], False, "", ""))    # Left
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_UP", "UP", mappings_use["JOYSTICK_UP"], retroPad[mappings_use["JOYSTICK_UP"]], False, "", ""))            # Up
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_RIGHT", "RIGHT", mappings_use["JOYSTICK_RIGHT"], retroPad[mappings_use["JOYSTICK_RIGHT"]], False, "", "")) # Right
            xml_input.appendChild(generateComboPortElement(pad, config, 'standard', pad.index, "UI_SELECT", "ENTER", 'a', retroPad['a'], False, "", ""))                                                     # Select

        if useControls in messControlDict.keys():
            for controlDef in messControlDict[useControls].keys():
                thisControl = messControlDict[useControls][controlDef]
                if nplayer == thisControl['player']:
                    if thisControl['type'] == 'special':
                        xml_input_alt.appendChild(generateSpecialPortElement(pad, config_alt, thisControl['tag'], nplayer, pad.index, thisControl['key'], thisControl['mapping'], \
                            retroPad[mappings_use[thisControl['useMapping']]], thisControl['reversed'], thisControl['mask'], thisControl['default']))
                    elif thisControl['type'] == 'main':
                        xml_input.appendChild(generateSpecialPortElement(pad, config_alt, thisControl['tag'], nplayer, pad.index, thisControl['key'], thisControl['mapping'], \
                            retroPad[mappings_use[thisControl['useMapping']]], thisControl['reversed'], thisControl['mask'], thisControl['default']))
                    elif thisControl['type'] == 'analog':
                        xml_input_alt.appendChild(generateAnalogPortElement(pad, config_alt, thisControl['tag'], nplayer, pad.index, thisControl['key'], mappings_use[thisControl['incMapping']], \
                            mappings_use[thisControl['decMapping']], retroPad[mappings_use[thisControl['useMapping1']]], retroPad[mappings_use[thisControl['useMapping2']]], thisControl['reversed'], \
                            thisControl['mask'], thisControl['default'], thisControl['delta'], thisControl['axis']))
                    elif thisControl['type'] == 'combo':
                        xml_input_alt.appendChild(generateComboPortElement(pad, config_alt, thisControl['tag'], pad.index, thisControl['key'], thisControl['kbMapping'], thisControl['mapping'], \
                            retroPad[mappings_use[thisControl['useMapping']]], thisControl['reversed'], thisControl['mask'], thisControl['default']))

        nplayer = nplayer + 1

        # save the config file
        #mameXml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        if overwriteMAME:
            mameXml = codecs.open(configFile, "w", "utf-8")
            dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            mameXml.write(dom_string)

        # Write alt config (if used, custom config is turned off or file doesn't exist yet)
        if messSysName in specialControlList and overwriteSystem:
            mameXml_alt = codecs.open(configFile_alt, "w", "utf-8")
            dom_string_alt = os.linesep.join([s for s in config_alt.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
            mameXml_alt.write(dom_string_alt)

def reverseMapping(key):
    if key == "joystick1down":
        return "joystick1up"
    if key == "joystick1right":
        return "joystick1left"
    if key == "joystick2down":
        return "joystick2up"
    if key == "joystick2right":
        return "joystick2left"
    return None

def generatePortElement(pad, config, nplayer, padindex, mapping, key, input, reversed, altButtons):
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(pad, key, input, padindex + 1, reversed, altButtons))
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElement(pad, config, tag, nplayer, padindex, mapping, key, input, reversed, mask, default):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(pad, key, input, padindex + 1, reversed, 0))
    xml_newseq.appendChild(value)
    return xml_port

def generateComboPortElement(pad, config, tag, padindex, mapping, kbkey, key, input, reversed, mask, default):
    # Maps a keycode + button - for important keyboard keys when available
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(f"KEYCODE_{kbkey} OR " + input2definition(pad, key, input, padindex + 1, reversed, 0))
    xml_newseq.appendChild(value)
    return xml_port

def generateAnalogPortElement(pad, config, tag, nplayer, padindex, mapping, inckey, deckey, mappedinput, mappedinput2, reversed, mask, default, delta, axis = ''):
    # Mapping analog to digital (mouse, etc)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_port.setAttribute("keydelta", delta)
    xml_newseq_inc = config.createElement("newseq")
    xml_newseq_inc.setAttribute("type", "increment")
    xml_port.appendChild(xml_newseq_inc)
    incvalue = config.createTextNode(input2definition(pad, inckey, mappedinput, padindex + 1, reversed, 0, True))
    xml_newseq_inc.appendChild(incvalue)
    xml_newseq_dec = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_dec)
    xml_newseq_dec.setAttribute("type", "decrement")
    decvalue = config.createTextNode(input2definition(pad, deckey, mappedinput2, padindex + 1, reversed, 0, True))
    xml_newseq_dec.appendChild(decvalue)
    xml_newseq_std = config.createElement("newseq")
    xml_port.appendChild(xml_newseq_std)
    xml_newseq_std.setAttribute("type", "standard")
    if axis == '':
        stdvalue = config.createTextNode("NONE")
    else:
        stdvalue = config.createTextNode("JOYCODE_{}_{}".format(padindex + 1, axis))
    xml_newseq_std.appendChild(stdvalue)
    return xml_port

def input2definition(pad, key, input, joycode, reversed, altButtons, ignoreAxis = False):
    if input.find("BUTTON") != -1 or input.find("HAT") != -1 or input == "START" or input == "SELECT":
        input = input.format(joycode) if "{0}" in input else input
        return f"JOYCODE_{joycode}_{input}"
    elif input.find("AXIS") != -1:
        if altButtons == "qbert": # Q*Bert Joystick
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad['joystick1up']}_{joycode}_{retroPad['joystick1right']} OR \
                    JOYCODE_{joycode}_{retroPad['up'].format(joycode)} JOYCODE_{joycode}_{retroPad['right'].format(joycode)}"
            elif key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad['joystick1down']} JOYCODE_{joycode}_{retroPad['joystick1left']} OR \
                    JOYCODE_{joycode}_{retroPad['down'].format(joycode)} JOYCODE_{joycode}_{retroPad['left'].format(joycode)}"
            elif key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad['joystick1left']} JOYCODE_{joycode}_{retroPad['joystick1up']} OR \
                    JOYCODE_{joycode}_{retroPad['left'].format(joycode)} JOYCODE_{joycode}_{retroPad['up'].format(joycode)}"
            elif key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad['joystick1right']} JOYCODE_{joycode}_{retroPad['joystick1down']} OR \
                    JOYCODE_{joycode}_{retroPad['right'].format(joycode)} JOYCODE_{joycode}_{retroPad['down'].format(joycode)}"
            else:
                return f"JOYCODE_{joycode}_{input}"
        elif ignoreAxis:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad['up'].format(joycode)}"
            elif key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad['down'].format(joycode)}"
            elif key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad['left'].format(joycode)}"
            elif key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad['right'].format(joycode)}"
        else:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['up'].format(joycode)}"
            elif key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['down'].format(joycode)}"
            elif key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['left'].format(joycode)}"
            elif key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['right'].format(joycode)}"
            elif(key == "joystick2up"):
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['x']}"
            elif(key == "joystick2down"):
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['b']}"
            elif(key == "joystick2left"):
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['y']}"
            elif(key == "joystick2right"):
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['a']}"
            else:
                return f"JOYCODE_{joycode}_{input}"
    else:
        return "unknown"

def getRoot(config, name):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def getSection(config, xml_root, name):
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def removeSection(config, xml_root, name):
    xml_section = xml_root.getElementsByTagName(name)

    for i in range(0, len(xml_section)):
        old = xml_root.removeChild(xml_section[i])
        old.unlink()
