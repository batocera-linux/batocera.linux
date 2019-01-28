#!/usr/bin/env python

import argparse
import time
import sys
import yaml
import collections
from sys import exit
from Emulator import Emulator
import generators
from generators.fba2x.fba2xGenerator import Fba2xGenerator
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
from generators.advancemame.advMameGenerator import AdvMameGenerator
from generators.citra.citraGenerator import CitraGenerator
import controllersConfig as controllers
import signal
import recalboxFiles
import os
import subprocess
import json
import utils.videoMode as videoMode
import utils.eslog as eslog

generators = {
    'fba2x': Fba2xGenerator(),
    'kodi': KodiGenerator(),
    'linapple': LinappleGenerator(os.path.join(recalboxFiles.HOME_INIT, '.linapple'),
                                  os.path.join(recalboxFiles.HOME, '.linapple')),
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
    'advancemame' : AdvMameGenerator(),
    'citra' : CitraGenerator()
}

def main(args):
    playersControllers = dict()
    # Read the controller configuration
    playersControllers = controllers.loadControllerConfig(args.p1index, args.p1guid, args.p1name, args.p1devicepath, args.p1nbaxes,
                                                          args.p2index, args.p2guid, args.p2name, args.p2devicepath, args.p2nbaxes,
                                                          args.p3index, args.p3guid, args.p3name, args.p3devicepath, args.p3nbaxes,
                                                          args.p4index, args.p4guid, args.p4name, args.p4devicepath, args.p4nbaxes,
                                                          args.p5index, args.p5guid, args.p5name, args.p5devicepath, args.p5nbaxes)
    # find the system to run
    systemName = args.system
    eslog.log("Running system: {}".format(systemName))
    system = getDefaultEmulator(systemName)
    system.configure(args.emulator, args.core, args.ratio, args.netplay)
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
        dirname = os.path.join(recalboxFiles.savesDir, system.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # run the emulator
        exitCode = runCommand(generators[system.config['emulator']].generate(system, args.rom, playersControllers, gameResolution))
    finally:
        # always restore the resolution
        if resolutionChanged:
            try:
                videoMode.changeMode(systemMode)
            except Exception:
                pass # don't fail
    # exit
    return exitCode

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

# to be updated for python3: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
def dict_merge(dct, merge_dct):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :return: None
    """
    for k, v in merge_dct.iteritems():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]

def get_system_config(system):
    systems_default      = yaml.load(file("/recalbox/system/configgen/configgen-defaults.yml", "r"))
    systems_default_arch = yaml.load(file("/recalbox/system/configgen/configgen-defaults-arch.yml", "r"))
    dict_all = {}

    if "default" in systems_default:
        dict_all = systems_default["default"]

    if "default" in systems_default_arch:
        dict_merge(dict_all, systems_default_arch["default"])

    if system in systems_default:
        dict_merge(dict_all, systems_default[system])

    if system in systems_default_arch:
        dict_merge(dict_all, systems_default_arch[system])

    # options are in the yaml, not in the system structure
    # it is flat in the recalbox.conf which is easier for the end user, but i prefer not flat in the yml files
    dict_result = {"emulator": dict_all["emulator"], "core": dict_all["core"]}
    if "options" in dict_all:
      dict_merge(dict_result, dict_all["options"])
    return dict_result

# List emulators with their default emulator/cores
def getDefaultEmulator(systemName):
    system = get_system_config(systemName)
    if "emulator" not in system or system["emulator"] == "":
        eslog.log("no emulator defined. exiting.")
        raise Exception("No emulator found")

    return Emulator(name=systemName, config=system)

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
    parser.add_argument("-p1nbaxes", help="player1 controller number of axes", type=str, required=False)
    parser.add_argument("-p2index", help="player2 controller index", type=int, required=False)
    parser.add_argument("-p2guid", help="player2 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p2name", help="player2 controller name", type=str, required=False)
    parser.add_argument("-p2devicepath", help="player2 controller device", type=str, required=False)
    parser.add_argument("-p2nbaxes", help="player2 controller number of axes", type=str, required=False)
    parser.add_argument("-p3index", help="player3 controller index", type=int, required=False)
    parser.add_argument("-p3guid", help="player3 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p3name", help="player3 controller name", type=str, required=False)
    parser.add_argument("-p3devicepath", help="player3 controller device", type=str, required=False)
    parser.add_argument("-p3nbaxes", help="player3 controller number of axes", type=str, required=False)
    parser.add_argument("-p4index", help="player4 controller index", type=int, required=False)
    parser.add_argument("-p4guid", help="player4 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p4name", help="player4 controller name", type=str, required=False)
    parser.add_argument("-p4devicepath", help="player4 controller device", type=str, required=False)
    parser.add_argument("-p4nbaxes", help="player4 controller number of axes", type=str, required=False)
    parser.add_argument("-p5index", help="player5 controller index", type=int, required=False)
    parser.add_argument("-p5guid", help="player5 controller SDL2 guid", type=str, required=False)
    parser.add_argument("-p5name", help="player5 controller name", type=str, required=False)
    parser.add_argument("-p5devicepath", help="player5 controller device", type=str, required=False)
    parser.add_argument("-p5nbaxes", help="player5 controller number of axes", type=str, required=False)
    parser.add_argument("-system", help="select the system to launch", type=str, required=True)
    parser.add_argument("-rom", help="rom absolute path", type=str, required=True)
    parser.add_argument("-emulator", help="force emulator", type=str, required=False)
    parser.add_argument("-core", help="force emulator core", type=str, required=False)
    parser.add_argument("-ratio", help="force game ratio", type=str, required=False)
    parser.add_argument("-netplay", help="host/client", type=str, required=False)

    args = parser.parse_args()
    try:
        exitcode = -1
        exitcode = main(args)
    except Exception as e:
        eslog.log("configgen exception: ")
        eslog.logtrace()
    time.sleep(1) # this seems to be required so that the gpu memory is restituated and available for es
    eslog.log("Exiting configgen with status {}".format(str(exitcode)))
    exit(exitcode)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
