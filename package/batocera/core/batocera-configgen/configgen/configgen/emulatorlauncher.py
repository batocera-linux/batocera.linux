#!/usr/bin/env python
# ruff: noqa: E402

from __future__ import annotations

import os

_profiler = None

# 1) touch /var/run/emulatorlauncher.perf
# 2) start a game
# 3) gprof2dot.py -f pstats -n 5 /var/run/emulatorlauncher.prof -o emulatorlauncher.dot # wget https://raw.githubusercontent.com/jrfonseca/gprof2dot/master/gprof2dot.py
# 4) dot -Tpng emulatorlauncher.dot -o emulatorlauncher.png
# 3) or upload the file /var/run/emulatorlauncher.prof on https://nejc.saje.info/pstats-viewer.html

if os.path.exists("/var/run/emulatorlauncher.perf"):  # noqa: PTH110
    import cProfile
    _profiler = cProfile.Profile()
    _profiler.enable()

### import always needed ###
import argparse
import json
import logging
import signal
import subprocess
import time
from pathlib import Path
from sys import exit
from typing import TYPE_CHECKING

from . import controllersConfig as controllers
from .batoceraPaths import SAVES, SYSTEM_SCRIPTS, USER_SCRIPTS
from .controller import Controller
from .Emulator import Emulator
from .generators import get_generator
from .gun import Gun
from .utils import bezels as bezelsUtil, videoMode, wheelsUtils
from .utils.hotkeygen import set_hotkeygen_context
from .utils.logger import setup_logging
from .utils.squashfs import squashfs_rom

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from types import FrameType

    from .Command import Command
    from .generators.Generator import Generator
    from .types import DeviceInfoDict, Resolution

_logger = logging.getLogger(__name__)

def main(args: argparse.Namespace, maxnbplayers: int) -> int:
    # squashfs roms if squashed
    if Path(args.rom).suffix == ".squashfs":
        with squashfs_rom(args.rom) as rom:
            return start_rom(args, maxnbplayers, rom, args.rom)
    else:
        return start_rom(args, maxnbplayers, args.rom, args.rom)

def start_rom(args: argparse.Namespace, maxnbplayers: int, rom: str, romConfiguration: str) -> int:
    player_controllers = Controller.load_for_players(maxnbplayers, args)

    # find the system to run
    systemName = args.system
    _logger.debug("Running system: %s", systemName)
    system = Emulator(systemName, romConfiguration)

    if args.emulator is not None:
        system.config["emulator"] = args.emulator
        system.config["emulator-forced"] = True
    if args.core is not None:
        system.config["core"] = args.core
        system.config["core-forced"] = True
    debugDisplay = system.config.copy()
    if "retroachievements.password" in debugDisplay:
        debugDisplay["retroachievements.password"] = "***"
    _logger.debug("Settings: %s", debugDisplay)
    if "emulator" in system.config and "core" in system.config:
        _logger.debug('emulator: %s, core: %s', system.config["emulator"], system.config["core"])
    else:
        if "emulator" in system.config:
            _logger.debug('emulator: %s', system.config["emulator"])

    # metadata
    metadata = controllers.getGamesMetaData(systemName, rom)

    # search guns in case use_guns is enabled for this game
    # force use_guns in case es tells it has a gun
    if not system.isOptSet('use_guns') and args.lightgun:
        system.config["use_guns"] = True

    guns = Gun.get_and_precalibrate_all(system, rom)

    # search wheels in case use_wheels is enabled for this game
    # force use_wheels in case es tells it has a wheel
    wheelProcesses = None
    if not system.isOptSet('use_wheels') and args.wheel:
        system.config["use_wheels"] = True
    if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels'):
        deviceInfos = controllers.getDevicesInformation()
        (wheelProcesses, player_controllers, deviceInfos) = wheelsUtils.reconfigureControllers(player_controllers, system, rom, metadata, deviceInfos)
        wheels = wheelsUtils.getWheelsFromDevicesInfos(deviceInfos)
    else:
        _logger.info("wheels disabled.")
        wheels: DeviceInfoDict = {}

    # find the generator
    generator = get_generator(system.config['emulator'])

    # the resolution must be changed before configuration while the configuration may depend on it (ie bezels)
    wantedGameMode = generator.getResolutionMode(system.config)
    systemMode = videoMode.getCurrentMode()

    resolutionChanged = False
    mouseChanged = False
    exitCode = -1
    try:
        # lower the resolution if mode is auto
        newsystemMode = systemMode # newsystemmode is the mode after minmax (ie in 1K if tv was in 4K), systemmode is the mode before (ie in es)
        if system.config["videomode"] == "" or system.config["videomode"] == "default":
            _logger.debug("minTomaxResolution")
            _logger.debug("video mode before minmax: %s", systemMode)
            videoMode.minTomaxResolution()
            newsystemMode = videoMode.getCurrentMode()
            if newsystemMode != systemMode:
                resolutionChanged = True

        _logger.debug("current video mode: %s", newsystemMode)
        _logger.debug("wanted video mode: %s", wantedGameMode)

        if wantedGameMode != 'default' and wantedGameMode != newsystemMode:
            videoMode.changeMode(wantedGameMode)
            resolutionChanged = True
        gameResolution = videoMode.getCurrentResolution()

        # if resolution is reversed (ie ogoa boards), reverse it in the gameResolution to have it correct
        if videoMode.isResolutionReversed():
            x = gameResolution["width"]
            gameResolution["width"]  = gameResolution["height"]
            gameResolution["height"] = x
        _logger.debug('resolution: %sx%s', gameResolution["width"], gameResolution["height"])

        # savedir: create the save directory if not already done
        dirname = SAVES / system.name
        if not dirname.exists():
            dirname.mkdir(parents=True)

        # core
        effectiveCore = ""
        if "core" in system.config and system.config["core"] is not None:
            effectiveCore = system.config["core"]
        effectiveRom = ""
        effectiveRomConfiguration = ""
        if rom is not None:
            effectiveRom = rom
            effectiveRomConfiguration = romConfiguration

        # network options
        if args.netplaymode is not None:
            system.config["netplay.mode"] = args.netplaymode
        if args.netplaypass is not None:
            system.config["netplay.password"] = args.netplaypass
        if args.netplayip is not None:
            system.config["netplay.server.ip"] = args.netplayip
        if args.netplayport is not None:
            system.config["netplay.server.port"] = args.netplayport
        if args.netplaysession is not None:
            system.config["netplay.server.session"] = args.netplaysession

        # autosave arguments
        if args.state_slot is not None:
            system.config["state_slot"] = args.state_slot
        if args.autosave is not None:
            system.config["autosave"] = args.autosave
        if args.state_filename is not None:
            system.config["state_filename"] = args.state_filename

        if generator.getMouseMode(system.config, rom):
            mouseChanged = True
            videoMode.changeMouse(True)

        # SDL VSync is a big deal on OGA and RPi4
        if system.isOptSet('sdlvsync') and not system.getOptBoolean('sdlvsync'):
            system.config["sdlvsync"] = '0'
        else:
            system.config["sdlvsync"] = '1'
        os.environ.update({'SDL_RENDER_VSYNC': system.config["sdlvsync"]})

        # run a script before emulator starts
        callExternalScripts(SYSTEM_SCRIPTS, "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts(USER_SCRIPTS, "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

        # run the emulator
        from .utils.evmapy import evmapy
        with (
            evmapy(systemName, system.config['emulator'], effectiveCore, effectiveRomConfiguration, player_controllers, guns),
            set_hotkeygen_context(generator, system)
        ):
            # change directory if wanted
            executionDirectory = generator.executionDirectory(system.config, effectiveRom)
            if executionDirectory is not None:
                os.chdir(executionDirectory)

            cmd = generator.generate(system, rom, player_controllers, metadata, guns, wheels, gameResolution)

            if system.isOptSet('hud_support') and system.getOptBoolean('hud_support'):
                hud_bezel = getHudBezel(system, generator, rom, gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
                if (system.isOptSet('hud') and system.config['hud'] != "" and system.config['hud'] != "none") or hud_bezel is not None:
                    gameinfos = extractGameInfosFromXml(args.gameinfoxml)
                    cmd.env["MANGOHUD_DLSYM"] = "1"
                    hudconfig = getHudConfig(system, args.systemname, system.config['emulator'], effectiveCore, rom, gameinfos, hud_bezel)
                    hud_config_file = Path('/var/run/hud.config')
                    with hud_config_file.open('w') as f:
                        f.write(hudconfig)
                    cmd.env["MANGOHUD_CONFIGFILE"] = hud_config_file
                    if not generator.hasInternalMangoHUDCall():
                        cmd.array.insert(0, "mangohud")

            if _profiler:
                _profiler.disable()
            exitCode = runCommand(cmd)
            if _profiler:
                _profiler.enable()

        # run a script after emulator shuts down
        callExternalScripts(USER_SCRIPTS, "gameStop", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts(SYSTEM_SCRIPTS, "gameStop", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

    finally:
        # always restore the resolution
        if resolutionChanged:
            try:
                videoMode.changeMode(systemMode)
            except Exception:
                pass # don't fail

        if mouseChanged:
            try:
                videoMode.changeMouse(False)
            except Exception:
                pass # don't fail

        if wheelProcesses is not None and len(wheelProcesses) > 0:
            try:
                wheelsUtils.resetControllers(wheelProcesses)
            except Exception:
                _logger.error("hum, unable to reset wheel controllers !")
                pass # don't fail
    # exit
    return exitCode

def getHudBezel(system: Emulator, generator: Generator, rom: str, gameResolution: Resolution, bordersSize: str | None, bordersRatio: str | None):
    if generator.supportsInternalBezels():
        _logger.debug("skipping bezels for emulator %s", system.config['emulator'])
        return None
    # no good reason for a bezel
    if ('bezel' not in system.config or system.config['bezel'] == "" or system.config['bezel'] == "none") and not (system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0") and bordersSize is None:
        return None
    # no bezel, generate a transparent one for the tatoo/gun borders ... and so on
    if ('bezel' not in system.config or system.config['bezel'] == "" or system.config['bezel'] == "none"):
        overlay_png_file  = Path("/tmp/bezel_transhud_black.png")
        overlay_info_file = Path("/tmp/bezel_transhud_black.info")
        bezelsUtil.createTransparentBezel(overlay_png_file, gameResolution["width"], gameResolution["height"])

        w = gameResolution["width"]
        h = gameResolution["height"]
        with overlay_info_file.open("w") as fd:
            fd.write(f'{{ "width":{w}, "height":{h}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000 }}')
    else:
        _logger.debug("hud enabled. trying to apply the bezel %s", system.config['bezel'])

        bezel = system.config['bezel']
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name, system.config['emulator'])
        if bz_infos is None:
            _logger.debug("no bezel info file found")
            return None

        overlay_info_file = bz_infos["info"]
        overlay_png_file  = bz_infos["png"]

    # check the info file
    # bottom, top, left and right must not cover too much the image to be considered as compatible
    if overlay_info_file.exists():
        try:
            with overlay_info_file.open() as f:
                infos = json.load(f)
        except:
            _logger.warning("unable to read %s", overlay_info_file)
            infos = {}
    else:
        infos = {}

    if "width" in infos and "height" in infos:
        bezel_width  = infos["width"]
        bezel_height = infos["height"]
        _logger.info("bezel size read from %s", overlay_info_file)
    else:
        bezel_width, bezel_height = bezelsUtil.fast_image_size(overlay_png_file)
        _logger.info("bezel size read from %s", overlay_png_file)

    # max cover proportion and ratio distortion
    max_cover = 0.05 # 5%
    max_ratio_delta = 0.01

    screen_ratio = gameResolution["width"] / gameResolution["height"]
    bezel_ratio  = bezel_width / bezel_height

    # the screen and bezel ratio must be approximatly the same
    if bordersSize is None:
        if abs(screen_ratio - bezel_ratio) > max_ratio_delta:
            _logger.debug(
                "screen ratio (%(screen_ratio)s) is too far from the bezel one (%(bezel_ratio)s) : %(screen_ratio)s - %(bezel_ratio)s > %(max_ratio_delta)s",
                {
                    'screen_ratio': screen_ratio,
                    'bezel_ratio': bezel_ratio,
                    'max_ratio_delta': max_ratio_delta
                }
            )
            return None

    # the ingame image and the bezel free space must feet
    ## the bezel top and bottom cover must be minimum
    # in case there is a border, force it
    if bordersSize is None:
        if "top" in infos and infos["top"] / bezel_height > max_cover:
            _logger.debug('bezel top covers too much the game image : %s / %s > %s', infos["top"], bezel_height, max_cover)
            return None
        if "bottom" in infos and infos["bottom"] / bezel_height > max_cover:
            _logger.debug('bezel bottom covers too much the game image : %s / %s > %s', infos["bottom"], bezel_height, max_cover)
            return None

    # if there is no information about top/bottom, assume default is 0

    ## the bezel left and right cover must be maximum
    ingame_ratio = generator.getInGameRatio(system.config, gameResolution, rom)
    img_height = bezel_height
    img_width  = img_height * ingame_ratio

    if "left" not in infos:
        _logger.debug("bezel has no left info in %s", overlay_info_file)
        # assume default is 4/3 over 16/9
        infos_left = (bezel_width - (bezel_height / 3 * 4)) / 2
        if bordersSize is None:
            if abs((infos_left  - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
                _logger.debug("bezel left covers too much the game image : %s / %s > %s", infos_left  - ((bezel_width-img_width)/2.0), img_width, max_cover)
                return None

    if "right" not in infos:
        _logger.debug("bezel has no right info in %s", overlay_info_file)
        # assume default is 4/3 over 16/9
        infos_right = (bezel_width - (bezel_height / 3 * 4)) / 2
        if bordersSize is None:
            if abs((infos_right - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
                _logger.debug("bezel right covers too much the game image : %s / %s > %s", infos_right  - ((bezel_width-img_width)/2.0), img_width, max_cover)
                return None

    if bordersSize is None:
        if "left"  in infos and abs((infos["left"]  - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
            _logger.debug("bezel left covers too much the game image : %s / %s > %s", infos["left"]  - ((bezel_width-img_width)/2.0), img_width, max_cover)
            return None
        if "right" in infos and abs((infos["right"] - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
            _logger.debug("bezel right covers too much the game image : %s / %s > %s", infos["right"]  - ((bezel_width-img_width)/2.0), img_width, max_cover)
            return None

    # if screen and bezel sizes doesn't match, resize
    # stretch option
    if system.isOptSet('bezel_stretch') and system.getOptBoolean('bezel_stretch'):
        bezel_stretch = True
    else:
        bezel_stretch = False
    if (bezel_width != gameResolution["width"] or bezel_height != gameResolution["height"]):
        _logger.debug("bezel needs to be resized")
        output_png_file = Path("/tmp/bezel.png")
        try:
            bezelsUtil.resizeImage(overlay_png_file, output_png_file, gameResolution["width"], gameResolution["height"], bezel_stretch)
        except Exception as e:
            _logger.error("failed to resize the image %s", e)
            return None
        overlay_png_file = output_png_file

    if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
        output_png_file = Path("/tmp/bezel_tattooed.png")
        bezelsUtil.tatooImage(overlay_png_file, output_png_file, system)
        overlay_png_file = output_png_file

    # borders
    if bordersSize is not None:
        _logger.debug("Draw gun borders")
        output_png_file = Path("/tmp/bezel_gunborders.png")
        innerSize, outerSize = bezelsUtil.gunBordersSize(bordersSize)
        _logger.debug("Gun border ratio = %s", bordersRatio)
        borderSize = bezelsUtil.gunBorderImage(overlay_png_file, output_png_file, bordersRatio, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
        overlay_png_file = output_png_file

    _logger.debug("applying bezel %s", overlay_png_file)
    return overlay_png_file

def extractGameInfosFromXml(xml: str) -> dict[str, str]:
    import xml.etree.ElementTree as ET

    vals: dict[str, str] = {}

    try:
        infos = ET.parse(xml)
        try:
            vals["name"] = infos.find("./game/name").text
        except:
            pass
        try:
            vals["thumbnail"] = infos.find("./game/thumbnail").text
        except:
            pass
    except:
        pass
    return vals

def callExternalScripts(folder: Path, event: str, args: Iterable[str | Path]) -> None:
    if not folder.is_dir():
        return

    for file in folder.iterdir():
        if file.is_dir():
            callExternalScripts(file, event, args)
        else:
            if os.access(file, os.X_OK):
                _logger.debug("calling external script: %s", [file, event, *args])
                subprocess.call([file, event, *args])

def hudConfig_protectStr(string: str | Path | None) -> str:
    if string is None:
        return ""
    return str(string)

def getHudConfig(system: Emulator, systemName: str, emulator: str, core: str, rom: str, gameinfos: Mapping[str, str], bezel: Path | None) -> str:
    configstr = ""

    if bezel != "" and bezel != "none" and bezel is not None:
        configstr = f"background_image={hudConfig_protectStr(bezel)}\nlegacy_layout=false\n"

    if not system.isOptSet('hud') or system.config['hud'] == "none":
        return configstr + "background_alpha=0\n" # hide the background

    mode = system.config["hud"]
    hud_position = "bottom-left"
    if system.isOptSet('hud_corner') and system.config["hud_corner"] != "" :
        if system.config["hud_corner"] == "NW":
            hud_position = "top-left"
        elif system.config["hud_corner"] == "NE":
            hud_position = "top-right"
        elif system.config["hud_corner"] == "SE":
            hud_position = "bottom-right"

    emulatorstr = emulator
    if emulator != core and core is not None:
        emulatorstr += f"/{core}"

    gameName = ""
    if "name" in gameinfos:
        gameName = gameinfos["name"]
    gameThumbnail = ""
    if "thumbnail" in gameinfos:
        gameThumbnail = gameinfos["thumbnail"]

    # predefined values
    if mode == "perf":
        configstr += f"position={hud_position}\nbackground_alpha=0.9\nlegacy_layout=false\ncustom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%\nfps\ngpu_name\nengine_version\nvulkan_driver\nresolution\nram\ngpu_stats\ngpu_temp\ncpu_stats\ncpu_temp\ncore_load"
    elif mode == "game":
        configstr += f"position={hud_position}\nbackground_alpha=0\nlegacy_layout=false\nfont_size=32\nimage_max_width=200\nimage=%THUMBNAIL%\ncustom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%"
    elif mode == "custom" and system.isOptSet('hud_custom') and system.config["hud_custom"] != "" :
        configstr += system.config["hud_custom"].replace("\\n", "\n")
    else:
        configstr = configstr + "background_alpha=0\n" # hide the background

    configstr = configstr.replace("%SYSTEMNAME%", hudConfig_protectStr(systemName))
    configstr = configstr.replace("%GAMENAME%", hudConfig_protectStr(gameName))
    configstr = configstr.replace("%EMULATORCORE%", hudConfig_protectStr(emulatorstr))
    configstr = configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))

    return configstr

def runCommand(command: Command) -> int:
    global proc

    # compute environment : first the current envs, then override by values set at generator level
    envvars: dict[str, str | Path] = dict(os.environ)
    envvars.update(command.env)
    command.env = envvars

    _logger.debug("command: %s", command)
    _logger.debug("command: %s", command.array)
    _logger.debug("env: %s", command.env)

    if not command.array:
        return -1

    proc = subprocess.Popen(command.array, env=command.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitcode = -1

    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        _logger.debug(out.decode())
        _logger.error(err.decode())
    except BrokenPipeError:
        # Seeing BrokenPipeError? This is probably caused by head truncating output in the front-end
        # Examine es-core/src/platform.cpp::runSystemCommand for additional context
        pass
    except:
        _logger.error("emulator exited")

    return exitcode

def signal_handler(signal: int, frame: FrameType | None):
    global proc
    _logger.debug('Exiting')
    if proc:
        _logger.debug('killing proc')
        proc.kill()

def launch() -> None:
    with setup_logging():
        global proc
        proc = None
        signal.signal(signal.SIGINT, signal_handler)
        parser = argparse.ArgumentParser(description='emulator-launcher script')

        maxnbplayers = 8
        for p in range(1, maxnbplayers+1):
            parser.add_argument(f"-p{p}index"     , help=f"player{p} controller index"            , type=int, required=False)
            parser.add_argument(f"-p{p}guid"      , help=f"player{p} controller SDL2 guid"        , type=str, required=False)
            parser.add_argument(f"-p{p}name"      , help=f"player{p} controller name"             , type=str, required=False)
            parser.add_argument(f"-p{p}devicepath", help=f"player{p} controller device"           , type=str, required=False)
            parser.add_argument(f"-p{p}nbbuttons" , help=f"player{p} controller number of buttons", type=int, required=False)
            parser.add_argument(f"-p{p}nbhats"    , help=f"player{p} controller number of hats"   , type=int, required=False)
            parser.add_argument(f"-p{p}nbaxes"    , help=f"player{p} controller number of axes"   , type=int, required=False)

        parser.add_argument("-system",         help="select the system to launch", type=str, required=True)
        parser.add_argument("-rom",            help="rom absolute path",           type=str, required=True)
        parser.add_argument("-emulator",       help="force emulator",              type=str, required=False)
        parser.add_argument("-core",           help="force emulator core",         type=str, required=False)
        parser.add_argument("-netplaymode",    help="host/client",                 type=str, required=False)
        parser.add_argument("-netplaypass",    help="enable spectator mode",       type=str, required=False)
        parser.add_argument("-netplayip",      help="remote ip",                   type=str, required=False)
        parser.add_argument("-netplayport",    help="remote port",                 type=str, required=False)
        parser.add_argument("-netplaysession", help="netplay session",             type=str, required=False)
        parser.add_argument("-state_slot",     help="state slot",                  type=str, required=False)
        parser.add_argument("-state_filename", help="state filename",              type=str, required=False)
        parser.add_argument("-autosave",       help="autosave",                    type=str, required=False)
        parser.add_argument("-systemname",     help="system fancy name",           type=str, required=False)
        parser.add_argument("-gameinfoxml",    help="game info xml",               type=str, nargs='?', default='/dev/null', required=False)
        parser.add_argument("-lightgun",       help="configure lightguns",         action="store_true")
        parser.add_argument("-wheel",          help="configure wheel",             action="store_true")
        parser.add_argument("-trackball",      help="configure trackball",         action="store_true")
        parser.add_argument("-spinner",        help="configure spinner",           action="store_true")

        args = parser.parse_args()
        try:
            exitcode = -1
            exitcode = main(args, maxnbplayers)
        except Exception as e:
            _logger.exception("configgen exception: ")

        if _profiler:
            _profiler.disable()
            _profiler.dump_stats('/var/run/emulatorlauncher.prof')

        time.sleep(1) # this seems to be required so that the gpu memory is restituated and available for es
        _logger.debug("Exiting configgen with status %s", exitcode)

        exit(exitcode)

if __name__ == '__main__':
    launch()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
