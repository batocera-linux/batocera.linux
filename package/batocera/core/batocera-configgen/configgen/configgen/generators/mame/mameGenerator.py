from __future__ import annotations

import csv
import logging
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING
from xml.dom import minidom

from PIL import Image

from ... import Command, controllersConfig
from ...batoceraPaths import (
    BATOCERA_SHARE_DIR,
    BIOS,
    CONFIGS,
    DEFAULTS_DIR,
    ROMS,
    SAVES,
    SCREENSHOTS,
    USER_DECORATIONS,
    mkdir_if_not_exists,
)
from ...utils import bezels as bezelsUtil, videoMode as videoMode
from ..Generator import Generator
from . import mameControllers
from .mamePaths import MAME_BIOS, MAME_CHEATS, MAME_CONFIG, MAME_DEFAULT_DATA, MAME_ROMS, MAME_SAVES

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...types import HotkeysContext, Resolution

eslog = logging.getLogger(__name__)


class MameGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "mame",
            "keys": { "exit": "KEY_ESC", "menu": "KEY_TAB", "pause": "KEY_F5", "coin": "KEY_5" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)
        # Extract "<romfile.zip>"
        romBasename = rom_path.name
        romDirname  = rom_path.parent
        romName = rom_path.stem
        romExt = rom_path.suffix

        softDir = Path("/var/run/mame_software/")
        softList = ""
        messModel = ""
        specialController = "none"
        subdirSoftList = [ "mac_hdd", "bbc_hdd", "cdi", "archimedes_hdd", "fmtowns_cd" ]

        # Generate userdata folders if needed
        mamePaths = [
            MAME_CONFIG,
            MAME_SAVES / "nvram",
            MAME_SAVES / "cfg",
            MAME_SAVES / "input",
            MAME_SAVES / "state",
            MAME_SAVES / "diff",
            MAME_SAVES / "comments",
            MAME_BIOS / "artwork" / "crosshairs",
            MAME_CHEATS,
            MAME_SAVES / "plugins",
            MAME_CONFIG / "ctrlr",
            MAME_CONFIG / "ini",
        ]
        for checkPath in mamePaths:
            mkdir_if_not_exists(checkPath)

        messSystems: list[str] = []
        messSysName: list[str] = []
        messRomType: list[str] = []
        messAutoRun: list[str] = []

        with (DEFAULTS_DIR / 'data' / 'mame' / 'messSystems.csv').open() as openFile:
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
            if (ROMS / "fmtowns" / f"{romDirname.name}.zip").exists():
                softList = 'fmtowns_cd'

        commandArray: list[str | Path] =  [ "/usr/bin/mame/mame" ]
        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        commandArray += [ "-skip_gameinfo" ]
        if messMode == -1:
            commandArray += [ "-rompath", f"{romDirname};{MAME_BIOS};{BIOS}" ]
        else:
            if softList in subdirSoftList:
                commandArray += [ "-rompath", f"{romDirname};{MAME_BIOS};{BIOS};{MAME_ROMS};{softDir}" ]
            else:
                commandArray += [ "-rompath", f"{romDirname};{MAME_BIOS};{BIOS};{MAME_ROMS}" ]

        # MAME various paths we can probably do better
        commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
        commandArray += [ "-fontpath",     "/usr/bin/mame/" ]               # Fonts can be left on ROM filesystem
        commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
        commandArray += [ "-pluginspath", f"/usr/bin/mame/plugins/;{MAME_SAVES / 'plugins'}" ]
        commandArray += [ "-samplepath",  MAME_BIOS / "samples" ] # Current batocera storage location for MAME samples
        commandArray += [ "-artpath",     f"/var/run/mame_artwork/;/usr/bin/mame/artwork/;{MAME_BIOS / 'artwork'};{USER_DECORATIONS}" ] # first for systems ; second for overlays

        # Enable cheats
        commandArray += [ "-cheat" ]
        commandArray += [ "-cheatpath",    MAME_CHEATS ]       # Should this point to path containing the cheat.7z file

        # logs
        commandArray += [ "-verbose" ]

        # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
        commandArray += [ "-nvram_directory" ,    MAME_SAVES / "nvram" ]

        # Set custom config path if option is selected or default path if not
        if system.isOptSet("customcfg"):
            customCfg = system.getOptBoolean("customcfg")
        else:
            customCfg = False

        if system.name == "mame":
            if customCfg:
                cfgPath = MAME_CONFIG / "custom"
            else:
                cfgPath = MAME_CONFIG
            mkdir_if_not_exists(MAME_CONFIG)
        else:
            if customCfg:
                cfgPath = MAME_CONFIG / messSysName[messMode] / "custom"
            else:
                cfgPath = MAME_CONFIG / messSysName[messMode]
            mkdir_if_not_exists(MAME_CONFIG / messSysName[messMode])
        mkdir_if_not_exists(cfgPath)

        # MAME will create custom configs per game for MAME ROMs and MESS ROMs with no system attached (LCD games, TV games, etc.)
        # This will allow an alternate config path per game for MESS console/computer ROMs that may need additional config.
        if system.isOptSet("pergamecfg") and system.getOptBoolean("pergamecfg"):
            if not messMode == -1:
                if not messSysName[messMode] == "":
                    base_path = MAME_CONFIG / messSysName[messMode]
                    mkdir_if_not_exists(base_path)
                    cfgPath = base_path / romBasename
                    mkdir_if_not_exists(cfgPath)
        commandArray += [ "-cfg_directory"   ,    cfgPath ]
        commandArray += [ "-input_directory" ,    MAME_SAVES / "input" ]
        commandArray += [ "-state_directory" ,    MAME_SAVES / "state" ]
        commandArray += [ "-snapshot_directory" , SCREENSHOTS ]
        commandArray += [ "-diff_directory" ,     MAME_SAVES / "diff" ]
        commandArray += [ "-comment_directory",   MAME_SAVES / "comments" ]
        commandArray += [ "-homepath" ,           MAME_SAVES / "plugins" ]
        commandArray += [ "-ctrlrpath" ,          MAME_CONFIG / "ctrlr" ]
        commandArray += [ "-inipath" ,            f"{MAME_CONFIG};{MAME_CONFIG / 'ini'}" ]
        commandArray += [ "-crosshairpath" ,      MAME_BIOS / "artwork" / "crosshairs" ]
        if softList != "":
            commandArray += [ "-swpath" ,        softDir ]
            commandArray += [ "-hashpath" ,      softDir / "hash" ]

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
            commandArray += [ "-video", "auto" ]

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
                        rom_extension = rom_path.suffix
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
                    mkdir_if_not_exists(softDir)
                    for checkFile in softDir.iterdir():
                        if checkFile.is_symlink():
                            checkFile.unlink()
                        if checkFile.is_dir():
                            shutil.rmtree(checkFile)
                    mkdir_if_not_exists(softDir / "hash")
                    # Clear existing hashfile links
                    for hashFile in (softDir / "hash").iterdir():
                        if hashFile.suffix == '.xml':
                            hashFile.unlink()
                    (softDir / "hash" / f"{softList}.xml").symlink_to(f"/usr/bin/mame/hash/{softList}.xml")
                    if softList in subdirSoftList:
                        (softDir / softList).symlink_to(romDirname.parents[0], target_is_directory=True)
                        commandArray += [ romDirname.name ]
                    else:
                        (softDir / softList).symlink_to(romDirname, target_is_directory=True)
                        commandArray += [ romName ]

            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually or FM Towns Marty.
            if system.isOptSet('addblankdisk') and system.getOptBoolean('addblankdisk'):
                if system.name == 'fmtowns':
                    blankDisk = Path('/usr/share/mame/blank.fmtowns')
                    targetFolder = MAME_SAVES / system.name
                    targetDisk = targetFolder / romName
                # Add elif statements here for other systems if enabled
                mkdir_if_not_exists(targetFolder)
                if not targetDisk.exists():
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
                    softListFile = Path('/usr/bin/mame/hash') / f'{softList}.xml'
                    if softListFile.exists():
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
                autoRunFile = MAME_CONFIG / 'autoload' / f'{system.name}_{romType}_autoload.csv'
                if autoRunFile.exists():
                    with autoRunFile.open() as openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row and not row[0].startswith('#'):
                                if row[0].casefold() == romName.casefold():
                                    autoRunCmd = row[1] + "\\n"
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = MAME_DEFAULT_DATA / f'{softList}_autoload.csv'
                if autoRunFile.exists():
                    with autoRunFile.open() as openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row[0].casefold() == romName.casefold():
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
                MameGenerator.writeBezelConfig(bezelSet, system, rom_path, messSysName[messMode], gameResolution, controllersConfig.gunsBordersSizeName(guns, system.config), controllersConfig.gunsBorderRatioType(guns, system.config))
            else:
                MameGenerator.writeBezelConfig(bezelSet, system, rom_path, "", gameResolution, controllersConfig.gunsBordersSizeName(guns, system.config), controllersConfig.gunsBorderRatioType(guns, system.config))
        except:
            MameGenerator.writeBezelConfig(None, system, rom_path, "", gameResolution, controllersConfig.gunsBordersSizeName(guns, system.config), controllersConfig.gunsBorderRatioType(guns, system.config))

        buttonLayout = getMameControlScheme(system, rom_path)

        if messMode == -1:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, "", buttonLayout, customCfg, specialController, bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)
        else:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, messModel, buttonLayout, customCfg, specialController, bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)

        # Change directory to MAME folder (allows data plugin to load properly)
        os.chdir('/usr/bin/mame')
        return Command.Command(array=commandArray, env={"PWD":"/usr/bin/mame/","XDG_CONFIG_HOME":CONFIGS, "XDG_CACHE_HOME":SAVES})

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
    def writeBezelConfig(bezelSet: str | None, system: Emulator, rom: Path, messSys: str, gameResolution: Resolution, gunsBordersSize: str | None, gunsBordersRatio: str | None) -> None:
        if messSys == "":
            tmpZipDir = Path("/var/run/mame_artwork") / rom.stem # ok, no need to zip, a folder is taken too
        else:
            tmpZipDir = Path("/var/run/mame_artwork") / messSys # ok, no need to zip, a folder is taken too
        # clean, in case no bezel is set, and in case we want to recreate it
        if tmpZipDir.exists():
            shutil.rmtree(tmpZipDir)

        if bezelSet is None and gunsBordersSize is None:
            return

        if (float (gameResolution["width"]) / float (gameResolution["height"]) < 1.6) and gunsBordersSize is None:
            return

        # let's generate the zip file
        tmpZipDir.mkdir(parents=True)

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
            overlay_png_file = Path("/tmp/bezel_transmame_black.png")
            bezelsUtil.createTransparentBezel(overlay_png_file, gameResolution["width"], gameResolution["height"])
            bz_infos = { "png": overlay_png_file }

        # copy the png inside
        if "mamezip" in bz_infos and bz_infos["mamezip"].exists():
            if messSys == "":
                artFile = Path("/var/run/mame_artwork") / f"{rom.stem}.zip"
            else:
                artFile = Path("/var/run/mame_artwork") / f"{messSys}.zip"
            if artFile.exists():
                artFile.unlink()
            artFile.symlink_to(bz_infos["mamezip"])
            # hum, not nice if guns need borders
            return
        elif "layout" in bz_infos and bz_infos["layout"].exists():
            (tmpZipDir / 'default.lay').symlink_to(bz_infos["layout"])
            (tmpZipDir / bz_infos["png"].name).symlink_to(bz_infos["png"])
        else:
            pngFile = tmpZipDir / "default.png"
            pngFile.symlink_to(bz_infos["png"])
            if "info" in bz_infos and bz_infos["info"].exists():
                bzInfoFile = bz_infos["info"].open("r")
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
                _, _, rotate = MameGenerator.getMameMachineSize(rom.stem, tmpZipDir)

                # assumes that all bezels are setup for 4:3H or 3:4V aspects
                if rotate == 270 or rotate == 90:
                    bz_width = int(img_height * (3 / 4))
                else:
                    bz_width = int(img_height * (4 / 3))
                bz_height = img_height
                bz_x = int((img_width - bz_width) / 2)
                bz_y = 0
                bz_alpha = 1.0

            f = (tmpZipDir / "default.lay").open('w')
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
                    tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{system.name}.png'
                    if not tattoo_file.exists():
                        tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
                    tattoo = Image.open(tattoo_file)
                except Exception as e:
                    eslog.error(f"Error opening controller overlay: {tattoo_file}")
            elif system.config['bezel.tattoo'] == 'custom' and Path(system.config['bezel.tattoo_file']).exists():
                try:
                    tattoo_file = Path(system.config['bezel.tattoo_file'])
                    tattoo = Image.open(tattoo_file)
                except:
                    eslog.error("Error opening custom file: {}".format('tattoo_file'))
            else:
                try:
                    tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
                    tattoo = Image.open(tattoo_file)
                except:
                    eslog.error("Error opening custom file: {}".format('tattoo_file'))
            output_png_file = Path("/tmp/bezel_tattooed.png")
            back = Image.open(pngFile)
            tattoo = tattoo.convert("RGBA")
            back = back.convert("RGBA")
            tw,th = bezelsUtil.fast_image_size(tattoo_file)
            tatwidth = int(240/1920 * img_width) # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
            pcent = float(tatwidth / tw)
            tatheight = int(float(th) * pcent)
            tattoo = tattoo.resize((tatwidth,tatheight), Image.Resampling.LANCZOS)
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
                pngFile.unlink()
            except:
                pass

            pngFile.symlink_to(output_png_file)

        # borders for guns
        if gunsBordersSize is not None:
            output_png_file = Path("/tmp/bezel_gunborders.png")
            innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
            borderSize = bezelsUtil.gunBorderImage(pngFile, output_png_file, gunsBordersRatio, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
            try:
                pngFile.unlink()
            except:
                pass
            pngFile.symlink_to(output_png_file)

    @staticmethod
    def getMameMachineSize(machine: str, tmpdir: Path):
        proc = subprocess.Popen(["/usr/bin/mame/mame", "-listxml", machine], stdout=subprocess.PIPE)
        (out, err) = proc.communicate()
        exitcode = proc.returncode

        if exitcode != 0:
            raise Exception("mame -listxml " + machine + " failed")

        infofile = tmpdir / "infos.xml"
        f = infofile.open("w")
        f.write(out.decode())
        f.close()

        infos = minidom.parse(str(infofile))
        display = infos.getElementsByTagName('display')

        for element in display:
            iwidth  = element.getAttribute("width")
            iheight = element.getAttribute("height")
            irotate = element.getAttribute("rotate")
            return int(iwidth), int(iheight), int(irotate)

        raise Exception("display element not found")

def getMameControlScheme(system: Emulator, rom_path: Path) -> str:
    # Game list files
    mameCapcom = MAME_DEFAULT_DATA / 'mameCapcom.txt'
    mameKInstinct = MAME_DEFAULT_DATA / 'mameKInstinct.txt'
    mameMKombat = MAME_DEFAULT_DATA / 'mameMKombat.txt'
    mameNeogeo = MAME_DEFAULT_DATA / 'mameNeogeo.txt'
    mameTwinstick = MAME_DEFAULT_DATA / 'mameTwinstick.txt'
    mameRotatedstick = MAME_DEFAULT_DATA / 'mameRotatedstick.txt'

    # Controls for games with 5-6 buttons or other unusual controls
    if system.isOptSet("altlayout"):
        controllerType = system.config["altlayout"] # Option was manually selected
    else:
        controllerType = "auto"

    if controllerType in [ "default", "neomini", "neocd", "twinstick", "qbert" ]:
        return controllerType
    else:
        capcomList = set(mameCapcom.read_text().split())
        mkList = set(mameMKombat.read_text().split())
        kiList = set(mameKInstinct.read_text().split())
        neogeoList = set(mameNeogeo.read_text().split())
        twinstickList = set(mameTwinstick.read_text().split())
        qbertList = set(mameRotatedstick.read_text().split())

        romName = rom_path.stem
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
