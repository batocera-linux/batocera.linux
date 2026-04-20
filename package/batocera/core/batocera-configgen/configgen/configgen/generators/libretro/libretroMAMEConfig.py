from __future__ import annotations

import codecs
import csv
import json
import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING
from xml.dom import minidom

from ...batoceraPaths import BIOS, CONFIGS, DEFAULTS_DIR, SAVES, USER_DECORATIONS, mkdir_if_not_exists
from ...exceptions import BatoceraException
from ..mame.mamePaths import MESS_AUTOBOOT_SCRIPTS, MESS_SYSTEMS_MAPPING
from ..mame.messUtils import (
    _build_config_args,
    _build_rom_ext_args,
    _compute_sha1,
    _load_softlist_map,
    _lookup_rom,
    _machine_from_softlist,
)

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
    "b":                "BUTTON1",
    "a":                "BUTTON2",
    "y":                "BUTTON3",
    "x":                "BUTTON4",
    "pageup":           "BUTTON5",
    "pagedown":         "BUTTON6",
    "l2":               "RZAXIS_POS_SWITCH",
    "r2":               "ZAXIS_POS_SWITCH",
    "l3":               "BUTTON12",
    "r3":               "BUTTON11",
    "select":           "SELECT",
    "start":            "START"
}


def _corePath(system: Emulator) -> str:
    if system.config.core in ['mame', 'mess', 'mamevirtual']:
        return f"lr-mame"
    return str(system.config.core)


def appendCommonCommandArgs(commandLine: list, system: Emulator, rom: Path) -> None:
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
    # Share plugins with standalone MAME (except TI99)
    if system.name != "ti99":
        commandLine += [ "-pluginspath", f"/usr/bin/mame/plugins/;{SAVES / 'mame' / 'plugins'}" ]
        commandLine += [ "-homepath" , SAVES / 'mame' / 'plugins' ]
    # Share samples with standalone MAME (except gamecom and TI99)
    if system.name not in ['gamecom', 'ti99']:
        commandLine += [ "-samplepath", BIOS / "mame" / "samples" ]
    mkdir_if_not_exists(SAVES / "mame" / "plugins")
    mkdir_if_not_exists(BIOS / "mame" / "samples")


def writeCmdFile(commandLine: list, rom: Path) -> None:
    cmdPath = Path("/var/run/cmdfiles")
    mkdir_if_not_exists(cmdPath)
    for file in cmdPath.iterdir():
        if file.suffix == ".cmd":
            file.unlink()
    cmdFilename = cmdPath / f"{rom.stem}.cmd"
    if Path(defaultCustomCmdFilepath := f"{rom}.cmd").is_file():
        shutil.copyfile(defaultCustomCmdFilepath, cmdFilename)
    else:
        cmdFile = cmdFilename.open("w")
        cmdFile.write(' '.join(str(item) for item in commandLine))
        cmdFile.close()


def generateMAMEConfigs(playersControllers: Controllers, system: Emulator, rom: Path, guns: Guns) -> None:
    if system.config.core == 'mess' or system.config.core == 'same_cdi':
        return generateMessConfigs(playersControllers, system, rom, guns)

    # Generate command line for MAME/MAMEVirtual
    commandLine: list[str | Path] = []
    romDrivername = rom.stem
    specialController = 'none'

    corePath = _corePath(system)

    if system.config.get_bool("customcfg"):
        cfgPath = CONFIGS / corePath / "custom"
    else:
        cfgPath = SAVES / "mame" / "mame" / "cfg"
    mkdir_if_not_exists(cfgPath)
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

    appendCommonCommandArgs(commandLine, system, rom)
    writeCmdFile(commandLine, rom)

    # Call Controller Config (arcade path always uses "" as messModel and 'none' as specialController)
    generateMAMEPadConfig(cfgPath, playersControllers, system, "", rom, specialController, guns)


def generateMessConfigs(playersControllers: Controllers, system: Emulator, rom: Path, guns: Guns) -> None:
    corePath = _corePath(system)
    specialController = 'none'

    # ------------------------------------------------------------------ #
    # 1. Identify system: attempt SHA1 autodetection first
    # ------------------------------------------------------------------ #
    softlist_map = _load_softlist_map()

    rom_sha1 = _compute_sha1(rom)
    _logger.debug("lr-MESS: SHA1 of %s = %s", rom.name, rom_sha1)

    rom_info = _lookup_rom(rom_sha1)
    if rom_info is not None:
        softlist = rom_info["softlist"]
        xml_media = rom_info["media"]
        _logger.info(
            "lr-MESS: identified %s as softlist=%s software=%s xml_media=%s",
            rom.name, softlist, rom_info["software"], xml_media,
        )
        sys_info = softlist_map.get(softlist, {})
        machine = system.config.get_str("altmodel") or sys_info.get("machine")
        if not machine:
            machine = _machine_from_softlist(softlist)
            _logger.info(
                "lr-MESS: softlist '%s' not in messSoftlistMap.json, inferred machine=%s",
                softlist, machine,
            )
        # Priority: user override > messSoftlistMap > MAME hash XML
        media = system.config.get_str("altromtype") or sys_info.get("media") or xml_media
        _logger.info(
            "lr-MESS: media resolved to %s (softlistmap=%s xml=%s)",
            media, sys_info.get("media"), xml_media,
        )
    else:
        # ROM not found — try messSystems.json lookup by system name + extension
        softlist = ""
        sys_info = {}
        try:
            systems_mapping = json.loads(MESS_SYSTEMS_MAPPING.read_text())
            sys_ext_map = systems_mapping.get(system.name, {})
            rom_ext = rom.suffix.lower()
            if rom_ext == ".zip":
                try:
                    with zipfile.ZipFile(rom, "r") as zf:
                        names = [n for n in zf.namelist() if not n.endswith("/")]
                        if names:
                            rom_ext = Path(names[0]).suffix.lower()
                except (zipfile.BadZipFile, OSError):
                    pass
            softlist = sys_ext_map.get(rom_ext) or sys_ext_map.get("*") or ""
            if softlist:
                _logger.info(
                    "lr-MESS: ROM not autodetected — found system '%s' ext '%s' in messSystems.json: softlist=%s",
                    system.name, rom_ext, softlist,
                )
        except OSError:
            _logger.warning("lr-MESS: messSystems.json not found at %s", MESS_SYSTEMS_MAPPING)

        if softlist:
            sys_info = softlist_map.get(softlist, {})
            machine = system.config.get_str("altmodel") or sys_info.get("machine")
            if not machine:
                machine = _machine_from_softlist(softlist)
                _logger.info(
                    "lr-MESS: softlist '%s' not in messSoftlistMap.json, inferred machine=%s",
                    softlist, machine,
                )
        else:
            machine = None

        machine = system.config.get_str("machine") or machine
        # Priority: user override > messSoftlistMap
        media = system.config.get_str("media") or sys_info.get("media")
        if not machine or not media:
            raise BatoceraException(
                f"ROM '{rom.name}' (sha1={rom_sha1}) was not found in the MAME "
                "software-list database. "
                "Machine and media must be configured manually "
                "(set 'machine' and 'media' in the system options)."
            )
        _logger.info("lr-MESS: ROM not autodetected — using machine=%s media=%s", machine, media)

    # ------------------------------------------------------------------ #
    # 2. Config path
    # ------------------------------------------------------------------ #
    if system.config.get_bool("customcfg"):
        cfgPath = CONFIGS / corePath / machine / "custom"
    else:
        cfgPath = SAVES / "mame" / "cfg" / machine
    if system.config.get_bool("pergamecfg"):
        cfgPath = CONFIGS / corePath / machine / rom.name
    mkdir_if_not_exists(cfgPath)

    # ------------------------------------------------------------------ #
    # 3. Build command line
    # ------------------------------------------------------------------ #
    commandLine: list[str | Path] = []

    # Machine
    commandLine += [machine]

    # Extra static args from softlist map
    for arg in sys_info.get("extra_args", []):
        commandLine.append(arg)

    # Config-driven args
    commandLine += _build_config_args(sys_info.get("config_args", []), system, machine)

    # Extension-driven args
    commandLine += _build_rom_ext_args(sys_info.get("rom_ext_args", []), rom)

    # Media flag and ROM path (quoted)
    commandLine += [f"-{media}", f'"{rom}"']

    # ROM search path
    commandLine += ["-rompath", f'"{rom.parent};/userdata/bios/"']

    # Config directory
    commandLine += ["-cfg_directory", f'"{cfgPath}"']

    # UI active (enabled by default for computer systems)
    if system.config.get_bool("enableui", True):
        commandLine += ["-ui_active"]

    # Autoboot Lua script
    lua_script_name = sys_info.get("lua_script")
    if lua_script_name:
        lua_path = MESS_AUTOBOOT_SCRIPTS / lua_script_name
        if lua_path.exists():
            commandLine += ["-autoboot_script", f'"{lua_path}"']
        else:
            _logger.warning("lr-MESS: Lua autoboot script not found: %s", lua_path)

    # Blank disk handling
    if system.config.get_bool("addblankdisk"):
        altromtype = system.config.get_str("altromtype")
        lr_mess_dsk = SAVES / 'lr-mess' / system.name / rom.stem
        if not lr_mess_dsk.exists():
            lr_mess_dsk.parent.mkdir(parents=True)
            shutil.copy2('/usr/share/mame/blank.dsk', lr_mess_dsk)
        if altromtype == 'flop2':
            commandLine += ['-flop1', f'"{lr_mess_dsk}"']
        else:
            commandLine += ['-flop2', f'"{lr_mess_dsk}"']

    # ------------------------------------------------------------------ #
    # 4. Common suffix args, write cmd file, pad config
    # ------------------------------------------------------------------ #
    appendCommonCommandArgs(commandLine, system, rom)
    writeCmdFile(commandLine, rom)
    generateMAMEPadConfig(cfgPath, playersControllers, system, machine, rom, specialController, guns)


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
        if controllerType in [ "auto", "snes", "fightstick" ]:
            return "sfsnes"
        if controllerType == "megadrive":
            return "megadrive"
    elif romName in mkList:
        if controllerType in [ "auto", "snes", "fightstick" ]:
            return "mksnes"
        if controllerType == "megadrive":
            return "mkmegadrive"
    elif romName in kiList:
        if controllerType in [ "auto", "snes", "fightstick" ]:
            return "kisnes"
        if controllerType == "megadrive":
            return "megadrive"
    elif romName in  neogeoList:
        return "neomini"
    elif romName in  twinstickList:
        return "twinstick"
    elif romName in  qbertList:
        return "qbert"
    else:
        if controllerType == "fightstick":
            return "sfsnes"

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
