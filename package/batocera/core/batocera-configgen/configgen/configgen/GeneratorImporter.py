#!/usr/bin/env python

import generators

# not the nicest way, possibly one of the faster i think
# some naming rules may allow to modify this function to less than 10 lines

def getGenerator(emulator):

    if emulator == 'kodi':
        from generators.kodi.kodiGenerator import KodiGenerator
        return KodiGenerator()

    if emulator == 'libretro':
        from generators.libretro.libretroGenerator import LibretroGenerator
        return LibretroGenerator()

    if emulator == 'moonlight':
        from generators.moonlight.moonlightGenerator import MoonlightGenerator
        return MoonlightGenerator()

    if emulator == 'scummvm':
        from generators.scummvm.scummvmGenerator import ScummVMGenerator
        return ScummVMGenerator()

    if emulator == 'dosbox':
        from generators.dosbox.dosboxGenerator import DosBoxGenerator
        return DosBoxGenerator()

    if emulator == 'dosbox_staging':
        from generators.dosboxstaging.dosboxstagingGenerator import DosBoxStagingGenerator
        return DosBoxStagingGenerator()

    if emulator == 'dosboxx':
        from generators.dosboxx.dosboxxGenerator import DosBoxxGenerator
        return DosBoxxGenerator()

    if emulator == 'mupen64plus':
        from generators.mupen.mupenGenerator import MupenGenerator
        return MupenGenerator()
    
    if emulator == 'vice':
        from generators.vice.viceGenerator import ViceGenerator
        return ViceGenerator()

    if emulator == 'fsuae':
        from generators.fsuae.fsuaeGenerator import FsuaeGenerator
        return FsuaeGenerator()

    if emulator == 'amiberry':
        from generators.amiberry.amiberryGenerator import AmiberryGenerator
        return AmiberryGenerator()

    if emulator == 'flycast':
        from generators.flycast.flycastGenerator import FlycastGenerator
        return FlycastGenerator()

    if emulator == 'dolphin':
        from generators.dolphin.dolphinGenerator import DolphinGenerator
        return DolphinGenerator()

    if emulator == 'dolphin_triforce':
        from generators.dolphin_triforce.dolphinTriforceGenerator import DolphinTriforceGenerator
        return DolphinTriforceGenerator()

    if emulator == 'pcsx2':
        from generators.pcsx2.pcsx2Generator import Pcsx2Generator
        return Pcsx2Generator()

    if emulator == 'ppsspp':
        from generators.ppsspp.ppssppGenerator import PPSSPPGenerator
        return PPSSPPGenerator()

    if emulator == 'citra' :
        from generators.citra.citraGenerator import CitraGenerator
        return CitraGenerator()

    if emulator == 'daphne' :
        from generators.daphne.daphneGenerator import DaphneGenerator
        return DaphneGenerator()

    if emulator == 'cannonball' :
        from generators.cannonball.cannonballGenerator import CannonballGenerator
        return CannonballGenerator()

    if emulator == 'sdlpop' :
        from generators.sdlpop.sdlpopGenerator import SdlPopGenerator
        return SdlPopGenerator()

    if emulator == 'openbor' :
        from generators.openbor.openborGenerator import OpenborGenerator
        return OpenborGenerator()

    if emulator == 'wine' :
        from generators.wine.wineGenerator import WineGenerator
        return WineGenerator()

    if emulator == 'cemu' :
        from generators.cemu.cemuGenerator import CemuGenerator
        return CemuGenerator()

    if emulator == 'melonds' :
        from generators.melonds.melondsGenerator import MelonDSGenerator
        return MelonDSGenerator()

    if emulator == 'rpcs3' :
        from generators.rpcs3.rpcs3Generator import Rpcs3Generator
        return Rpcs3Generator()

    if emulator == 'mame' :
        from generators.mame.mameGenerator import MameGenerator
        return MameGenerator()

    if emulator == 'pygame':
        from generators.pygame.pygameGenerator import PygameGenerator
        return PygameGenerator()

    if emulator == 'devilutionx':
        from generators.devilutionx.devilutionxGenerator import DevilutionXGenerator
        return DevilutionXGenerator()

    if emulator == 'hatari':
        from generators.hatari.hatariGenerator import HatariGenerator
        return HatariGenerator()

    if emulator == 'solarus':
        from generators.solarus.solarusGenerator import SolarusGenerator
        return SolarusGenerator()

    if emulator == 'easyrpg':
        from generators.easyrpg.easyrpgGenerator import EasyRPGGenerator
        return EasyRPGGenerator()

    if emulator == 'redream':
        from generators.redream.redreamGenerator import RedreamGenerator
        return RedreamGenerator()

    if emulator == 'supermodel':
        from generators.supermodel.supermodelGenerator import SupermodelGenerator
        return SupermodelGenerator()

    if emulator == 'xash3d_fwgs':
        from generators.xash3d_fwgs.xash3dFwgsGenerator import Xash3dFwgsGenerator
        return Xash3dFwgsGenerator()

    if emulator == 'tsugaru':
        from generators.tsugaru.tsugaruGenerator import TsugaruGenerator
        return TsugaruGenerator()

    if emulator == 'mugen':
        from generators.mugen.mugenGenerator import MugenGenerator
        return MugenGenerator()

    if emulator == 'fpinball':
        from generators.fpinball.fpinballGenerator import FpinballGenerator
        return FpinballGenerator()

    if emulator == 'lightspark':
        from generators.lightspark.lightsparkGenerator import LightsparkGenerator
        return LightsparkGenerator()

    if emulator == 'ruffle':
        from generators.ruffle.ruffleGenerator import RuffleGenerator
        return RuffleGenerator()

    if emulator == 'duckstation':
        from generators.duckstation.duckstationGenerator import DuckstationGenerator
        return DuckstationGenerator()

    if emulator == 'drastic':
        from generators.drastic.drasticGenerator import DrasticGenerator
        return DrasticGenerator()

    if emulator == 'xemu':
        from generators.xemu.xemuGenerator import XemuGenerator
        return XemuGenerator()

    if emulator == 'cgenius':
        from generators.cgenius.cgeniusGenerator import CGeniusGenerator
        return CGeniusGenerator()

    if emulator == 'flatpak':
        from generators.flatpak.flatpakGenerator import FlatpakGenerator
        return FlatpakGenerator()

    if emulator == 'steam':
        from generators.steam.steamGenerator import SteamGenerator
        return SteamGenerator()

    if emulator == 'ecwolf':
        from generators.ecwolf.ecwolfGenerator import ECWolfGenerator
        return ECWolfGenerator()

    if emulator == 'lexaloffle':
        from generators.lexaloffle.lexaloffleGenerator import LexaloffleGenerator
        return LexaloffleGenerator()

    if emulator == 'model2emu':
        from generators.model2emu.model2emuGenerator import Model2EmuGenerator
        return Model2EmuGenerator()

    if emulator == 'sonic2013':
        from generators.sonicretro.sonicretroGenerator import SonicRetroGenerator
        return SonicRetroGenerator()

    if emulator == 'soniccd':
        from generators.sonicretro.sonicretroGenerator import SonicRetroGenerator        
        return SonicRetroGenerator()

    if emulator == 'gsplus':
        from generators.gsplus.gsplusGenerator import GSplusGenerator
        return GSplusGenerator()

    if emulator == 'fba2x':
        from generators.fba2x.fba2xGenerator import Fba2xGenerator
        return Fba2xGenerator()

    if emulator == 'yuzu':
        from generators.yuzu.yuzuGenerator import YuzuGenerator
        return YuzuGenerator()

    if emulator == 'ryujinx':
        from generators.ryujinx.ryujinxGenerator import RyujinxGenerator
        return RyujinxGenerator()

    if emulator == 'samcoupe':
        from generators.samcoupe.samcoupeGenerator import SamcoupeGenerator
        return SamcoupeGenerator()

    if emulator == 'abuse':
        from generators.abuse.abuseGenerator import AbuseGenerator
        return AbuseGenerator()

    if emulator == 'cdogs':
        from generators.cdogs.cdogsGenerator import CdogsGenerator
        return CdogsGenerator()

    if emulator == 'hcl':
        from generators.hcl.hclGenerator import HclGenerator
        return HclGenerator()

    if emulator == 'openmsx':
        from generators.openmsx.openmsxGenerator import OpenmsxGenerator
        return OpenmsxGenerator()

    if emulator == 'demul':
        from generators.demul.demulGenerator import DemulGenerator
        return DemulGenerator()

    if emulator == 'xenia' or emulator == 'xenia-canary':
        from generators.xenia.xeniaGenerator import XeniaGenerator
        return XeniaGenerator()

    if emulator == 'odcommander':
        from generators.odcommander.odcommanderGenerator import OdcommanderGenerator
        return OdcommanderGenerator()
    
    if emulator == 'gzdoom':
        from generators.gzdoom.gzdoomGenerator import GZDoomGenerator
        return GZDoomGenerator()

    if emulator == "eduke32":
        from generators.eduke32.eduke32Generator import EDuke32Generator
        return EDuke32Generator()

    if emulator == "raze":
        from generators.raze.razeGenerator import RazeGenerator
        return RazeGenerator()

    if emulator == "vita3k":
        from generators.vita3k.vita3kGenerator import Vita3kGenerator
        return Vita3kGenerator()

    if emulator == "ikemen":
        from generators.ikemen.ikemenGenerator import IkemenGenerator
        return IkemenGenerator()

    #if emulator == 'play':
    #from generators.play.playGenerator import PlayGenerator
    #return PlayGenerator(),

    if emulator == 'sh':
        from generators.sh.shGenerator import ShGenerator
        return ShGenerator()

    raise Exception(f"no generator found for emulator {emulator}")
