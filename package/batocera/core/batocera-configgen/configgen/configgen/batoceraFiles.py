#!/usr/bin/env python
HOME_INIT = '/usr/share/batocera/datainit/system/'
HOME = '/userdata/system'
CONF_INIT = HOME_INIT + '/configs'
CONF = HOME + '/configs'
SAVES = '/userdata/saves'
SCREENSHOTS = '/userdata/screenshots'
BIOS = '/userdata/bios'
OVERLAYS = '/userdata/overlays'
CACHE = '/userdata/system/cache'
ROMS = '/userdata/roms'

esInputs = CONF + '/emulationstation/es_input.cfg'
esSettings = CONF + '/emulationstation/es_settings.cfg'
batoceraConf = HOME + '/batocera.conf'
logdir = HOME + '/logs/'

# This dict is indexed on the emulator name, not on the system
batoceraBins = {'dosbox'      : '/usr/bin/dosbox'
              , 'kodi'        : '/usr/bin/batocera-kodilauncher'
              , 'libretro'    : '/usr/bin/retroarch'
              , 'linapple'    : '/usr/bin/linapple'
              , 'moonlight'   : '/usr/bin/moonlight'
              , 'mupen64plus' : '/usr/bin/mupen64plus'
              , 'ppsspp'      : '/usr/bin/PPSSPPSDL'
              , 'reicast'     : '/usr/bin/reicast.elf'
              , 'scummvm'     : '/usr/bin/scummvm'
              , 'vice'        : '/usr/bin/'
              , 'fsuae'       : '/usr/bin/fs-uae'
              , 'amiberry'    : '/usr/bin/amiberry'
              , 'dolphin'     : '/usr/bin/dolphin-emu'
              , 'pcsx2'       : '/usr/PCSX/bin/PCSX2'
              , 'pcsx2_avx2'  : '/usr/PCSX_AVX2/bin/PCSX2'
              , 'citra'       : '/usr/bin/citra-qt'
              , 'daphne'       : '/usr/bin/hypseus'
}


retroarchRoot = CONF + '/retroarch'
retroarchRootInit = CONF_INIT + '/retroarch'
retroarchCustom = retroarchRoot + '/retroarchcustom.cfg'
retroarchCoreCustom = retroarchRoot + "/cores/retroarch-core-options.cfg"

retroarchCores = "/usr/lib/libretro/"
libretroExt = '_libretro.so'
screenshotsDir = "/userdata/screenshots/"
savesDir = "/userdata/saves/"

mupenConf = CONF + '/mupen64/'
mupenCustom = mupenConf + "mupen64plus.cfg"
mupenInput = mupenConf + "InputAutoCfg.ini"
mupenSaves = SAVES + "/n64"
mupenMappingUser    = mupenConf + 'input.xml'
mupenMappingSystem  = '/usr/share/batocera/datainit/system/configs/mupen64/input.xml'

kodiJoystick = HOME + '/.kodi/userdata/addon_data/peripheral.joystick/resources/buttonmaps/xml/linux/batocera_{}.xml'

moonlightCustom = CONF+'/moonlight'
moonlightConfig = moonlightCustom + '/moonlight.conf'
moonlightGamelist = moonlightCustom + '/gamelist.txt'
moonlightMapping = dict()
moonlightMapping[1] = moonlightCustom + '/mappingP1.conf'
moonlightMapping[2] = moonlightCustom + '/mappingP2.conf'
moonlightMapping[3] = moonlightCustom + '/mappingP3.conf'
moonlightMapping[4] = moonlightCustom + '/mappingP4.conf'

reicastCustom = CONF + '/reicast'
reicastMapping = reicastCustom + '/mappings'
reicastConfig = reicastCustom + '/emu.cfg'
reicastSaves = SAVES + '/dreamcast'
reicastBios = BIOS
reicastVMUBlank = '/usr/lib/python2.7/site-packages/configgen/datainit/reicast/vmu_save_blank.bin'
reicastVMUA1 = reicastSaves + '/reicast/vmu_save_A1.bin'
reicastVMUA2 = reicastSaves + '/reicast/vmu_save_A2.bin'

dolphinConfig  = CONF + "/dolphin-emu"
dolphinData    = SAVES + "/dolphin-emu"
dolphinIni     = dolphinConfig + '/Dolphin.ini'
dolphinGfxIni  = dolphinConfig + '/GFX.ini'
dolphinSYSCONF = dolphinData + "/Wii/shared2/sys/SYSCONF"

pcsx2PluginsDir     = "/usr/PCSX/bin/plugins"
pcsx2Avx2PluginsDir = "/usr/PCSX_AVX2/bin/plugins"
pcsx2ConfigDir      = "/userdata/system/configs/PCSX2"

ppssppConf = CONF + '/ppsspp/PSP/SYSTEM'
ppssppControlsIni = ppssppConf + '/controls.ini'
ppssppControls = CONF + '/ppsspp/gamecontrollerdb.txt'
ppssppControlsInit = HOME_INIT + 'configs/ppsspp/PSP/SYSTEM/controls.ini'
ppssppConfig = ppssppConf + '/ppsspp.ini'

citraConfig = CONF + '/citra-emu/qt-config.ini'
citraSaves = SAVES + '/3ds'

dosboxCustom = CONF + '/dosbox'
dosboxConfig = dosboxCustom + '/dosbox.conf'

fsuaeBios = BIOS
fsuaeConfig = CONF + "/fs-uae"
fsuaeSaves = SAVES + "/amiga"

scummvmSaves = SAVES + '/scummvm'

viceConfig = CONF + "/vice"

overlaySystem = "/usr/share/batocera/datainit/decorations"
overlayUser = "/userdata/decorations"
overlayConfigFile = "/userdata/system/configs/retroarch/overlay.cfg"

amiberryRoot = CONF + '/amiberry'
amiberryRetroarchInputsDir = amiberryRoot + '/conf/retroarch/inputs'
amiberryRetroarchCustom = amiberryRoot + '/conf/retroarch/retroarchcustom.cfg'

hatariConf = CONF + '/hatari/hatari.cfg'

daphneConfig = CONF + '/daphne/hypinput.ini'
daphneHomedir = ROMS + '/daphne'
daphneDatadir = '/usr/share/daphne'
daphneSaves = SAVES + '/daphne'