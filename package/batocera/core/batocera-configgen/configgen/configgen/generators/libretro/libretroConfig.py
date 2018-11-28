#!/usr/bin/env python
import sys
import os
import recalboxFiles
import settings
from settings.unixSettings import UnixSettings
import json
import utils.eslog as eslog

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

libretroSettings = UnixSettings(recalboxFiles.retroarchCustom, separator=' ')
coreSettings = UnixSettings(recalboxFiles.retroarchCoreCustom, separator=' ')


# return true if the option is considered enabled (for boolean options)
def enabled(key, dict):
    return key in dict and (dict[key] == '1' or dict[key] == 'true')


# return true if the option is considered defined
def defined(key, dict):
    return key in dict and isinstance(dict[key], str) and len(dict[key]) > 0


# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L132
ratioIndexes = ["4/3", "16/9", "16/10", "16/15", "21/9", "1/1", "2/1", "3/2", "3/4", "4/1", "4/4", "5/4", "6/5", "7/9", "8/3",
                "8/7", "19/12", "19/14", "30/17", "32/9", "config", "squarepixel", "core", "custom"]


# Define the libretro device type corresponding to the libretro cores, when needed.
coreToP1Device = {'cap32': '513', '81': '257', 'fuse': '513'};
coreToP2Device = {'fuse': '513'};

# Define systems compatible with retroachievements
systemToRetroachievements = {'snes', 'nes', 'gba', 'gb', 'gbc', 'megadrive', 'mastersystem', 'pcengine', 'lynx', 'ngp', 'atari2600', 'virtualboy', 'neogeo'};

# Define systems not compatible with rewind option
systemNoRewind = {'sega32x', 'psx', 'zxspectrum', 'odyssey2', 'mame', 'n64', 'dreamcast', 'naomi'};

# Define system emulated by bluemsx core
systemToBluemsx = {'msx': '"MSX2"', 'msx1': '"MSX2"', 'msx2': '"MSX2"', 'colecovision': '"COL - ColecoVision"' };

# Define the libretro device type corresponding to the libretro cores, when needed.
systemToP1Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };
systemToP2Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };

# Netplay modes
systemNetplayModes = {'host', 'client'}

def writeLibretroConfig(system, controllers, rom, bezel, gameResolution):
    writeLibretroConfigToFile(createLibretroConfig(system, controllers, rom, bezel, gameResolution))


# take a system, and returns a dict of retroarch.cfg compatible parameters
def createLibretroConfig(system, controllers, rom, bezel, gameResolution):
    retroarchConfig = dict()
    recalboxConfig = system.config
    if enabled('smooth', recalboxConfig):
        retroarchConfig['video_smooth'] = 'true'
    else:
        retroarchConfig['video_smooth'] = 'false'

    if defined('shaders', recalboxConfig):
        retroarchConfig['video_shader'] = recalboxConfig['shaders']
        retroarchConfig['video_shader_enable'] = 'true'
        retroarchConfig['video_smooth'] = 'false'
    else:
        retroarchConfig['video_shader_enable'] = 'false'

    retroarchConfig['aspect_ratio_index'] = '' # reset in case config was changed (or for overlays)
    if defined('ratio', recalboxConfig):
        if recalboxConfig['ratio'] in ratioIndexes:
            retroarchConfig['aspect_ratio_index'] = ratioIndexes.index(recalboxConfig['ratio'])
            retroarchConfig['video_aspect_ratio_auto'] = 'false'
        elif recalboxConfig['ratio'] == "custom":
            retroarchConfig['video_aspect_ratio_auto'] = 'false'
        else:
            retroarchConfig['video_aspect_ratio_auto'] = 'true'
            retroarchConfig['aspect_ratio_index'] = ''

    retroarchConfig['rewind_enable'] = 'false'

    if enabled('rewind', recalboxConfig):
        if(not system.name in systemNoRewind):
            retroarchConfig['rewind_enable'] = 'true'
    else:
        retroarchConfig['rewind_enable'] = 'false'

    if enabled('autosave', recalboxConfig):
        retroarchConfig['savestate_auto_save'] = 'true'
        retroarchConfig['savestate_auto_load'] = 'true'
    else:
        retroarchConfig['savestate_auto_save'] = 'false'
        retroarchConfig['savestate_auto_load'] = 'false'

    if defined('inputdriver', recalboxConfig):
        retroarchConfig['input_joypad_driver'] = recalboxConfig['inputdriver']
    else:
        retroarchConfig['input_joypad_driver'] = 'udev'

    retroarchConfig['savestate_directory'] = recalboxFiles.savesDir + system.name
    retroarchConfig['savefile_directory'] = recalboxFiles.savesDir + system.name

    retroarchConfig['input_libretro_device_p1'] = '1'
    retroarchConfig['input_libretro_device_p2'] = '1'

    if(system.config['core'] in coreToP1Device):
        retroarchConfig['input_libretro_device_p1'] = coreToP1Device[system.config['core']]

    if(system.config['core'] in coreToP2Device):
        retroarchConfig['input_libretro_device_p2'] = coreToP2Device[system.config['core']]

    if len(controllers) > 2 and (system.config['core'] == 'snes9x_next' or system.config['core'] == 'snes9x'):
        retroarchConfig['input_libretro_device_p2'] = '257'

    if system.config['core'] == 'atari800':
        retroarchConfig['input_libretro_device_p1'] = '513'
        retroarchConfig['input_libretro_device_p2'] = '513'

    retroarchConfig['cheevos_enable'] = 'false'
    retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
    retroarchConfig['cheevos_leaderboards_enable'] = 'false'
    retroarchConfig['cheevos_verbose_enable'] = 'false'
    retroarchConfig['cheevos_auto_screenshot'] = 'false'

    if enabled('retroachievements', recalboxConfig):
        if(system.name in systemToRetroachievements):
            retroarchConfig['cheevos_enable'] = 'true'
            retroarchConfig['cheevos_username'] = recalboxConfig.get('retroachievements.username', "")
            retroarchConfig['cheevos_password'] = recalboxConfig.get('retroachievements.password', "")
            # retroachievements_hardcore_mode
            if enabled('retroachievements.hardcore', recalboxConfig):
                retroarchConfig['cheevos_hardcore_mode_enable'] = 'true'
            else:
                retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
            # retroachievements_leaderboards
            if enabled('retroachievements.leaderboards', recalboxConfig):
                retroarchConfig['cheevos_leaderboards_enable'] = 'true'
            else:
                retroarchConfig['cheevos_leaderboards_enable'] = 'false'
            # retroachievements_verbose_mode
            if enabled('retroachievements.verbose', recalboxConfig):
                retroarchConfig['cheevos_verbose_enable'] = 'true'
            else:
                retroarchConfig['cheevos_verbose_enable'] = 'false'
            # retroachievements_automatic_screenshot
            if enabled('retroachievements.screenshot', recalboxConfig):
                retroarchConfig['cheevos_auto_screenshot'] = 'true'
            else:
                retroarchConfig['cheevos_auto_screenshot'] = 'false'
    else:
        retroarchConfig['cheevos_enable'] = 'false'

    if enabled('integerscale', recalboxConfig):
        retroarchConfig['video_scale_integer'] = 'true'
    else:
        retroarchConfig['video_scale_integer'] = 'false'

    # disable the threaded video while it is causing issues to several people ?
    # this must be set to true on xu4 for performance issues
    retroarchConfig['video_threaded'] = 'true'

    # core options
    if(system.name in systemToBluemsx):
        if system.config['core'] == 'bluemsx':
            coreSettings.save('bluemsx_msxtype', systemToBluemsx[system.name])
            retroarchConfig['input_libretro_device_p1'] = systemToP1Device[system.name]
            retroarchConfig['input_libretro_device_p2'] = systemToP2Device[system.name]
    # forced values (so that if the config is not correct, fix it)
    if system.config['core'] == 'tgbdual':
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("core")) # reset each time in this function
        coreSettings.save('tgbdual_audio_output',     'Game Boy #1')
        coreSettings.save('tgbdual_gblink_enable',    'enabled')
        coreSettings.save('tgbdual_screen_placement', 'left-right')
        coreSettings.save('tgbdual_single_screen_mp', 'both players')
        coreSettings.save('tgbdual_switch_screens',   'normal')

    # Netplay management
    if 'netplaymode' in system.config and system.config['netplaymode'] in systemNetplayModes:
        # Security : hardcore mode disables save states, which would kill netplay
        retroarchConfig['cheevos_hardcore_mode_enable'] = 'false'
        # Quite strangely, host mode requires netplay_mode to be set to false when launched from command line
        retroarchConfig['netplay_mode']              = "false"
        retroarchConfig['netplay_ip_port']           = recalboxConfig.get('netplay.server.port', "")
        retroarchConfig['netplay_delay_frames']      = recalboxConfig.get('netplay.frames', "")
        retroarchConfig['netplay_nickname']          = recalboxConfig.get('netplay.nick', "")
        retroarchConfig['netplay_client_swap_input'] = "false"
        if system.config['netplaymode'] == 'client':
            # But client needs netplay_mode = true ... bug ?
            retroarchConfig['netplay_mode']              = "true"
            retroarchConfig['netplay_ip_address']        = recalboxConfig.get('netplay.server.ip', "")
            retroarchConfig['netplay_client_swap_input'] = "true"

    # Display FPS
    if enabled('showFPS', recalboxConfig):
        retroarchConfig['fps_show'] = 'true'
    else:
        retroarchConfig['fps_show'] = 'false'

    # bezel
    writeBezelConfig(bezel, retroarchConfig, system.name, rom, gameResolution)

    return retroarchConfig

def writeLibretroConfigToFile(config):
    for setting in config:
        libretroSettings.save(setting, config[setting])

def writeBezelConfig(bezel, retroarchConfig, systemName, rom, gameResolution):
    # disable the overlay
    # if all steps are passed, enable them
    retroarchConfig['input_overlay_hide_in_menu'] = "false"
    overlay_cfg_file  = recalboxFiles.overlayConfigFile

    # bezel are disabled
    # default values in case something wrong append
    retroarchConfig['input_overlay_enable'] = "false"
    retroarchConfig['video_message_pos_x']  = 0.05
    retroarchConfig['video_message_pos_y']  = 0.05

    if bezel is None:
        return

    # by order choose :
    # rom name in the user directory (mario.png)
    # rom name in the system directory (mario.png)
    # system name in the user directory (gb.png)
    # system name in the system directory (gb.png)
    # default name (default.png)
    # else return
    romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
    overlay_info_file = recalboxFiles.overlayUser + "/" + bezel + "/games/" + rom + ".info"
    overlay_png_file  = recalboxFiles.overlayUser + "/" + bezel + "/games/" + rom + ".png"
    if not (os.path.isfile(overlay_info_file) and os.path.isfile(overlay_png_file)):
        overlay_info_file = recalboxFiles.overlaySystem + "/" + bezel + "/games/" + rom + ".info"
        overlay_png_file  = recalboxFiles.overlaySystem + "/" + bezel + "/games/" + rom + ".png"
        if not (os.path.isfile(overlay_info_file) and os.path.isfile(overlay_png_file)):
            overlay_info_file = recalboxFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".info"
            overlay_png_file  = recalboxFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".png"
            if not (os.path.isfile(overlay_info_file) and os.path.isfile(overlay_png_file)):
                overlay_info_file = recalboxFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".info"
                overlay_png_file  = recalboxFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".png"
                if not (os.path.isfile(overlay_info_file) and os.path.isfile(overlay_png_file)):
                    overlay_info_file = recalboxFiles.overlayUser + "/" + bezel + "/default.info"
                    overlay_png_file  = recalboxFiles.overlayUser + "/" + bezel + "/default.png"
                    if not (os.path.isfile(overlay_info_file) and os.path.isfile(overlay_png_file)):
                        overlay_info_file = recalboxFiles.overlaySystem + "/" + bezel + "/default.info"
                        overlay_png_file  = recalboxFiles.overlaySystem + "/" + bezel + "/default.png"
                        if not (os.path.isfile(overlay_info_file) and os.path.isfile(overlay_png_file)):
                            return
    infos = json.load(open(overlay_info_file))

    # if image is not at the correct size, find the correct size
    bezelNeedAdaptation = False
    if gameResolution["width"] != infos["width"] and gameResolution["height"] != infos["height"]:
        infosRatio = float(infos["width"]) / float(infos["height"])
        gameRatio  = float(gameResolution["width"]) / float(gameResolution["height"])
        if gameRatio >= infosRatio - 0.1: # keep a marge
            bezelNeedAdaptation = True
        else:
            return

    retroarchConfig['input_overlay_enable']       = "true"
    retroarchConfig['input_overlay_scale']        = "1.0"
    retroarchConfig['input_overlay']              = overlay_cfg_file
    retroarchConfig['input_overlay_hide_in_menu'] = "true"
    retroarchConfig['input_overlay_opacity']  = infos["opacity"]
    retroarchConfig['aspect_ratio_index']     = str(ratioIndexes.index("custom")) # overwritted from the beginning of this file

    if bezelNeedAdaptation:
        wratio = gameResolution["width"]  / float(infos["width"])
        hratio = gameResolution["height"] / float(infos["height"])
        retroarchConfig['custom_viewport_x']      = infos["left"] * wratio
        retroarchConfig['custom_viewport_y']      = infos["top"] * hratio
        retroarchConfig['custom_viewport_width']  = (infos["width"]  - infos["left"] - infos["right"])  * wratio
        retroarchConfig['custom_viewport_height'] = (infos["height"] - infos["top"]  - infos["bottom"]) * hratio
        retroarchConfig['video_message_pos_x']    = infos["messagex"] * wratio
        retroarchConfig['video_message_pos_y']    = infos["messagey"] * hratio
    else:
        retroarchConfig['custom_viewport_x']      = infos["left"]
        retroarchConfig['custom_viewport_y']      = infos["top"]
        retroarchConfig['custom_viewport_width']  = infos["width"]  - infos["left"] - infos["right"]
        retroarchConfig['custom_viewport_height'] = infos["height"] - infos["top"]  - infos["bottom"]
        retroarchConfig['video_message_pos_x']    = infos["messagex"]
        retroarchConfig['video_message_pos_y']    = infos["messagey"]

    writeBezelCfgConfig(overlay_cfg_file, overlay_png_file)

def writeBezelCfgConfig(cfgFile, overlay_png_file):
    fd = open(cfgFile, "w")
    fd.write("overlays = 1\n")
    fd.write("overlay0_overlay = " + overlay_png_file + "\n")
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()
