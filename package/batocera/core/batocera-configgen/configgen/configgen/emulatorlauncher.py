#!/usr/bin/env python

import argparse
import time
import sys
from sys import exit
from Emulator import Emulator
from Evmapy import Evmapy
import generators
from generators.kodi.kodiGenerator import KodiGenerator
from generators.linapple.linappleGenerator import LinappleGenerator
from generators.libretro.libretroGenerator import LibretroGenerator
from generators.moonlight.moonlightGenerator import MoonlightGenerator
from generators.mupen.mupenGenerator import MupenGenerator
from generators.ppsspp.ppssppGenerator import PPSSPPGenerator
from generators.flycast.flycastGenerator import FlycastGenerator
from generators.dolphin.dolphinGenerator import DolphinGenerator
from generators.pcsx2.pcsx2Generator import Pcsx2Generator
from generators.scummvm.scummvmGenerator import ScummVMGenerator
from generators.dosbox.dosboxGenerator import DosBoxGenerator
from generators.dosboxstaging.dosboxstagingGenerator import DosBoxStagingGenerator
from generators.dosboxx.dosboxxGenerator import DosBoxxGenerator
from generators.vice.viceGenerator import ViceGenerator
from generators.fsuae.fsuaeGenerator import FsuaeGenerator
from generators.amiberry.amiberryGenerator import AmiberryGenerator
from generators.citra.citraGenerator import CitraGenerator
from generators.daphne.daphneGenerator import DaphneGenerator
from generators.cannonball.cannonballGenerator import CannonballGenerator
from generators.sdlpop.sdlpopGenerator import SdlPopGenerator
from generators.openbor.openborGenerator import OpenborGenerator
from generators.wine.wineGenerator import WineGenerator
from generators.cemu.cemuGenerator import CemuGenerator
from generators.melonds.melondsGenerator import MelonDSGenerator
from generators.rpcs3.rpcs3Generator import Rpcs3Generator
from generators.pygame.pygameGenerator import PygameGenerator
from generators.mame.mameGenerator import MameGenerator
from generators.devilutionx.devilutionxGenerator import DevilutionXGenerator
from generators.hatari.hatariGenerator import HatariGenerator
from generators.solarus.solarusGenerator import SolarusGenerator
from generators.easyrpg.easyrpgGenerator import EasyRPGGenerator
from generators.redream.redreamGenerator import RedreamGenerator
from generators.supermodel.supermodelGenerator import SupermodelGenerator
from generators.xash3d_fwgs.xash3dFwgsGenerator import Xash3dFwgsGenerator
from generators.tsugaru.tsugaruGenerator import TsugaruGenerator
from generators.mugen.mugenGenerator import MugenGenerator
from generators.fpinball.fpinballGenerator import FpinballGenerator
from generators.lightspark.lightsparkGenerator import LightsparkGenerator
from generators.ruffle.ruffleGenerator import RuffleGenerator
from generators.duckstation.duckstationGenerator import DuckstationGenerator
from generators.drastic.drasticGenerator import DrasticGenerator
from generators.xemu.xemuGenerator import XemuGenerator
from generators.cgenius.cgeniusGenerator import CGeniusGenerator
from generators.flatpak.flatpakGenerator import FlatpakGenerator

import controllersConfig as controllers
import signal
import batoceraFiles
import os
import subprocess
import utils.videoMode as videoMode
from utils.logger import eslog

generators = {
    'kodi': KodiGenerator(),
    'linapple': LinappleGenerator(),
    'libretro': LibretroGenerator(),
    'moonlight': MoonlightGenerator(),
    'scummvm': ScummVMGenerator(),
    'dosbox': DosBoxGenerator(),
    'dosbox_staging': DosBoxStagingGenerator(),
    'dosboxx': DosBoxxGenerator(),
    'mupen64plus': MupenGenerator(),
    'vice': ViceGenerator(),
    'fsuae': FsuaeGenerator(),
    'amiberry': AmiberryGenerator(),
    'flycast': FlycastGenerator(),
    'dolphin': DolphinGenerator(),
    'pcsx2': Pcsx2Generator(),
    'ppsspp': PPSSPPGenerator(),
    'citra' : CitraGenerator(),
    'daphne' : DaphneGenerator(),
    'cannonball' : CannonballGenerator(),
    'sdlpop' : SdlPopGenerator(),
    'openbor' : OpenborGenerator(),
    'wine' : WineGenerator(),
    'cemu' : CemuGenerator(),
    'melonds' : MelonDSGenerator(),
    'rpcs3' : Rpcs3Generator(),
    'mame' : MameGenerator(),
    'pygame': PygameGenerator(),
    'devilutionx': DevilutionXGenerator(),
    'hatari': HatariGenerator(),
    'solarus': SolarusGenerator(),
    'easyrpg': EasyRPGGenerator(),
    'redream': RedreamGenerator(),
    'supermodel': SupermodelGenerator(),
    'xash3d_fwgs': Xash3dFwgsGenerator(),
    'tsugaru': TsugaruGenerator(),
    'mugen': MugenGenerator(),
    'fpinball': FpinballGenerator(),
    'lightspark': LightsparkGenerator(),
    'ruffle': RuffleGenerator(),
    'duckstation': DuckstationGenerator(),
    'drastic': DrasticGenerator(),
    'xemu': XemuGenerator(),
    'cgenius': CGeniusGenerator(),
    'flatpak': FlatpakGenerator(),
}

def main(args, maxnbplayers):
    playersControllers = dict()

    controllersInput = []
    for p in range(1, maxnbplayers+1):
        ci = {}
        ci["index"]      = getattr(args, "p{}index"     .format(p))
        ci["guid"]       = getattr(args, "p{}guid"      .format(p))
        ci["name"]       = getattr(args, "p{}name"      .format(p))
        ci["devicepath"] = getattr(args, "p{}devicepath".format(p))
        ci["nbbuttons"]  = getattr(args, "p{}nbbuttons" .format(p))
        ci["nbhats"]     = getattr(args, "p{}nbhats"    .format(p))
        ci["nbaxes"]     = getattr(args, "p{}nbaxes"    .format(p))
        controllersInput.append(ci)

    # Read the controller configuration
    playersControllers = controllers.loadControllerConfig(controllersInput)
    # find the system to run
    systemName = args.system
    eslog.log("Running system: {}".format(systemName))
    system = Emulator(systemName, args.rom)

    if args.emulator is not None:
        system.config["emulator"] = args.emulator
        system.config["emulator-forced"] = True
    if args.core is not None:
        system.config["core"] = args.core
        system.config["core-forced"] = True
    debugDisplay = system.config.copy()
    if "retroachievements.password" in debugDisplay:
        debugDisplay["retroachievements.password"] = "***"
    eslog.debug("Settings: {}".format(debugDisplay))
    if "emulator" in system.config and "core" in system.config:
        eslog.log("emulator: {}, core: {}".format(system.config["emulator"], system.config["core"]))
    else:
        if "emulator" in system.config:
            eslog.log("emulator: {}".format(system.config["emulator"]))

    # the resolution must be changed before configuration while the configuration may depend on it (ie bezels)
    wantedGameMode = generators[system.config['emulator']].getResolutionMode(system.config)
    systemMode = videoMode.getCurrentMode()

    resolutionChanged = False
    mouseChanged = False
    exitCode = -1
    try:
        # lower the resolution if mode is auto
        newsystemMode = systemMode # newsystemmode is the mode after minmax (ie in 1K if tv was in 4K), systemmode is the mode before (ie in es)
        if system.config["videomode"] == "" or system.config["videomode"] == "default":
            eslog.log("minTomaxResolution")
            eslog.log("video mode before minmax: {}".format(systemMode))
            videoMode.minTomaxResolution()
            newsystemMode = videoMode.getCurrentMode()
            if newsystemMode != systemMode:
                resolutionChanged = True

        eslog.log("current video mode: {}".format(newsystemMode))
        eslog.log("wanted video mode: {}".format(wantedGameMode))

        if wantedGameMode != 'default' and wantedGameMode != newsystemMode:
            videoMode.changeMode(wantedGameMode)
            resolutionChanged = True
        gameResolution = videoMode.getCurrentResolution()

        # if resolution is reversed (ie ogoa boards), reverse it in the gameResolution to have it correct
        if system.isOptSet('resolutionIsReversed') and system.getOptBoolean('resolutionIsReversed') == True:
            x = gameResolution["width"]
            gameResolution["width"]  = gameResolution["height"]
            gameResolution["height"] = x
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
        if args.netplaypass is not None:
            system.config["netplay.password"] = args.netplaypass
        if args.netplayip is not None:
            system.config["netplay.server.ip"] = args.netplayip
        if args.netplayport is not None:
            system.config["netplay.server.port"] = args.netplayport

        # autosave arguments
        if args.state_slot is not None:
            system.config["state_slot"] = args.state_slot
        if args.autosave is not None:
            system.config["autosave"] = args.autosave

        if generators[system.config['emulator']].getMouseMode(system.config):
            mouseChanged = True
            videoMode.changeMouse(True)

        # run a script before emulator starts
        callExternalScripts("/usr/share/batocera/configgen/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts("/userdata/system/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

        # run the emulator
        try:
            Evmapy.start(systemName, system.config['emulator'], effectiveCore, effectiveRom, playersControllers)
            exitCode = runCommand(generators[system.config['emulator']].generate(system, args.rom, playersControllers, gameResolution))
        finally:
            Evmapy.stop()

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

        if mouseChanged:
            try:
                videoMode.changeMouse(False)
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
    exitcode = -1
    if command.array:
        proc = subprocess.Popen(command.array, env=command.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        return exitcode
    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        sys.stdout.write(out)
        sys.stderr.write(err)
    except:
        eslog.log("emulator exited")

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

    maxnbplayers = 8
    for p in range(1, maxnbplayers+1):
        parser.add_argument("-p{}index"     .format(p), help="player{} controller index"            .format(p), type=int, required=False)
        parser.add_argument("-p{}guid"      .format(p), help="player{} controller SDL2 guid"        .format(p), type=str, required=False)
        parser.add_argument("-p{}name"      .format(p), help="player{} controller name"             .format(p), type=str, required=False)
        parser.add_argument("-p{}devicepath".format(p), help="player{} controller device"           .format(p), type=str, required=False)
        parser.add_argument("-p{}nbbuttons" .format(p), help="player{} controller number of buttons".format(p), type=str, required=False)
        parser.add_argument("-p{}nbhats"    .format(p), help="player{} controller number of hats"   .format(p), type=str, required=False)
        parser.add_argument("-p{}nbaxes"    .format(p), help="player{} controller number of axes"   .format(p), type=str, required=False)
    
    parser.add_argument("-system", help="select the system to launch", type=str, required=True)
    parser.add_argument("-rom", help="rom absolute path", type=str, required=True)
    parser.add_argument("-emulator", help="force emulator", type=str, required=False)
    parser.add_argument("-core", help="force emulator core", type=str, required=False)
    parser.add_argument("-netplaymode", help="host/client", type=str, required=False)
    parser.add_argument("-netplaypass", help="enable spectator mode", type=str, required=False)
    parser.add_argument("-netplayip", help="remote ip", type=str, required=False)
    parser.add_argument("-netplayport", help="remote port", type=str, required=False)
    parser.add_argument("-state_slot", help="state slot", type=str, required=False)
    parser.add_argument("-autosave", help="autosave", type=str, required=False)

    args = parser.parse_args()
    try:
        exitcode = -1
        exitcode = main(args, maxnbplayers)
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
