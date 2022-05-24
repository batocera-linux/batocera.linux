#!/usr/bin/env python

import argparse
import time
import sys
from sys import exit
from Emulator import Emulator
from Evmapy import Evmapy
import generators
import xml.etree.ElementTree as ET
import json
from generators.kodi.kodiGenerator import KodiGenerator
from generators.linapple.linappleGenerator import LinappleGenerator
from generators.libretro.libretroGenerator import LibretroGenerator
from generators.moonlight.moonlightGenerator import MoonlightGenerator
from generators.mupen.mupenGenerator import MupenGenerator
from generators.ppsspp.ppssppGenerator import PPSSPPGenerator
from generators.flycast.flycastGenerator import FlycastGenerator
from generators.dolphin.dolphinGenerator import DolphinGenerator
from generators.dolphin_triforce.dolphinTriforceGenerator import DolphinTriforceGenerator
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
from generators.steam.steamGenerator import SteamGenerator
from generators.ecwolf.ecwolfGenerator import ECWolfGenerator
from generators.lexaloffle.lexaloffleGenerator import LexaloffleGenerator
from generators.model2emu.model2emuGenerator import Model2EmuGenerator
from generators.sonicretro.sonicretroGenerator import SonicRetroGenerator
from generators.gsplus.gsplusGenerator import GSplusGenerator
from generators.fba2x.fba2xGenerator import Fba2xGenerator
from generators.yuzu.yuzuGenerator import YuzuGenerator
from generators.ryujinx.ryujinxGenerator import RyujinxGenerator
from generators.samcoupe.samcoupeGenerator import SamcoupeGenerator
from generators.abuse.abuseGenerator import AbuseGenerator
from generators.cdogs.cdogsGenerator import CdogsGenerator
from generators.hcl.hclGenerator import HclGenerator
from generators.openmsx.openmsxGenerator import OpenmsxGenerator
from generators.demul.demulGenerator import DemulGenerator
from generators.sh.shGenerator import ShGenerator
from generators.xenia.xeniaGenerator import XeniaGenerator
from generators.odcommander.odcommanderGenerator import OdcommanderGenerator
#from generators.play.playGenerator import PlayGenerator

import controllersConfig as controllers
import signal
import batoceraFiles
import os
import subprocess
import utils.videoMode as videoMode
import utils.bezels as bezelsUtil
from utils.logger import get_logger

eslog = get_logger(__name__)

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
    'dolphin_triforce': DolphinTriforceGenerator(),
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
    'steam': SteamGenerator(),
    'ecwolf': ECWolfGenerator(),
    'lexaloffle': LexaloffleGenerator(),
    'model2emu': Model2EmuGenerator(),
    'sonic2013': SonicRetroGenerator(),
    'soniccd': SonicRetroGenerator(),
    'gsplus': GSplusGenerator(),
    'fba2x': Fba2xGenerator(),
    'yuzu': YuzuGenerator(),
    'ryujinx': RyujinxGenerator(),
    'samcoupe': SamcoupeGenerator(),
    'abuse': AbuseGenerator(),
    'cdogs': CdogsGenerator(),
    'hcl': HclGenerator(),
    'openmsx': OpenmsxGenerator(),
    'demul': DemulGenerator(),
    'xenia': XeniaGenerator(),
    'odcommander': OdcommanderGenerator(),
    #'play': PlayGenerator(),
    'sh': ShGenerator(),
}

emulatorNoBezel = [ "sdlpop", "odcommander" ]

def squashfs_begin(rom):
    eslog.debug("squashfs_begin({})".format(rom))
    rommountpoint = "/var/run/squashfs/" + os.path.basename(rom)[:-9]

    if not os.path.exists("/var/run/squashfs"):
        os.mkdir("/var/run/squashfs")

    # first, try to clean an empty remaining directory (for example because of a crash)
    if os.path.exists(rommountpoint) and os.path.isdir(rommountpoint):
        eslog.debug("squashfs_begin: {} already exists".format(rommountpoint))
        # try to remove an empty directory, else, run the directory, ignoring the .squashfs
        try:
            os.rmdir(rommountpoint)
        except:
            eslog.debug("squashfs_begin: failed to rmdir {}".format(rommountpoint))
            return False, None, rommountpoint

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    os.mkdir(rommountpoint)
    return_code = subprocess.call(["mount", rom, rommountpoint])
    if return_code != 0:
        eslog.debug("squashfs_begin: mounting {} failed".format(rommountpoint))
        try:
            os.rmdir(rommountpoint)
        except:
            pass
        raise Exception("unable to mount the file {}".format(rom))

    # if the squashfs contains a single file with the same name, take it as the rom file
    romsingle = rommountpoint + "/" + os.path.basename(rom)[:-9]
    if len(os.listdir(rommountpoint)) == 1 and  os.path.exists(romsingle):
        eslog.debug("squashfs: single rom ".format(romsingle))
        return True, rommountpoint, romsingle

    return True, rommountpoint, rommountpoint

def squashfs_end(rommountpoint):
    eslog.debug("squashfs_end({})".format(rommountpoint))

    # umount
    return_code = subprocess.call(["umount", rommountpoint])
    if return_code != 0:
        eslog.debug("squashfs_begin: unmounting {} failed".format(rommountpoint))
        raise Exception("unable to umount the file {}".format(rommountpoint))

    # cleaning the empty directory
    os.rmdir(rommountpoint)

def main(args, maxnbplayers):
    # squashfs roms if squashed
    extension = os.path.splitext(args.rom)[1][1:].lower()
    if extension == "squashfs":
        exitCode = 0
        need_end = False
        try:
            need_end, rommountpoint, rom = squashfs_begin(args.rom)
            exitCode = start_rom(args, maxnbplayers, rom, args.rom)
        finally:
            if need_end:
                squashfs_end(rommountpoint)
        return exitCode
    else:
        return start_rom(args, maxnbplayers, args.rom, args.rom)

def start_rom(args, maxnbplayers, rom, romConfiguration):
    # controllers
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
    eslog.debug("Running system: {}".format(systemName))
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
    eslog.debug("Settings: {}".format(debugDisplay))
    if "emulator" in system.config and "core" in system.config:
        eslog.debug("emulator: {}, core: {}".format(system.config["emulator"], system.config["core"]))
    else:
        if "emulator" in system.config:
            eslog.debug("emulator: {}".format(system.config["emulator"]))

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
            eslog.debug("minTomaxResolution")
            eslog.debug("video mode before minmax: {}".format(systemMode))
            videoMode.minTomaxResolution()
            newsystemMode = videoMode.getCurrentMode()
            if newsystemMode != systemMode:
                resolutionChanged = True

        eslog.debug("current video mode: {}".format(newsystemMode))
        eslog.debug("wanted video mode: {}".format(wantedGameMode))

        if wantedGameMode != 'default' and wantedGameMode != newsystemMode:
            videoMode.changeMode(wantedGameMode)
            resolutionChanged = True
        gameResolution = videoMode.getCurrentResolution()

        # if resolution is reversed (ie ogoa boards), reverse it in the gameResolution to have it correct
        if videoMode.isResolutionReversed():
            x = gameResolution["width"]
            gameResolution["width"]  = gameResolution["height"]
            gameResolution["height"] = x
        eslog.debug("resolution: {}x{}".format(str(gameResolution["width"]), str(gameResolution["height"])))

        # savedir: create the save directory if not already done
        dirname = os.path.join(batoceraFiles.savesDir, system.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

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

        # autosave arguments
        if args.state_slot is not None:
            system.config["state_slot"] = args.state_slot
        if args.autosave is not None:
            system.config["autosave"] = args.autosave
        if args.state_filename is not None:
            system.config["state_filename"] = args.state_filename

        if generators[system.config['emulator']].getMouseMode(system.config):
            mouseChanged = True
            videoMode.changeMouse(True)

        # SDL VSync is a big deal on OGA and RPi4
        if system.isOptSet('sdlvsync') and system.getOptBoolean('sdlvsync') == False:
            system.config["sdlvsync"] = '0'
        else:
            system.config["sdlvsync"] = '1'
        os.environ.update({'SDL_RENDER_VSYNC': system.config["sdlvsync"]})

        # run a script before emulator starts
        callExternalScripts("/usr/share/batocera/configgen/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts("/userdata/system/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

        # run the emulator
        try:
            Evmapy.start(systemName, system.config['emulator'], effectiveCore, effectiveRomConfiguration, playersControllers)
            # change directory if wanted
            executionDirectory = generators[system.config['emulator']].executionDirectory(system.config, effectiveRom)
            if executionDirectory is not None:
                os.chdir(executionDirectory)

            cmd = generators[system.config['emulator']].generate(system, rom, playersControllers, gameResolution)

            if system.isOptSet('hud_support') and system.getOptBoolean('hud_support') == True:
                hud_bezel = getHudBezel(system, rom, gameResolution)
                if (system.isOptSet('hud') and system.config["hud"] != "" and system.config["hud"] != "none") or hud_bezel is not None:
                    gameinfos = extractGameInfosFromXml(args.gameinfoxml)
                    cmd.env["MANGOHUD_DLSYM"] = "1"
                    hudconfig = getHudConfig(system, args.systemname, system.config['emulator'], effectiveCore, rom, gameinfos, hud_bezel)
                    with open('/var/run/hud.config', 'w') as f:
                        f.write(hudconfig)
                    cmd.env["MANGOHUD_CONFIGFILE"] = "/var/run/hud.config"
                    if generators[system.config['emulator']].hasInternalMangoHUDCall() == False:
                        cmd.array.insert(0, "mangohud")

            exitCode = runCommand(cmd)
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

def getHudBezel(system, rom, gameResolution):
    if 'bezel' not in system.config or system.config['bezel'] == "" or system.config['bezel'] == "none" or system.config['emulator'] in emulatorNoBezel:
        return None

    eslog.debug("hud enabled. trying to apply the bezel {}".format(system.config['bezel']))

    if generators[system.config['emulator']].supportsInternalBezels():
        eslog.debug("skipping bezels for emulator {}".format(system.config['emulator']))
        return None

    bezel = system.config['bezel']
    if system.config['emulator'] == 'libretro':
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name, True)
    else:
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name)
    if bz_infos is None:
        eslog.debug("no bezel info file found")
        return None

    overlay_info_file = bz_infos["info"]
    overlay_png_file  = bz_infos["png"]

    # check the info file
    # bottom, top, left and right must not cover too much the image to be considered as compatible
    if os.path.exists(overlay_info_file):
        try:
            infos = json.load(open(overlay_info_file))
        except:
            eslog.warning("unable to read {}".format(overlay_info_file))
            infos = {}
    else:
        infos = {}

    if "width" in infos and "height" in infos:
        bezel_width  = infos["width"]
        bezel_height = infos["height"]
        eslog.info("bezel size read from {}".format(overlay_info_file))
    else:
        bezel_width, bezel_height = bezelsUtil.fast_image_size(overlay_png_file)
        eslog.info("bezel size read from {}".format(overlay_png_file))

    # max cover proportion and ratio distortion
    max_cover = 0.05 # 5%
    max_ratio_delta = 0.01

    screen_ratio = gameResolution["width"] / gameResolution["height"]
    bezel_ratio  = bezel_width / bezel_height

    # the screen and bezel ratio must be approximatly the same
    if abs(screen_ratio - bezel_ratio) > max_ratio_delta:
        eslog.debug("screen ratio ({}) is too far from the bezel one ({}) : {} - {} > {}".format(screen_ratio, bezel_ratio, screen_ratio, bezel_ratio, max_ratio_delta))
        return None

    # the ingame image and the bezel free space must feet
    ## the bezel top and bottom cover must be minimum
    if "top" in infos and infos["top"] / bezel_height > max_cover:
        eslog.debug("bezel top covers too much the game image : {} / {} > {}".format(infos["top"], bezel_height, max_cover))
        return None
    if "bottom" in infos and infos["bottom"] / bezel_height > max_cover:
        eslog.debug("bezel bottom covers too much the game image : {} / {} > {}".format(infos["bottom"], bezel_height, max_cover))
        return None

    # if there is no information about top/bottom, assume default is 0

    ## the bezel left and right cover must be maximum
    ingame_ratio = generators[system.config['emulator']].getInGameRatio(system.config, gameResolution, rom)
    img_height = bezel_height
    img_width  = img_height * ingame_ratio

    if "left" not in infos:
        eslog.debug("bezel has no left info in {}".format(overlay_info_file))
        # assume default is 4/3 over 16/9
        infos_left = (bezel_width - (bezel_height / 3 * 4)) / 2
        if abs((infos_left  - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
            eslog.debug("bezel left covers too much the game image : {} / {} > {}".format(infos_left  - ((bezel_width-img_width)/2.0), img_width, max_cover))
            return None
        
    if "right" not in infos:
        eslog.debug("bezel has no right info in {}".format(overlay_info_file))
        # assume default is 4/3 over 16/9
        infos_right = (bezel_width - (bezel_height / 3 * 4)) / 2
        if abs((infos_right - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
            eslog.debug("bezel right covers too much the game image : {} / {} > {}".format(infos_right  - ((bezel_width-img_width)/2.0), img_width, max_cover))
            return None
    
    if "left"  in infos and abs((infos["left"]  - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
        eslog.debug("bezel left covers too much the game image : {} / {} > {}".format(infos["left"]  - ((bezel_width-img_width)/2.0), img_width, max_cover))
        return None
    if "right" in infos and abs((infos["right"] - ((bezel_width-img_width)/2.0)) / img_width) > max_cover:
        eslog.debug("bezel right covers too much the game image : {} / {} > {}".format(infos["right"]  - ((bezel_width-img_width)/2.0), img_width, max_cover))
        return None

    # if screen and bezel sizes doesn't match, resize
    # stretch option
    if system.isOptSet('bezel_stretch') and system.getOptBoolean('bezel_stretch') == True:
        bezel_stretch = True
    else:
        bezel_stretch = False
    if (bezel_width != gameResolution["width"] or bezel_height != gameResolution["height"]):
        eslog.debug("bezel needs to be resized")
        output_png_file = "/tmp/bezel.png"
        try:
            bezelsUtil.resizeImage(overlay_png_file, output_png_file, gameResolution["width"], gameResolution["height"], bezel_stretch)
        except Exception as e:
            eslog.error("failed to resize the image {}".format(e))
            return None
        overlay_png_file = output_png_file

    if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
        output_png_file = "/tmp/bezel_tattooed.png"
        bezelsUtil.tatooImage(overlay_png_file, output_png_file, system)
        overlay_png_file = output_png_file

    eslog.debug("applying bezel {}".format(overlay_png_file))
    return overlay_png_file

def extractGameInfosFromXml(xml):
    vals = {}

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

def callExternalScripts(folder, event, args):
    if not os.path.isdir(folder):
        return

    for file in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, file)):
            callExternalScripts(os.path.join(folder, file), event, args)
        else:
            if os.access(os.path.join(folder, file), os.X_OK):
                eslog.debug("calling external script: " + str([os.path.join(folder, file), event] + args))
                subprocess.call([os.path.join(folder, file), event] + args)

def hudConfig_protectStr(str):
    if str is None:
        return ""
    return str

def getHudConfig(system, systemName, emulator, core, rom, gameinfos, bezel):
    configstr = ""

    if bezel != "" and bezel is not None:
        configstr = "background_image={}\nlegacy_layout=false\n".format(hudConfig_protectStr(bezel))

    if not system.isOptSet('hud'):
        return configstr + "background_alpha=0\n" # hide the background

    mode = system.config["hud"]

    emulatorstr = emulator
    if emulator != core and core is not None:
        emulatorstr += "/" + core

    gameName = ""
    if "name" in gameinfos:
        gameName = gameinfos["name"]
    gameThumbnail = ""
    if "thumbnail" in gameinfos:
        gameThumbnail = gameinfos["thumbnail"]

    # predefined values
    if mode == "perf":
        configstr += "position=bottom-left\nbackground_alpha=0.9\nlegacy_layout=false\ncustom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%\nfps\ngpu_name\nengine_version\nvulkan_driver\nresolution\nram\ngpu_stats\ngpu_temp\ncpu_stats\ncpu_temp\ncore_load"
    elif mode == "game":
        configstr += "position=bottom-left\nbackground_alpha=0\nlegacy_layout=false\nfont_size=32\nimage_max_width=200\nimage=%THUMBNAIL%\ncustom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%"
    elif mode == "custom" and system.isOptSet('hud_custom') and system.config["hud_custom"] != "" :
        configstr += system.config["hud_custom"].replace("\\n", "\n")
    else:
        configstr = configstr + "background_alpha=0\n" # hide the background

    configstr = configstr.replace("%SYSTEMNAME%", hudConfig_protectStr(systemName))
    configstr = configstr.replace("%GAMENAME%", hudConfig_protectStr(gameName))
    configstr = configstr.replace("%EMULATORCORE%", hudConfig_protectStr(emulatorstr))
    configstr = configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))

    return configstr

def runCommand(command):
    global proc

    command.env.update(os.environ)
    eslog.debug("command: {}".format(str(command)))
    eslog.debug("command: {}".format(str(command.array)))
    eslog.debug("env: {}".format(str(command.env)))
    exitcode = -1
    if command.array:
        proc = subprocess.Popen(command.array, env=command.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        return exitcode
    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        eslog.debug(out.decode())
        eslog.error(err.decode())
    except BrokenPipeError:
        # Seeing BrokenPipeError? This is probably caused by head truncating output in the front-end
        # Examine es-core/src/platform.cpp::runSystemCommand for additional context
        pass
    except:
        eslog.error("emulator exited")

    return exitcode

def signal_handler(signal, frame):
    global proc
    eslog.debug('Exiting')
    if proc:
        eslog.debug('killing proc')
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
    parser.add_argument("-state_filename", help="state filename", type=str, required=False)
    parser.add_argument("-autosave", help="autosave", type=str, required=False)
    parser.add_argument("-systemname", help="system fancy name", type=str, required=False)
    parser.add_argument("-gameinfoxml", help="game info xml", type=str, nargs='?', default='/dev/null', required=False)

    args = parser.parse_args()
    try:
        exitcode = -1
        exitcode = main(args, maxnbplayers)
    except Exception as e:
        eslog.error("configgen exception: ", exc_info=True)
    time.sleep(1) # this seems to be required so that the gpu memory is restituated and available for es
    eslog.debug("Exiting configgen with status {}".format(str(exitcode)))
    exit(exitcode)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
