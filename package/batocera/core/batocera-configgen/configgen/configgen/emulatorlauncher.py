#!/usr/bin/env python
# ruff: noqa: E402

from __future__ import annotations

from . import profiler

profiler.start()

### import always needed ###
import argparse
import json
import logging
import os
import signal
import subprocess
import time
import threading
import pyudev
import sdl2
import sdl2.ext
import ctypes
from pathlib import Path
from sys import exit
from copy import deepcopy
from typing import TYPE_CHECKING

from . import controllersConfig as controllers
from .batoceraPaths import BATOCERA_SHARE_DIR, SAVES, SYSTEM_SCRIPTS, USER_SCRIPTS
from .controller import Controller
from .Emulator import Emulator
from .exceptions import BadCommandLineArguments, BaseBatoceraException, BatoceraException, UnexpectedEmulatorExit
from .generators import get_generator
from .gun import Gun
from .utils import bezels as bezelsUtil, videoMode, wheelsUtils
from .utils.hotkeygen import set_hotkeygen_context
from .utils.logger import setup_logging
from .utils.squashfs import squashfs_rom
from .utils.evmapy import evmapy

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import FrameType

    from .Command import Command
    from .generators.Generator import Generator
    from .types import Resolution

_logger = logging.getLogger(__name__)

# A lock to safely modify the active controller list from multiple threads
_player_controllers_lock = threading.Lock()
# A global variable to hold the current, up-to-date list of player controllers
_active_player_controllers = []
# Global reference to the evmapy configurator instance
_evmapy_instance = None

def main(args: argparse.Namespace, maxnbplayers: int) -> int:
    # squashfs roms if squashed
    if args.rom.suffix == ".squashfs":
        with squashfs_rom(args.rom) as rom:
            return start_rom(args, maxnbplayers, rom, args.rom)
    else:
        return start_rom(args, maxnbplayers, args.rom, args.rom)

def start_rom(args: argparse.Namespace, maxnbplayers: int, rom: Path, original_rom: Path) -> int:
    global _active_player_controllers, _evmapy_instance

    player_controllers = Controller.load_for_players(maxnbplayers, args)

    # Initialize the global state with the initial controller list
    with _player_controllers_lock:
        _active_player_controllers = list(player_controllers)
    
    # Start the background monitor thread.
    monitor_thread = threading.Thread(target=_controller_monitor_thread, daemon=True)

    # find the system to run
    systemName = args.system
    _logger.debug("Running system: %s", systemName)
    system = Emulator(args, original_rom)

    _logger.debug("Settings: %s", {
        key: '***' if 'password' in key else value for key, value in system.config.items()
    })

    if "emulator" in system.config and "core" in system.config:
        _logger.debug('emulator: %s, core: %s', system.config.emulator, system.config.core)
    else:
        if "emulator" in system.config:
            _logger.debug('emulator: %s', system.config.emulator)

    # metadata
    metadata = controllers.getGamesMetaData(systemName, rom)

    guns = Gun.get_and_precalibrate_all(system, rom)

    with wheelsUtils.configure_wheels(player_controllers, system, metadata) as (player_controllers, wheels):
        # find the generator
        generator = get_generator(system.config.emulator)

        # the resolution must be changed before configuration while the configuration may depend on it (ie bezels)
        wantedGameMode = generator.getResolutionMode(system.config)
        systemMode = videoMode.getCurrentMode()

        resolutionChanged = False
        mouseChanged = False
        exitCode = 0
        try:
            # lower the resolution if mode is auto
            newsystemMode = systemMode  # newsystemMode is the mode after minmax (ie in 1K if tv was in 4K), systemmode is the mode before (ie in es)
            if system.config.video_mode == "" or system.config.video_mode == "default":
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
            if "core" in system.config and system.config.core is not None:
                effectiveCore = system.config.core

            if generator.getMouseMode(system.config, rom):
                mouseChanged = True
                videoMode.changeMouse(True)

            # SDL VSync is a big deal on OGA and RPi4
            if not system.config.get_bool('sdlvsync', True):
                system.config["sdlvsync"] = '0'
            else:
                system.config["sdlvsync"] = '1'
            os.environ.update({'SDL_RENDER_VSYNC': system.config["sdlvsync"]})

            # run a script before emulator starts
            callExternalScripts(SYSTEM_SCRIPTS, "gameStart", [systemName, system.config.emulator, effectiveCore, rom])
            callExternalScripts(USER_SCRIPTS, "gameStart", [systemName, system.config.emulator, effectiveCore, rom])

            # run the emulator
            _evmapy_instance = evmapy(systemName, system.config.emulator, effectiveCore, original_rom, player_controllers, guns)
            with (
                _evmapy_instance,
                set_hotkeygen_context(generator, system)
            ):
                # change directory if wanted
                executionDirectory = generator.executionDirectory(system.config, rom)
                if executionDirectory is not None:
                    os.chdir(executionDirectory)

                cmd = generator.generate(system, rom, player_controllers, metadata, guns, wheels, gameResolution)

                if system.config.get_bool('hud_support'):
                    hud_bezel = getHudBezel(system, generator, rom, gameResolution, system.guns_borders_size_name(guns), system.guns_border_ratio_type(guns))
                    if ((hud := system.config.get('hud')) and hud != "none") or hud_bezel is not None:
                        cmd.env["MANGOHUD_DLSYM"] = "1"
                        hudconfig = getHudConfig(system, args.systemname, system.config.emulator, effectiveCore, rom, hud_bezel)
                        hud_config_file = Path('/var/run/hud.config')
                        with hud_config_file.open('w') as f:
                            f.write(hudconfig)
                        cmd.env["MANGOHUD_CONFIGFILE"] = hud_config_file
                        if not generator.hasInternalMangoHUDCall():
                            cmd.array.insert(0, "mangohud")

                with profiler.pause():
                    monitor_thread.start()
                    exitCode = runCommand(cmd)

            # run a script after emulator shuts down
            callExternalScripts(USER_SCRIPTS, "gameStop", [systemName, system.config.emulator, effectiveCore, rom])
            callExternalScripts(SYSTEM_SCRIPTS, "gameStop", [systemName, system.config.emulator, effectiveCore, rom])

        finally:
            # always restore the resolution
            if resolutionChanged:
                try:
                    videoMode.changeMode(systemMode)
                except Exception:
                    pass  # don't fail

            if mouseChanged:
                try:
                    videoMode.changeMouse(False)
                except Exception:
                    pass  # don't fail

    # exit
    return exitCode

def getHudBezel(system: Emulator, generator: Generator, rom: Path, gameResolution: Resolution, bordersSize: str | None, bordersRatio: str | None):
    if generator.supportsInternalBezels():
        _logger.debug("skipping bezels for emulator %s", system.config.emulator)
        return None
    # no good reason for a bezel
    bezel = system.config.get_str('bezel', 'none')
    bezel_tattoo = system.config.get_str('bezel.tattoo', '0')
    bezel_qrcode = system.config.get_str('bezel.qrcode', '0')

    if (not bezel or bezel == 'none') and (not bezel_tattoo or bezel_tattoo == '0') and (not bezel_qrcode or bezel_qrcode == '0') and bordersSize is None:
        return None

    # no bezel, generate a transparent one for the tatoo/gun borders ... and so on
    if not bezel or bezel == 'none':
        overlay_png_file  = Path("/tmp/bezel_transhud_black.png")
        overlay_info_file = Path("/tmp/bezel_transhud_black.info")
        bezelsUtil.createTransparentBezel(overlay_png_file, gameResolution["width"], gameResolution["height"])

        w = gameResolution["width"]
        h = gameResolution["height"]
        with overlay_info_file.open("w") as fd:
            fd.write(f'{{ "width":{w}, "height":{h}, "opacity":1.0000000, "messagex":0.220000, "messagey":0.120000 }}')
    else:
        _logger.debug("hud enabled. trying to apply the bezel %s", bezel)

        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name, system.config.emulator)
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
        except Exception:
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
    if bordersSize is None and abs(screen_ratio - bezel_ratio) > max_ratio_delta:
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
        if bordersSize is None and abs((infos_left  - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
            _logger.debug("bezel left covers too much the game image : %s / %s > %s", infos_left  - ((bezel_width-img_width)/2.0), img_width, max_cover)
            return None

    if "right" not in infos:
        _logger.debug("bezel has no right info in %s", overlay_info_file)
        # assume default is 4/3 over 16/9
        infos_right = (bezel_width - (bezel_height / 3 * 4)) / 2
        if bordersSize is None and abs((infos_right - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
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
    bezel_stretch = system.config.get_bool('bezel_stretch')
    if (bezel_width != gameResolution["width"] or bezel_height != gameResolution["height"]):
        _logger.debug("bezel needs to be resized")
        output_png_file = Path("/tmp/bezel.png")
        try:
            bezelsUtil.resizeImage(overlay_png_file, output_png_file, gameResolution["width"], gameResolution["height"], bezel_stretch)
        except Exception as e:
            _logger.error("failed to resize the image %s", e)
            return None
        overlay_png_file = output_png_file

    if bezel_tattoo != "0":
        output_png_file = Path("/tmp/bezel_tattooed.png")
        bezelsUtil.tatooImage(overlay_png_file, output_png_file, system)
        overlay_png_file = output_png_file

    if bezel_qrcode != "0" and (cheevos_id := system.es_game_info.get("cheevosId", "0")) != "0":
        output_png_file = Path("/tmp/bezel_qrcode.png")
        bezelsUtil.addQRCode(overlay_png_file, output_png_file, cheevos_id, system)
        overlay_png_file = output_png_file

    # borders
    if bordersSize is not None:
        _logger.debug("Draw gun borders")
        output_png_file = Path("/tmp/bezel_gunborders.png")
        innerSize, outerSize = bezelsUtil.gunBordersSize(bordersSize)
        _logger.debug("Gun border ratio = %s", bordersRatio)
        bezelsUtil.gunBorderImage(overlay_png_file, output_png_file, bordersRatio, innerSize, outerSize, bezelsUtil.gunsBordersColorFomConfig(system.config))
        overlay_png_file = output_png_file

    _logger.debug("applying bezel %s", overlay_png_file)
    return overlay_png_file

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

def getHudConfig(system: Emulator, systemName: str, emulator: str, core: str, rom: Path, bezel: Path | None) -> str:
    configstr = ""

    if bezel != "" and bezel != "none" and bezel is not None:
        configstr = f"background_image={hudConfig_protectStr(bezel)}\nlegacy_layout=false\n"

    if (mode := system.config.get('hud', 'none')) == 'none':
        return configstr + "background_alpha=0\n" # hide the background

    hud_position = "bottom-left"
    if (hud_corner := system.config.get('hud_corner', '')) != '':
        if hud_corner == "NW":
            hud_position = "top-left"
        elif hud_corner == "NE":
            hud_position = "top-right"
        elif hud_corner == "SE":
            hud_position = "bottom-right"

    emulatorstr = emulator
    if emulator != core and core is not None:
        emulatorstr += f"/{core}"

    gameName = system.es_game_info.get("name", "")
    gameThumbnail = system.es_game_info.get("thumbnail", "")

    # predefined values
    if mode == "perf":
        configstr += f"position={hud_position}\nbackground_alpha=0.9\nlegacy_layout=false\ncustom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%\nfps\ngpu_name\nengine_version\nvulkan_driver\nresolution\nram\ngpu_stats\ngpu_temp\ncpu_stats\ncpu_temp\ncore_load"
    elif mode == "game":
        configstr += f"position={hud_position}\nbackground_alpha=0\nlegacy_layout=false\nfont_size=32\nimage_max_width=200\nimage=%THUMBNAIL%\ncustom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%"
    elif mode == "custom" and (hud_custom := system.config.get_str('hud_custom')):
        configstr += hud_custom.replace("\\n", "\n")
    else:
        configstr = configstr + "background_alpha=0\n" # hide the background

    configstr = configstr.replace("%SYSTEMNAME%", hudConfig_protectStr(systemName))
    configstr = configstr.replace("%GAMENAME%", hudConfig_protectStr(gameName))
    configstr = configstr.replace("%EMULATORCORE%", hudConfig_protectStr(emulatorstr))
    return configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))

def _reconfigure_evmapy_on_the_fly():
    # Re-runs the evmapy configuration by creating a NEW evmapy instance with the latest controller list.
    global _evmapy_instance, _active_player_controllers

    with _player_controllers_lock:
        if not _evmapy_instance:
            return

        _logger.info(">>> --- STARTING EVMAPY RECONFIGURATION ---")
        
        valid_controllers = [c for c in _active_player_controllers if c is not None]
        _logger.info(f">>> Found {len(valid_controllers)} valid controllers to configure.")
        for c in valid_controllers:
            _logger.info(f">>>   - Configuring P{c.player_number} with Path: {c.device_path}")

        new_evmapy_instance = evmapy(
            system=_evmapy_instance.system,
            emulator=_evmapy_instance.emulator,
            core=_evmapy_instance.core,
            rom=_evmapy_instance.rom,
            controllers=deepcopy(valid_controllers),
            guns=_evmapy_instance.guns
        )
        
        _evmapy_instance = new_evmapy_instance
        
        subprocess.call(['batocera-evmapy', 'stop'])
        time.sleep(0.5)
        _evmapy_instance._evmapy__prepare()
        subprocess.call(['batocera-evmapy', 'start'])
        
        _logger.info(">>> --- EVMAPY RECONFIGURATION COMPLETE ---")


def _controller_monitor_thread():
    # Runs in the background, watching for controller add/remove events.
    # Uses pysdl2 to reliably get controller GUIDs and paths, then intelligently "revives"
    # the original controller object to preserve player order without disrupting the emulator.
    global _active_player_controllers
    
    initial_controllers_snapshot = []
    with _player_controllers_lock:
        initial_controllers_snapshot = deepcopy(_active_player_controllers)
        for i, p_controller in enumerate(initial_controllers_snapshot):
            if p_controller and p_controller.guid:
                _logger.info(f">>>   [P{i+1}] Stored GUID: {p_controller.guid}, Initial Path: {p_controller.device_path}")

    we_initialized_sdl = False
    try:
        if sdl2.SDL_WasInit(sdl2.SDL_INIT_JOYSTICK) == 0:
            _logger.info(">>> SDL2 joystick subsystem not initialized. Initializing it now.")
            sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
            we_initialized_sdl = True
        else:
            _logger.info(">>> SDL2 joystick subsystem already initialized by host (emulator). Will not re-initialize.")
    except Exception as e:
        _logger.error(f"FATAL: Could not initialize pysdl2 for controller monitoring: {e}")
        return

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')

    _logger.info(">>> Starting background controller monitor.")
    for device in iter(monitor.poll, None):
        if device.get('ID_INPUT_JOYSTICK') != '1':
            continue

        _logger.info(f"--- Joystick Event Detected: {device.action} on {device.sys_path} ---")
        reconfigure_needed = False
        
        sdl2.SDL_JoystickUpdate()
        online_controllers_map = {}
        for i in range(sdl2.SDL_NumJoysticks()):
            try:
                guid_struct = sdl2.SDL_JoystickGetDeviceGUID(i)
                guid_str_buffer = (ctypes.c_char * 33)()
                sdl2.SDL_JoystickGetGUIDString(guid_struct, guid_str_buffer, 33)
                guid = guid_str_buffer.value.decode('utf-8')
                
                path_bytes = sdl2.SDL_JoystickPathForIndex(i)
                path = path_bytes.decode('utf-8') if path_bytes else None
                
                if guid and path:
                    online_controllers_map[guid] = path
            except Exception as e:
                _logger.warning(f"Error while querying joystick index {i} with pysdl2: {e}")
        
        _logger.info(f">>> [Check 1] Pysdl2 scan found online controllers: {online_controllers_map}")
        
        with _player_controllers_lock:
            new_active_controllers = [None] * len(initial_controllers_snapshot)
            
            for i, initial_controller in enumerate(initial_controllers_snapshot):
                if initial_controller and initial_controller.guid in online_controllers_map:
                    new_path = online_controllers_map[initial_controller.guid]
                    if initial_controller.device_path != new_path:
                        _logger.info(f">>> [Revival] Player {initial_controller.player_number} (GUID: {initial_controller.guid}) path has changed.")
                        initial_controller.device_path = new_path
                    new_active_controllers[i] = initial_controller

            current_paths = [c.device_path if c else None for c in _active_player_controllers]
            new_paths = [c.device_path if c else None for c in new_active_controllers]
            
            if current_paths != new_paths:
                _logger.info(f">>> [Check 2] Controller state changed. Old Paths: {current_paths}. New Paths: {new_paths}")
                _active_player_controllers = new_active_controllers
                reconfigure_needed = True
            else:
                _logger.info(">>> [Check 2] No change in assigned controller paths detected.")

        if reconfigure_needed:
            time.sleep(1) 
            _reconfigure_evmapy_on_the_fly()

    if we_initialized_sdl:
        sdl2.SDL_QuitSubSystem(sdl2.SDL_INIT_JOYSTICK)

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
        raise BadCommandLineArguments

    proc = subprocess.Popen(command.array, env=command.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitcode = 0

    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        _logger.debug(out.decode(errors='backslashreplace'))
        _logger.error(err.decode(errors='backslashreplace'))
    except BrokenPipeError:
        # Seeing BrokenPipeError? This is probably caused by head truncating output in the front-end
        # Examine es-core/src/platform.cpp::runSystemCommand for additional context
        pass
    except BaseException as e:
        _logger.error("emulator exited")

        raise UnexpectedEmulatorExit from e

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

        batocera_version = 'UNKNOWN'
        if (version_file := BATOCERA_SHARE_DIR / 'batocera.version').exists():
            batocera_version = version_file.read_text().strip()
        _logger.info('Batocera version: %s', batocera_version)

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
        parser.add_argument("-rom",            help="rom absolute path",           type=Path, required=True)
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
        exitcode = 0
        try:
            exitcode = main(args, maxnbplayers)
        except BaseBatoceraException as e:
            _logger.exception("configgen exception: ")
            exitcode = e.exit_code

            if isinstance(e, BatoceraException):
                Path('/tmp/launch_error.log').write_text(e.args[0])
        except Exception:
            _logger.exception("configgen exception: ")

        profiler.stop()

        time.sleep(1) # this seems to be required so that the gpu memory is restituated and available for es

        if exitcode < 0:
            signal_number = exitcode * -1

            if signal_number < signal.NSIG:
                signal_description = signal.strsignal(signal_number)

                if signal_description and ':' not in signal_description:
                    signal_description = f'{signal_description}: {signal_number}'

                _logger.debug("Emulator terminated by signal (%s)", signal_description)
                exitcode = 0

        _logger.debug("Exiting configgen with status %s", exitcode)

        exit(exitcode)

if __name__ == '__main__':
    launch()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
