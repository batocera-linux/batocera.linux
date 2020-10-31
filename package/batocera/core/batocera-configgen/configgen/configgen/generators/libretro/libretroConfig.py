#!/usr/bin/env python
import sys
import os
import batoceraFiles
import libretroOptions
from Emulator import Emulator
import settings
from settings.unixSettings import UnixSettings
import json
from utils.logger import eslog
from PIL import Image, ImageOps
import struct

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# return true if the option is considered defined
def defined(key, dict):
    return key in dict and isinstance(dict[key], basestring) and len(dict[key]) > 0


# Warning the values in the array must be exactly at the same index than
# https://github.com/libretro/RetroArch/blob/master/gfx/video_driver.c#L132
ratioIndexes = ["4/3", "16/9", "16/10", "16/15", "21/9", "1/1", "2/1", "3/2", "3/4", "4/1", "4/4", "5/4", "6/5", "7/9", "8/3",
                "8/7", "19/12", "19/14", "30/17", "32/9", "config", "squarepixel", "core", "custom"]

# Define the libretro device type corresponding to the libretro cores, when needed.
coreToP1Device = {'cap32': '513', '81': '257', 'fuse': '513'};
coreToP2Device = {'fuse': '513'};

# Define systems compatible with retroachievements
systemToRetroachievements = {'atari2600', 'atari7800', 'atarijaguar', 'colecovision', 'nes', 'snes', 'virtualboy', 'n64', 'sg1000', 'mastersystem', 'megadrive', 'segacd', 'sega32x', 'saturn', 'pcengine', 'pcenginecd', 'supergrafx', 'psx', 'mame', 'hbmame', 'fbneo', 'neogeo', 'lightgun', 'apple2', 'lynx', 'wswan', 'wswanc', 'gb', 'gbc', 'gba', 'nds', 'pokemini', 'gamegear', 'ngp', 'ngpc'}; 

# Define systems not compatible with rewind option
systemNoRewind = {'sega32x', 'psx', 'zxspectrum', 'odyssey2', 'mame', 'hbmame', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'neogeocd', 'saturn', 'fbneo'};

# Define systems not compatible with run-ahead option (warning: this option is CPU intensive!)
systemNoRunahead = {'sega32x', 'n64', 'dreamcast', 'atomiswave', 'naomi', 'neogeocd', 'saturn'};

# Define system emulated by bluemsx core
systemToBluemsx = {'msx': '"MSX2"', 'msx1': '"MSX2"', 'msx2': '"MSX2"', 'colecovision': '"COL - ColecoVision"' };

# Define the libretro device type corresponding to the libretro cores, when needed.
systemToP1Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };
systemToP2Device = {'msx': '257', 'msx1': '257', 'msx2': '257', 'colecovision': '1' };

# Netplay modes
systemNetplayModes = {'host', 'client', 'spectator'}

def writeLibretroConfig(retroconfig, system, controllers, rom, bezel, gameResolution):
    writeLibretroConfigToFile(retroconfig, createLibretroConfig(system, controllers, rom, bezel, gameResolution))

# Much faster than PIL Image.size
def fast_image_size(image_file):
    if not os.path.exists(image_file):
        return -1, -1
    with open(image_file, 'rb') as fhandle:
        head = fhandle.read(32)
        if len(head) != 32:
           # corrupted header, or not a PNG
           return -1, -1
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
           # Not a PNG
           return -1, -1
        return struct.unpack('>ii', head[16:24]) #image width, height

# take a system, and returns a dict of retroarch.cfg compatible parameters
def createLibretroConfig(system, controllers, rom, bezel, gameResolution):
    # Create/update retroarch-core-options.cfg
    libretroOptions.generateCoreSettings(batoceraFiles.retroarchCoreCustom, system)

    # Create/update hatari.cfg
    if system.name == 'atarist':
        libretroOptions.generateHatariConf(batoceraFiles.hatariConf)

    retroarchConfig = dict()
    systemConfig = system.config
    renderConfig = system.renderconfig

    # basic configuration
    retroarchConfig['quit_press_twice'] = 'false'            # not aligned behavior on other emus
    retroarchConfig['video_driver'] = '"gl"'                 # needed for the ozone menu
    retroarchConfig['video_black_frame_insertion'] = 'false' # don't use anymore this value while it doesn't allow the shaders to work
    retroarchConfig['pause_nonactive'] = 'false'             # required at least on x86 x86_64 otherwise, the game is paused at launch
    retroarchConfig['audio_driver'] = 'alsa'                 # force ALSA. TODO: check audio.backend
    retroarchConfig['midi_driver'] = 'alsa'
    retroarchConfig['cache_directory'] = '/userdata/system/.cache'

    # fs is required at least for x86* and odroidn2
    retroarchConfig['video_fullscreen'] = 'true'

    if system.isOptSet('smooth') and system.getOptBoolean('smooth') == True:
        retroarchConfig['video_smooth'] = 'true'
    else:
        retroarchConfig['video_smooth'] = 'false'

    if 'shader' in renderConfig and renderConfig['shader'] != None:
        retroarchConfig['video_shader_enable'] = 'true'
        retroarchConfig['video_smooth']        = 'false'     # seems to be necessary for weaker SBCs
        shaderFilename = renderConfig['shader'] + ".glslp"
        if os.path.exists("/userdata/shaders/" + shaderFilename):
            retroarchConfig['video_shader_dir'] = "/userdata/shaders"
            eslog.log("shader {} found in /userdata/shaders".format(shaderFilename))
        else:
            retroarchConfig['video_shader_dir'] = "/usr/share/batocera/shaders"
    else:
        retroarchConfig['video_shader_enable'] = 'false'

    retroarchConfig['aspect_ratio_index'] = '' # reset in case config was changed (or for overlays)
    if defined('ratio', systemConfig):
        if systemConfig['ratio'] in ratioIndexes:
            retroarchConfig['aspect_ratio_index'] = ratioIndexes.index(systemConfig['ratio'])
            retroarchConfig['video_aspect_ratio_auto'] = 'false'
        elif systemConfig['ratio'] == "custom":
            retroarchConfig['video_aspect_ratio_auto'] = 'false'
        else:
            retroarchConfig['video_aspect_ratio_auto'] = 'true'
            retroarchConfig['aspect_ratio_index'] = ''

    retroarchConfig['rewind_enable'] = 'false'

    if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
        if(not system.name in systemNoRewind):
            retroarchConfig['rewind_enable'] = 'true'
    else:
        retroarchConfig['rewind_enable'] = 'false'

    retroarchConfig['run_ahead_enabled'] = 'false'
    retroarchConfig['run_ahead_frames'] = '0'
    retroarchConfig['run_ahead_secondary_instance'] = 'false'

    if system.isOptSet('runahead') and int(system.config['runahead']) >0:
       if (not system.name in systemNoRunahead):
          retroarchConfig['run_ahead_enabled'] = 'true'
          retroarchConfig['run_ahead_frames'] = system.config['runahead']
          if system.isOptSet('secondinstance') and system.getOptBoolean('secondinstance') == True:
              retroarchConfig['run_ahead_secondary_instance'] = 'true'

    if system.isOptSet('autosave') and system.getOptBoolean('autosave') == True:
        retroarchConfig['savestate_auto_save'] = 'true'
        retroarchConfig['savestate_auto_load'] = 'true'
    else:
        retroarchConfig['savestate_auto_save'] = 'false'
        retroarchConfig['savestate_auto_load'] = 'false'

    retroarchConfig['input_joypad_driver'] = 'udev'
    retroarchConfig['input_max_users'] = "16" # allow up to 16 players

    retroarchConfig['savestate_directory'] = batoceraFiles.savesDir + system.name
    retroarchConfig['savefile_directory'] = batoceraFiles.savesDir + system.name

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

    if system.isOptSet('retroachievements') and system.getOptBoolean('retroachievements') == True:
        if(system.name in systemToRetroachievements):
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

    # disable the threaded video while it is causing issues to several people ?
    # this must be set to true on xu4 for performance issues
    if system.config['video_threaded']:
        retroarchConfig['video_threaded'] = 'true'
    else:
        retroarchConfig['video_threaded'] = 'false'

    # core options
    if(system.name in systemToBluemsx):
        if system.config['core'] == 'bluemsx':
            retroarchConfig['input_libretro_device_p1'] = systemToP1Device[system.name]
            retroarchConfig['input_libretro_device_p2'] = systemToP2Device[system.name]
    # forced values (so that if the config is not correct, fix it)
    if system.config['core'] == 'tgbdual':
        retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("core")) # reset each time in this function

    # Virtual keyboard for Amstrad CPC (select+start)
    if system.config['core'] == 'cap32':
        retroarchConfig['cap32_combokey'] = 'y'

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

        # connect as client
        if system.config['netplay.mode'] == 'client':
            if 'netplay.password' in system.config:
                retroarchConfig['netplay_password'] = '"' + systemConfig.get("netplay.password", "") + '"'
            else:
                retroarchConfig['netplay_password'] = ""

        # connect as spectator
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

        # enable or disable server spectator mode
        if system.isOptSet('netplay.spectator') and system.getOptBoolean('netplay.spectator') == True:
            retroarchConfig['netplay_spectator_mode_enable'] = 'true'
        else:
            retroarchConfig['netplay_spectator_mode_enable'] = 'false'

        # relay
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

    # adaptation for small resolution
    if isLowResolution(gameResolution):
        retroarchConfig['video_font_size'] = '12'
        retroarchConfig['menu_driver'] = 'rgui'
        retroarchConfig['width']  = gameResolution["width"]  *2 # on low resolution, higher values for width and height makes a nicer image (640x480 on the gpi case)
        retroarchConfig['height'] = gameResolution["height"] *2 # default value
        retroarchConfig['menu_linear_filter'] = 'true'
        retroarchConfig['rgui_aspect_ratio'] = '0'
        retroarchConfig['rgui_aspect_ratio_lock'] = '3'
    else:
        retroarchConfig['video_font_size'] = '32'
        retroarchConfig['menu_driver'] = 'ozone'
        # force the assets directory while it was wrong in some beta versions
        retroarchConfig['assets_directory'] = '/usr/share/libretro/assets'
        retroarchConfig['width']  = gameResolution["width"]  # default value
        retroarchConfig['height'] = gameResolution["height"] # default value

    # AI service for game translations
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

    # bezel
    if system.isOptSet('bezel_stretch') and system.getOptBoolean('bezel_stretch') == True:
        bezel_stretch = True
    else:
        bezel_stretch = False
    try:
        writeBezelConfig(bezel, retroarchConfig, system.name, rom, gameResolution, bezel_stretch)
    except:
        # error with bezels, disabling them
        writeBezelConfig(None, retroarchConfig, system.name, rom, gameResolution, bezel_stretch)

    # custom : allow the user to configure directly retroarch.cfg via batocera.conf via lines like : snes.retroarch.menu_driver=rgui
    for user_config in systemConfig:
        if user_config[:10] == "retroarch.":
            retroarchConfig[user_config[10:]] = systemConfig[user_config]

    return retroarchConfig

def writeLibretroConfigToFile(retroconfig, config):
    for setting in config:
        retroconfig.save(setting, config[setting])

def writeBezelConfig(bezel, retroarchConfig, systemName, rom, gameResolution, bezel_stretch):
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

    # by order choose :
    # rom name in the system subfolder of the user directory (gb/mario.png)
    # rom name in the system subfolder of the system directory (gb/mario.png)
    # rom name in the user directory (mario.png)
    # rom name in the system directory (mario.png)
    # system name in the user directory (gb.png)
    # system name in the system directory (gb.png)
    # default name (default.png)
    # else return
    romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
    overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".info"
    overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + systemName + "/" + romBase + ".png"
    bezel_game = True
    if not os.path.exists(overlay_png_file):
        overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + systemName + "/" + romBase + ".info"
        overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + systemName + "/" + romBase + ".png"
        bezel_game = True
        if not os.path.exists(overlay_png_file):
            overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".info"
            overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/games/" + romBase + ".png"
            bezel_game = True
            if not os.path.exists(overlay_png_file):
                overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + romBase + ".info"
                overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/games/" + romBase + ".png"
                bezel_game = True
                if not os.path.exists(overlay_png_file):
                    overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".info"
                    overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/systems/" + systemName + ".png"
                    bezel_game = False
                    if not os.path.exists(overlay_png_file):
                        overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".info"
                        overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/systems/" + systemName + ".png"
                        bezel_game = False
                        if not os.path.exists(overlay_png_file):
                            overlay_info_file = batoceraFiles.overlayUser + "/" + bezel + "/default.info"
                            overlay_png_file  = batoceraFiles.overlayUser + "/" + bezel + "/default.png"
                            bezel_game = True
                            if not os.path.exists(overlay_png_file):
                                overlay_info_file = batoceraFiles.overlaySystem + "/" + bezel + "/default.info"
                                overlay_png_file  = batoceraFiles.overlaySystem + "/" + bezel + "/default.png"
                                bezel_game = True
                                if not os.path.exists(overlay_png_file):
                                    return

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
                infos["width"], infos["height"] = fast_image_size(overlay_png_file)
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
        else:
            retroarchConfig['aspect_ratio_index'] = str(ratioIndexes.index("custom")) # overwritten from the beginning of this file

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
            oldwidth, oldheight = fast_image_size(output_png_file)
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
                eslog.log("Generating a new adapted bezel file {}".format(output_png_file))
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
                    ix,iy = imgin.size
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

    eslog.log("Bezel file set to {}".format(overlay_png_file))
    writeBezelCfgConfig(overlay_cfg_file, overlay_png_file)

def isLowResolution(gameResolution):
    return gameResolution["width"] < 400 or gameResolution["height"] < 400

def writeBezelCfgConfig(cfgFile, overlay_png_file):
    fd = open(cfgFile, "w")
    fd.write("overlays = 1\n")
    fd.write("overlay0_overlay = \"" + overlay_png_file + "\"\n")
    fd.write("overlay0_full_screen = true\n")
    fd.write("overlay0_descs = 0\n")
    fd.close()
