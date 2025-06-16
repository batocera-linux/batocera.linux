from __future__ import annotations

import codecs
import csv
import logging
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING
from xml.dom import minidom

from ...batoceraPaths import BIOS, CONFIGS, DEFAULTS_DIR, ROMS, SAVES, USER_DECORATIONS, mkdir_if_not_exists

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ...controller import Controller, Controllers
    from ...Emulator import Emulator
    from ...gun import Guns

_logger = logging.getLogger(__name__)

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

def generateMAMEConfigs(playersControllers: Controllers, system: Emulator, rom: Path, guns: Guns) -> None:
    # Generate command line for MAME/MESS/MAMEVirtual
    commandLine: list[str | Path] = []
    romDrivername = rom.stem
    specialController = 'none'

    if system.config.core in [ 'mame', 'mess', 'mamevirtual' ]:
        corePath = f"lr-{system.config.core}"
    else:
        corePath = str(system.config.core)

    if system.name in [ 'mame', 'neogeo', 'lcdgames', 'plugnplay', 'vis', 'namco22' ]:
        # Set up command line for basic systems
        # ie. no media, softlists, etc.
        if system.config.get_bool("customcfg"):
            cfgPath = CONFIGS / corePath / "custom"
        else:
            cfgPath = SAVES / "mame" / "mame" / "cfg"
        mkdir_if_not_exists(cfgPath)
        if system.name == 'vis':
            commandLine += [ 'vis', '-cdrom', f'"{rom}"' ]
        else:
            commandLine += [ romDrivername ]
        commandLine += [ '-cfg_directory', f'"{cfgPath}"' ]
        commandLine += [ '-rompath', f'"{rom.parent};/userdata/bios/mame/;/userdata/bios/"' ]
        pluginsToLoad: list[str] = []
        if system.config.get_bool("hiscoreplugin", True):
            pluginsToLoad += [ "hiscore" ]
        if system.config.get_bool("coindropplugin"):
            pluginsToLoad += [ "coindrop" ]
        if pluginsToLoad:
            commandLine += [ "-plugins", "-plugin", ",".join(pluginsToLoad) ]
        messMode = -1
        messModel = ''
    else:
        # Set up command line for MESS or MAMEVirtual
        softDir = Path("/var/run/mame_software")
        subdirSoftList = [ "mac_hdd", "bbc_hdd", "cdi", "archimedes_hdd", "fmtowns_cd" ]
        softList = system.config.get("softList", "none")
        if softList == "none":
            softList = ""

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if system.name == 'fmtowns' and softList == '' and (ROMS / 'fmtowns' / f'{rom.parent.name}.zip').exists():
            softList = 'fmtowns_cd'

        # Determine MESS system name (if needed)
        openFile = (DEFAULTS_DIR / "data" / "mame" / "messSystems.csv").open()
        messSystems: list[str] = []
        messSysName: list[str] = []
        messRomType: list[str] = []
        messAutoRun: list[str] = []
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
        if altmodel := system.config.get("altmodel"):
            messModel = altmodel
        commandLine += [ messModel ]

        if messSysName[messMode] == "":
            # Command line for non-arcade, non-system ROMs (lcdgames, plugnplay)
            if system.config.get_bool("customcfg"):
                cfgPath = CONFIGS / corePath / "custom"
            else:
                cfgPath = SAVES / "mame" / "mame" / "cfg"
            mkdir_if_not_exists(cfgPath)
            commandLine += [ romDrivername ]
            commandLine += [ '-cfg_directory', f'"{cfgPath}"' ]
            commandLine += [ '-rompath', f'"{rom.parent};/userdata/bios/"' ]
        else:
            # Command line for MESS consoles/computers
            # TI-99 32k RAM expansion & speech modules
            # Don't enable 32k by default
            if system.name == "ti99":
                commandLine += [ "-ioport", "peb" ]
                if system.config.get_bool("ti99_32kram"):
                    commandLine += ["-ioport:peb:slot2", "32kmem"]
                if system.config.get_bool("ti99_speech", True):
                    commandLine += ["-ioport:peb:slot3", "speech"]

            #Laser 310 Memory Expansion & joystick
            if system.name == "laser310":
                commandLine += ['-io', 'joystick', "-mem", system.config.get('memslot', 'laser_64k')]

            # BBC Joystick
            if system.name == "bbc" and system.config.get('sticktype', 'none') != 'none':
                commandLine += ["-analogue", system.config['sticktype']]
                specialController = system.config['sticktype']

            # Apple II
            if system.name == "apple2":
                rom_extension = rom.suffix.lower()
                # only add SD/IDE control if provided a hard drive image
                if rom_extension in {".hdv", ".2mg", ".chd", ".iso", ".bin", ".cue"}:
                    commandLine += ["-sl7", "cffa202"]
                if (gameio := system.config.get('gameio', 'none')) != 'none':
                    if gameio == 'joyport' and messModel != 'apple2p':
                        _logger.debug("Joyport is only compatible with Apple II Plus")
                    else:
                        commandLine += ["-gameio", gameio]
                        specialController = gameio

            # RAM size (Mac excluded, special handling below)
            ramSize = system.config.get_int('ramsize')
            if system.name != "macintosh" and ramSize:
                commandLine += [ '-ramsize', str(ramSize) + 'M' ]

            # Mac RAM & Image Reader (if applicable)
            if system.name == "macintosh" and ramSize:
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
                    imageSlot = system.config.get('imagereader', 'nba')
                    if imageSlot != "disabled":
                        commandLine += [ f"-{imageSlot}", "image" ]

            altromtype = system.config.get_str("altromtype")
            boot_disk = system.config.get("bootdisk")

            if softList != "":
                # Software list ROM commands
                prepSoftwareList(subdirSoftList, softList, softDir, BIOS / "mame" / "hash", rom.parent)
                if softList in subdirSoftList:
                    commandLine += [ rom.parent.name ]
                else:
                    commandLine += [ romDrivername ]
                commandLine += [ "-rompath", f'"{softDir};/userdata/bios/"' ]
                commandLine += [ "-swpath", f'"{softDir}"' ]
                commandLine += [ "-verbose" ]
            else:
                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                if system.name != "macintosh":
                    if altromtype:
                        if altromtype == "flop1" and messModel == "fmtmarty":
                            commandLine += [ "-flop" ]
                        else:
                            commandLine += [ "-" + altromtype ]
                    elif system.name == "adam":
                        # add some logic based on the extension
                        rom_extension = rom.suffix.lower()
                        if rom_extension == ".ddp":
                            commandLine += [ "-cass1" ]
                        elif rom_extension == ".dsk":
                            commandLine += [ "-flop1" ]
                        else:
                            commandLine += [ "-cart1" ]
                    elif system.name == "coco":
                        if rom.suffix.casefold() == ".cas":
                            commandLine += [ "-cass" ]
                        elif rom.suffix.casefold() == ".dsk":
                            commandLine += [ "-flop1" ]
                        else:
                            commandLine += [ "-cart" ]
                    # try to choose the right floppy for Apple2gs
                    elif system.name == "apple2gs":
                        rom_extension = rom.suffix.lower()
                        if rom_extension == ".zip":
                            with zipfile.ZipFile(rom, 'r') as zip_file:
                                file_list = zip_file.namelist()
                                # assume only one file in zip
                                if len(file_list) == 1:
                                    filename = file_list[0]
                                    rom_extension = Path(filename).suffix.lower()
                        if rom_extension in [".2mg", ".2img", ".img", ".image"]:
                            commandLine += [ "-flop3" ]
                        else:
                            commandLine += [ "-flop1" ]
                    else:
                        commandLine += [ "-" + messRomType[messMode] ]
                else:
                    if boot_disk:
                        if (altromtype == "flop1" or not altromtype) and boot_disk in [ "macos30", "macos608", "macos701", "macos75" ]:
                            commandLine += [ "-flop2" ]
                        elif altromtype:
                            commandLine += [ "-" + altromtype ]
                        else:
                            commandLine += [ "-" + messRomType[messMode] ]
                    else:
                        if altromtype:
                            commandLine += [ "-" + altromtype ]
                        else:
                            commandLine += [ "-" + messRomType[messMode] ]
                # Use the full filename for MESS non-softlist ROMs
                commandLine += [ f'"{rom}"' ]
                commandLine += [ "-rompath", f'"{rom.parent};/userdata/bios/"' ]

                # Boot disk for Macintosh
                # Will use Floppy 1 or Hard Drive, depending on the disk.
                if system.name == "macintosh" and boot_disk:
                    if system.config["bootdisk"] in [ "macos30", "macos608", "macos701", "macos75" ]:
                        bootType = "-flop1"
                        bootDisk = '"/userdata/bios/' + boot_disk + '.img"'
                    else:
                        bootType = "-hard"
                        bootDisk = '"/userdata/bios/' + boot_disk + '.chd"'
                    commandLine += [ bootType, bootDisk ]

                # Create & add a blank disk if needed, insert into drive 2
                # or drive 1 if drive 2 is selected manually or FM Towns Marty.
                if system.config.get_bool('addblankdisk'):
                    if system.name == 'fmtowns':
                        blankDisk = Path('/usr/share/mame/blank.fmtowns')
                        targetFolder = SAVES / 'mame' / system.name
                        targetDisk = targetFolder / f'{rom.stem}.fmtowns'
                    # Add elif statements here for other systems if enabled
                    else:
                        blankDisk = Path('/usr/share/mame/blank.default')
                        targetFolder = SAVES / 'mame' / system.name
                        targetDisk = targetFolder / f'{rom.stem}.default'
                    mkdir_if_not_exists(targetFolder)
                    if not targetDisk.exists():
                        shutil.copy2(blankDisk, targetDisk)
                    # Add other single floppy systems to this if statement
                    if messModel == "fmtmarty":
                        commandLine += [ '-flop', f'"{targetDisk}"' ]
                    elif altromtype == 'flop2':
                        commandLine += [ '-flop1', f'"{targetDisk}"' ]
                    else:
                        commandLine += [ '-flop2', f'"{targetDisk}"' ]

            # UI enable - for computer systems, the default sends all keys to the emulated system.
            # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
            if system.config.get_bool("enableui", True):
                commandLine += [ "-ui_active" ]

            # MESS config folder
            if system.config.get_bool("customcfg"):
                cfgPath = CONFIGS / corePath / messSysName[messMode] / "custom"
            else:
                cfgPath = SAVES / "mame" / "cfg" / messSysName[messMode]
            if system.config.get_bool("pergamecfg"):
                cfgPath = CONFIGS / corePath / messSysName[messMode] / rom.name
            mkdir_if_not_exists(cfgPath)
            commandLine += [ '-cfg_directory', f'"{cfgPath}"' ]

            # Autostart via ini file
            # Init variables, delete old ini if it exists, prepare ini path
            # lr-mame does NOT support multiple ini paths
            autoRunCmd = ""
            autoRunDelay = 0
            mameIniDir = SAVES / "mame" / "mame" / "ini"
            mkdir_if_not_exists(mameIniDir)
            if (mameIniDir / "batocera.ini").exists():
                (mameIniDir / "batocera.ini").unlink()
            # bbc has different boots for floppy & cassette, no special boot for carts
            if system.name == "bbc":
                if altromtype or softList:
                    if altromtype == "cass" or softList[-4:] == "cass":
                        autoRunCmd = '*tape\\nchain""\\n'
                        autoRunDelay = 2
                    elif (altromtype and altromtype.startswith("flop")) or "flop" in softList:
                        autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                        autoRunDelay = 3
                else:
                    autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                    autoRunDelay = 3
            # fm7 boots floppies, needs cassette loading
            elif system.name == "fm7":
                if (
                    system.config.get("altromtype") == "cass"
                    or (softList != "" and softList[-4:] == "cass")
                ):
                    autoRunCmd = 'LOADM”“,,R\\n'
                    autoRunDelay = 5
            elif system.name == "coco":
                romType = 'cart'
                autoRunDelay = 2

                # if using software list, use "usage" for autoRunCmd (if provided)
                if softList != "":
                    softListFile = Path(f'/usr/bin/mame/hash/{softList}.xml')
                    if softListFile.exists():
                        softwarelist = ET.parse(softListFile)
                        for software in softwarelist.findall('software'):
                            if software.attrib and software.get('name') == romDrivername:
                                for info in software.iter('info'):
                                    if info.get('name') == 'usage':
                                        autoRunCmd = f'{info.get('value')}\\n'

                # if still undefined, default autoRunCmd based on media type
                if autoRunCmd == "":
                    if altromtype == "cass" or (softList and softList.endswith("cass")) or rom.suffix.casefold() == ".cas":
                        romType = 'cass'
                        if romDrivername.casefold().endswith(".bas"):
                            autoRunCmd = 'CLOAD:RUN\\n'
                        else:
                            autoRunCmd = 'CLOADM:EXEC\\n'
                    if altromtype == "flop1" or (softList and softList.endswith("flop")) or rom.suffix.casefold() == ".dsk":
                        romType = 'flop'
                        if romDrivername.casefold().endswith(".bas"):
                            autoRunCmd = f'RUN \"{romDrivername}\"\\n'
                        else:
                            autoRunCmd = f'LOADM \"{romDrivername}\":EXEC\\n'

                # check for a user override
                autoRunFile = CONFIGS / 'mame' / 'autoload' / f'{system.name}_{romType}_autoload.csv'
                if autoRunFile.exists():
                    with autoRunFile.open() as openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row and not row[0].startswith('#') and row[0].casefold() == romDrivername.casefold():
                                autoRunCmd = row[1] + "\\n"
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = DEFAULTS_DIR / 'data' / 'mame' / f'{softList}_autoload.csv'
                if autoRunFile.exists():
                    with autoRunFile.open() as openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row[0].casefold() == rom.stem.casefold():
                                autoRunCmd = row[1] + "\\n"
                                autoRunDelay = 3

            inipath = SAVES / 'mame' / 'mame' / 'ini'
            commandLine += [ '-inipath', f'"{inipath}"' ]
            if autoRunCmd != "":
                if autoRunCmd.startswith("'"):
                    autoRunCmd.replace("'", "")
                iniFile = (SAVES / 'mame' / 'mame' / 'ini' / 'batocera.ini').open("w")
                iniFile.write('autoboot_command          ' + autoRunCmd + "\n")
                iniFile.write('autoboot_delay            ' + str(autoRunDelay))
                iniFile.close()
            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually.
            if system.config.get_bool('addblankdisk'):
                lr_mess_dsk = SAVES / 'lr-mess' / system.name / rom.stem
                if not lr_mess_dsk.exists():
                    lr_mess_dsk.parent.mkdir(parents=True)
                    shutil.copy2('/usr/share/mame/blank.dsk', lr_mess_dsk)
                if altromtype == 'flop2':
                    commandLine += [ '-flop1', f'"{lr_mess_dsk}"' ]
                else:
                    commandLine += [ '-flop2', f'"{lr_mess_dsk}"' ]

    # Lightgun reload option
    if system.config.get_bool('offscreenreload'):
        commandLine += [ "-offscreen_reload" ]

    # Art paths - lr-mame displays artwork in the game area and not in the bezel area, so using regular MAME artwork + shaders is not recommended.
    # By default, will ignore standalone MAME's art paths.
    if system.config.core != 'same_cdi':
        if system.config.get_bool("sharemameart", True):
            artPath = f"/var/run/mame_artwork/;/usr/bin/mame/artwork/;{BIOS / 'lr-mame' / 'artwork'};{BIOS / 'mame' / 'artwork'};{USER_DECORATIONS}"
        else:
            artPath = f"/var/run/mame_artwork/;/usr/bin/mame/artwork/;{BIOS / 'lr-mame' / 'artwork'}"
        if system.name != "ti99":
            commandLine += [ '-artpath', f'"{artPath}"' ]

    # Artwork crop - default to On for lr-mame
    # Exceptions for PDP-1 (status lights) and VGM Player (indicators)
    if "artworkcrop" not in system.config:
        if system.name not in [ 'pdp1', 'vgmplay', 'ti99' ]:
            commandLine += [ "-artwork_crop" ]
    else:
        if system.config.get_bool("artworkcrop"):
            commandLine += [ "-artwork_crop" ]

    # Share plugins & samples with standalone MAME (except TI99)
    if system.name != "ti99":
        commandLine += [ "-pluginspath", f"/usr/bin/mame/plugins/;{SAVES / 'mame' / 'plugins'}" ]
        commandLine += [ "-homepath" , SAVES / 'mame' / 'plugins' ]
        commandLine += [ "-samplepath", BIOS / "mame" / "samples" ]
    mkdir_if_not_exists(SAVES / "mame" / "plugins")
    mkdir_if_not_exists(BIOS / "mame" / "samples")

    # Delete old cmd files & prepare path
    cmdPath = Path("/var/run/cmdfiles")
    mkdir_if_not_exists(cmdPath)
    for file in cmdPath.iterdir():
        if file.suffix == ".cmd":
            file.unlink()

    # Write command line file
    cmdFilename = cmdPath / f"{romDrivername}.cmd"
    # Check to see whether user provided a custom cmd file at the default location
    if Path(defaultCustomCmdFilepath := f"{rom}.cmd").is_file():
        shutil.copyfile(defaultCustomCmdFilepath, cmdFilename)
    else:
        # User did not provide a custom .cmd file. Use the logic above to create a new .cmd file
        cmdFile = cmdFilename.open("w")
        cmdFile.write(' '.join(str(item) for item in commandLine))
        cmdFile.close()

    # Call Controller Config
    if messMode == -1:
        generateMAMEPadConfig(cfgPath, playersControllers, system, "", rom, specialController, guns)
    else:
        generateMAMEPadConfig(cfgPath, playersControllers, system, messModel, rom, specialController, guns)

def prepSoftwareList(subdirSoftList: Sequence[str], softList: str, softDir: Path, hashDir: Path, romParent: Path):
    mkdir_if_not_exists(softDir)
    # Check for/remove existing symlinks, remove hashfile folder
    for checkFile in softDir.iterdir():
        if checkFile.is_symlink():
            checkFile.unlink()
        if checkFile.is_dir():
            shutil.rmtree(checkFile)
    # Prepare hashfile path
    mkdir_if_not_exists(hashDir)
    # Remove existing xml files
    for file in hashDir.iterdir():
        if file.suffix == ".xml":
            file.unlink()
    # Copy hashfile
    shutil.copy2(Path("/usr/bin/mame/hash") / f"{softList}.xml", hashDir / f"{softList}.xml")
    # Link ROM's parent folder if needed, ROM's folder otherwise
    if softList in subdirSoftList:
        (softDir / softList).symlink_to(romParent.parent, target_is_directory=True)
    else:
        (softDir / softList).symlink_to(romParent, target_is_directory=True)

def getMameControlScheme(system: Emulator, rom: Path) -> str:
    # Game list files
    mame_data_dir = DEFAULTS_DIR / 'data' / 'mame'
    mameCapcom = mame_data_dir / 'mameCapcom.txt'
    mameKInstinct = mame_data_dir / 'mameKInstinct.txt'
    mameMKombat = mame_data_dir / 'mameMKombat.txt'
    mameNeogeo = mame_data_dir / 'mameNeogeo.txt'
    mameTwinstick = mame_data_dir / 'mameTwinstick.txt'
    mameRotatedstick = mame_data_dir / 'mameRotatedstick.txt'

    # Controls for games with 5-6 buttons or other unusual controls
    controllerType = system.config.get("altlayout", "auto")

    if controllerType in [ "default", "neomini", "neocd", "twinstick", "qbert" ]:
        return controllerType

    capcomList = set(mameCapcom.read_text().split())
    mkList = set(mameMKombat.read_text().split())
    kiList = set(mameKInstinct.read_text().split())
    neogeoList = set(mameNeogeo.read_text().split())
    twinstickList = set(mameTwinstick.read_text().split())
    qbertList = set(mameRotatedstick.read_text().split())

    romName = rom.stem
    if romName in capcomList:
        if controllerType in [ "auto", "snes" ]:
            return "sfsnes"
        if controllerType == "megadrive":
            return "megadrive"
        if controllerType == "fightstick":
            return "sfstick"
    elif romName in mkList:
        if controllerType in [ "auto", "snes" ]:
            return "mksnes"
        if controllerType == "megadrive":
            return "mkmegadrive"
        if controllerType == "fightstick":
            return "mkstick"
    elif romName in kiList:
        if controllerType in [ "auto", "snes" ]:
            return "kisnes"
        if controllerType == "megadrive":
            return "megadrive"
        if controllerType == "fightstick":
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

def generateMAMEPadConfig(
    cfgPath: Path,
    playersControllers: Controllers,
    system: Emulator,
    messSysName: str,
    rom: Path,
    specialController: str,
    guns: Guns,
) -> None:
    # config file
    config = minidom.Document()
    configFile = cfgPath / "default.cfg"
    if configFile.exists():
        try:
            config = minidom.parse(str(configFile))
        except Exception:
            pass # reinit the file

    customCfg = system.config.get_bool('customcfg')

    # Don't overwrite if using custom configs
    if configFile.exists() and customCfg:
        overwriteMAME = False
    else:
        overwriteMAME = True

    # Get controller scheme
    altButtons = getMameControlScheme(system, rom)

    # Load standard controls from csv
    controlFile = DEFAULTS_DIR / 'data' / 'mame' / 'mameControls.csv'
    controlDict: dict[str, dict[str, str]] = {}
    with controlFile.open() as openFile:
        controlList = csv.reader(openFile)
        for row in controlList:
            if row[0] not in controlDict:
                controlDict[row[0]] = {}
            controlDict[row[0]][row[1]] = row[2]

    # Common controls
    mappings: dict[str, str] = {}
    for controlDef in controlDict['default']:
        mappings[controlDef] = controlDict['default'][controlDef]

    # Buttons that change based on game/setting
    if altButtons in controlDict:
        for controlDef in controlDict[altButtons]:
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

    config_alt: minidom.Document | None = None
    xml_input_alt: minidom.Element | None = None
    overwriteSystem = True
    configFile_alt: Path | None = None

    # Open or create alternate config file for systems with special controllers/settings
    # If the system/game is set to per game config, don't try to open/reset an existing file, only write if it's blank or going to the shared cfg folder
    specialControlList = [ "cdimono1", "apfm1000", "astrocde", "adam", "arcadia", "gamecom", "tutor", "crvision", "bbcb", "bbcm", "bbcm512", "bbcmc", "xegs", \
        "socrates", "vgmplay", "pdp1", "vc4000", "fmtmarty", "gp32", "apple2p", "apple2e", "apple2ee" ]
    if messSysName in specialControlList:
        # Load mess controls from csv
        messControlFile = DEFAULTS_DIR / 'data' / 'mame' / 'messControls.csv'
        with messControlFile.open() as openMessFile:
            controlList = csv.reader(openMessFile, delimiter=';')
            for row in controlList:
                if row[0] not in messControlDict:
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
                    currentEntry['reversed'] = False
                else:
                    currentEntry['reversed'] = True

        config_alt = minidom.Document()
        configFile_alt = cfgPath / f"{messSysName}.cfg"
        if configFile_alt.exists():
            try:
                config_alt = minidom.parse(str(configFile_alt))
            except Exception:
                pass # reinit the file

        perGameCfg = system.config.get_bool('pergamecfg')
        if configFile_alt.exists() and (customCfg or perGameCfg):
            overwriteSystem = False

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
    if system.config.use_guns and guns:
        return

    # Fill in controls on cfg files
    for nplayer, pad in enumerate(playersControllers, start=1):
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

        if useControls in messControlDict:
            for controlDef in messControlDict[useControls]:
                thisControl = messControlDict[useControls][controlDef]
                if nplayer == thisControl['player'] and xml_input_alt is not None and config_alt is not None:
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


        # save the config file
        #mameXml = open(configFile, "w")
        # TODO: python 3 - workawround to encode files in utf-8
        if overwriteMAME:
            with codecs.open(str(configFile), "w", "utf-8") as mameXml:
                dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
                mameXml.write(dom_string)

        # Write alt config (if used, custom config is turned off or file doesn't exist yet)
        if messSysName in specialControlList and overwriteSystem and config_alt is not None and configFile_alt is not None:
            with codecs.open(str(configFile_alt), "w", "utf-8") as mameXml_alt:
                dom_string_alt = os.linesep.join([s for s in config_alt.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
                mameXml_alt.write(dom_string_alt)

def reverseMapping(key: str) -> str | None:
    if key == "joystick1down":
        return "joystick1up"
    if key == "joystick1right":
        return "joystick1left"
    if key == "joystick2down":
        return "joystick2up"
    if key == "joystick2right":
        return "joystick2left"
    return None

def generatePortElement(pad: Controller, config: minidom.Document, nplayer: int, padindex: int, mapping: str, key: str, input: str, reversed: bool, altButtons: str):
    # Generic input
    xml_port = config.createElement("port")
    xml_port.setAttribute("type", f"P{nplayer}_{mapping}")
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    value = config.createTextNode(input2definition(pad, key, input, padindex + 1, reversed, altButtons))
    xml_newseq.appendChild(value)
    return xml_port

def generateSpecialPortElement(pad: Controller, config: minidom.Document, tag: str, nplayer: int, padindex: int, mapping: str, key: str, input: str, reversed: bool, mask: str, default: str):
    # Special button input (ie mouse button to gamepad)
    xml_port = config.createElement("port")
    xml_port.setAttribute("tag", tag)
    xml_port.setAttribute("type", mapping)
    xml_port.setAttribute("mask", mask)
    xml_port.setAttribute("defvalue", default)
    xml_newseq = config.createElement("newseq")
    xml_newseq.setAttribute("type", "standard")
    xml_port.appendChild(xml_newseq)
    txt = input2definition(pad, key, input, padindex + 1, reversed, 0)
    if mapping == "COIN" + str(nplayer) and nplayer == 1:
        txt = txt + f" OR KEYCODE_{nplayer}_F{nplayer + 11}" # f12 for player 1
    value = config.createTextNode(txt)
    xml_newseq.appendChild(value)
    return xml_port

def generateComboPortElement(pad: Controller, config: minidom.Document, tag: str, padindex: int, mapping: str, kbkey: str, key: str, input: str, reversed: bool, mask: str, default: str):
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

def generateAnalogPortElement(pad: Controller, config: minidom.Document, tag: str, nplayer: int, padindex: int, mapping: str, inckey: str, deckey: str, mappedinput: str, mappedinput2: str, reversed: bool, mask: str, default: str, delta: str, axis: str = ''):
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
        stdvalue = config.createTextNode(f"JOYCODE_{padindex + 1}_{axis}")
    xml_newseq_std.appendChild(stdvalue)
    return xml_port

def input2definition(pad: Controller, key: str, input: str, joycode: int, reversed: bool, altButtons: str | int, ignoreAxis: bool = False) -> str:
    if input.find("BUTTON") != -1 or input.find("HAT") != -1 or input == "START" or input == "SELECT":
        input = input.format(joycode) if "{0}" in input else input
        return f"JOYCODE_{joycode}_{input}"
    if input.find("AXIS") != -1:
        if altButtons == "qbert": # Q*Bert Joystick
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad['joystick1up']}_{joycode}_{retroPad['joystick1right']} OR \
                    JOYCODE_{joycode}_{retroPad['up'].format(joycode)} JOYCODE_{joycode}_{retroPad['right'].format(joycode)}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad['joystick1down']} JOYCODE_{joycode}_{retroPad['joystick1left']} OR \
                    JOYCODE_{joycode}_{retroPad['down'].format(joycode)} JOYCODE_{joycode}_{retroPad['left'].format(joycode)}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad['joystick1left']} JOYCODE_{joycode}_{retroPad['joystick1up']} OR \
                    JOYCODE_{joycode}_{retroPad['left'].format(joycode)} JOYCODE_{joycode}_{retroPad['up'].format(joycode)}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad['joystick1right']} JOYCODE_{joycode}_{retroPad['joystick1down']} OR \
                    JOYCODE_{joycode}_{retroPad['right'].format(joycode)} JOYCODE_{joycode}_{retroPad['down'].format(joycode)}"
            return f"JOYCODE_{joycode}_{input}"

        if ignoreAxis:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad['up'].format(joycode)}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad['down'].format(joycode)}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad['left'].format(joycode)}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad['right'].format(joycode)}"
        else:
            if key == "joystick1up" or key == "up":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['up'].format(joycode)}"
            if key == "joystick1down" or key == "down":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['down'].format(joycode)}"
            if key == "joystick1left" or key == "left":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['left'].format(joycode)}"
            if key == "joystick1right" or key == "right":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['right'].format(joycode)}"
            if key == "joystick2up":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['x']}"
            if key == "joystick2down":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['b']}"
            if key == "joystick2left":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['y']}"
            if key == "joystick2right":
                return f"JOYCODE_{joycode}_{retroPad[key]} OR JOYCODE_{joycode}_{retroPad['a']}"

            return f"JOYCODE_{joycode}_{input}"
    return "unknown"

def getRoot(config: minidom.Document, name: str, /) -> minidom.Element:
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def getSection(config: minidom.Document, xml_root: minidom.Element, name: str, /) -> minidom.Element:
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

def removeSection(config: minidom.Document, xml_root: minidom.Element, name: str, /) -> None:
    xml_section = xml_root.getElementsByTagName(name)

    for i in range(len(xml_section)):
        old = xml_root.removeChild(xml_section[i])
        old.unlink()
