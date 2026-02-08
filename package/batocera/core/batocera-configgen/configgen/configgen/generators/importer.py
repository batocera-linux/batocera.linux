from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Final

from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from .Generator import Generator


_GENERATOR_MAP: Final[dict[str, tuple[str, str]]] = {
    'applewin': ('applewin.applewinGenerator', 'AppleWinGenerator'),
    'bigpemu': ('bigpemu.bigpemuGenerator', 'BigPEmuGenerator'),
    'bstone': ('bstone.bstoneGenerator', 'BstoneGenerator'),
    'catacombgl': ('catacombgl.catacombglGenerator', 'CatacombGLGenerator'),
    'cgenius': ('cgenius.cgeniusGenerator', 'CGeniusGenerator'),
    'clk': ('clk.clkGenerator', 'ClkGenerator'),
    'corsixth': ('corsixth.corsixthGenerator', 'CorsixTHGenerator'),
    'devilutionx': ('devilutionx.devilutionxGenerator', 'DevilutionXGenerator'),
    'dhewm3': ('dhewm3.dhewm3Generator', 'Dhewm3Generator'),
    'dolphin_triforce': ('dolphin_triforce.dolphinTriforceGenerator', 'DolphinTriforceGenerator'),
    'dosbox': ('dosbox.dosboxGenerator', 'DosBoxGenerator'),
    'dosbox_staging': ('dosboxstaging.dosboxstagingGenerator', 'DosBoxStagingGenerator'),
    'dosboxx': ('dosboxx.dosboxxGenerator', 'DosBoxxGenerator'),
    'duckstation-legacy': ('duckstation_legacy.duckstationLegacyGenerator', 'DuckstationLegacyGenerator'),
    'dxx-rebirth': ('dxx_rebirth.dxx_rebirthGenerator', 'DXX_RebirthGenerator'),
    'easyrpg': ('easyrpg.easyrpgGenerator', 'EasyRPGGenerator'),
    'ecwolf': ('ecwolf.ecwolfGenerator', 'ECWolfGenerator'),
    'eduke32': ('eduke32.eduke32Generator', 'EDuke32Generator'),
    'flycast': ('flycast.flycastGenerator', 'FlycastGenerator'),
    'fsuae': ('fsuae.fsuaeGenerator', 'FsuAEGenerator'),
    'gsplus': ('gsplus.gsplusGenerator', 'GSplusGenerator'),
    'hatarib': ('hatarib.hataribGenerator', 'HataribGenerator'),
    'hypseus-singe': ('hypseus_singe.hypseusSingeGenerator', 'HypseusSingeGenerator'),
    'iortcw': ('iortcw.iortcwGenerator', 'IOrtcWGenerator'),
    'ioquake3': ('ioquake3.ioquake3Generator', 'IOQuake3Generator'),
    'jzintv': ('jzintv.jzintvGenerator', 'JzIntvGenerator'),
    'lightspark': ('lightspark.lightsparkGenerator', 'LightsparkGenerator'),
    'melonds': ('melonds.melondsGenerator', 'MelonDSGenerator'),
    'model2emu': ('model2emu.model2emuGenerator', 'Model2EmuGenerator'),
    'mupen64plus': ('mupen.mupenGenerator', 'MupenGenerator'),
    'openbor': ('openbor.openborGenerator', 'OpenBORGenerator'),
    'opentyrian': ('opentyrian.opentyrianGenerator', 'OpenTyrianGenerator'),
    'ppsspp': ('ppsspp.ppssppGenerator', 'PPSSPPGenerator'),
    'redream': ('redream.redreamGenerator', 'RedreamGenerator'),
    'retroarch': ('libretro.libretroGenerator', 'LibretroGenerator'),
    'ryujinx': ('ryujinx.ryujinxGenerator', 'RyujinxGenerator'),
    'scummvm': ('scummvm.scummvmGenerator', 'ScummVMGenerator'),
    'sdlpop': ('sdlpop.sdlpopGenerator', 'SdlPopGenerator'),
    'snes9x': ('snes9x.snes9xGenerator', 'Snes9xGenerator'),
    'sonic2013': ('sonicretro.sonicretroGenerator', 'SonicRetroGenerator'),
    'sonic3-air': ('sonic3_air.sonic3_airGenerator', 'Sonic3AIRGenerator'),
    'soniccd': ('sonicretro.sonicretroGenerator', 'SonicRetroGenerator'),
    'supermodel-legacy': ('supermodel_legacy.supermodelLegacyGenerator', 'SupermodelLegacyGenerator'),
    'theforceengine': ('theforceengine.theforceengineGenerator', 'TheForceEngineGenerator'),
    'thextech': ('thextech.thextechGenerator', 'TheXTechGenerator'),
    'tr1x': ('tr1x.tr1xGenerator', 'TR1XGenerator'),
    'tr2x': ('tr2x.tr2xGenerator', 'TR2XGenerator'),
    'vkquake': ('vkquake.vkquakeGenerator', 'VKQuakeGenerator'),
    'vkquake2': ('vkquake2.vkquake2Generator', 'VKQuake2Generator'),
    'vkquake3': ('ioquake3.ioquake3Generator', 'IOQuake3Generator'),
    'vpinball': ('vpinball.vpinballGenerator', 'VPinballGenerator'),
    'xash3d_fwgs': ('xash3d_fwgs.xash3dFwgsGenerator', 'Xash3dFwgsGenerator'),
    'xenia-canary': ('xenia.xeniaGenerator', 'XeniaGenerator'),
    'ymir': ('ymir.ymirGenerator', 'YmirGenerator'),
    'yquake2': ('yquake2.yquake2Generator', 'YQuake2Generator'),
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
            raise BatoceraException(f'No generator found for emulator {emulator}') from e

        raise BatoceraException(f'Error importing generator for emulator {emulator}') from e
    except AttributeError as e:
        raise BatoceraException(f'No generator found for emulator {emulator}') from e

    return generator_cls()
