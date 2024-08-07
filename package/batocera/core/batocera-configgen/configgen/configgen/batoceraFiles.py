#!/usr/bin/env python

HOME_INIT = '/usr/share/batocera/datainit/system/'
HOME = '/userdata/system'
CONF_INIT = HOME_INIT + '/configs'
CONF = HOME + '/configs'
EVMAPY = CONF + '/evmapy'
SAVES = '/userdata/saves'
SCREENSHOTS = '/userdata/screenshots'
RECORDINGS = '/userdata/recordings'
BIOS = '/userdata/bios'
OVERLAYS = '/userdata/overlays'
CACHE = '/userdata/system/cache'
ROMS = '/userdata/roms'

esInputs = CONF + '/emulationstation/es_input.cfg'
esSettings = CONF + '/emulationstation/es_settings.cfg'
esGunsMetadata = "/usr/share/emulationstation/resources/gungames.xml"
esWheelsMetadata = "/usr/share/emulationstation/resources/wheelgames.xml"
esGamesMetadata = "/usr/share/emulationstation/resources/gamesdb.xml"
batoceraConf = HOME + '/batocera.conf'
logdir = HOME + '/logs/'

# This dict is indexed on the emulator name, not on the system
batoceraBins = {'dosbox'         : '/usr/bin/dosbox'
              , 'dosbox_staging' : '/usr/bin/dosbox-staging'
              , 'dosboxx'        : '/usr/bin/dosbox-x'
              , 'kodi'           : '/usr/bin/batocera-kodilauncher'
              , 'libretro'       : '/usr/bin/retroarch'
              , 'moonlight'      : '/usr/bin/moonlight'
              , 'mupen64plus'    : '/usr/bin/mupen64plus'
              , 'flycast'        : '/usr/bin/flycast'
              , 'scummvm'        : '/usr/bin/scummvm'
              , 'vice'           : '/usr/bin/'
              , 'fsuae'          : '/usr/bin/fs-uae'
              , 'amiberry'       : '/usr/bin/amiberry'
              , 'hypseus-singe'  : '/usr/bin/hypseus'
              , 'melonds'        : '/usr/bin/melonDS'
              , 'rpcs3'          : '/usr/bin/rpcs3'
              , 'hatari'         : '/usr/bin/hatari'
              , 'supermodel'     : '/usr/bin/supermodel'
              , 'tsugaru'        : '/usr/bin/Tsugaru_CUI'
              , 'xemu'           : '/usr/bin/xemu'
              , 'gsplus'         : '/usr/bin/GSplus'
              , 'applewin'       : '/usr/bin/applewin'
              , 'fba2x'          : '/usr/bin/fba2x'
}


retroarchRoot = CONF + '/retroarch'
retroarchRootInit = CONF_INIT + '/retroarch'
retroarchCustom = retroarchRoot + '/retroarchcustom.cfg'
retroarchCoreCustom = retroarchRoot + "/cores/retroarch-core-options.cfg"

retroarchCores = "/usr/lib/libretro/"
screenshotsDir = "/userdata/screenshots/"
savesDir = "/userdata/saves/"

mupenConf = CONF + '/mupen64/'
mupenCustom = mupenConf + "mupen64plus.cfg"
mupenInput = mupenConf + "InputAutoCfg.ini"
mupenSaves = SAVES + "/n64"
mupenMappingUser    = mupenConf + 'input.xml'
mupenMappingSystem  = '/usr/share/batocera/datainit/system/configs/mupen64/input.xml'

moonlightCustom = CONF + '/moonlight'
moonlightConfigFile = moonlightCustom + '/moonlight.conf'
moonlightStagingConfigFile = moonlightCustom + '/staging/moonlight.conf'
moonlightGamelist = moonlightCustom + '/gamelist.txt'
moonlightMapping = dict()
moonlightMapping[1] = moonlightCustom + '/mappingP1.conf'
moonlightMapping[2] = moonlightCustom + '/mappingP2.conf'
moonlightMapping[3] = moonlightCustom + '/mappingP3.conf'
moonlightMapping[4] = moonlightCustom + '/mappingP4.conf'

dolphinConfig  = CONF + "/dolphin-emu"
dolphinData    = SAVES + "/dolphin-emu"
dolphinIni     = dolphinConfig + '/Dolphin.ini'
dolphinGfxIni  = dolphinConfig + '/GFX.ini'
dolphinSYSCONF = dolphinData + "/Wii/shared2/sys/SYSCONF"

dolphinTriforceConfig  = CONF + "/dolphin-triforce"
dolphinTriforceData    = SAVES + "/dolphin-triforce"
dolphinTriforceIni     = dolphinTriforceConfig + '/Config/Dolphin.ini'
dolphinTriforceGfxIni  = dolphinTriforceConfig + '/Config/gfx_opengl.ini'
dolphinTriforceLoggerIni    = dolphinTriforceConfig + '/Config/Logger.ini'
dolphinTriforceGameSettings = dolphinTriforceConfig + "/GameSettings"

dosboxCustom = CONF + '/dosbox'
dosboxConfig = dosboxCustom + '/dosbox.conf'

dosboxStagingCustom = CONF + '/dosbox'
dosboxStagingConfig = dosboxStagingCustom + '/dosbox.conf'

dosboxxCustom = CONF + '/dosbox'
dosboxxConfig = dosboxxCustom + '/dosboxx.conf'

fsuaeBios = BIOS + "/amiga"
fsuaeConfig = CONF + "/fs-uae"
fsuaeSaves = SAVES + "/amiga"

scummvmSaves = SAVES + '/scummvm'

solarusSaves = SAVES + '/solarus'

viceConfig = CONF + "/vice"

overlaySystem = "/usr/share/batocera/datainit/decorations"
overlayUser = "/userdata/decorations"
overlayConfigFile = "/userdata/system/configs/retroarch/overlay.cfg"

amiberryRoot = CONF + '/amiberry'
amiberryRetroarchInputsDir = amiberryRoot + '/conf/retroarch/inputs'
amiberryRetroarchCustom = amiberryRoot + '/conf/retroarch/retroarchcustom.cfg'

hatariConf = CONF + '/hatari/hatari.cfg'

daphneRomdir = ROMS + '/daphne'
singeRomdir = ROMS + '/singe'
hypseusDatadir = CONF + '/hypseus-singe'
hypseusConfig = hypseusDatadir+ '/hypinput.ini'
hypseusConfigfile = 'hypinput.ini'
hypseusSaves = SAVES + '/hypseus'

flycastCustom = CONF + '/flycast'
flycastMapping = flycastCustom + '/mappings'
flycastConfig = flycastCustom + '/emu.cfg'
flycastSaves = SAVES + '/dreamcast'
flycastBios = BIOS + '/dc'
flycastVMUBlank = '/usr/share/batocera/configgen/data/dreamcast/vmu_save_blank.bin'
flycastVMUA1 = flycastSaves + '/flycast/vmu_save_A1.bin'
flycastVMUA2 = flycastSaves + '/flycast/vmu_save_A2.bin'

rpcs3Config = CONF
rpcs3Homedir = ROMS + '/ps3'
rpcs3Saves = SAVES
rpcs3CurrentConfig = CONF + '/rpcs3/GuiConfigs/CurrentSettings.ini'
rpcs3config = CONF + '/rpcs3/config.yml'
rpcs3configInput = CONF + '/rpcs3/config_input.yml'
rpcs3configevdev = CONF + '/rpcs3/InputConfigs/Evdev/Default Profile.yml'

supermodelCustom = CONF + '/supermodel'
supermodelIni = supermodelCustom + '/Supermodel.ini'

xemuConfig = CONF + '/xemu/xemu.toml'

sdlpopConfigDir = CONF + '/sdlpop'
sdlpopSrcCfg = sdlpopConfigDir + '/SDLPoP.cfg'
sdlpopSrcIni = sdlpopConfigDir + '/SDLPoP.ini'
sdlpopDestCfg = '/usr/share/sdlpop/SDLPoP.cfg'
sdlpopDestIni = '/usr/share/sdlpop/SDLPoP.ini'
