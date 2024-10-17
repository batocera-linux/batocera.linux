from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .Generator import Generator


_GENERATOR_MAP: Final[dict[str, tuple[str, str]]] = {
    'kodi': ('kodi.kodiGenerator', 'KodiGenerator'),
    'libretro': ('libretro.libretroGenerator', 'LibretroGenerator'),
    'moonlight': ('moonlight.moonlightGenerator', 'MoonlightGenerator'),
    'scummvm': ('scummvm.scummvmGenerator', 'ScummVMGenerator'),
    'dosbox': ('dosbox.dosboxGenerator', 'DosBoxGenerator'),
    'dosbox_staging': ('dosboxstaging.dosboxstagingGenerator', 'DosBoxStagingGenerator'),
    'dosboxx': ('dosboxx.dosboxxGenerator', 'DosBoxxGenerator'),
    'mupen64plus': ('mupen.mupenGenerator', 'MupenGenerator'),
    'vice': ('vice.viceGenerator', 'ViceGenerator'),
    'fsuae': ('fsuae.fsuaeGenerator', 'FsuaeGenerator'),
    'amiberry': ('amiberry.amiberryGenerator', 'AmiberryGenerator'),
    'flycast': ('flycast.flycastGenerator', 'FlycastGenerator'),
    'dolphin': ('dolphin.dolphinGenerator', 'DolphinGenerator'),
    'dolphin_triforce': ('dolphin_triforce.dolphinTriforceGenerator', 'DolphinTriforceGenerator'),
    'pcsx2': ('pcsx2.pcsx2Generator', 'Pcsx2Generator'),
    'ppsspp': ('ppsspp.ppssppGenerator', 'PPSSPPGenerator'),
    'citra' : ('citra.citraGenerator', 'CitraGenerator'),
    'hypseus-singe' : ('hypseus_singe.hypseusSingeGenerator', 'HypseusSingeGenerator'),
    'cannonball' : ('cannonball.cannonballGenerator', 'CannonballGenerator'),
    'sdlpop' : ('sdlpop.sdlpopGenerator', 'SdlPopGenerator'),
    'openbor' : ('openbor.openborGenerator', 'OpenborGenerator'),
    'wine' : ('wine.wineGenerator', 'WineGenerator'),
    'cemu' : ('cemu.cemuGenerator', 'CemuGenerator'),
    'melonds' : ('melonds.melondsGenerator', 'MelonDSGenerator'),
    'rpcs3' : ('rpcs3.rpcs3Generator', 'Rpcs3Generator'),
    'mame' : ('mame.mameGenerator', 'MameGenerator'),
    'pygame': ('pygame.pygameGenerator', 'PygameGenerator'),
    'devilutionx': ('devilutionx.devilutionxGenerator', 'DevilutionXGenerator'),
    'hatari': ('hatari.hatariGenerator', 'HatariGenerator'),
    'solarus': ('solarus.solarusGenerator', 'SolarusGenerator'),
    'easyrpg': ('easyrpg.easyrpgGenerator', 'EasyRPGGenerator'),
    'redream': ('redream.redreamGenerator', 'RedreamGenerator'),
    'supermodel': ('supermodel.supermodelGenerator', 'SupermodelGenerator'),
    'xash3d_fwgs': ('xash3d_fwgs.xash3dFwgsGenerator', 'Xash3dFwgsGenerator'),
    'tsugaru': ('tsugaru.tsugaruGenerator', 'TsugaruGenerator'),
    'mugen': ('mugen.mugenGenerator', 'MugenGenerator'),
    'fpinball': ('fpinball.fpinballGenerator', 'FpinballGenerator'),
    'lightspark': ('lightspark.lightsparkGenerator', 'LightsparkGenerator'),
    'ruffle': ('ruffle.ruffleGenerator', 'RuffleGenerator'),
    'duckstation': ('duckstation.duckstationGenerator', 'DuckstationGenerator'),
    'duckstation-legacy': ('duckstation_legacy.duckstationLegacyGenerator', 'DuckstationLegacyGenerator'),
    'drastic': ('drastic.drasticGenerator', 'DrasticGenerator'),
    'xemu': ('xemu.xemuGenerator', 'XemuGenerator'),
    'cgenius': ('cgenius.cgeniusGenerator', 'CGeniusGenerator'),
    'flatpak': ('flatpak.flatpakGenerator', 'FlatpakGenerator'),
    'steam': ('steam.steamGenerator', 'SteamGenerator'),
    'ecwolf': ('ecwolf.ecwolfGenerator', 'ECWolfGenerator'),
    'lexaloffle': ('lexaloffle.lexaloffleGenerator', 'LexaloffleGenerator'),
    'model2emu': ('model2emu.model2emuGenerator', 'Model2EmuGenerator'),
    'sonic2013': ('sonicretro.sonicretroGenerator', 'SonicRetroGenerator'),
    'soniccd': ('sonicretro.sonicretroGenerator', 'SonicRetroGenerator'),
    'gsplus': ('gsplus.gsplusGenerator', 'GSplusGenerator'),
    'fba2x': ('fba2x.fba2xGenerator', 'Fba2xGenerator'),
    'suyu': ('suyu.suyuGenerator', 'SuyuGenerator'),
    'ryujinx': ('ryujinx.ryujinxGenerator', 'RyujinxGenerator'),
    'samcoupe': ('samcoupe.samcoupeGenerator', 'SamcoupeGenerator'),
    'abuse': ('abuse.abuseGenerator', 'AbuseGenerator'),
    'cdogs': ('cdogs.cdogsGenerator', 'CdogsGenerator'),
    'hcl': ('hcl.hclGenerator', 'HclGenerator'),
    'hurrican': ('hurrican.hurricanGenerator', 'HurricanGenerator'),
    'tyrian': ('tyrian.tyrianGenerator', 'TyrianGenerator'),
    'openjazz': ('openjazz.openjazzGenerator', 'OpenJazzGenerator'),
    'openmsx': ('openmsx.openmsxGenerator', 'OpenmsxGenerator'),
    'xenia': ('xenia.xeniaGenerator', 'XeniaGenerator'),
    'xenia-canary': ('xenia.xeniaGenerator', 'XeniaGenerator'),
    'odcommander': ('odcommander.odcommanderGenerator', 'OdcommanderGenerator'),
    'gzdoom': ('gzdoom.gzdoomGenerator', 'GZDoomGenerator'),
    'eduke32': ('eduke32.eduke32Generator', 'EDuke32Generator'),
    'raze': ('raze.razeGenerator', 'RazeGenerator'),
    'vita3k': ('vita3k.vita3kGenerator', 'Vita3kGenerator'),
    'ikemen': ('ikemen.ikemenGenerator', 'IkemenGenerator'),
    'bigpemu': ('bigpemu.bigpemuGenerator', 'BigPEmuGenerator'),
    'pyxel': ('pyxel.pyxelGenerator', 'PyxelGenerator'),
    'play': ('play.playGenerator', 'PlayGenerator'),
    'ioquake3': ('ioquake3.ioquake3Generator', 'IOQuake3Generator'),
    'thextech': ('thextech.thextechGenerator', 'TheXTechGenerator'),
    'vpinball': ('vpinball.vpinballGenerator', 'VPinballGenerator'),
    'applewin': ('applewin.applewinGenerator', 'AppleWinGenerator'),
    'corsixth': ('corsixth.corsixthGenerator', 'CorsixTHGenerator'),
    'stella': ('stella.stellaGenerator', 'StellaGenerator'),
    'theforceengine': ('theforceengine.theforceengineGenerator', 'TheForceEngineGenerator'),
    'iortcw': ('iortcw.iortcwGenerator', 'IORTCWGenerator'),
    'fallout1-ce': ('fallout1.fallout1Generator', 'Fallout1Generator'),
    'fallout2-ce': ('fallout2.fallout2Generator', 'Fallout2Generator'),
    'dxx-rebirth': ('dxx_rebirth.dxx_rebirthGenerator', 'DXX_RebirthGenerator'),
    'etlegacy': ('etlegacy.etlegacyGenerator', 'ETLegacyGenerator'),
    'sonic3-air': ('sonic3_air.sonic3_airGenerator', 'Sonic3AIRGenerator'),
    'sonic-mania': ('sonic_mania.sonic_maniaGenerator', 'SonicManiaGenerator'),
    'uqm': ('uqm.uqmGenerator', 'UqmGenerator'),
    'taradino': ('taradino.taradinoGenerator', 'TaradinoGenerator'),
    'x16emu': ('x16emu.x16emuGenerator', 'X16emuGenerator'),
    'shadps4' : ('shadps4.shadps4Generator', 'shadPS4Generator'),
    'dhewm3' : ('dhewm3.dhewm3Generator', 'Dhewm3Generator'),
    'sh': ('sh.shGenerator', 'ShGenerator'),
}


def get_generator(emulator: str) -> Generator:
    if emulator in _GENERATOR_MAP:
        module_path, cls_name = _GENERATOR_MAP[emulator]
    else:
        module_path = f'{emulator}.{emulator}Generator'
        cls_name = f'{emulator[0].upper()}{emulator[1:]}Generator'

    try:
        module = import_module(f'..{module_path}', package=__name__)
        generator_cls: type[Generator] = getattr(module, cls_name)
    except ImportError as e:
        if e.name is not None and e.name.startswith(__name__.split('.')[0]):
            raise Exception(f'no generator found for emulator {emulator}') from e
        else:
            raise
    except AttributeError as e:
        raise Exception(f'no generator found for emulator {emulator}') from e

    return generator_cls()
