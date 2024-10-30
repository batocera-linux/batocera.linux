from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .Generator import Generator


_GENERATOR_MAP: Final[dict[str, tuple[str, str]]] = {
    'scummvm': ('scummvm.scummvmGenerator', 'ScummVMGenerator'),
    'dosbox': ('dosbox.dosboxGenerator', 'DosBoxGenerator'),
    'dosbox_staging': ('dosboxstaging.dosboxstagingGenerator', 'DosBoxStagingGenerator'),
    'dosboxx': ('dosboxx.dosboxxGenerator', 'DosBoxxGenerator'),
    'mupen64plus': ('mupen.mupenGenerator', 'MupenGenerator'),
    'dolphin_triforce': ('dolphin_triforce.dolphinTriforceGenerator', 'DolphinTriforceGenerator'),
    'ppsspp': ('ppsspp.ppssppGenerator', 'PPSSPPGenerator'),
    'hypseus-singe': ('hypseus_singe.hypseusSingeGenerator', 'HypseusSingeGenerator'),
    'sdlpop': ('sdlpop.sdlpopGenerator', 'SdlPopGenerator'),
    'melonds': ('melonds.melondsGenerator', 'MelonDSGenerator'),
    'devilutionx': ('devilutionx.devilutionxGenerator', 'DevilutionXGenerator'),
    'easyrpg': ('easyrpg.easyrpgGenerator', 'EasyRPGGenerator'),
    'xash3d_fwgs': ('xash3d_fwgs.xash3dFwgsGenerator', 'Xash3dFwgsGenerator'),
    'duckstation-legacy': ('duckstation_legacy.duckstationLegacyGenerator', 'DuckstationLegacyGenerator'),
    'cgenius': ('cgenius.cgeniusGenerator', 'CGeniusGenerator'),
    'ecwolf': ('ecwolf.ecwolfGenerator', 'ECWolfGenerator'),
    'model2emu': ('model2emu.model2emuGenerator', 'Model2EmuGenerator'),
    'sonic2013': ('sonicretro.sonicretroGenerator', 'SonicRetroGenerator'),
    'soniccd': ('sonicretro.sonicretroGenerator', 'SonicRetroGenerator'),
    'gsplus': ('gsplus.gsplusGenerator', 'GSplusGenerator'),
    'openjazz': ('openjazz.openjazzGenerator', 'OpenJazzGenerator'),
    'xenia-canary': ('xenia.xeniaGenerator', 'XeniaGenerator'),
    'gzdoom': ('gzdoom.gzdoomGenerator', 'GZDoomGenerator'),
    'eduke32': ('eduke32.eduke32Generator', 'EDuke32Generator'),
    'bigpemu': ('bigpemu.bigpemuGenerator', 'BigPEmuGenerator'),
    'ioquake3': ('ioquake3.ioquake3Generator', 'IOQuake3Generator'),
    'thextech': ('thextech.thextechGenerator', 'TheXTechGenerator'),
    'vpinball': ('vpinball.vpinballGenerator', 'VPinballGenerator'),
    'applewin': ('applewin.applewinGenerator', 'AppleWinGenerator'),
    'corsixth': ('corsixth.corsixthGenerator', 'CorsixTHGenerator'),
    'theforceengine': ('theforceengine.theforceengineGenerator', 'TheForceEngineGenerator'),
    'iortcw': ('iortcw.iortcwGenerator', 'IORTCWGenerator'),
    'fallout1-ce': ('fallout1.fallout1Generator', 'Fallout1Generator'),
    'fallout2-ce': ('fallout2.fallout2Generator', 'Fallout2Generator'),
    'dxx-rebirth': ('dxx_rebirth.dxx_rebirthGenerator', 'DXX_RebirthGenerator'),
    'etlegacy': ('etlegacy.etlegacyGenerator', 'ETLegacyGenerator'),
    'sonic3-air': ('sonic3_air.sonic3_airGenerator', 'Sonic3AIRGenerator'),
    'sonic-mania': ('sonic_mania.sonic_maniaGenerator', 'SonicManiaGenerator'),
    'shadps4': ('shadps4.shadps4Generator', 'shadPS4Generator'),
    'jazz2-native': ('jazz2_native.jazz2_nativeGenerator', 'Jazz2_NativeGenerator'),
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
