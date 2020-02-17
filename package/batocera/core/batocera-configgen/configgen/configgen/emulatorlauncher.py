#!/usr/bin/env python

import argparse
import time
import sys
from sys import exit
from Emulator import Emulator
import generators
from generators.kodi.kodiGenerator import KodiGenerator
from generators.linapple.linappleGenerator import LinappleGenerator
from generators.libretro.libretroGenerator import LibretroGenerator
from generators.moonlight.moonlightGenerator import MoonlightGenerator
from generators.mupen.mupenGenerator import MupenGenerator
from generators.ppsspp.ppssppGenerator import PPSSPPGenerator
from generators.reicast.reicastGenerator import ReicastGenerator
from generators.dolphin.dolphinGenerator import DolphinGenerator
from generators.pcsx2.pcsx2Generator import Pcsx2Generator
from generators.scummvm.scummvmGenerator import ScummVMGenerator
from generators.dosbox.dosboxGenerator import DosBoxGenerator
from generators.vice.viceGenerator import ViceGenerator
from generators.fsuae.fsuaeGenerator import FsuaeGenerator
from generators.amiberry.amiberryGenerator import AmiberryGenerator
from generators.citra.citraGenerator import CitraGenerator
from generators.daphne.daphneGenerator import DaphneGenerator
import controllersConfig as controllers
import signal
import batoceraFiles
import os
import subprocess
import json
import utils.videoMode as videoMode
from utils.logger import eslog

generators = {
    'kodi': KodiGenerator(),
    'linapple': LinappleGenerator(os.path.join(batoceraFiles.HOME_INIT, '.linapple'),
                                  os.path.join(batoceraFiles.HOME, '.linapple')),
    'libretro': LibretroGenerator(),
    'moonlight': MoonlightGenerator(),
    'scummvm': ScummVMGenerator(),
    'dosbox': DosBoxGenerator(),
    'mupen64plus': MupenGenerator(),
    'vice': ViceGenerator(),
    'fsuae': FsuaeGenerator(),
    'amiberry': AmiberryGenerator(),
    'reicast': ReicastGenerator(),
    'dolphin': DolphinGenerator(),
    'pcsx2': Pcsx2Generator(),
    'ppsspp': PPSSPPGenerator(),
    'citra' : CitraGenerator(),
    'daphne' : DaphneGenerator()
}

def main(args):
    playersControllers = dict()
    # Read the controller configuration
    playersControllers = controllers.loadControllerConfig(args.p1index, args.p1guid, args.p1name, args.p1devicepath, args.p1nbbuttons, args.p1nbhats, args.p1nbaxes,
                                                          args.p2index, args.p2guid, args.p2name, args.p2devicepath, args.p2nbbuttons, args.p2nbhats, args.p2nbaxes,
                                                          args.p3index, args.p3guid, args.p3name, args.p3devicepath, args.p3nbbuttons, args.p3nbhats, args.p3nbaxes,
                                                          args.p4index, args.p4guid, args.p4name, args.p4devicepath, args.p4nbbuttons, args.p4nbhats, args.p4nbaxes,
                                                          args.p5index, args.p5guid, args.p5name, args.p5devicepath, args.p5nbbuttons, args.p5nbhats, args.p5nbaxes)
    # find the system to run
    systemName = args.system
    eslog.log("Running system: {}".format(systemName))
    system = Emulator(systemName, args.rom)

    if args.emulator is not None:
        system.config["emulator"] = args.emulator
    if args.core is not None:
        system.config["core"] = args.core

    eslog.debug("Settings: {}".format(system.config))
    if "emulator" in system.config and "core" in system.config:
        eslog.log("emulator: {}, core: {}".format(system.config["emulator"], system.config["core"]))
    else:
        if "emulator" in system.config:
            eslog.log("emulator: {}".format(system.config["emulator"]))

    # the resolution must be changed before configuration while the configuration may depend on it (ie bezels)
    wantedGameMode = generators[system.config['emulator']].getResolutionMode(system.config)
    systemMode = videoMode.getCurrentMode()
    resolutionChanged = False
    exitCode = -1
    try:
        eslog.log("current video mode: {}".format(systemMode))
        eslog.log("wanted video mode: {}".format(wantedGameMode))
        if wantedGameMode != 'default' and wantedGameMode != systemMode:
            videoMode.changeMode(wantedGameMode)
            resolutionChanged = True
        gameResolution = videoMode.getCurrentResolution()
        eslog.log("resolution: {}x{}".format(str(gameResolution["width"]), str(gameResolution["height"])))

        # savedir: create the save directory if not already done
        dirname = os.path.join(batoceraFiles.savesDir, system.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # core
        effectiveCore = ""
        if "core" in system.config and system.config["core"] is not None:
            effectiveCore = system.config["core"]
        effectiveRom = ""
        if args.rom is not None:
            effectiveRom = args.rom

        # network options
        if args.netplaymode is not None:
            system.config["netplay.mode"] = args.netplaymode
        if args.netplayip is not None:
            system.config["netplay.server.ip"] = args.netplayip
        if args.netplayport is not None:
            system.config["netplay.server.port"] = args.netplayport

        # run a script before emulator starts
        callExternalScripts("/usr/share/batocera/configgen/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts("/userdata/system/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

        # run the emulator
        exitCode = runCommand(generators[system.config['emulator']].generate(system, args.rom, playersControllers, gameResolution))

        # run a script after emulator shuts down
        callExternalScripts("/userdata/system/scripts", "gameStop", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts("/usr/share/batocera/configgen/scripts", "gameStop", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
   
    finally:
        # always restore the resolution
        if resolutionChanged:
            try:
                videoMode.changeMode(systemMode)
            except Exception:
                pass # don't fail
    # exit
    return exitCode

def callExternalScripts(folder, event, args):
    if not os.path.isdir(folder):
        return

    for file in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, file)):
            callExternalScripts(os.path.join(folder, file), event, args)
        else:
            if os.access(os.path.join(folder, file), os.X_OK):
                eslog.log("calling external script: " + str([os.path.join(folder, file), event] + args))
                subprocess.call([os.path.join(folder, file), event] + args)

def runCommand(command):
    global proc

    command.env.update(os.environ)
    eslog.log("command: {}".format(str(command)))
    eslog.log("command: {}".format(str(command.array)))
    eslog.log("env: {}".format(str(command.env)))
    proc = subprocess.Popen(command.array, env=command.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exitcode = -1
    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        sys.stdout.write(out)
        sys.stderr.write(err)
    except:
        eslog("emulator exited")

    return exitcode

def signal_handler(signal, frame):
    global proc
    print('Exiting')
    if proc:
        print('killing proc')
        proc.kill()

if __name__ == '__main__':
    proc = None
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description='emulator-launcher script')
    parser.add_argument("-p1index", help="player1 controller index", type=int, required=False)
    parser.add_argument("-p1guid", help="player1 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p1name", help="player1 controller name", type=str, required=False)
    parser.add_argument("-p1devicepath", help="player1 controller device", type=str, required=False)
    parser.add_argument("-p1nbbuttons", help="player1 controller number of buttons", type=str, required=False)
    parser.add_argument("-p1nbhats", help="player1 controller number of hats", type=str, required=False)
    parser.add_argument("-p1nbaxes", help="player1 controller number of axes", type=str, required=False)
    parser.add_argument("-p2index", help="player2 controller index", type=int, required=False)
    parser.add_argument("-p2guid", help="player2 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p2name", help="player2 controller name", type=str, required=False)
    parser.add_argument("-p2devicepath", help="player2 controller device", type=str, required=False)
    parser.add_argument("-p2nbbuttons", help="player2 controller number of buttons", type=str, required=False)
    parser.add_argument("-p2nbhats", help="player2 controller number of hats", type=str, required=False)
    parser.add_argument("-p2nbaxes", help="player2 controller number of axes", type=str, required=False)
    parser.add_argument("-p3index", help="player3 controller index", type=int, required=False)
    parser.add_argument("-p3guid", help="player3 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p3name", help="player3 controller name", type=str, required=False)
    parser.add_argument("-p3devicepath", help="player3 controller device", type=str, required=False)
    parser.add_argument("-p3nbbuttons", help="player3 controller number of buttons", type=str, required=False)
    parser.add_argument("-p3nbhats", help="player3 controller number of hats", type=str, required=False)
    parser.add_argument("-p3nbaxes", help="player3 controller number of axes", type=str, required=False)
    parser.add_argument("-p4index", help="player4 controller index", type=int, required=False)
    parser.add_argument("-p4guid", help="player4 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p4name", help="player4 controller name", type=str, required=False)
    parser.add_argument("-p4devicepath", help="player4 controller device", type=str, required=False)
    parser.add_argument("-p4nbbuttons", help="player4 controller number of buttons", type=str, required=False)
    parser.add_argument("-p4nbhats", help="player4 controller number of hats", type=str, required=False)
    parser.add_argument("-p4nbaxes", help="player4 controller number of axes", type=str, required=False)
    parser.add_argument("-p5index", help="player5 controller index", type=int, required=False)
    parser.add_argument("-p5guid", help="player5 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p5name", help="player5 controller name", type=str, required=False)
    parser.add_argument("-p5devicepath", help="player5 controller device", type=str, required=False)
    parser.add_argument("-p5nbbuttons", help="player5 controller number of buttons", type=str, required=False)
    parser.add_argument("-p5nbhats", help="player5 controller number of hats", type=str, required=False)
    parser.add_argument("-p5nbaxes", help="player5 controller number of axes", type=str, required=False)
    parser.add_argument("-system", help="select the system to launch", type=str, required=True)
    parser.add_argument("-rom", help="rom absolute path", type=str, required=True)
    parser.add_argument("-emulator", help="force emulator", type=str, required=False)
    parser.add_argument("-core", help="force emulator core", type=str, required=False)
    parser.add_argument("-netplaymode", help="host/client", type=str, required=False)
    parser.add_argument("-netplayip", help="remote ip", type=str, required=False)
    parser.add_argument("-netplayport", help="remote port", type=str, required=False)

    args = parser.parse_args()
    try:
        exitcode = -1
        exitcode = main(args)
    except Exception as e:
        eslog.error("configgen exception: ", exc_info=True)
    time.sleep(1) # this seems to be required so that the gpu memory is restituated and available for es
    eslog.log("Exiting configgen with status {}".format(str(exitcode)))
    exit(exitcode)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
