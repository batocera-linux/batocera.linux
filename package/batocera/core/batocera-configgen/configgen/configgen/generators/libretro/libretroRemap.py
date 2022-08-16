#!/usr/bin/env python
import sys
import os
import batoceraFiles
from . import libretroOptions

from Emulator import Emulator
import settings
from settings.unixSettings import UnixSettings
import json
import socket
from utils.logger import get_logger

eslog = get_logger(__name__)
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# return true if the option is considered defined
def defined(key, dict):
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0

def writeLibretroCommonRemap(self, retroconfig, system, playersControllers, guns, rom):

    # Define the libretro device type corresponding to the libretro CORE (when needed)
    coreToP1Device = {'atari800': '513', 'cap32': '513', '81': '259', 'fuse': '769'};
    coreToP2Device = {'atari800': '513', 'fuse': '513'};

    # Define the libretro device type corresponding to the libretro SYSTEM (when needed)
    systemToP1Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };
    systemToP2Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };

    # Define system emulated by bluemsx core
    systemToBluemsx = {'msx': '"MSX2"', 'msx1': '"MSX2"', 'msx2': '"MSX2"', 'colecovision': '"COL - ColecoVision"' };

    commonRemap = dict()

    ## Specific choices
    if(system.config['core'] in coreToP1Device):
        commonRemap['input_libretro_device_p1'] = coreToP1Device[system.config['core']]
    if(system.config['core'] in coreToP2Device):
        commonRemap['input_libretro_device_p2'] = coreToP2Device[system.config['core']]

    ## AMIGA OCS-ECS/AGA/CD32
    if system.config['core'] == 'puae' or system.config['core'] == 'puae2021':
        if system.name != 'amigacd32':
            if system.isOptSet('controller1_puae'):
                commonRemap['input_libretro_device_p1'] = system.config['controller1_puae']
            else:
                commonRemap['input_libretro_device_p1'] = '1'
            if system.isOptSet('controller2_puae'):
                commonRemap['input_libretro_device_p2'] = system.config['controller2_puae']
            else:
                commonRemap['input_libretro_device_p2'] = '1'
        else:
            commonRemap['input_libretro_device_p1'] = '517'     # CD 32 Pad

    ## BlueMSX choices by System
    if(system.name in systemToBluemsx):
        if system.config['core'] == 'bluemsx':
            commonRemap['input_libretro_device_p1'] = systemToP1Device[system.name]
            commonRemap['input_libretro_device_p2'] = systemToP2Device[system.name]

    ## SNES9x and SNES9x_next (2010) controller
    if system.config['core'] == 'snes9x' or system.config['core'] == 'snes9x_next':
        if system.isOptSet('controller1_snes9x'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_snes9x']
        elif system.isOptSet('controller1_snes9x_next'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_snes9x_next']
        else:
            commonRemap['input_libretro_device_p1'] = '1'
        # Player 2
        if system.isOptSet('controller2_snes9x'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_snes9x']
        elif system.isOptSet('controller2_snes9x_next'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_snes9x_next']
        elif len(controllers) > 2:                              # More than 2 controller connected
            commonRemap['input_libretro_device_p2'] = '257'
        else:
            commonRemap['input_libretro_device_p2'] = '1'
        # Player 3
        if system.isOptSet('Controller3_snes9x'):
            commonRemap['input_libretro_device_p3'] = system.config['Controller3_snes9x']
        else:
            commonRemap['input_libretro_device_p3'] = '1'

    ## NES controller
    if system.config['core'] == 'fceumm':
        if system.isOptSet('controller1_nes'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_nes']
        else:
            commonRemap['input_libretro_device_p1'] = '1'
        if system.isOptSet('controller2_nes'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_nes']
        else:
            commonRemap['input_libretro_device_p2'] = '1'

    ## PlayStation controller
    if (system.config['core'] == 'mednafen_psx'):               # Madnafen
        if system.isOptSet('beetle_psx_Controller1'):
            commonRemap['input_libretro_device_p1'] = system.config['beetle_psx_Controller1']
            if system.config['beetle_psx_Controller1'] != '1':
                commonRemap['input_player1_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player1_analog_dpad_mode'] = '1'
        if system.isOptSet('beetle_psx_Controller2'):
            commonRemap['input_libretro_device_p2'] = system.config['beetle_psx_Controller2']
            if system.config['beetle_psx_Controller2'] != '1':
                commonRemap['input_player2_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player2_analog_dpad_mode'] = '1'
    if (system.config['core'] == 'pcsx_rearmed'):               # PCSX Rearmed
        if system.isOptSet('controller1_pcsx'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_pcsx']
            if system.config['controller1_pcsx'] != '1':
                commonRemap['input_player1_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player1_analog_dpad_mode'] = '1'
        if system.isOptSet('controller2_pcsx'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_pcsx']
            if system.config['controller2_pcsx'] != '1':
                commonRemap['input_player2_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player2_analog_dpad_mode'] = '1'

    ## Sega Dreamcast controller
    if system.config['core'] == 'flycast':
        if system.isOptSet('controller1_dc'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_dc']
        else:
            commonRemap['input_libretro_device_p1'] = '1'
        if system.isOptSet('controller2_dc'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_dc']
        else:
            commonRemap['input_libretro_device_p2'] = '1'
        if system.isOptSet('controller3_dc'):
            commonRemap['input_libretro_device_p3'] = system.config['controller3_dc']
        else:
            commonRemap['input_libretro_device_p3'] = '1'
        if system.isOptSet('controller4_dc'):
            commonRemap['input_libretro_device_p4'] = system.config['controller4_dc']
        else:
            commonRemap['input_libretro_device_p4'] = '1'

    ## Sega Megadrive controller
    if system.config['core'] == 'genesisplusgx' and system.name == 'megadrive':
        if system.isOptSet('controller1_md'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_md']
        else:
            commonRemap['input_libretro_device_p1'] = '513' # 6 button
        if system.isOptSet('controller2_md'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_md']
        else:
            commonRemap['input_libretro_device_p2'] = '513' # 6 button

    ## Sega Mastersystem controller
    if system.config['core'] == 'genesisplusgx' and system.name == 'mastersystem':
        if system.isOptSet('controller1_ms'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_ms']
        else:
            commonRemap['input_libretro_device_p1'] = '769'
        if system.isOptSet('controller2_ms'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_ms']
        else:
            commonRemap['input_libretro_device_p2'] = '769'

    ## Sega Saturn controller
    if system.config['core'] == 'yabasanshiro' and system.name == 'saturn':
        if system.isOptSet('controller1_saturn'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_saturn']
        else:
            commonRemap['input_libretro_device_p1'] = '1' # Saturn pad
        if system.isOptSet('controller2_saturn'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_saturn']
        else:
            commonRemap['input_libretro_device_p2'] = '1' # Saturn pad

    ## NEC PCEngine controller
    if system.config['core'] == 'pce' or system.config['core'] == 'pce_fast':
        if system.isOptSet('controller1_pce'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_pce']
        else:
            commonRemap['input_libretro_device_p1'] = '1'

    ## MS-DOS controller
    if (system.config['core'] == 'dosbox_pure'):               # Dosbox-Pure
        if system.isOptSet('controller1_dosbox_pure'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_dosbox_pure']
            if system.config['controller1_dosbox_pure'] != '3':
                commonRemap['input_player1_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player1_analog_dpad_mode'] = '3'
        if system.isOptSet('controller2_dosbox_pure'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_dosbox_pure']
            if system.config['controller2_dosbox_pure'] != '3':
                commonRemap['input_player2_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player2_analog_dpad_mode'] = '3'

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
            commonRemap['input_libretro_device_p1'] = system.config['duckstation_Controller1']
            if system.config['duckstation_Controller1'] != '1':
                commonRemap['input_player1_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player1_analog_dpad_mode'] = '3'
        if system.isOptSet('duckstation_Controller2'):
            commonRemap['input_libretro_device_p2'] = system.config['duckstation_Controller2']
            if system.config['duckstation_Controller2'] != '1':
                commonRemap['input_player2_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player2_analog_dpad_mode'] = '3'

    ## PORTS
    ## Quake
    if (system.config['core'] == 'tyrquake'):
        if system.isOptSet('tyrquake_controller1'):
            commonRemap['input_libretro_device_p1'] = system.config['tyrquake_controller1']
            if system.config['tyrquake_controller1'] == '773' or system.config['tyrquake_controller1'] == '3':
                commonRemap['input_player1_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player1_analog_dpad_mode'] = '1'
        else:
            commonRemap['input_libretro_device_p1'] = '1'

    ## DOOM
    if (system.config['core'] == 'prboom'):
        if system.isOptSet('prboom_controller1'):
            commonRemap['input_libretro_device_p1'] = system.config['prboom_controller1']
            if system.config['prboom_controller1'] != '1' or system.config['prboom_controller1'] == '3':
                commonRemap['input_player1_analog_dpad_mode'] = '0'
            else:
                commonRemap['input_player1_analog_dpad_mode'] = '1'
        else:
            commonRemap['input_libretro_device_p1'] = '1'

    ## ZX Spectrum
    if (system.config['core'] == 'fuse'):
        if system.isOptSet('controller1_zxspec'):
            commonRemap['input_libretro_device_p1'] = system.config['controller1_zxspec']
        else:
            commonRemap['input_libretro_device_p1'] = '769'                               #Sinclair 1 controller - most used on games
        if system.isOptSet('controller2_zxspec'):
            commonRemap['input_libretro_device_p2'] = system.config['controller2_zxspec']
        else:
            commonRemap['input_libretro_device_p2'] = '1025'                              #Sinclair 2 controller
        if system.isOptSet('controller3_zxspec'):
            commonRemap['input_libretro_device_p3'] = system.config['controller3_zxspec']
        else:
            commonRemap['input_libretro_device_p3'] = '259'

    # Guns
    # clear
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
        if len(guns) >= 1:
            clearGunInputsForPlayer(1, retroarchConfig)
        if len(guns) >= 2:
            clearGunInputsForPlayer(2, retroarchConfig)

    gun_mapping = {
        "bsnes"         : { "default" : { "device": 260,          "p2": 0,
                                          "gameDependant": [ { "key": "gun", "value": "justifier", "mapkey": "device", "mapvalue": "516" },
                                                             { "key": "reversedbuttons", "value": "true", "mapcorekey": "bsnes_touchscreen_lightgun_superscope_reverse", "mapcorevalue": "ON" } ] } },
        "mesen-s"       : { "default" : { "device": 262,          "p2": 0 } },
        "snes9x"        : { "default" : { "device": 260,          "p2": 0, "p3": 1, "device_p3": 772, # different device for the 2nd gun...
                                          "gameDependant": [ { "key": "gun", "value": "justifier", "mapkey": "device", "mapvalue": "516" },
                                                             { "key": "reversedbuttons", "value": "true", "mapcorekey": "snes9x_superscope_reverse_buttons", "mapcorevalue": "enabled" } ] } },
        "snes9x_next"   : { "default" : { "device": 260,          "p2": 0,
                                          "gameDependant": [ { "key": "gun", "value": "justifier", "mapkey": "device", "mapvalue": "516" } ]} },
        "nestopia"      : { "default" : { "device": 262,          "p2": 0 } },
        "fceumm"        : { "default" : { "device": 258,          "p2": 0 } },
        "genesisplusgx" : { "megadrive" : { "device": 516, "p2": 0,
                                            "gameDependant": [ { "key": "gun", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ] },
                            "mastersystem" : { "device": 260, "p1": 0, "p2": 1 },
                            "segacd" : { "device": 516, "p2": 0,
                                         "gameDependant": [ { "key": "gun", "value": "justifier", "mapkey": "device", "mapvalue": "772" } ]} },
        "fbneo"         : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "mame078plus"   : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "mame0139"      : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "flycast"       : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "mednafen_psx"  : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "pcsx_rearmed"  : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "swanstation"   : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "beetle-saturn" : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "opera"         : { "default" : { "device": 260, "p1": 0, "p2": 1 } },
        "stella"        : { "default" : { "device":   4, "p1": 0, "p2": 1 } },
        "vice_x64"      : { "default" : { "gameDependant": [ { "key": "gun", "value": "stack_light_rifle", "mapcorekey": "vice_joyport_type", "mapcorevalue": "15" } ] } }
    }

    # apply mapping
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
        if system.config['core'] in gun_mapping:
            # conf from general mapping
            if system.name in gun_mapping[system.config['core']]:
                ragunconf = gun_mapping[system.config['core']][system.name]
            else:
                ragunconf = gun_mapping[system.config['core']]["default"]
            raguncoreconf = {}

            # overwrite configuration by gungames.xml
            if "gameDependant" in ragunconf:
                gunsmetadata = controllersConfig.getGameGunsMetaData(system.name, rom)
                for gd in ragunconf["gameDependant"]:
                    if gd["key"] in gunsmetadata and gunsmetadata[gd["key"]] == gd["value"] and "mapkey" in gd and "mapvalue" in gd:
                        ragunconf[gd["mapkey"]] = gd["mapvalue"]
                    if gd["key"] in gunsmetadata and gunsmetadata[gd["key"]] == gd["value"] and "mapcorekey" in gd and "mapcorevalue" in gd:
                        raguncoreconf[gd["mapcorekey"]] = gd["mapcorevalue"]

            for nplayer in range(1, 3+1):
                if "p"+str(nplayer) in ragunconf and len(guns)-1 >= ragunconf["p"+str(nplayer)]:
                    if "device_p"+str(nplayer) in ragunconf:
                        retroarchConfig['input_libretro_device_p'+str(nplayer)] = ragunconf["device_p"+str(nplayer)]
                    else:
                        retroarchConfig['input_libretro_device_p'+str(nplayer)] = ragunconf["device"]
                    configureGunInputsForPlayer(nplayer, guns[ragunconf["p"+str(nplayer)]], controllers, retroarchConfig)

            # override core settings
            for key in raguncoreconf:
                coreSettings.save(key, '"' + raguncoreconf[key] + '"')

    for setting in commonRemap:
        retroconfig.save(setting, commonRemap[setting])
