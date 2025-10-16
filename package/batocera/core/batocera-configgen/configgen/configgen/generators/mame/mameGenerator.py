from __future__ import annotations

import csv
import json
import logging
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING
from xml.dom import minidom

from PIL import Image

from ... import Command
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
from ...exceptions import BatoceraException
from ...utils import bezels as bezelsUtil, videoMode
from ..Generator import Generator
from . import mameControllers
from .mameCommon import is_atom_floppy
from .mamePaths import MAME_BIOS, MAME_CHEATS, MAME_CONFIG, MAME_DEFAULT_DATA, MAME_ROMS, MAME_SAVES

if TYPE_CHECKING:
    from ...Emulator import Emulator
    from ...types import HotkeysContext, Resolution
    from .mameTypes import MameControlScheme

_logger = logging.getLogger(__name__)


class MameGenerator(Generator):

    def supportsInternalBezels(self):
        return True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "mame",
            "keys": { "exit":  "KEY_ESC",
                      "menu":  "KEY_TAB",
                      "pause": "KEY_F5",
                      "reset": "KEY_F3",
                      "coin":  "KEY_5",
                      "fastforward": "KEY_PAGEDOWN",
                      "save_state" : [ "KEY_LEFTSHIFT", "KEY_F6" ],
                      "restore_state": [ "KEY_LEFTSHIFT", "KEY_F7" ] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Extract "<romfile.zip>"
        romBasename = rom.name
        romDirname  = rom.parent
        romName = rom.stem
        romExt = rom.suffix

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

        softList = system.config.get_str("softList", "none")
        softList = softList if softList != "none" else ""

        # Auto softlist for FM Towns if there is a zip that matches the folder name
        # Used for games that require a CD and floppy to both be inserted
        if system.name == 'fmtowns' and softList == '' and (ROMS / "fmtowns" / f"{romDirname.name}.zip").exists():
            softList = 'fmtowns_cd'

        commandArray: list[str | Path] =  [ "/usr/bin/mame/mame" ]
        
        # MAME options used here are explained as it's not always straightforward
        # A lot more options can be configured, just run mame -showusage and have a look
        
        # set audio to pipewire to fix audio from 0.278
        commandArray += [ "-sound", "pipewire" ]
        # skip game info at start
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
        customCfg = system.config.get_bool("customcfg")

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
        if system.config.get_bool("pergamecfg") and messMode != -1 and messSysName[messMode] != "":
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
        video = system.config.get("video")
        if video == "bgfx":
            commandArray += [ "-video", "bgfx" ]

            # BGFX backend
            bgfxbackend = system.config.get("bgfxbackend", "automatic")
            commandArray += [ "-bgfx_backend", "auto" if bgfxbackend == "automatic" else bgfxbackend ]

            # BGFX shaders effects
            commandArray += [ "-bgfx_screen_chains", system.config.get("bgfxshaders", "default") ]

        # Other video modes
        elif video == "accel":
            commandArray += ["-video", "accel" ]
        else:
            commandArray += [ "-video", "auto" ]

        # CRT / SwitchRes support
        if system.config.get_bool("switchres"):
            commandArray += [ "-modeline_generation" ]
            commandArray += [ "-changeres" ]
            commandArray += [ "-modesetting" ]
            commandArray += [ "-readconfig" ]
        else:
            commandArray += [ "-resolution", f"{gameResolution['width']}x{gameResolution['height']}" ]

        # Refresh rate options to help with screen tearing
        # syncrefresh is unlisted, it requires specific display timings and 99.9% of users will get unplayable games.
        # Leaving it so it can be set manually, for CRT or other arcade-specific display users.
        if system.config.get_bool("vsync"):
            commandArray += [ "-waitvsync" ]
        if system.config.get_bool("syncrefresh"):
            commandArray += [ "-syncrefresh" ]

        # Rotation / TATE options
        if (rotation := system.config.get("rotation")) in ["autoror", "autorol"]:
            commandArray += [ f"-{rotation}" ]

        # Artwork crop
        if system.config.get_bool("artworkcrop"):
            commandArray += [ "-artwork_crop" ]

        # UI enable - for computer systems, the default sends all keys to the emulated system.
        # This will enable hotkeys, but some keys may pass through to MAME and not be usable in the emulated system.
        # Hotkey + D-Pad Up will toggle this when in use (scroll lock key)
        if system.config.get_bool("enableui", True):
            commandArray += [ "-ui_active" ]

        # Load selected plugins
        pluginsToLoad = []
        if system.config.get_bool("hiscoreplugin", True):
            pluginsToLoad += [ "hiscore" ]
        if system.config.get_bool("coindropplugin"):
            pluginsToLoad += [ "coindrop" ]
        if system.config.get_bool("dataplugin"):
            pluginsToLoad += [ "data" ]
        if pluginsToLoad:
            commandArray += [ "-plugins", "-plugin", ",".join(pluginsToLoad) ]

        # Mouse
        useMouse = False
        if system.config.get_bool('use_mouse') or not (messSysName[messMode] == "" or messMode == -1):
            useMouse = True
            commandArray += [ "-dial_device", "mouse" ]
            commandArray += [ "-trackball_device", "mouse" ]
            commandArray += [ "-paddle_device", "mouse" ]
            commandArray += [ "-positional_device", "mouse" ]
            commandArray += [ "-mouse_device", "mouse" ]
            commandArray += [ "-ui_mouse" ]
            if not system.config.use_guns:
                commandArray += [ "-lightgun_device", "mouse" ]
                commandArray += [ "-adstick_device", "mouse" ]
        else:
            commandArray += [ "-dial_device", "joystick" ]
            commandArray += [ "-trackball_device", "joystick" ]
            commandArray += [ "-paddle_device", "joystick" ]
            commandArray += [ "-positional_device", "joystick" ]
            commandArray += [ "-mouse_device", "joystick" ]
            if not system.config.use_guns:
                commandArray += [ "-lightgun_device", "joystick" ]
                commandArray += [ "-adstick_device", "joystick" ]
        # Multimouse option currently hidden in ES, SDL only detects one mouse.
        # Leaving code intact for testing & possible ManyMouse integration
        multiMouse = system.config.get_bool('multimouse')
        if multiMouse:
            commandArray += [ "-multimouse" ]

        # guns
        useGuns = system.config.use_guns
        if useGuns:
            commandArray += [ "-lightgunprovider", "udev" ]
            commandArray += [ "-lightgun_device", "lightgun" ]
            commandArray += [ "-adstick_device", "lightgun" ]
        if system.config.get_bool('offscreenreload'):
            commandArray += [ "-offscreen_reload" ]

        # wheels
        useWheels = system.config.use_wheels

        if system.config.get_bool('multiscreens'):
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
            if altmodel := system.config.get("altmodel"):
                messModel = altmodel
            commandArray += [ messModel ]

            #TI-99 32k RAM expansion & speech modules - enabled by default
            if system.name == "ti99":
                commandArray += [ "-ioport", "peb" ]
                if system.config.get_bool("ti99_32kram", True):
                    commandArray += ["-ioport:peb:slot2", "32kmem"]
                if system.config.get_bool("ti99_speech", True):
                    commandArray += ["-ioport", "speechsyn"]

            #Laser 310 Memory Expansion & Joystick
            if system.name == "laser310":
                commandArray += ['-io', 'joystick', "-mem", system.config.get('memslot', 'laser_64k')]

            # BBC Joystick
            if system.name == "bbc" and (sticktype := system.config.get('sticktype', 'none')) != 'none':
                commandArray += ["-analogue", sticktype]
                specialController = sticktype

            # Apple II
            if system.name == "apple2":
                rom_extension = rom.suffix.lower()
                # only add SD/IDE control if provided a hard drive image
                if rom_extension in {".hdv", ".2mg", ".chd", ".iso", ".bin", ".cue"}:
                    commandArray += ["-sl7", "cffa202"]
                if (gameio := system.config.get('gameio', 'none')) != 'none':
                    if gameio == 'joyport' and messModel != 'apple2p':
                        _logger.debug("Joyport joystick is only compatible with Apple II Plus")
                    else:
                        commandArray += ["-gameio", gameio]
                        specialController = gameio

            # RAM size (Mac excluded, special handling below)
            ramSize = system.config.get_int('ramsize')
            if system.name != "macintosh" and ramSize:
                commandArray += [ '-ramsize', f'{ramSize}M' ]

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
                    commandArray += [ '-ramsize', f'{ramSize}M' ]
                if messModel == 'maciix':
                    imageSlot = system.config.get('imagereader', 'nba')
                    if imageSlot != "disabled":
                        commandArray += [ f"-{imageSlot}", "image" ]

            altromtype = system.config.get_str("altromtype")

            if softList == "":
                # Boot disk for Macintosh
                # Will use Floppy 1 or Hard Drive, depending on the disk.
                boot_disk = system.config.get("bootdisk")
                if system.name == "macintosh" and boot_disk:
                    if boot_disk in [ "macos30", "macos608", "macos701", "macos75" ]:
                        bootType = "-flop1"
                        bootDisk = f"/userdata/bios/{boot_disk}.img"
                    else:
                        bootType = "-hard"
                        bootDisk = f"/userdata/bios/{boot_disk}.chd"
                    commandArray += [ bootType, bootDisk ]

                # Alternate ROM type for systems with mutiple media (ie cassette & floppy)
                # Mac will auto change floppy 1 to 2 if a boot disk is enabled
                # Only one drive on FMTMarty
                if system.name != "macintosh":
                    if altromtype:
                        if messModel == "fmtmarty" and altromtype == "flop1":
                            commandArray += [ "-flop" ]
                        else:
                            commandArray += [ f'-{altromtype}' ]
                    elif system.name == "adam":
                        # add some logic based on the rom extension
                        rom_extension = rom.suffix
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
                        commandArray += [ f'-{messRomType[messMode]}' ]
                else:
                    if boot_disk:
                        if (altromtype == "flop1" or not altromtype) and boot_disk in [ "macos30", "macos608", "macos701", "macos75" ]:
                            commandArray += [ "-flop2" ]
                        elif altromtype:
                            commandArray += [ f'-{altromtype}' ]
                        else:
                            commandArray += [ f'-{messRomType[messMode]}' ]
                    else:
                        if altromtype:
                            commandArray += [ f'-{altromtype}' ]
                        else:
                            commandArray += [ f'-{messRomType[messMode]}' ]
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
                    (softDir / "hash" / f"{softList}.xml").symlink_to(f"/usr/bin/mame/hash/{softList}.xml")
                    if softList in subdirSoftList:
                        (softDir / softList).symlink_to(romDirname.parents[0], target_is_directory=True)
                        commandArray += [ romDirname.name ]
                    else:
                        (softDir / softList).symlink_to(romDirname, target_is_directory=True)
                        commandArray += [ romName ]

            # Create & add a blank disk if needed, insert into drive 2
            # or drive 1 if drive 2 is selected manually or FM Towns Marty.
            if system.config.get_bool('addblankdisk'):
                if system.name == 'fmtowns':
                    blankDisk = Path('/usr/share/mame/blank.fmtowns')
                    targetFolder = MAME_SAVES / system.name
                    targetDisk = targetFolder / romName
                # Add elif statements here for other systems if enabled
                else:
                    blankDisk = Path('/usr/share/mame/blank.default')
                    targetFolder = MAME_SAVES / system.name
                    targetDisk = targetFolder / f'{romName}.default'
                mkdir_if_not_exists(targetFolder)
                if not targetDisk.exists():
                    shutil.copy2(blankDisk, targetDisk)
                # Add other single floppy systems to this if statement
                if messModel == "fmtmarty":
                    commandArray += [ '-flop', targetDisk ]
                elif system.config.get('altromtype') == 'flop2':
                    commandArray += [ '-flop1', targetDisk ]
                else:
                    commandArray += [ '-flop2', targetDisk ]

            autoRunCmd = ""
            autoRunDelay = 0
            # Autostart computer games where applicable
            # bbc has different boots for floppy & cassette, no special boot for carts
            if system.name == "bbc":
                if altromtype or softList:
                    if altromtype == "cass" or softList.endswith("cass"):
                        autoRunCmd = '*tape\\nchain""\\n'
                        autoRunDelay = 2
                    elif (altromtype and altromtype.startswith("flop")) or softList.endswith("flop"):
                        autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                        autoRunDelay = 3
                else:
                    autoRunCmd = '*cat\\n\\n\\n\\n*exec !boot\\n'
                    autoRunDelay = 3
            # fm7 boots floppies, needs cassette loading
            elif system.name == "fm7":
                if (
                    altromtype == "cass"
                    or (softList and softList[-4:] == "cass")
                ):
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
                            if software.attrib and software.get('name') == romName:
                                for info in software.iter('info'):
                                    if info.get('name') == 'usage':
                                        autoRunCmd = f"{info.get('value')}\\n"

                # if still undefined, default autoRunCmd based on media type
                if autoRunCmd == "":
                    if altromtype == "cass" or (softList and softList.endswith("cass")) or romExt.casefold() == ".cas":
                        romType = 'cass'
                        if romName.casefold().endswith(".bas"):
                            autoRunCmd = 'CLOAD:RUN\\n'
                        else:
                            autoRunCmd = 'CLOADM:EXEC\\n'
                    if (altromtype == "flop1") or (softList and softList.endswith("flop")) or romExt.casefold() == ".dsk":
                        romType = 'flop'
                        if romName.casefold().endswith(".bas"):
                            autoRunCmd = f'RUN \"{romName}\"\\n'
                        else:
                            autoRunCmd = f'LOADM \"{romName}\":EXEC\\n'

                # check for a user override
                autoRunFile = MAME_CONFIG / 'autoload' / f'{system.name}_{romType}_autoload.csv'
                if autoRunFile.exists():
                    with autoRunFile.open() as openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row and not row[0].startswith('#') and row[0].casefold() == romName.casefold():
                                autoRunCmd = f"{row[1]}\\n"
            elif system.name == "atom":
                autoRunDelay = 1
                autoRunCmd = messAutoRun[messMode]
                # Check if the media being used is a floppy type
                if (
                    (altromtype == "flop1") or
                    (softList and softList.endswith("flop")) or
                    is_atom_floppy(rom)
                ):
                    autoRunFile = MAME_DEFAULT_DATA / 'atom_flop_autoload.csv'
                    if autoRunFile.exists():
                        with autoRunFile.open() as openARFile:
                            autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                            for row in autoRunList:
                                if row and not row[0].startswith('#') and row[0].casefold() == romName.casefold():
                                    autoRunCmd = f"{row[1]}\\n"
                                    break
            else:
                # Check for an override file, otherwise use generic (if it exists)
                autoRunCmd = messAutoRun[messMode]
                autoRunFile = MAME_DEFAULT_DATA / f'{softList}_autoload.csv'
                if autoRunFile.exists():
                    with autoRunFile.open() as openARFile:
                        autoRunList = csv.reader(openARFile, delimiter=';', quotechar="'")
                        for row in autoRunList:
                            if row[0].casefold() == romName.casefold():
                                autoRunCmd = f"{row[1]}\\n"
                                autoRunDelay = 3
            if autoRunCmd != "":
                if autoRunCmd.startswith("'"):
                    autoRunCmd.replace("'", "")
                commandArray += [ "-autoboot_delay", str(autoRunDelay), "-autoboot_command", autoRunCmd ]

        # bezels
        bezelSet = system.config.get_str('bezel') or None
        if system.config.get_bool('forceNoBezel'):
            bezelSet = None

        try:
            if messMode != -1:
                MameGenerator.writeBezelConfig(bezelSet, system, rom, messSysName[messMode], gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
            else:
                MameGenerator.writeBezelConfig(bezelSet, system, rom, "", gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
        except Exception:
            MameGenerator.writeBezelConfig(None, system, rom, "", gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))

        buttonLayout = getMameControlScheme(system, rom)

        if messMode == -1:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, "", buttonLayout, customCfg, specialController, bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)
        else:
            mameControllers.generatePadsConfig(cfgPath, playersControllers, messModel, buttonLayout, customCfg, specialController, bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)

        # If user provided a custom cmd file at the default location, use that as the customized commandArray
        if (defaultCustomCmdFilepath := Path(f"{rom}.cmd")).is_file():
            with defaultCustomCmdFilepath.open() as f:
                commandArray = f.read().splitlines()  # pyright: ignore

        # Change directory to MAME folder (allows data plugin to load properly)
        os.chdir('/usr/bin/mame')
        return Command.Command(
            array=commandArray,
            env={
                "PWD":"/usr/bin/mame/",
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_CACHE_HOME": SAVES
                }
            )

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
            if bz_infos is None and gunsBordersSize is None:
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

        if "layout" in bz_infos and bz_infos["layout"].exists():
            (tmpZipDir / 'default.lay').symlink_to(bz_infos["layout"])
            pngFile = tmpZipDir / bz_infos["png"].name
            pngFile.symlink_to(bz_infos["png"])
            img_width, img_height = bezelsUtil.fast_image_size(bz_infos["png"])
        else:
            pngFile = tmpZipDir / "default.png"
            pngFile.symlink_to(bz_infos["png"])
            if "info" in bz_infos and bz_infos["info"].exists():
                bz_info_data = json.loads(bz_infos["info"].read_text())

                img_width: int = bz_info_data["width"]
                img_height: int = bz_info_data["height"]
                bz_y: int = bz_info_data["top"]
                bz_x: int = bz_info_data["left"]
                bz_bottom: int = bz_info_data["bottom"]
                bz_right: int = bz_info_data["right"]
                bz_alpha: float = bz_info_data.get("opacity", 1.0)  # Just in case it's not set in the info file

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
            f.write(f"<screen index=\"0\"><bounds x=\"{bz_x}\" y=\"{bz_y}\" width=\"{bz_width}\" height=\"{bz_height}\" /></screen>\n")
            f.write(f"<element ref=\"bezel\"><bounds x=\"0\" y=\"0\" width=\"{img_width}\" height=\"{img_height}\" alpha=\"{bz_alpha}\" /></element>\n")
            f.write("</view>\n")
            f.write("</mamelayout>\n")
            f.close()

        if (bezel_tattoo := system.config.get_str('bezel.tattoo', "0")) != "0":
            tattoo: Image.Image | None = None

            if bezel_tattoo == 'system':
                tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / f'{system.name}.png'
                if not tattoo_file.exists():
                    tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error("Error opening controller overlay: %s", tattoo_file)
            elif bezel_tattoo == 'custom' and (bezel_tattoo_file := system.config.get_str('bezel.tattoo_file')) and (tattoo_file := Path(bezel_tattoo_file)).exists():
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error("Error opening custom file: %s", tattoo_file)
            else:
                tattoo_file = BATOCERA_SHARE_DIR / 'controller-overlays' / 'generic.png'
                try:
                    tattoo = Image.open(tattoo_file)
                except Exception:
                    _logger.error("Error opening custom file: %s", tattoo_file)

            if tattoo is not None:
                output_png_file = Path("/tmp/bezel_tattooed.png")
                back = Image.open(pngFile)
                tattoo = tattoo.convert("RGBA")
                back = back.convert("RGBA")
                tw,th = bezelsUtil.fast_image_size(tattoo_file)
                tatwidth = int(240/1920 * img_width) # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
                pcent = float(tatwidth / tw)
                tatheight = int(float(th) * pcent)
                tattoo = tattoo.resize((tatwidth,tatheight), Image.Resampling.LANCZOS)
                alphatat = tattoo.split()[-1]
                corner = system.config.get_str('bezel.tattoo_corner', 'NW')
                if corner.upper() == 'NE':
                    back.paste(tattoo, (img_width-tatwidth,20), alphatat) # 20 pixels vertical margins (on 1080p)
                elif corner.upper() == 'SE':
                    back.paste(tattoo, (img_width-tatwidth,img_height-tatheight-20), alphatat)
                elif corner.upper() == 'SW':
                    back.paste(tattoo, (0,img_height-tatheight-20), alphatat)
                else: # default = NW
                    back.paste(tattoo, (0,20), alphatat)
                imgnew = Image.new("RGBA", (img_width,img_height), (0,0,0,255))
                imgnew.paste(back, (0,0,img_width,img_height))
                imgnew.save(output_png_file, mode="RGBA", format="PNG")

                try:
                    pngFile.unlink()
                except Exception:
                    pass

                pngFile.symlink_to(output_png_file)

        # borders for guns
        if gunsBordersSize is not None:
            output_png_file = Path("/tmp/bezel_gunborders.png")
            innerSize, outerSize = bezelsUtil.gunBordersSize(gunsBordersSize)
            bezelsUtil.gunBorderImage(pngFile, output_png_file, gunsBordersRatio, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
            try:
                pngFile.unlink()
            except Exception:
                pass
            pngFile.symlink_to(output_png_file)

    @staticmethod
    def getMameMachineSize(machine: str, tmpdir: Path):
        proc = subprocess.Popen(["/usr/bin/mame/mame", "-listxml", machine], stdout=subprocess.PIPE)
        (out, _) = proc.communicate()
        exitcode = proc.returncode

        if exitcode != 0:
            raise BatoceraException(f"mame -listxml {machine} failed")

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

        raise BatoceraException("Display element not found")

def getMameControlScheme(system: Emulator, rom_path: Path) -> MameControlScheme:
    # Game list files
    mameCapcom = MAME_DEFAULT_DATA / 'mameCapcom.txt'
    mameKInstinct = MAME_DEFAULT_DATA / 'mameKInstinct.txt'
    mameMKombat = MAME_DEFAULT_DATA / 'mameMKombat.txt'
    mameNeogeo = MAME_DEFAULT_DATA / 'mameNeogeo.txt'
    mameTwinstick = MAME_DEFAULT_DATA / 'mameTwinstick.txt'
    mameRotatedstick = MAME_DEFAULT_DATA / 'mameRotatedstick.txt'

    # Controls for games with 5-6 buttons or other unusual controls
    controllerType = system.config.get("altlayout", "auto")

    if controllerType in [ "default", "neomini", "neocd", "twinstick", "qbert" ]:
        return controllerType  # pyright: ignore[reportReturnType]

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
        if controllerType == "megadrive":
            return "mddefault"

    return "default"
