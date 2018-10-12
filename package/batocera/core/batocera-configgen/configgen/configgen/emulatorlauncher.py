#!/usr/bin/env python

import argparse
import time
import sys
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
    'advancemame' : AdvMameGenerator()
}

def main(args):
    playersControllers = dict()
    if not args.demo:
        # Read the controller configuration
        playersControllers = controllers.loadControllerConfig(args.p1index, args.p1guid, args.p1name, args.p1devicepath, args.p1nbaxes,
                                                              args.p2index, args.p2guid, args.p2name, args.p2devicepath, args.p2nbaxes,
                                                              args.p3index, args.p3guid, args.p3name, args.p3devicepath, args.p3nbaxes,
                                                              args.p4index, args.p4guid, args.p4name, args.p4devicepath, args.p4nbaxes,
                                                              args.p5index, args.p5guid, args.p5name, args.p5devicepath, args.p5nbaxes)
    # find the system to run
    systemName = args.system
    eslog.log("Running system: " + systemName)
    system = getDefaultEmulator(systemName)
    if system is None:
        eslog.log("no emulator defined. exiting.")
        return 1
    system.configure(args.emulator, args.core, args.ratio, args.netplay)

    # the resolution must be changed before configuration while the configuration may depend on it (ie bezels)
    newResolution = generators[system.config['emulator']].getResolution(system.config)
    exitCode = -1
    try:
        videoMode.changeResolution(newResolution)
        gameResolution = videoMode.getCurrentResolution()
        eslog.log("resolution: " + str(gameResolution["width"]) + "x" + str(gameResolution["height"]))

        # savedir: create the save directory is not already done
        dirname = os.path.join(recalboxFiles.savesDir, system.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # run the emulator
        exitCode = runCommand(generators[system.config['emulator']].generate(system, args.rom, playersControllers, gameResolution))
    finally:
        # always restore the resolution
        if newResolution != 'default':
            try:
                videoMode.resetResolution()
            except Exception:
                pass # don't fail
    # exit
    return exitCode

def runCommand(command):
    global proc

    command.env.update(os.environ)
    eslog.log("command:" + str(command.array))
    eslog.log("env: "    + str(command.env))
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

# List emulators with their default emulator/cores
def getDefaultEmulator(systemName):

    # Nintendo
    if systemName == "nes":
        return Emulator(name='nes',        emulator='libretro',    core='fceunext')
    if systemName == "snes":
        return Emulator(name='snes',       emulator='libretro',    core='pocketsnes')
    if systemName == "n64":
        return Emulator(name='n64',        emulator='mupen64plus', core='gliden64')
    if systemName == "gba":
        return Emulator(name='gba',        emulator='libretro',    core='gpsp')
    if systemName == "gb":
        return Emulator(name='gb',         emulator='libretro',    core='gambatte')
    if systemName == "gbc":
        return Emulator(name='gbc',        emulator='libretro',    core='gambatte')
    if systemName == "gb2players":
        return Emulator(name='gb2players',         emulator='libretro',    core='tgbdual')
    if systemName == "gbc2players":
        return Emulator(name='gbc2players',        emulator='libretro',    core='tgbdual')
    if systemName == "fds":
        return Emulator(name='fds',        emulator='libretro',    core='nestopia')
    if systemName == "virtualboy":
        return Emulator(name='virtualboy', emulator='libretro',    core='vb')
    if systemName == "gamecube":
        return Emulator(name='gamecube',   emulator='dolphin')
    if systemName == "wii":
        return Emulator(name='wii',        emulator='dolphin')
    if systemName == "ps2":
        return Emulator(name='ps2',        emulator='pcsx2')
    if systemName == "nds":
        return Emulator(name='nds',        emulator='libretro',    core='desmume')

    # Sega
    if systemName == "sg1000":
        return Emulator(name='sg1000',       emulator='libretro', core='genesisplusgx')
    if systemName == "mastersystem":
        return Emulator(name='mastersystem', emulator='libretro', core='picodrive')
    if systemName == "megadrive":
        return Emulator(name='megadrive',    emulator='libretro', core='picodrive')
    if systemName == "gamegear":
        return Emulator(name='gamegear',     emulator='libretro', core='genesisplusgx')
    if systemName == "sega32x":
        return Emulator(name='sega32x',      emulator='libretro', core='picodrive')
    if systemName == "segacd":
        return Emulator(name='segacd',       emulator='libretro', core='picodrive')
    if systemName == "saturn":
        return Emulator(name='saturn',       emulator='libretro', core='yabause')
    if systemName == "dreamcast":
        return Emulator(name='dreamcast',    emulator='reicast')

     # Arcade
    if systemName == "neogeo":
        return Emulator(name='neogeo',       emulator='fba2x')
    if systemName == "mame":
        return Emulator(name='mame',         emulator='libretro', core='mame078')
    if systemName == "fba":
        return Emulator(name='fba',          emulator='fba2x')
    if systemName == "fba_libretro":
        return Emulator(name='fba_libretro', emulator='libretro', core='fba')
    if systemName == "advancemame":
        return Emulator(name='advancemame',  emulator='advmame')

     # Computers
    if systemName == "msx":
        return Emulator(name='msx',  emulator='libretro', core='bluemsx')
    if systemName == "msx1":
        return Emulator(name='msx1', emulator='libretro', core='bluemsx')
    if systemName == "msx2":
        return Emulator(name='msx2', emulator='libretro', core='bluemsx')

     # Amiga
    if systemName == "amiga500":
        return Emulator(name='amiga500',  emulator='fsuae', core='A500')
    if systemName == "amiga500p":
        return Emulator(name='amiga500p', emulator='fsuae', core='A500+')
    if systemName == "amiga600":
        return Emulator(name='amiga600',  emulator='fsuae', core='A600')
    if systemName == "amiga1000":
        return Emulator(name='amiga1000', emulator='fsuae', core='A1000')
    if systemName == "amiga1200":
        return Emulator(name='amiga1200', emulator='fsuae', core='A1200')
    if systemName == "amiga3000":
        return Emulator(name='amiga3000', emulator='fsuae', core='A3000')
    if systemName == "amiga4000":
        return Emulator(name='amiga4000', emulator='fsuae', core='A4000')
    if systemName == "amigacd32":
        return Emulator(name='amigacd32', emulator='fsuae', core='CD32')
    if systemName == "amigacdtv":
        return Emulator(name='amigacdtv', emulator='fsuae', core='CDTV')

    #
    if systemName == "amstradcpc":
        return Emulator(name='amstradcpc', emulator='libretro', core='cap32')
    if systemName == "apple2":
        return Emulator(name='apple2',     emulator='linapple', videomode='default')
    if systemName == "atarist":
        return Emulator(name='atarist',    emulator='libretro', core='hatari')
    if systemName == "zxspectrum":
        return Emulator(name='zxspectrum', emulator='libretro', core='fuse')
    if systemName == "odyssey2":
        return Emulator(name='odyssey2',   emulator='libretro', core='o2em')
    if systemName == "zx81":
        return Emulator(name='zx81',       emulator='libretro', core='81')
    if systemName == "dos":
        return Emulator(name='dos',        emulator='dosbox', videomode='default')
    if systemName == "c64":
        return Emulator(name='c64',        emulator='vice',     core='x64')
    if systemName == "x68000":
        return Emulator(name='x68000',     emulator='libretro', core='px68k')

     #
    if systemName == "ngp":
        return Emulator(name='ngp', emulator='libretro', core='mednafen_ngp')
    if systemName == "ngpc":
        return Emulator(name='ngpc', emulator='libretro', core='mednafen_ngp')
    if systemName == "gw":
        return Emulator(name='gw', emulator='libretro', core='gw')
    if systemName == "vectrex":
        return Emulator(name='vectrex', emulator='libretro', core='vecx')
    if systemName == "lynx":
        return Emulator(name='lynx', emulator='libretro', core='mednafen_lynx')
    if systemName == "lutro":
        return Emulator(name='lutro', emulator='libretro', core='lutro')
    if systemName == "wswan":
        return Emulator(name='wswan', emulator='libretro', core='mednafen_wswan', ratio='16/10')
    if systemName == "wswanc":
        return Emulator(name='wswanc', emulator='libretro', core='mednafen_wswan', ratio='16/10')
    if systemName == "pcengine":
        return Emulator(name='pcengine', emulator='libretro', core='mednafen_supergrafx')
    if systemName == "pcenginecd":
        return Emulator(name='pcenginecd', emulator='libretro', core='mednafen_supergrafx')
    if systemName == "supergrafx":
        return Emulator(name='supergrafx', emulator='libretro', core='mednafen_supergrafx')
    if systemName == "pcfx":
        return Emulator(name='pcfx', emulator='libretro', core='pcfx')
    if systemName == "intellivision":
        return Emulator(name='intellivision', emulator='libretro', core='freeintv')
    if systemName == "atari2600":
        return Emulator(name='atari2600', emulator='libretro', core='stella')
    if systemName == "atari5200":
        return Emulator(name='atari5200', emulator='libretro', core='atari800')
    if systemName == "atari7800":
        return Emulator(name='atari7800', emulator='libretro', core='prosystem')
    if systemName == "prboom":
        return Emulator(name='prboom', emulator='libretro', core='prboom')
    if systemName == "psx":
        return Emulator(name='psx', emulator='libretro', core='pcsx_rearmed')
    if systemName == "cavestory":
        return Emulator(name='cavestory', emulator='libretro', core='nxengine')
    if systemName == "imageviewer":
        return Emulator(name='imageviewer', emulator='libretro', core='imageviewer')
    if systemName == "scummvm":
        return Emulator(name='scummvm', emulator='scummvm', videomode='default')
    if systemName == "colecovision":
        return Emulator(name='colecovision', emulator='libretro', core='bluemsx')
    if systemName == "jaguar":
        return Emulator(name='jaguar', emulator='libretro', core='virtualjaguar')
    if systemName == "3do":
        return Emulator(name='3do', emulator='libretro', core='4do')
    if systemName == "kodi":
        return Emulator(name='kodi', emulator='kodi', videomode='default')
    if systemName == "moonlight":
        return Emulator(name='moonlight', emulator='moonlight')
    if systemName == "psp":
        return Emulator(name='psp', emulator='ppsspp')

    # nothing found
    return None

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
    parser.add_argument("-demo", help="mode demo", type=bool, required=False)
    parser.add_argument("-netplay", help="host/client", type=str, required=False)

    args = parser.parse_args()
    try:
        exitcode = -1
        exitcode = main(args)
    except Exception as e:
        eslog.log("configgen exception: ")
        eslog.logtrace()
    time.sleep(1) # this seems to be required so that the gpu memory is restituated and available for es
    eslog.log("Exiting configgen with status " + str(exitcode))
    exit(exitcode)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
