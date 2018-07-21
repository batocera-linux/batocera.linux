#!/usr/bin/env python

esInputs = '/recalbox/share/system/.emulationstation/es_input.cfg'
esSettings = '/recalbox/share/system/.emulationstation/es_settings.cfg'
recalboxConf = '/recalbox/share/system/recalbox.conf'

retroarchRoot = '/recalbox/share/system/configs/retroarch'
retroarchRootInit = '/recalbox/share_init/system/configs/retroarch'
retroarchCustom = retroarchRoot + '/retroarchcustom.cfg'
retroarchCustomOrigin = retroarchRootInit + "/retroarchcustom.cfg"
retroarchCoreCustom = retroarchRoot + "/cores/retroarch-core-options.cfg"

retroarchBin = "retroarch"
retroarchCores = "/usr/lib/libretro/"
shadersRoot = "/recalbox/share_init/shaders/presets/"
shadersExt = '.gplsp'
libretroExt = '_libretro.so'

fbaRoot = '/recalbox/share/system/configs/fba/'
fbaCustom = fbaRoot + 'fba2x.cfg'
fbaCustomOrigin = fbaRoot + 'fba2x.cfg.origin'
fba2xBin = '/usr/bin/fba2x'

mupenCustom = "/recalbox/share/system/configs/mupen64/mupen64plus.cfg"

shaderPresetRoot = "/recalbox/share/system/configs/shadersets/"

kodiJoystick = '/recalbox/share/system/.kodi/userdata/keymaps/recalbox.xml'
kodiMapping  = '/recalbox/share/system/configs/kodi/input.xml'

kodiBin  = '/recalbox/scripts/kodilauncher.sh'

logdir = '/recalbox/share/system/logs/'
