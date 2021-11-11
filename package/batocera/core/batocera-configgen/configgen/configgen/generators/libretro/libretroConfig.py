#!/usr/bin/env python
import sys
import os
import batoceraFiles
from . import libretroOptions
from Emulator import Emulator
import settings
from settings.unixSettings import UnixSettings
import json
from utils.logger import get_logger
from PIL import Image, ImageOps
import utils.bezels as bezelsUtil

eslog = get_logger(__name__)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# return true if the option is considered defined
def defined(key, dict):
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0


# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L132
ratioIndexes = ["4/3", "16/9", "16/10", "16/15", "21/9", "1/1", "2/1", "3/2", "3/4", "4/1", "4/4", "5/4", "6/5", "7/9", "8/3",
                "8/7", "19/12", "19/14", "30/17", "32/9", "config", "squarepixel", "core", "custom", "full"]

# Define system emulated by bluemsx core
systemToBluemsx = {'msx': '"MSX2"', 'msx1': '"MSX2"', 'msx2': '"MSX2"', 'colecovision': '"COL - ColecoVision"' };

# Define systems compatible with retroachievements
systemToRetroachievements = {'atari2600', 'atari7800', 'jaguar', 'colecovision', 'nes', 'snes', 'virtualboy', 'n64', 'sg1000', 'mastersystem', 'megadrive', 'segacd', 'sega32x', 'saturn', 'pcengine', 'pcenginecd', 'supergrafx', 'psx', 'mame', 'fbneo', 'neogeo', 'lightgun', 'apple2', 'lynx', 'wswan', 'wswanc', 'gb', 'gbc', 'gba', 'sgb', 'nds', 'pokemini', 'gamegear', 'ngp', 'ngpc', 'supervision', 'sufami', 'pc88', 'pcfx', '3do', 'intellivision', 'odyssey2', 'vectrex', 'wonderswan', 'psp', 'snes-msu1', 'satellaview'};

# Define Retroarch Core compatible with retroachievements
# List taken from https://docs.libretro.com/guides/retroachievements/#cores-compatibility
coreToRetroachievements = {'beetle-saturn', 'blastem', 'bluemsx', 'bsnes', 'bsnes_hd', 'desmume', 'duckstation', 'fbneo', 'fceumm', 'freeintv', 'gambatte', 'genesisplusgx', 'genesisplusgx-wide', 'handy', 'kronos', 'mednafen_lynx', 'mednafen_ngp', 'mednafen_psx', 'mednafen_supergrafx', 'mednafen_wswan', 'melonds', 'mesens', 'mgba', 'mupen64plus-next', 'nestopia', 'o2em', 'opera', 'parallel_n64', 'pce', 'pce_fast', 'pcfx', 'pcsx_rearmed', 'picodrive', 'pokemini', 'potator', 'ppsspp', 'prosystem', 'quasi88', 'snes9x', 'snes9x_next', 'stella', 'stella2014', 'swanstation', 'vb', 'vba-m', 'vecx', 'virtualjaguar'}

# Define systems NOT compatible with rewind option
systemNoRewind = {'sega32x', 'psx', 'zxspectrum', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'saturn'};
# 'odyssey2', 'mame', 'neogeocd', 'fbneo'

# Define systems NOT compatible with run-ahead option (warning: this option is CPU intensive!)
systemNoRunahead = {'sega32x', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'neogeocd', 'saturn'};

# Define the libretro device type corresponding to the libretro CORE (when needed)
coreToP1Device = {'atari800': '513', 'cap32': '513', '81': '259', 'fuse': '769'};
coreToP2Device = {'atari800': '513', 'fuse': '513'};

# Define the libretro device type corresponding to the libretro SYSTEM (when needed)
systemToP1Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };
systemToP2Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };

# Netplay modes
systemNetplayModes = {'host', 'client', 'spectator'}

# Cores that require .slang shaders (even on OpenGL, not only Vulkan)
coreForceSlangShaders = { 'mupen64plus-next' }

def writeLibretroConfig(retroconfig, system, controllers, rom, bezel, gameResolution):
    writeLibretroConfigToFile(retroconfig, createLibretroConfig(system, controllers, rom, bezel, gameResolution))

# Take a system, and returns a dict of retroarch.cfg compatible parameters
def createLibretroConfig(system, controllers, rom, bezel, gameResolution):

    # retroarch-core-options.cfg
    retroarchCore = batoceraFiles.retroarchCoreCustom
    if not os.path.exists(os.path.dirname(retroarchCore)):
        os.makedirs(os.path.dirname(retroarchCore))

    try:
        coreSettings = UnixSettings(retroarchCore, separator=' ')
    except UnicodeError:
        # invalid retroarch-core-options.cfg
        # remove it and try again
        os.remove(retroarchCore)
        coreSettings = UnixSettings(retroarchCore, separator=' ')

    # Create/update retroarch-core-options.cfg
    libretroOptions.generateCoreSettings(coreSettings, system, rom)

    # Create/update hatari.cfg
    if system.name == 'atarist':
        libretroOptions.generateHatariConf(batoceraFiles.hatariConf)

    retroarchConfig = dict()
    systemConfig = system.config
    renderConfig = system.renderconfig

    # Basic configuration
    retroarchConfig['quit_press_twice'] = 'false'               # not aligned behavior on other emus
    retroarchConfig['menu_show_restart_retroarch'] = 'false'    # this option messes everything up on Batocera if ever clicked
    retroarchConfig['video_driver'] = '"gl"'                    # needed for the ozone menu
    retroarchConfig['audio_latency'] = '64'                     #best balance with audio perf
    if (system.isOptSet("audio_latency")):
        retroarchConfig['audio_latency'] = system.config['audio_latency']

    with open("/usr/share/batocera/batocera.arch") as fb:
        arch = fb.readline().strip()

    if (system.isOptSet("display.rotate") and arch not in [ 'x86_64', 'x86']):
        # 0 => 0 ; 1 => 270; 2 => 180 ; 3 => 90
        if system.config["display.rotate"] == "0":
            retroarchConfig['video_rotation'] = "0"
        elif system.config["display.rotate"] == "1":
            retroarchConfig['video_rotation'] = "3"
        elif system.config["display.rotate"] == "2":
            retroarchConfig['video_rotation'] = "2"
        elif system.config["display.rotate"] == "3":
            retroarchConfig['video_rotation'] = "1"
    else:
        retroarchConfig['video_rotation'] = '0'

    if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == "vulkan":
        retroarchConfig['video_driver'] = '"vulkan"'

    if system.isOptSet('video_threaded') and system.getOptBoolean('video_threaded') == True:
        retroarchConfig['video_threaded'] = 'true'
    else:
        retroarchConfig['video_threaded'] = 'false'

    # required at least for vulkan (to get the correct resolution)
    retroarchConfig['video_fullscreen_x'] = gameResolution["width"]
    retroarchConfig['video_fullscreen_y'] = gameResolution["height"]

    retroarchConfig['video_black_frame_insertion'] = 'false'    # don't use anymore this value while it doesn't allow the shaders to work
    retroarchConfig['pause_nonactive'] = 'false'                # required at least on x86 x86_64 otherwise, the game is paused at launch
    retroarchConfig['cache_directory'] = '/userdata/system/.cache'

    retroarchConfig['video_fullscreen'] = 'true'                # Fullscreen is required at least for x86* and odroidn2

    retroarchConfig['savestate_directory'] = batoceraFiles.savesDir + system.name
    retroarchConfig['savefile_directory'] = batoceraFiles.savesDir + system.name

    # Forced values (so that if the config is not correct, fix it)
    if system.config['core'] == 'tgbdual':
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("core")) # Reset each time in this function

    # Disable internal image viewer (ES does it, and pico-8 won't load .p8.png)
    retroarchConfig['builtin_imageviewer_enable'] = 'false'

    # Input configuration
    retroarchConfig['input_joypad_driver'] = 'udev'
    retroarchConfig['input_max_users'] = "16"                   # Allow up to 16 players

    retroarchConfig['input_libretro_device_p1'] = '1'           # Default devices choices
    retroarchConfig['input_libretro_device_p2'] = '1'

    # D-pad = Left analog stick forcing on PUAE and VICE (New D2A system on RA doesn't work with these cores.)
    if system.config['core'] == 'puae' or system.config['core'] == 'vice_x64':
        retroarchConfig['input_player1_analog_dpad_mode'] = '3'
        retroarchConfig['input_player2_analog_dpad_mode'] = '3'

    # force notification messages
    retroarchConfig['video_font_enable'] = '"true"'

    ## Specific choices
    if(system.config['core'] in coreToP1Device):
        retroarchConfig['input_libretro_device_p1'] = coreToP1Device[system.config['core']]
    if(system.config['core'] in coreToP2Device):
        retroarchConfig['input_libretro_device_p2'] = coreToP2Device[system.config['core']]

    ## AMIGA OCS-ECS/AGA/CD32
    if system.config['core'] == 'puae':
        if system.name != 'amigacd32':
            if system.isOptSet('controller1_puae'):
                retroarchConfig['input_libretro_device_p1'] = system.config['controller1_puae']
            else:
                retroarchConfig['input_libretro_device_p1'] = '1'
            if system.isOptSet('controller2_puae'):
                retroarchConfig['input_libretro_device_p2'] = system.config['controller2_puae']
            else:
                retroarchConfig['input_libretro_device_p2'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '517'     # CD 32 Pad

    ## BlueMSX choices by System
    if(system.name in systemToBluemsx):
        if system.config['core'] == 'bluemsx':
            retroarchConfig['input_libretro_device_p1'] = systemToP1Device[system.name]
            retroarchConfig['input_libretro_device_p2'] = systemToP2Device[system.name]

    ## SNES9x and SNES9x_next (2010) controller
    if system.config['core'] == 'snes9x' or system.config['core'] == 'snes9x_next':
        if system.isOptSet('controller1_snes9x'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_snes9x']
        elif system.isOptSet('controller1_snes9x_next'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_snes9x_next']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        # Player 2
        if system.isOptSet('controller2_snes9x'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_snes9x']
        elif system.isOptSet('controller2_snes9x_next'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_snes9x_next']
        elif len(controllers) > 2:                              # More than 2 controller connected
            retroarchConfig['input_libretro_device_p2'] = '257'
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
        # Player 3
        if system.isOptSet('Controller3_snes9x'):
            retroarchConfig['input_libretro_device_p3'] = system.config['Controller3_snes9x']
        else:
            retroarchConfig['input_libretro_device_p3'] = '1'

    ## NES controller
    if system.config['core'] == 'fceumm':
        if system.isOptSet('controller1_nes'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_nes']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        if system.isOptSet('controller2_nes'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_nes']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'

    ## PlayStation controller
    if (system.config['core'] == 'mednafen_psx'):               # Madnafen
        if system.isOptSet('beetle_psx_Controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['beetle_psx_Controller1']
            if system.config['beetle_psx_Controller1'] != '1':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        if system.isOptSet('beetle_psx_Controller2'):
            retroarchConfig['input_libretro_device_p2'] = system.config['beetle_psx_Controller2']
            if system.config['beetle_psx_Controller2'] != '1':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '1'
    if (system.config['core'] == 'pcsx_rearmed'):               # PCSX Rearmed
        if system.isOptSet('controller1_pcsx'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_pcsx']
            if system.config['controller1_pcsx'] != '1':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        if system.isOptSet('controller2_pcsx'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_pcsx']
            if system.config['controller2_pcsx'] != '1':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '1'

    ## Sega Dreamcast controller
    if system.config['core'] == 'flycast':
        if system.name != 'dreamcast':
            retroarchConfig['input_player1_analog_dpad_mode'] = '3'
            retroarchConfig['input_player2_analog_dpad_mode'] = '3'
            retroarchConfig['input_player3_analog_dpad_mode'] = '3'
            retroarchConfig['input_player4_analog_dpad_mode'] = '3'
        else:
            retroarchConfig['input_player1_analog_dpad_mode'] = '1'
            retroarchConfig['input_player2_analog_dpad_mode'] = '1'
            retroarchConfig['input_player3_analog_dpad_mode'] = '1'
            retroarchConfig['input_player4_analog_dpad_mode'] = '1'
        if system.isOptSet('controller1_dc'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_dc']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'
        if system.isOptSet('controller2_dc'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_dc']
        else:
            retroarchConfig['input_libretro_device_p2'] = '1'
        if system.isOptSet('controller3_dc'):
            retroarchConfig['input_libretro_device_p3'] = system.config['controller3_dc']
        else:
            retroarchConfig['input_libretro_device_p3'] = '1'
        if system.isOptSet('controller4_dc'):
            retroarchConfig['input_libretro_device_p4'] = system.config['controller4_dc']
        else:
            retroarchConfig['input_libretro_device_p4'] = '1'

    ## Sega Megadrive controller
    if system.config['core'] == 'genesisplusgx' and system.name == 'megadrive':
        if system.isOptSet('controller1_md'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_md']
        else:
            retroarchConfig['input_libretro_device_p1'] = '513' # 6 button
        if system.isOptSet('controller2_md'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_md']
        else:
            retroarchConfig['input_libretro_device_p2'] = '513' # 6 button

    ## Sega Mastersystem controller
    if system.config['core'] == 'genesisplusgx' and system.name == 'mastersystem':
        if system.isOptSet('controller1_ms'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_ms']
        else:
            retroarchConfig['input_libretro_device_p1'] = '769'
        if system.isOptSet('controller2_ms'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_ms']
        else:
            retroarchConfig['input_libretro_device_p2'] = '769'

    ## NEC PCEngine controller
    if system.config['core'] == 'pce' or system.config['core'] == 'pce_fast':
        if system.isOptSet('controller1_pce'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_pce']
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'

    ## MS-DOS controller
    if (system.config['core'] == 'dosbox_pure'):               # Dosbox-Pure
        if system.isOptSet('controller1_dosbox_pure'):
            retroarchConfig['input_libretro_device_p1'] = system.config['controller1_dosbox_pure']
            if system.config['controller1_dosbox_pure'] != '3':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '3'
        if system.isOptSet('controller2_dosbox_pure'):
            retroarchConfig['input_libretro_device_p2'] = system.config['controller2_dosbox_pure']
            if system.config['controller2_dosbox_pure'] != '3':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '3'

    ## PS1 Swanstation and Duckstation
    if (system.config['core'] == 'swanstation'):               # Swanstation
        # Controller 1 Type
        if system.isOptSet('duckstation_Controller1'):
            coreSettings.save('duckstation_Controller1.Type', system.config['duckstation_Controller1'])
        else:
            coreSettings.save('duckstation_Controller1.Type', '"DigitalController"')
        # Controller 2 Type
        if system.isOptSet('duckstation_Controller2'):
            coreSettings.save('duckstation_Controller2.Type', system.config['duckstation_Controller2'])
        else:
            coreSettings.save('duckstation_Controller2.Type', '"DigitalController"')
    if (system.config['core'] == 'duckstation'):               # Duckstation
        if system.isOptSet('duckstation_Controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['duckstation_Controller1']
            if system.config['duckstation_Controller1'] != '1':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '3'
        if system.isOptSet('duckstation_Controller2'):
            retroarchConfig['input_libretro_device_p2'] = system.config['duckstation_Controller2']
            if system.config['duckstation_Controller2'] != '1':
                retroarchConfig['input_player2_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player2_analog_dpad_mode'] = '3'


    ## PORTS
    ## Quake
    if (system.config['core'] == 'tyrquake'):
        if system.isOptSet('tyrquake_controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['tyrquake_controller1']
            if system.config['tyrquake_controller1'] == '773' or system.config['tyrquake_controller1'] == '3':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'

    ## DOOM
    if (system.config['core'] == 'prboom'):
        if system.isOptSet('prboom_controller1'):
            retroarchConfig['input_libretro_device_p1'] = system.config['prboom_controller1']
            if system.config['prboom_controller1'] != '1' or system.config['prboom_controller1'] == '3':
                retroarchConfig['input_player1_analog_dpad_mode'] = '0'
            else:
                retroarchConfig['input_player1_analog_dpad_mode'] = '1'
        else:
            retroarchConfig['input_libretro_device_p1'] = '1'

    # Smooth option
    if system.isOptSet('smooth') and system.getOptBoolean('smooth') == True:
        retroarchConfig['video_smooth'] = 'true'
    else:
        retroarchConfig['video_smooth'] = 'false'

    # Shader option
    if 'shader' in renderConfig and renderConfig['shader'] != None:
        retroarchConfig['video_shader_enable'] = 'true'
        retroarchConfig['video_smooth']        = 'false'     # seems to be necessary for weaker SBCs
    else:
        retroarchConfig['video_shader_enable'] = 'false'

    # Ratio option
    retroarchConfig['aspect_ratio_index'] = ''              # reset in case config was changed (or for overlays)
    if defined('ratio', systemConfig):
        if systemConfig['ratio'] in ratioIndexes:
            retroarchConfig['aspect_ratio_index'] = ratioIndexes.index(systemConfig['ratio'])
            retroarchConfig['video_aspect_ratio_auto'] = 'false'
        elif systemConfig['ratio'] == "custom":
            retroarchConfig['video_aspect_ratio_auto'] = 'false'
        else:
            retroarchConfig['video_aspect_ratio_auto'] = 'true'
            retroarchConfig['aspect_ratio_index'] = ''

    # Rewind option
    retroarchConfig['rewind_enable'] = 'false'
    if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        if(not system.name in systemNoRewind):
            retroarchConfig['rewind_enable'] = 'true'
        else:
            retroarchConfig['rewind_enable'] = 'false'
    else:
        retroarchConfig['rewind_enable'] = 'false'

    # Run-ahead option (latency reduction)
    retroarchConfig['run_ahead_enabled'] = 'false'
    retroarchConfig['run_ahead_frames'] = '0'
    retroarchConfig['run_ahead_secondary_instance'] = 'false'
    if system.isOptSet('runahead') and int(system.config['runahead']) >0:
       if (not system.name in systemNoRunahead):
          retroarchConfig['run_ahead_enabled'] = 'true'
          retroarchConfig['run_ahead_frames'] = system.config['runahead']
          if system.isOptSet('secondinstance') and system.getOptBoolean('secondinstance') == True:
              retroarchConfig['run_ahead_secondary_instance'] = 'true'

    # Retroachievement option
    if system.isOptSet("retroachievements.sound") and system.config["retroachievements.sound"] != "none":
        retroarchConfig['cheevos_unlock_sound_enable'] = 'true'
        retroarchConfig['cheevos_unlock_sound'] = system.config["retroachievements.sound"]
    else:
        retroarchConfig['cheevos_unlock_sound_enable'] = 'false'

    # Autosave option
    if system.isOptSet('autosave') and system.getOptBoolean('autosave') == True:
        retroarchConfig['savestate_auto_save'] = 'true'
        retroarchConfig['savestate_auto_load'] = 'true'
    else:
        retroarchConfig['savestate_auto_save'] = 'false'
        retroarchConfig['savestate_auto_load'] = 'false'

    # state_slot option
    if system.isOptSet('state_slot'):
        retroarchConfig['state_slot'] = system.config['state_slot']
    else:
        retroarchConfig['state_slot'] = '0'

    # Retroachievements option
    retroarchConfig['cheevos_enable'] = 'false'
    retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
    retroarchConfig['cheevos_leaderboards_enable'] = 'false'
    retroarchConfig['cheevos_verbose_enable'] = 'false'
    retroarchConfig['cheevos_auto_screenshot'] = 'false'

    if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
        if(system.name in systemToRetroachievements) or (system.config['core'] in coreToRetroachievements) or (system.isOptSet('cheevos_force') and system.getOptBoolean('cheevos_force') == True):
            retroarchConfig['cheevos_enable'] = 'true'
            retroarchConfig['cheevos_username'] = systemConfig.get('retroachievements.username', "")
            retroarchConfig['cheevos_password'] = systemConfig.get('retroachievements.password', "")
            # retroachievements_hardcore_mode
            if system.isOptSet('retroachievements.hardcore') and system.getOptBoolean('retroachievements.hardcore') == True:
                retroarchConfig['cheevos_hardcore_mode_enable'] = 'true'
            else:
                retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
            # retroachievements_leaderboards
            if system.isOptSet('retroachievements.leaderboards') and system.getOptBoolean('retroachievements.leaderboards') == True:
                retroarchConfig['cheevos_leaderboards_enable'] = 'true'
            else:
                retroarchConfig['cheevos_leaderboards_enable'] = 'false'
            # retroachievements_verbose_mode
            if system.isOptSet('retroachievements.verbose') and system.getOptBoolean('retroachievements.verbose') == True:
                retroarchConfig['cheevos_verbose_enable'] = 'true'
            else:
                retroarchConfig['cheevos_verbose_enable'] = 'false'
            # retroachievements_automatic_screenshot
            if system.isOptSet('retroachievements.screenshot') and system.getOptBoolean('retroachievements.screenshot') == True:
                retroarchConfig['cheevos_auto_screenshot'] = 'true'
            else:
                retroarchConfig['cheevos_auto_screenshot'] = 'false'
    else:
        retroarchConfig['cheevos_enable'] = 'false'

    if system.isOptSet('integerscale') and system.getOptBoolean('integerscale') == True:
        retroarchConfig['video_scale_integer'] = 'true'
    else:
        retroarchConfig['video_scale_integer'] = 'false'

    # Netplay management
    if 'netplay.mode' in system.config and system.config['netplay.mode'] in systemNetplayModes:
        # Security : hardcore mode disables save states, which would kill netplay
        retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
        # Quite strangely, host mode requires netplay_mode to be set to false when launched from command line
        retroarchConfig['netplay_mode']              = "false"
        retroarchConfig['netplay_ip_port']           = systemConfig.get('netplay.port', "")
        retroarchConfig['netplay_delay_frames']      = systemConfig.get('netplay.frames', "")
        retroarchConfig['netplay_nickname']          = systemConfig.get('netplay.nickname', "")
        retroarchConfig['netplay_client_swap_input'] = "false"
        if system.config['netplay.mode'] == 'client' or system.config['netplay.mode'] == 'spectator':
            # But client needs netplay_mode = true ... bug ?
            retroarchConfig['netplay_mode']              = "true"
            retroarchConfig['netplay_ip_address']        = systemConfig.get('netplay.server.ip', "")
            retroarchConfig['netplay_ip_port']           = systemConfig.get('netplay.server.port', "")
            retroarchConfig['netplay_client_swap_input'] = "true"

        # Connect as client
        if system.config['netplay.mode'] == 'client':
            if 'netplay.password' in system.config:
                retroarchConfig['netplay_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            else:
                retroarchConfig['netplay_password'] = ""

        # Connect as spectator
        if system.config['netplay.mode'] == 'spectator':
            retroarchConfig['netplay_start_as_spectator'] = "true"
            if 'netplay.password' in system.config:
                retroarchConfig['netplay_spectate_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            else:
                retroarchConfig['netplay_spectate_password'] = ""
        else:
            retroarchConfig['netplay_start_as_spectator'] = "false"

         # Netplay host passwords
        if system.config['netplay.mode'] == 'host':
            retroarchConfig['netplay_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            retroarchConfig['netplay_spectate_password'] = '"' + systemConfig.get("netplay.spectatepassword", "") + '"'

        # Netplay hide the gameplay
        if system.isOptSet('netplay_public_announce') and system.getOptBoolean('netplay_public_announce') == False:
            retroarchConfig['netplay_public_announce'] = 'false'
        else:
            retroarchConfig['netplay_public_announce'] = 'true'

        # Enable or disable server spectator mode
        if system.isOptSet('netplay.spectator') and system.getOptBoolean('netplay.spectator') == True:
            retroarchConfig['netplay_spectator_mode_enable'] = 'true'
        else:
            retroarchConfig['netplay_spectator_mode_enable'] = 'false'

        # Relay
        if 'netplay.relay' in system.config and system.config['netplay.relay'] != "" and system.config['netplay.relay'] != "none" :
            retroarchConfig['netplay_use_mitm_server'] = "true"
            retroarchConfig['netplay_mitm_server'] = systemConfig.get('netplay.relay', "")
        else:
            retroarchConfig['netplay_use_mitm_server'] = "false"

    # Display FPS
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
        retroarchConfig['fps_show'] = 'true'
    else:
        retroarchConfig['fps_show'] = 'false'

    # Adaptation for small resolution (GPICase)
    if isLowResolution(gameResolution):
        retroarchConfig['width']  = gameResolution["width"]
        retroarchConfig['height'] = gameResolution["height"]
        retroarchConfig['video_font_size'] = '12'
        retroarchConfig['menu_widget_scale_auto'] = 'false'
        retroarchConfig['menu_widget_scale_factor'] = '2.0000'
        retroarchConfig['menu_widget_scale_factor_windowed'] = '2.0000'
    else:
        retroarchConfig['video_font_size'] = '32'
        # don't force any so that the user can choose
        #retroarchConfig['menu_driver'] = 'ozone'
        # force the assets directory while it was wrong in some beta versions
        retroarchConfig['assets_directory'] = '/usr/share/libretro/assets'
        retroarchConfig['width']  = gameResolution["width"]  # default value
        retroarchConfig['height'] = gameResolution["height"] # default value

    # AI option (service for game translations)
    if system.isOptSet('ai_service_enabled') and system.getOptBoolean('ai_service_enabled') == True:
        retroarchConfig['ai_service_enable'] = 'true'
        retroarchConfig['ai_service_mode'] = '0'
        retroarchConfig['ai_service_source_lang'] = '0'
        if system.isOptSet('ai_target_lang'):
            chosen_lang=system.config['ai_target_lang']
        else:
            chosen_lang='En'
        if system.isOptSet('ai_service_url') and system.config['ai_service_url']:
            retroarchConfig['ai_service_url'] = system.config['ai_service_url']+'&mode=Fast&output=png&target_lang='+chosen_lang
        else:
            retroarchConfig['ai_service_url'] = 'http://ztranslate.net/service?api_key=BATOCERA&mode=Fast&output=png&target_lang='+chosen_lang
        if system.isOptSet('ai_service_pause') and system.getOptBoolean('ai_service_pause') == True:
            retroarchConfig['ai_service_pause'] = 'true'
        else:
            retroarchConfig['ai_service_pause'] = 'false'
    else:
        retroarchConfig['ai_service_enable'] = 'false'

    # Bezel option
    try:
        writeBezelConfig(bezel, retroarchConfig, rom, gameResolution, system)
    except Exception as e:
        # error with bezels, disabling them
        writeBezelConfig(None, retroarchConfig, rom, gameResolution, system)
        eslog.error("Error with bezel {}: {}".format(bezel, e))

    # custom : allow the user to configure directly retroarch.cfg via batocera.conf via lines like : snes.retroarch.menu_driver=rgui
    for user_config in systemConfig:
        if user_config[:10] == "retroarch.":
            retroarchConfig[user_config[10:]] = systemConfig[user_config]

    return retroarchConfig

def writeLibretroConfigToFile(retroconfig, config):
    for setting in config:
        retroconfig.save(setting, config[setting])

def writeBezelConfig(bezel, retroarchConfig, rom, gameResolution, system):
    # disable the overlay
    # if all steps are passed, enable them
    retroarchConfig['input_overlay_hide_in_menu'] = "false"
    overlay_cfg_file  = batoceraFiles.overlayConfigFile

    # bezel are disabled
    # default values in case something wrong append
    retroarchConfig['input_overlay_enable'] = "false"
    retroarchConfig['video_message_pos_x']  = 0.05
    retroarchConfig['video_message_pos_y']  = 0.05

    if bezel is None:
        return

    bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name)
    if bz_infos is None:
        return

    overlay_info_file = bz_infos["info"]
    overlay_png_file  = bz_infos["png"]
    bezel_game  = bz_infos["specific_to_game"]

    # only the png file is mandatory
    if os.path.exists(overlay_info_file):
        try:
            infos = json.load(open(overlay_info_file))
        except:
            infos = {}
    else:
        infos = {}

    # if image is not at the correct size, find the correct size
    bezelNeedAdaptation = False
    viewPortUsed = True
    if "width" not in infos or "height" not in infos or "top" not in infos or "left" not in infos or "bottom" not in infos or "right" not in infos:
        viewPortUsed = False

    gameRatio  = float(gameResolution["width"]) / float(gameResolution["height"])

    if viewPortUsed:
        if gameResolution["width"] != infos["width"] or gameResolution["height"] != infos["height"]:
            if gameRatio < 1.6: # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios
                return
            else:
                bezelNeedAdaptation = True
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("custom")) # overwritten from the beginning of this file
    else:
        # when there is no information about width and height in the .info, assume that the tv is HD 16/9 and infos are core provided
        if gameRatio < 1.6: # let's use bezels only for 16:10, 5:3, 16:9 and wider aspect ratios
            return
        else:
            # No info on the bezel, let's get the bezel image width and height and apply the
            # ratios from usual 16:9 1920x1080 bezels (example: theBezelProject)
            try:
                infos["width"], infos["height"] = bezelsUtil.fast_image_size(overlay_png_file)
                infos["top"]    = int(infos["height"] * 2 / 1080)
                infos["left"]   = int(infos["width"] * 241 / 1920) # 241 = (1920 - (1920 / (4:3))) / 2 + 1 pixel = where viewport start
                infos["bottom"] = int(infos["height"] * 2 / 1080)
                infos["right"]  = int(infos["width"] * 241 / 1920)
                bezelNeedAdaptation = True
            except:
                pass # outch, no ratio will be applied.
        if gameResolution["width"] == infos["width"] and gameResolution["height"] == infos["height"]:
            bezelNeedAdaptation = False
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("core"))

    retroarchConfig['input_overlay_enable']       = "true"
    retroarchConfig['input_overlay_scale']        = "1.0"
    retroarchConfig['input_overlay']              = overlay_cfg_file
    retroarchConfig['input_overlay_hide_in_menu'] = "true"

    if "opacity" not in infos:
        infos["opacity"] = 1.0
    if "messagex" not in infos:
        infos["messagex"] = 0.0
    if "messagey" not in infos:
        infos["messagey"] = 0.0

    retroarchConfig['input_overlay_opacity'] = infos["opacity"]

    # stretch option
    if system.isOptSet('bezel_stretch') and system.getOptBoolean('bezel_stretch') == True:
        bezel_stretch = True
    else:
        bezel_stretch = False

    if bezelNeedAdaptation:
        wratio = gameResolution["width"] / float(infos["width"])
        hratio = gameResolution["height"] / float(infos["height"])

        # If width or height < original, can't add black borders, need to stretch
        if gameResolution["width"] < infos["width"] or gameResolution["height"] < infos["height"]:
            bezel_stretch = True

        if bezel_stretch:
            retroarchConfig['custom_viewport_x']      = infos["left"] * wratio
            retroarchConfig['custom_viewport_y']      = infos["top"] * hratio
            retroarchConfig['custom_viewport_width']  = (infos["width"]  - infos["left"] - infos["right"])  * wratio
            retroarchConfig['custom_viewport_height'] = (infos["height"] - infos["top"]  - infos["bottom"]) * hratio
            retroarchConfig['video_message_pos_x']    = infos["messagex"] * wratio
            retroarchConfig['video_message_pos_y']    = infos["messagey"] * hratio
        else:
            if bezel_game is True:
                output_png_file = "/tmp/bezel_game_adapted.png"
                create_new_bezel_file = True
            else:
                create_new_bezel_file = False
                output_png_file = "/tmp/" + os.path.splitext(os.path.basename(overlay_png_file))[0] + "_adapted.png"
                if os.path.exists(output_png_file) is False:
                    create_new_bezel_file = True
                else:
                    if os.path.getmtime(output_png_file) < os.path.getmtime(overlay_png_file):
                        create_new_bezel_file = True
            # fast way of checking the size of a png
            oldwidth, oldheight = bezelsUtil.fast_image_size(output_png_file)
            if (oldwidth != gameResolution["width"] or oldheight != gameResolution["height"]):
                create_new_bezel_file = True

            xoffset = gameResolution["width"]  - infos["width"]
            yoffset = gameResolution["height"] - infos["height"]
            retroarchConfig['custom_viewport_x']      = infos["left"] + xoffset/2
            retroarchConfig['custom_viewport_y']      = infos["top"] + yoffset/2
            retroarchConfig['custom_viewport_width']  = infos["width"]  - infos["left"] - infos["right"]
            retroarchConfig['custom_viewport_height'] = infos["height"] - infos["top"]  - infos["bottom"]
            retroarchConfig['video_message_pos_x']    = infos["messagex"] + xoffset/2
            retroarchConfig['video_message_pos_y']    = infos["messagey"] + yoffset/2

            if create_new_bezel_file is True:
                # Padding left and right borders for ultrawide screens (larger than 16:9 aspect ratio)
                # or up/down for 4K
                eslog.debug("Generating a new adapted bezel file {}".format(output_png_file))
                fillcolor = 'black'

                borderw = 0
                borderh = 0
                if wratio > 1:
                    borderw = xoffset / 2
                if hratio > 1:
                    borderh = yoffset / 2
                imgin = Image.open(overlay_png_file)
                if imgin.mode != "RGBA":
                    # TheBezelProject have Palette + alpha, not RGBA. PIL can't convert from P+A to RGBA.
                    # Even if it can load P+A, it can't save P+A as PNG. So we have to recreate a new image to adapt it.
                    if not 'transparency' in imgin.info:
                        return # no transparent layer for the viewport, abort
                    alpha = imgin.split()[-1]  # alpha from original palette + alpha
                    ix,iy = bezelsUtil.fast_image_size(overlay_png_file)
                    imgnew = Image.new("RGBA", (ix,iy), (0,0,0,255))
                    imgnew.paste(alpha, (0,0,ix,iy))
                    imgout = ImageOps.expand(imgnew, border=(borderw, borderh, xoffset-borderw, yoffset-borderh), fill=fillcolor)
                    imgout.save(output_png_file, mode="RGBA", format="PNG")
                else:
                    imgout = ImageOps.expand(imgin, border=(borderw, borderh, xoffset-borderw, yoffset-borderh), fill=fillcolor)
                    imgout.save(output_png_file, mode="RGBA", format="PNG")
            overlay_png_file = output_png_file # replace by the new file (recreated or cached in /tmp)
    else:
        if viewPortUsed:
            retroarchConfig['custom_viewport_x']      = infos["left"]
            retroarchConfig['custom_viewport_y']      = infos["top"]
            retroarchConfig['custom_viewport_width']  = infos["width"]  - infos["left"] - infos["right"]
            retroarchConfig['custom_viewport_height'] = infos["height"] - infos["top"]  - infos["bottom"]
        retroarchConfig['video_message_pos_x']    = infos["messagex"]
        retroarchConfig['video_message_pos_y']    = infos["messagey"]

    if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
        if system.config['bezel.tattoo'] == 'system':
            try:
                tattoo_file = '/usr/share/batocera/controller-overlays/'+system.name+'.png'
                if not os.path.exists(tattoo_file):
                    tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
                tattoo = Image.open(tattoo_file)
            except:
                eslog.error("Error opening controller overlay: {}".format('tattoo_file'))
        elif system.config['bezel.tattoo'] == 'custom' and os.path.exists(system.config['bezel.tattoo_file']):
            try:
                tattoo_file = system.config['bezel.tattoo_file']
                tattoo = Image.open(tattoo_file)
            except:
                eslog.error("Error opening custom file: {}".format('tattoo_file'))
        else:
            try:
                tattoo_file = '/usr/share/batocera/controller-overlays/generic.png'
                tattoo = Image.open(tattoo_file)
            except:
                eslog.error("Error opening custom file: {}".format('tattoo_file'))
        output_png_file = "/tmp/bezel_tattooed.png"
        back = Image.open(overlay_png_file)
        tattoo = tattoo.convert("RGBA")
        back = back.convert("RGBA")
        w,h = bezelsUtil.fast_image_size(overlay_png_file)
        tw,th = bezelsUtil.fast_image_size(tattoo_file)
        tatwidth = int(240/1920 * w) # 240 = half of the difference between 4:3 and 16:9 on 1920px (0.5*1920/16*4)
        pcent = float(tatwidth / tw)
        tatheight = int(float(th) * pcent)
        tattoo = tattoo.resize((tatwidth,tatheight), Image.ANTIALIAS)
        alpha = back.split()[-1]
        alphatat = tattoo.split()[-1]
        if system.isOptSet('bezel.tattoo_corner'):
            corner = system.config['bezel.tattoo_corner']
        else:
            corner = 'NW'
        if (corner.upper() == 'NE'):
            back.paste(tattoo, (w-tatwidth,20), alphatat) # 20 pixels vertical margins (on 1080p)
        elif (corner.upper() == 'SE'):
            back.paste(tattoo, (w-tatwidth,h-tatheight-20), alphatat)
        elif (corner.upper() == 'SW'):
            back.paste(tattoo, (0,h-tatheight-20), alphatat)
        else: # default = NW
            back.paste(tattoo, (0,20), alphatat)
        imgnew = Image.new("RGBA", (w,h), (0,0,0,255))
        imgnew.paste(back, (0,0,w,h))
        imgnew.save(output_png_file, mode="RGBA", format="PNG")
        overlay_png_file = output_png_file

    eslog.debug("Bezel file set to {}".format(overlay_png_file))
    writeBezelCfgConfig(overlay_cfg_file, overlay_png_file)

def isLowResolution(gameResolution):
    return gameResolution["width"] <= 480 or gameResolution["height"] <= 480

def writeBezelCfgConfig(cfgFile, overlay_png_file):
    fd = open(cfgFile, "w")
    fd.write("overlays = 1\n")
    fd.write("overlay0_overlay = \"" + overlay_png_file + "\"\n")
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()
