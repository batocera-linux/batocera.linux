from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING
from xml.dom import minidom

from PIL import Image

from ... import Command
from ...batoceraPaths import (
    BATOCERA_SHARE_DIR,
    BIOS,
    CONFIGS,
    SAVES,
    SCREENSHOTS,
    USER_DECORATIONS,
    mkdir_if_not_exists,
)
from ...exceptions import BatoceraException
from ...utils import bezels as bezelsUtil, videoMode
from ..Generator import Generator
from . import mameControllers
from .mamePaths import MAME_BIOS, MAME_CHEATS, MAME_CONFIG, MAME_DEFAULT_DATA, MAME_SAVES, MESS_AUTOBOOT_SCRIPTS, MESS_SYSTEMS_MAPPING
from .messUtils import (
    _build_config_args,
    _build_rom_ext_args,
    _compute_sha1,
    _load_softlist_map,
    _lookup_rom,
    _machine_from_softlist,
)

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
        if system.config.core == 'mess':
            return _generate_mess(system, rom, playersControllers, metadata, guns, wheels, gameResolution)
        else:
            return _generate_mame(system, rom, playersControllers, metadata, guns, wheels, gameResolution)

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

def _generate_mame(system, rom, playersControllers, metadata, guns, wheels, gameResolution):
    romBasename = rom.name
    customCfg = system.config.get_bool("customcfg")
    cfgPath = MAME_CONFIG / "custom" if customCfg else MAME_CONFIG

    extra_plugins = [ "offscreenreload" ] if system.config.get_bool('offscreenreload') else []
    commandArray = _mame_common_options(system, rom, cfgPath, gameResolution, extra_plugins)

    # Mouse
    useMouse = False
    if system.config.get_bool('use_mouse'):
        useMouse = True
        commandArray += [ "-dial_device", "mouse", "-trackball_device", "mouse",
                          "-paddle_device", "mouse", "-positional_device", "mouse",
                          "-mouse_device", "mouse", "-ui_mouse" ]
        if not system.config.use_guns:
            commandArray += [ "-lightgun_device", "mouse", "-adstick_device", "mouse" ]
    else:
        commandArray += [ "-dial_device", "joystick", "-trackball_device", "joystick",
                          "-paddle_device", "joystick", "-positional_device", "joystick",
                          "-mouse_device", "joystick" ]
        if not system.config.use_guns:
            commandArray += [ "-lightgun_device", "joystick", "-adstick_device", "joystick" ]

    # Multimouse option currently hidden in ES, SDL only detects one mouse.
    # Leaving code intact for testing & possible ManyMouse integration
    multiMouse = system.config.get_bool('multimouse')
    if multiMouse:
        commandArray += [ "-multimouse" ]

    useGuns = system.config.use_guns
    if useGuns:
        commandArray += [ "-lightgunprovider", "udev",
                          "-lightgun_device", "lightgun", "-adstick_device", "lightgun" ]

    useWheels = system.config.use_wheels

    commandArray += [ romBasename ]

    bezelSet = system.config.get_str('bezel') or None
    if system.config.get_bool('forceNoBezel'):
        bezelSet = None
    try:
        MameGenerator.writeBezelConfig(bezelSet, system, rom, "", gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
    except Exception:
        MameGenerator.writeBezelConfig(None, system, rom, "", gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))

    buttonLayout = getMameControlScheme(system, rom)
    mameControllers.generatePadsConfig(cfgPath, playersControllers, "", buttonLayout, customCfg, "none", bezelSet, useGuns, guns, useWheels, wheels, useMouse, multiMouse, system)

    if (defaultCustomCmdFilepath := Path(f"{rom}.cmd")).is_file():
        with defaultCustomCmdFilepath.open() as f:
            commandArray = f.read().splitlines()

    os.chdir('/usr/bin/mame')
    return Command.Command(
        array=commandArray,
        env={
            "PWD":"/usr/bin/mame/",
            "XDG_CONFIG_HOME": CONFIGS,
            "XDG_CACHE_HOME": SAVES,
        }
    )


def _mame_common_options(system, rom, cfgPath, gameResolution, extra_plugins=None):
    """Build the command-line args and create dirs common to MAME arcade and MESS."""
    romDirname = rom.parent

    for path in [
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
    ]:
        mkdir_if_not_exists(path)
    mkdir_if_not_exists(cfgPath)

    # MAME options used here are explained as it's not always straightforward
    # A lot more options can be configured, just run mame -showusage and have a look
    commandArray: list[str | Path] = [ "/usr/bin/mame/mame" ]

    # set audio to pipewire to fix audio from 0.278
    commandArray += [ "-sound", "pipewire" ]
    # skip game info at start
    commandArray += [ "-skip_gameinfo" ]
    commandArray += [ "-rompath", f"{romDirname};{MAME_BIOS};{BIOS}" ]

    # MAME various paths we can probably do better
    commandArray += [ "-bgfx_path",    "/usr/bin/mame/bgfx/" ]          # Core bgfx files can be left on ROM filesystem
    commandArray += [ "-fontpath",     "/usr/bin/mame/" ]               # Fonts can be left on ROM filesystem
    commandArray += [ "-languagepath", "/usr/bin/mame/language/" ]      # Translations can be left on ROM filesystem
    commandArray += [ "-pluginspath",  f"/usr/bin/mame/plugins/;{MAME_SAVES / 'plugins'}" ]
    commandArray += [ "-samplepath",   MAME_BIOS / "samples" ]          # Current batocera storage location for MAME samples
    commandArray += [ "-artpath",      f"/var/run/mame_artwork/;/usr/bin/mame/artwork/;{MAME_BIOS / 'artwork'};{USER_DECORATIONS}" ] # first for systems ; second for overlays

    # Enable cheats
    commandArray += [ "-cheat" ]
    commandArray += [ "-cheatpath",    MAME_CHEATS ]       # Should this point to path containing the cheat.7z file

    # Logs and SwitchRes ini read by default (including its own verbose)
    commandArray += [ "-verbose" ]
    commandArray += [ "-switchres_ini" ]

    # MAME saves a lot of stuff, we need to map this on /userdata/saves/mame/<subfolder> for each one
    commandArray += [ "-nvram_directory",    MAME_SAVES / "nvram" ]
    commandArray += [ "-cfg_directory",      cfgPath ]
    commandArray += [ "-input_directory",    MAME_SAVES / "input" ]
    commandArray += [ "-state_directory",    MAME_SAVES / "state" ]
    commandArray += [ "-snapshot_directory", SCREENSHOTS ]
    commandArray += [ "-diff_directory",     MAME_SAVES / "diff" ]
    commandArray += [ "-comment_directory",  MAME_SAVES / "comments" ]
    commandArray += [ "-homepath",           MAME_SAVES / "plugins" ]
    commandArray += [ "-ctrlrpath",          MAME_CONFIG / "ctrlr" ]
    commandArray += [ "-inipath",            f"{MAME_CONFIG};{MAME_CONFIG / 'ini'}" ]
    commandArray += [ "-crosshairpath",      MAME_BIOS / "artwork" / "crosshairs" ]

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
        commandArray += [ "-video", "accel" ]
    else:
        commandArray += [ "-video", "auto" ]

    # CRT / SwitchRes support
    if system.config.get_bool("switchres"):
        commandArray += [ "-modeline_generation", "-changeres", "-modesetting", "-readconfig" ]
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
    if extra_plugins:
        pluginsToLoad.extend(extra_plugins)
    if pluginsToLoad:
        commandArray += [ "-plugins", "-plugin", ",".join(pluginsToLoad) ]

    if system.config.get_bool("multiscreens"):
        screens = videoMode.getScreensInfos(system.config)
        if len(screens) > 1:
            commandArray += [ "-numscreens", str(len(screens)) ]

    return commandArray


def _generate_mess(system, rom, playersControllers, metadata, guns, wheels, gameResolution):
    for path in [
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
    ]:
        mkdir_if_not_exists(path)

    softlist_map = _load_softlist_map()
    rom_sha1 = _compute_sha1(rom)
    _logger.debug("MESS: SHA1 of %s = %s", rom.name, rom_sha1)

    rom_info = _lookup_rom(rom_sha1)
    if rom_info is not None:
        softlist = rom_info["softlist"]
        xml_media = rom_info["media"]
        _logger.info("MESS: identified %s as softlist=%s software=%s xml_media=%s",
                     rom.name, softlist, rom_info["software"], xml_media)
        sys_info = softlist_map.get(softlist, {})
        machine = system.config.get_str("altmodel") or sys_info.get("machine")
        if not machine:
            machine = _machine_from_softlist(softlist)
            _logger.info("MESS: softlist '%s' not in messSoftlistMap.json, inferred machine=%s",
                         softlist, machine)
        media = system.config.get_str("altromtype") or sys_info.get("media") or xml_media
        _logger.info("MESS: media resolved to %s (softlistmap=%s xml=%s)",
                     media, sys_info.get("media"), xml_media)
    else:
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
                _logger.info("MESS: ROM not autodetected — found system '%s' ext '%s' in messSystems.json: softlist=%s",
                             system.name, rom_ext, softlist)
        except OSError:
            _logger.warning("MESS: messSystems.json not found at %s", MESS_SYSTEMS_MAPPING)

        if softlist:
            sys_info = softlist_map.get(softlist, {})
            machine = system.config.get_str("altmodel") or sys_info.get("machine")
            if not machine:
                machine = _machine_from_softlist(softlist)
                _logger.info("MESS: softlist '%s' not in messSoftlistMap.json, inferred machine=%s",
                             softlist, machine)
        else:
            machine = None

        machine = system.config.get_str("machine") or machine
        media = system.config.get_str("media") or sys_info.get("media")
        if not machine or not media:
            raise BatoceraException(
                f"ROM '{rom.name}' (sha1={rom_sha1}) was not found in the MAME "
                "software-list database. "
                "Machine and media must be configured manually "
                "(set 'machine' and 'media' in the system options)."
            )
        _logger.info("MESS: ROM not autodetected — using machine=%s media=%s", machine, media)

    customCfg = system.config.get_bool("customcfg")
    mkdir_if_not_exists(MAME_CONFIG / machine)
    cfgPath = MAME_CONFIG / machine / "custom" if customCfg else MAME_CONFIG / machine

    commandArray = _mame_common_options(system, rom, cfgPath, gameResolution)

    # Computer systems always use mouse
    commandArray += [
        "-dial_device",       "mouse",
        "-trackball_device",  "mouse",
        "-paddle_device",     "mouse",
        "-positional_device", "mouse",
        "-mouse_device",      "mouse",
        "-ui_mouse",
    ]
    if not system.config.use_guns:
        commandArray += ["-lightgun_device", "mouse", "-adstick_device", "mouse"]
    if system.config.use_guns:
        commandArray += ["-lightgunprovider", "udev",
                         "-lightgun_device",  "lightgun",
                         "-adstick_device",   "lightgun"]

    commandArray += [machine]
    for arg in sys_info.get("extra_args", []):
        commandArray.append(arg)
    commandArray += _build_config_args(sys_info.get("config_args", []), system, machine)
    commandArray += _build_rom_ext_args(sys_info.get("rom_ext_args", []), rom)

    commandArray += [f"-{media}", str(rom)]

    if system.config.get_bool("addblankdisk"):
        machine_blank = Path(f"/usr/share/mame/blank.{machine}")
        blankDisk = machine_blank if machine_blank.exists() else Path("/usr/share/mame/blank.default")
        targetFolder = MAME_SAVES / system.name
        targetDisk = targetFolder / f"{rom.stem}.{blankDisk.name.split('.', 1)[-1]}"
        mkdir_if_not_exists(targetFolder)
        if not targetDisk.exists():
            shutil.copy2(blankDisk, targetDisk)
        if machine in ("fmtmarty", "fmtowns"):
            commandArray += ["-flop", targetDisk]
        elif system.config.get_str("altromtype") == "flop2":
            commandArray += ["-flop1", targetDisk]
        else:
            commandArray += ["-flop2", targetDisk]

    lua_script_name = sys_info.get("lua_script")
    if lua_script_name:
        lua_path = MESS_AUTOBOOT_SCRIPTS / lua_script_name
        if lua_path.exists():
            commandArray += ["-autoboot_script", str(lua_path)]
        else:
            _logger.warning("MESS: Lua autoboot script not found: %s", lua_path)

    if (custom_cmd_file := Path(f"{rom}.cmd")).is_file():
        commandArray = custom_cmd_file.read_text().splitlines()

    bezelSet = system.config.get_str("bezel") or None
    if system.config.get_bool("forceNoBezel"):
        bezelSet = None
    try:
        MameGenerator.writeBezelConfig(bezelSet, system, rom, machine, gameResolution,
                                       system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
    except Exception:
        MameGenerator.writeBezelConfig(None, system, rom, machine, gameResolution,
                                       system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))

    mameControllers.generatePadsConfig(
        cfgPath, playersControllers, machine,
        "default", customCfg, "none", bezelSet,
        system.config.use_guns, guns,
        system.config.use_wheels, wheels,
        True, False, system,
    )

    os.chdir("/usr/bin/mame")
    return Command.Command(
        array=commandArray,
        env={
            "PWD": "/usr/bin/mame/",
            "XDG_CONFIG_HOME": CONFIGS,
            "XDG_CACHE_HOME":  SAVES,
        },
    )


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
