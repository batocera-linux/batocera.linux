#!/usr/bin/env python
import sys
import os
import batoceraFiles
import ConfigParser
from settings.unixSettings import UnixSettings

def generateRetroarchCustom():
    # retroarchcustom.cfg
    if not os.path.exists(os.path.dirname(batoceraFiles.retroarchCustom)):
        os.makedirs(os.path.dirname(batoceraFiles.retroarchCustom))

    try:
        retroarchSettings = UnixSettings(batoceraFiles.retroarchCustom, separator=' ')
    except UnicodeError:
        os.remove(batoceraFiles.retroarchCustom)
        retroarchSettings = UnixSettings(batoceraFiles.retroarchCustom, separator=' ')

    # Path Retroarch
    retroarchSettings.save('core_options_path',             '"/userdata/system/configs/retroarch/cores/retroarch-core-options.cfg"')
    retroarchSettings.save('assets_directory',              '"/usr/share/libretro/assets"')
    retroarchSettings.save('screenshot_directory',          '"/userdata/screenshots/"')
    retroarchSettings.save('recording_output_directory',    '"/userdata/screenshots/"')
    retroarchSettings.save('savestate_directory',           '"/userdata/saves/"')
    retroarchSettings.save('savefile_directory',            '"/userdata/saves/"')
    retroarchSettings.save('extraction_directory',          '"/userdata/extractions/"')
    retroarchSettings.save('cheat_database_path',           '"/usr/share/batocera/datainit/cheats/cht/"')
    retroarchSettings.save('cheat_settings_path',           '"/userdata/cheats/saves/"')
    retroarchSettings.save('system_directory',              '"/userdata/bios/"')
    retroarchSettings.save('joypad_autoconfig_dir',         '"/userdata/system/configs/retroarch/inputs/"')
    retroarchSettings.save('video_shader_dir',              '"/usr/share/batocera/shaders/"')
    retroarchSettings.save('video_font_path',               '"/usr/share/fonts/dejavu/DejaVuSansMono.ttf"')
    retroarchSettings.save('video_filter_dir',              '"/usr/share/video_filters"')
    retroarchSettings.save('audio_filter_dir',              '"/usr/share/audio_filters"')

    # Use Interface
    retroarchSettings.save('menu_driver',                       '"ozone"')
    retroarchSettings.save('content_show_favorites',            '"false"')
    retroarchSettings.save('content_show_images',               '"false"')
    retroarchSettings.save('content_show_music',                '"false"')
    retroarchSettings.save('content_show_video',                '"false"')
    retroarchSettings.save('content_show_history',              '"false"')
    retroarchSettings.save('content_show_playlists',            '"false"')
    retroarchSettings.save('content_show_add',                  '"false"')
    retroarchSettings.save('menu_show_load_core',               '"false"')
    retroarchSettings.save('menu_show_load_content',            '"false"')
    retroarchSettings.save('menu_show_online_updater',          '"false"')
    retroarchSettings.save('menu_show_core_updater',            '"false"')

    # Input
    retroarchSettings.save('input_autodetect_enable',           '"false"')
    retroarchSettings.save('input_joypad_driver',               '"sdl2"')
    retroarchSettings.save('input_player1_analog_dpad_mode',    '"1"')
    retroarchSettings.save('input_player2_analog_dpad_mode',    '"1"')
    retroarchSettings.save('input_player3_analog_dpad_mode',    '"1"')
    retroarchSettings.save('input_player4_analog_dpad_mode',    '"1"')
    retroarchSettings.save('input_enable_hotkey_btn',           '"16"')
    retroarchSettings.save('input_enable_hotkey',               '"escape"')
    retroarchSettings.save('input_exit_emulator',               '"escape"')

    # Video
    retroarchSettings.save('video_aspect_ratio_auto',           '"true"')
    retroarchSettings.save('video_gpu_screenshot',              '"true"')
    retroarchSettings.save('video_shader_enable',               '"false"')
    
    # Audio
    retroarchSettings.save('audio_volume',                       '"8.0"')
    
    # Settings
    retroarchSettings.save('config_save_on_exit',               '"false"')
    retroarchSettings.save('savestate_auto_save',               '"false"')
    retroarchSettings.save('savestate_auto_load',               '"false"')
    retroarchSettings.save('menu_swap_ok_cancel_buttons',       '"true"')
    
    # Accentuation
    retroarchSettings.save('rgui_extended_ascii',               '"true"')

    # Hide the welcome message in Retroarch
    retroarchSettings.save('rgui_show_start_screen',            '"false"')

    # Enable usage of OSD messages (Text messages not in badge)
    retroarchSettings.save('video_font_enable',                 '"false"')

    # Take a screenshot of the savestate
    retroarchSettings.save('savestate_thumbnail_enable',        '"true"')

    # Allow any RetroPad to control the menu (Only the player 1)
    retroarchSettings.save('all_users_control_menu',            '"false"')

    # Show badges in Retroarch cheevos list
    retroarchSettings.save('cheevos_badges_enable',             '"true"')

