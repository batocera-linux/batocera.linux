#!/usr/bin/env python
import sys
import os
import configparser
from settings.unixSettings import UnixSettings
import batoceraFiles
import csv
from pathlib import Path
import controllersConfig

def generateCoreSettings(coreSettings, system, rom, guns, wheels):

    # Amstrad CPC / GX4000
    if (system.config['core'] == 'cap32'):
        # Virtual Keyboard by default (select+start) change to (start+Y)
        coreSettings.save('cap32_combokey', '"y"')
        # Auto Select Model
        if (system.name == 'gx4000'):
            coreSettings.save('cap32_model', '"6128+ (experimental)"')
        elif system.isOptSet('cap32_model'):
            coreSettings.save('cap32_model', '"' + system.config['cap32_model'] + '"')
        else:
            coreSettings.save('cap32_model', '"6128"')
        # Ram size
        if system.isOptSet('cap32_ram'):
            coreSettings.save('cap32_ram', '"' + system.config['cap32_ram'] + '"')
        else:
            coreSettings.save('cap32_ram', '"128"')
        # colour depth
        if system.isOptSet('cap32_colour'):
            coreSettings.save('cap32_gfx_colors', '"' + system.config['cap32_colour'] + '"')
        else:
            coreSettings.save('cap32_gfx_colors', '"24bit"')
        # language
        if system.isOptSet('cap32_language'):
            coreSettings.save('cap32_lang_layout', '"' + system.config['cap32_language'] + '"')
        else:
            coreSettings.save('cap32_lang_layout', '"english"')

    # Atari 800 and 5200
    if (system.config['core'] == 'atari800'):

        if (system.name == 'atari800'):
            # Select Atari 800
            # Let user overide Atari System
            if system.isOptSet('atari800_system'):
                coreSettings.save('atari800_system', '"' + system.config['atari800_system'] + '"')
            else:
                coreSettings.save('atari800_system', '"800XL (64K)"')
            # Video Standard
            if system.isOptSet('atari800_ntscpal'):
                coreSettings.save('atari800_ntscpal', '"' + system.config['atari800_ntscpal'] + '"')
            else:
                coreSettings.save('atari800_ntscpal', '"NTSC"')
            # SIO Acceleration
            if system.isOptSet('atari800_sioaccel'):
                coreSettings.save('atari800_sioaccel', '"' + system.config['atari800_sioaccel'] + '"')
            else:
                coreSettings.save('atari800_sioaccel', '"enabled"')
            # Hi-Res Artifacting
            if system.isOptSet('atari800_artifacting'):
                coreSettings.save('atari800_artifacting', '"' + system.config['atari800_artifacting'] + '"')
            else:
                coreSettings.save('atari800_artifacting', '"disabled"')
            # Internal resolution
            if system.isOptSet('atari800_resolution'):
                coreSettings.save('atari800_resolution', '"' + system.config['atari800_resolution'] + '"')
            else:
                coreSettings.save('atari800_resolution', '""') # Default : 336x240
            # Internal BASIC interpreter
            if system.isOptSet('atari800_internalbasic'):
                coreSettings.save('atari800_internalbasic', '"' + system.config['atari800_internalbasic'] + '"')
            else:
                coreSettings.save('atari800_internalbasic', '"disabled"')

            # WARNING: Now we must stop to use "atari800.cfg" because core options crush them

        else:
            # Select Atari 5200
            coreSettings.save('atari800_system', '"5200"')
            # Autodetect A5200 CartType (Off/On)
            coreSettings.save('atari800_CartType', '"enabled"')
            # Joy Hack (for robotron)
            if system.isOptSet('atari800_opt2'):
                coreSettings.save('atari800_opt2', '"' + system.config['atari800_opt2'] + '"')
            else:
                coreSettings.save('atari800_opt2', '"disabled"')

    # Atari Jaguar
    if (system.config['core'] == 'virtualjaguar'):
        # Fast Blitter (Older, Faster, Less compatible)
        if system.isOptSet('usefastblitter'):
            coreSettings.save('virtualjaguar_usefastblitter', '"' + system.config['usefastblitter'] + '"')
        else:
            coreSettings.save('virtualjaguar_usefastblitter', '"enabled"')
        # Show Bios Bootlogo
        if system.isOptSet('bios_vj'):
            coreSettings.save('virtualjaguar_bios', '"' + system.config['bios_vj'] + '"')
        else:
            coreSettings.save('virtualjaguar_bios', '"enabled"')
        # Doom Res Hack
        if system.isOptSet('doom_res_hack'):
            coreSettings.save('virtualjaguar_doom_res_hack', '"' + system.config['doom_res_hack'] + '"')
        else:
            coreSettings.save('virtualjaguar_doom_res_hack', '"disabled"')

    # Atari Lynx
    if (system.config['core'] == 'handy'):
        # Display rotation
        # Set this option to start game at 'None' because it crash the emulator
        coreSettings.save('handy_rot', '"None"')

    # Commodore 64
    if (system.config['core'] == 'vice_x64') or (system.config['core'] == 'vice_x64sc') or (system.config['core'] == 'vice_xscpu64'):

        # Activate Jiffydos
        coreSettings.save('vice_jiffydos',          '"enabled"')
        # Enable Automatic Load Warp
        coreSettings.save('vice_autoloadwarp',      '"enabled"')
        # Disable Datasette Hotkeys
        coreSettings.save('vice_datasette_hotkeys', '"disabled"')
        # Not Read 'vicerc'
        coreSettings.save('vice_read_vicerc',       '"disabled"')
        # Select Joystick Type
        coreSettings.save('vice_Controller',        '"joystick"')
        # Disable Turbo Fire
        coreSettings.save('vice_turbo_fire',        '"disabled"')
        # Controller options for c64 are in libretroControllers.py
        c64_mapping = { 'a': "---",
                'aspect_ratio_toggle': "---",
                'b': "---",
                'joyport_switch': "RETROK_F10",
                'l': "RETROK_ESCAPE",
                'l2': "RETROK_F11",
                'l3': "SWITCH_JOYPORT",
                'ld': "---",
                'll': "---",
                'lr': "---",
                'lu': "---",
                'r': "RETROK_PAGEUP",
                'r2': "RETROK_LSHIFT",
                'rd': "RETROK_F7",
                'reset': "---",
                'rl': "RETROK_F3",
                'rr': "RETROK_F5",
                'ru': "RETROK_F1",
                'select': "TOGGLE_VKBD",
                'start': "RETROK_RETURN",
                'statusbar': "RETROK_F9",
                'vkbd': "RETROK_F12",
                'warp_mode': "RETROK_F11",
                'turbo_fire_toggle': "RETROK_RCTRL",
                'x': "RETROK_RCTRL",
                'y': "RETROK_SPACE" }
        for key in c64_mapping:
            coreSettings.save('vice_mapper_' + key, c64_mapping[key])

        # Model type
        if system.isOptSet('c64_model'):
            coreSettings.save('vice_c64_model', '"' + system.config['c64_model'] + '"')
        else:
            coreSettings.save('vice_c64_model', '"C64 PAL auto"')
        # Aspect Ratio
        if system.isOptSet('vice_aspect_ratio'):
            coreSettings.save('vice_aspect_ratio', '"' + system.config['vice_aspect_ratio'] + '"')
        else:
            coreSettings.save('vice_aspect_ratio', '"pal"')
        # Zoom Mode
        if system.isOptSet('vice_zoom_mode'):
            if system.config['vice_zoom_mode'] == 'automatic':
                coreSettings.save('vice_crop', '"auto"')
            else:
                coreSettings.save('vice_crop', '"' + system.config['vice_zoom_mode'] + '"')
        else:
            coreSettings.save('vice_crop', '"auto_disable"')
        coreSettings.save('vice_zoom_mode', '"deprecated"')
        # External palette
        if system.isOptSet('vice_external_palette'):
            coreSettings.save('vice_external_palette', '"' + system.config['vice_external_palette'] + '"')
        else:
            coreSettings.save('vice_external_palette', '"colodore"')
        # Button options
        if system.isOptSet('vice_retropad_options'):
            coreSettings.save('vice_retropad_options', '"' + system.config['vice_retropad_options'] + '"')
        else:
            coreSettings.save('vice_retropad_options', '"jump"')
        # Select Controller Port
        if system.isOptSet('vice_joyport'):
            coreSettings.save('vice_joyport', '"' + system.config['vice_joyport'] + '"')
        else:
            coreSettings.save('vice_joyport', '"2"')
        # Select Controller Type
        # gun
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('vice_joyport_type', '"14"')
        else:
            if system.isOptSet('vice_joyport_type'):
                coreSettings.save('vice_joyport_type', '"' + system.config['vice_joyport_type'] + '"')
            else:
                coreSettings.save('vice_joyport_type', '"1"')
        # RAM Expansion Unit (REU)
        if system.isOptSet('vice_ram_expansion_unit'):
            coreSettings.save('vice_ram_expansion_unit', '"' + system.config['vice_ram_expansion_unit'] + '"')
        else:
            coreSettings.save('vice_ram_expansion_unit', '"none"')
        # Keyboard Pass-through for Pad2Key
        if system.isOptSet('vice_keyboard_pass_through'):
            coreSettings.save('vice_physical_keyboard_pass_through', '"' + system.config['vice_keyboard_pass_through'] + '"')
        else:
            coreSettings.save('vice_physical_keyboard_pass_through', '"disabled"')

    # Commodore 128
    if (system.config['core'] == 'vice_x128'):

        # Activate Jiffydos
        coreSettings.save('vice_jiffydos',          '"enabled"')
        # Enable Automatic Load Warp
        coreSettings.save('vice_autoloadwarp',      '"enabled"')
        # Disable Datasette Hotkeys
        coreSettings.save('vice_datasette_hotkeys', '"disabled"')
        # Not Read 'vicerc'
        coreSettings.save('vice_read_vicerc',       '"disabled"')
        # Select Joystick Type
        coreSettings.save('vice_Controller',        '"joystick"')
        # Disable Turbo Fire
        coreSettings.save('vice_turbo_fire',        '"disabled"')

        # Model type
        if system.isOptSet('c128_model'):
            coreSettings.save('vice_c128_model', '"' + system.config['c128_model'] + '"')
        else:
            coreSettings.save('vice_c128_model', '"C128 PAL"')
        # Aspect Ratio
        if system.isOptSet('vice_aspect_ratio'):
            coreSettings.save('vice_aspect_ratio', '"' + system.config['vice_aspect_ratio'] + '"')
        else:
            coreSettings.save('vice_aspect_ratio', '"pal"')
        # Zoom Mode
        if system.isOptSet('vice_zoom_mode'):
            if system.config['vice_zoom_mode'] == 'automatic':
                coreSettings.save('vice_crop', '"auto"')
            else:
                coreSettings.save('vice_crop', '"' + system.config['vice_zoom_mode'] + '"')
        else:
            coreSettings.save('vice_crop', '"auto_disable"')
        coreSettings.save('vice_zoom_mode', '"deprecated"')
        # External palette
        if system.isOptSet('vice_external_palette'):
            coreSettings.save('vice_external_palette', '"' + system.config['vice_external_palette'] + '"')
        else:
            coreSettings.save('vice_external_palette', '"colodore"')
        # Button options
        if system.isOptSet('vice_retropad_options'):
            coreSettings.save('vice_retropad_options', '"' + system.config['vice_retropad_options'] + '"')
        else:
            coreSettings.save('vice_retropad_options', '"disabled"')
        # Select Controller Port
        if system.isOptSet('vice_joyport'):
            coreSettings.save('vice_joyport', '"' + system.config['vice_joyport'] + '"')
        else:
            coreSettings.save('vice_joyport', '"2"')
        # Select Controller Type
        if system.isOptSet('vice_joyport_type'):
            coreSettings.save('vice_joyport_type', '"' + system.config['vice_joyport_type'] + '"')
        else:
            coreSettings.save('vice_joyport_type', '"1"')
        # Keyboard Pass-through for Pad2Key
        if system.isOptSet('vice_keyboard_pass_through'):
            coreSettings.save('vice_physical_keyboard_pass_through', '"' + system.config['vice_keyboard_pass_through'] + '"')
        else:
            coreSettings.save('vice_physical_keyboard_pass_through', '"disabled"')

    # Commodore Plus/4
    if (system.config['core'] == 'vice_xplus4'):

        # Enable Automatic Load Warp
        coreSettings.save('vice_autoloadwarp',      '"enabled"')
        # Disable Datasette Hotkeys
        coreSettings.save('vice_datasette_hotkeys', '"disabled"')
        # Not Read 'vicerc'
        coreSettings.save('vice_read_vicerc',       '"disabled"')
        # Select Joystick Type
        coreSettings.save('vice_Controller',        '"joystick"')
        # Disable Turbo Fire
        coreSettings.save('vice_turbo_fire',        '"disabled"')

        # Model type
        if system.isOptSet('plus4_model'):
            coreSettings.save('vice_plus4_model', '"' + system.config['plus4_model'] + '"')
        else:
            coreSettings.save('vice_plus4_model', '"PLUS4 PAL"')
        # Aspect Ratio
        if system.isOptSet('vice_aspect_ratio'):
            coreSettings.save('vice_aspect_ratio', '"' + system.config['vice_aspect_ratio'] + '"')
        else:
            coreSettings.save('vice_aspect_ratio', '"pal"')
        # Zoom Mode
        if system.isOptSet('vice_zoom_mode'):
            if system.config['vice_zoom_mode'] == 'automatic':
                coreSettings.save('vice_crop', '"auto"')
            else:
                coreSettings.save('vice_crop', '"' + system.config['vice_zoom_mode'] + '"')
        else:
            coreSettings.save('vice_crop', '"auto_disable"')
        coreSettings.save('vice_zoom_mode', '"deprecated"')
        # External palette
        if system.isOptSet('vice_plus4_external_palette'):
            coreSettings.save('vice_plus4_external_palette', '"' + system.config['vice_plus4_external_palette'] + '"')
        else:
            coreSettings.save('vice_plus4_external_palette', '"colodore_ted"')
        # Button options
        if system.isOptSet('vice_retropad_options'):
            coreSettings.save('vice_retropad_options', '"' + system.config['vice_retropad_options'] + '"')
        else:
            coreSettings.save('vice_retropad_options', '"disabled"')
        # Select Controller Port
        if system.isOptSet('vice_joyport'):
            coreSettings.save('vice_joyport', '"' + system.config['vice_joyport'] + '"')
        else:
            coreSettings.save('vice_joyport', '"2"')
        # Select Controller Type
        if system.isOptSet('vice_joyport_type'):
            coreSettings.save('vice_joyport_type', '"' + system.config['vice_joyport_type'] + '"')
        else:
            coreSettings.save('vice_joyport_type', '"1"')
        # Keyboard Pass-through for Pad2Key
        if system.isOptSet('vice_keyboard_pass_through'):
            coreSettings.save('vice_physical_keyboard_pass_through', '"' + system.config['vice_keyboard_pass_through'] + '"')
        else:
            coreSettings.save('vice_physical_keyboard_pass_through', '"disabled"')

    # Commodore VIC-20
    if (system.config['core'] == 'vice_xvic'):

        # Enable Automatic Load Warp
        coreSettings.save('vice_autoloadwarp',      '"enabled"')
        # Disable Datasette Hotkeys
        coreSettings.save('vice_datasette_hotkeys', '"disabled"')
        # Not Read 'vicerc'
        coreSettings.save('vice_read_vicerc',       '"disabled"')
        # Select Joystick Type
        coreSettings.save('vice_Controller',        '"joystick"')
        # Disable Turbo Fire
        coreSettings.save('vice_turbo_fire',        '"disabled"')

        # Model type
        if system.isOptSet('vic20_model'):
            coreSettings.save('vice_vic20_model', '"' + system.config['vic20_model'] + '"')
        else:
            coreSettings.save('vice_vic20_model', '"VIC20 PAL auto"')
        # Aspect Ratio
        if system.isOptSet('vice_aspect_ratio'):
            coreSettings.save('vice_aspect_ratio', '"' + system.config['vice_aspect_ratio'] + '"')
        else:
            coreSettings.save('vice_aspect_ratio', '"pal"')
        # Zoom Mode
        if system.isOptSet('vice_zoom_mode'):
            if system.config['vice_zoom_mode'] == 'automatic':
                coreSettings.save('vice_crop', '"auto"')
            else:
                coreSettings.save('vice_crop', '"' + system.config['vice_zoom_mode'] + '"')
        else:
            coreSettings.save('vice_crop', '"auto_disable"')
        coreSettings.save('vice_zoom_mode', '"deprecated"')
        # External palette
        if system.isOptSet('vice_vic20_external_palette'):
            coreSettings.save('vice_vic20_external_palette', '"' + system.config['vice_vic20_external_palette'] + '"')
        else:
            coreSettings.save('vice_vic20_external_palette', '"colodore_vic"')
        # Button options
        if system.isOptSet('vice_retropad_options'):
            coreSettings.save('vice_retropad_options', '"' + system.config['vice_retropad_options'] + '"')
        else:
            coreSettings.save('vice_retropad_options', '"disabled"')
        # Select Controller Port
        if system.isOptSet('vice_joyport'):
            coreSettings.save('vice_joyport', '"' + system.config['vice_joyport'] + '"')
        else:
            coreSettings.save('vice_joyport', '"2"')
        # Select Controller Type
        if system.isOptSet('vice_joyport_type'):
            coreSettings.save('vice_joyport_type', '"' + system.config['vice_joyport_type'] + '"')
        else:
            coreSettings.save('vice_joyport_type', '"1"')
        # Keyboard Pass-through for Pad2Key
        if system.isOptSet('vice_keyboard_pass_through'):
            coreSettings.save('vice_physical_keyboard_pass_through', '"' + system.config['vice_keyboard_pass_through'] + '"')
        else:
            coreSettings.save('vice_physical_keyboard_pass_through', '"disabled"')

    # Commodore PET
    if (system.config['core'] == 'vice_xpet'):

        # Enable Automatic Load Warp
        coreSettings.save('vice_autoloadwarp',      '"enabled"')
        # Disable Datasette Hotkeys
        coreSettings.save('vice_datasette_hotkeys', '"disabled"')
        # Not Read 'vicerc'
        coreSettings.save('vice_read_vicerc',       '"disabled"')
        # Select Joystick Type
        coreSettings.save('vice_Controller',        '"joystick"')
        # Disable Turbo Fire
        coreSettings.save('vice_turbo_fire',        '"disabled"')

        # Model type
        if system.isOptSet('pet_model'):
            coreSettings.save('vice_pet_model', '"' + system.config['pet_model'] + '"')
        else:
            coreSettings.save('vice_pet_model', '"8032"')
        # Aspect Ratio
        if system.isOptSet('vice_aspect_ratio'):
            coreSettings.save('vice_aspect_ratio', '"' + system.config['vice_aspect_ratio'] + '"')
        else:
            coreSettings.save('vice_aspect_ratio', '"pal"')
        # Zoom Mode
        if system.isOptSet('vice_zoom_mode'):
            if system.config['vice_zoom_mode'] == 'automatic':
                coreSettings.save('vice_crop', '"auto"')
            else:
                coreSettings.save('vice_crop', '"' + system.config['vice_zoom_mode'] + '"')
        else:
            coreSettings.save('vice_crop', '"auto_disable"')
        coreSettings.save('vice_zoom_mode', '"deprecated"')
        # External palette
        if system.isOptSet('vice_pet_external_palette'):
            coreSettings.save('vice_pet_external_palette', '"' + system.config['vice_pet_external_palette'] + '"')
        else:
            coreSettings.save('vice_pet_external_palette', '"default"')
        # Button options
        if system.isOptSet('vice_retropad_options'):
            coreSettings.save('vice_retropad_options', '"' + system.config['vice_retropad_options'] + '"')
        else:
            coreSettings.save('vice_retropad_options', '"disabled"')
        # Select Controller Port
        if system.isOptSet('vice_joyport'):
            coreSettings.save('vice_joyport', '"' + system.config['vice_joyport'] + '"')
        else:
            coreSettings.save('vice_joyport', '"2"')
        # Select Controller Type
        if system.isOptSet('vice_joyport_type'):
            coreSettings.save('vice_joyport_type', '"' + system.config['vice_joyport_type'] + '"')
        else:
            coreSettings.save('vice_joyport_type', '"1"')
        # Keyboard Pass-through for Pad2Key
        if system.isOptSet('vice_keyboard_pass_through'):
            coreSettings.save('vice_physical_keyboard_pass_through', '"' + system.config['vice_keyboard_pass_through'] + '"')
        else:
            coreSettings.save('vice_physical_keyboard_pass_through', '"disabled"')

    # Commodore AMIGA
    if (system.config['core'] == 'puae') or (system.config['core'] == 'puae2021'):
        # Functional mapping for Amiga system
        # If you want to change them, you can add
        # some strings to batocera.conf by using
        # this syntax: SYSTEMNAME.retroarchcore.puae_mapper_BUTTONNAME=VALUE
        if (system.name != 'amigacd32') and not ( system.isOptSet('controller1_puae') and ( system.config['controller1_puae'] == "517" ) ) and not ( system.isOptSet('controller2_puae') and ( system.config['controller2_puae'] == "517" ) ):
            # Controller mapping for A500 and A1200
            uae_mapping = { 'aspect_ratio_toggle': "---",
                'mouse_toggle': "RETROK_RCTRL",
                'statusbar': "RETROK_F11",
                'vkbd': "---",
                'reset': "---",
                'crop_toggle': "RETROK_F12",
                'zoom_mode_toggle': "---",
                'a': "---",
                'b': "---",
                'x': "RETROK_LALT",
                'y': "RETROK_SPACE",
                'l': "RETROK_ESCAPE",
                'l2': "MOUSE_LEFT_BUTTON",
                'l3': "SWITCH_JOYMOUSE",
                'ld': "---",
                'll': "---",
                'lr': "---",
                'lu': "---",
                'r': "RETROK_F1",
                'r2': "MOUSE_RIGHT_BUTTON",
                'r3': "TOGGLE_STATUSBAR",
                'rd': "---",
                'rl': "---",
                'rr': "---",
                'ru': "---",
                'select': "TOGGLE_VKBD",
                'start': "RETROK_RETURN",}
            for key in uae_mapping:
                coreSettings.save('puae_mapper_' + key, uae_mapping[key])
        else:
            # Controller mapping for CD32
            uae_mapping = { 'aspect_ratio_toggle': "---",
                'mouse_toggle': "RETROK_RCTRL",
                'statusbar': "RETROK_F11",
                'vkbd': "---",
                'reset': "---",
                'crop_toggle': "RETROK_F12",
                'zoom_mode_toggle': "---",
                'a': "---",
                'b': "---",
                'x': "---",
                'y': "---",
                'l': "---",
                'l2': "MOUSE_LEFT_BUTTON",
                'l3': "SWITCH_JOYMOUSE",
                'ld': "---",
                'll': "---",
                'lr': "---",
                'lu': "---",
                'r': "---",
                'r2': "MOUSE_RIGHT_BUTTON",
                'r3': "TOGGLE_STATUSBAR",
                'rd': "---",
                'rl': "---",
                'rr': "---",
                'ru': "---",
                'select': "---",
                'start': "---",}
            for key in uae_mapping:
                coreSettings.save('puae_mapper_' + key, uae_mapping[key])
        # Show Video Options
        coreSettings.save('puae_video_options_display', '"enabled"')
        # Amiga Model
        if system.isOptSet('puae_model') and system.config['puae_model'] != 'automatic':
            coreSettings.save('puae_model', '"' + system.config['puae_model'] + '"')
        else:
            if system.name == 'amiga1200':
                coreSettings.save('puae_model', '"A1200"')
            elif system.name == 'amigacd32':
                coreSettings.save('puae_model', '"CD32FR"')
            elif (system.name == 'amigacdtv'):
                coreSettings.save('puae_model', '"CDTV"')
            else:
                # Will default to A500 when booting floppy disks, A600 when booting hard drives
                coreSettings.save('puae_model', '"auto"')

        # CPU Compatibility
        if system.isOptSet('cpu_compatibility'):
            coreSettings.save('puae_cpu_compatibility', '"' + system.config['cpu_compatibility'] + '"')
        else:
            coreSettings.save('puae_cpu_compatibility', '"normal"')
        # CPU Multiplier (Overclock)
        if system.isOptSet('cpu_throttle'):
            coreSettings.save('puae_cpu_throttle', '"' + system.config['cpu_throttle'] + '"')
            coreSettings.save('puae_cpu_multiplier', '"0"')
        else:
            coreSettings.save('puae_cpu_throttle', '"0.0"')
            coreSettings.save('puae_cpu_multiplier', '"0"')
        # CPU Cycle Exact Speed (Overclock)
        if system.isOptSet('cpu_compatibility') and system.config['cpu_compatibility'] == 'exact':
            if system.isOptSet('cpu_multiplier'):
                coreSettings.save('puae_cpu_throttle', '"0.0"')
                coreSettings.save('puae_cpu_multiplier', '"' + system.config['cpu_multiplier'] + '"')
            else:
                coreSettings.save('puae_cpu_throttle', '"0.0"')
                coreSettings.save('puae_cpu_multiplier', '"0"')
        # Standard Video
        if system.isOptSet('video_standard'):
            coreSettings.save('puae_video_standard', '"' + system.config['video_standard'] + '"')
        else:
            coreSettings.save('puae_video_standard', '"PAL auto"')
        # Video Resolution
        if system.isOptSet('video_resolution'):
            coreSettings.save('puae_video_resolution', '"' + system.config['video_resolution'] + '"')
        else:
            coreSettings.save('puae_video_resolution', '"hires"')
        # Zoom Mode
        if system.isOptSet('zoom_mode') and system.config['zoom_mode'] != 'automatic':
            coreSettings.save('puae_crop', '"' + system.config['zoom_mode'] + '"')
        else:
            coreSettings.save('puae_crop', '"auto"')
        coreSettings.save('puae_zoom_mode', '"deprecated"')
        # Frameskip
        if system.isOptSet('gfx_framerate'):
            coreSettings.save('puae_gfx_framerate', '"' + system.config['gfx_framerate'] + '"')
        else:
            coreSettings.save('puae_gfx_framerate', '"disabled"')
        # Mouse Speed
        if system.isOptSet('mouse_speed'):
            coreSettings.save('puae_mouse_speed', '"' + system.config['mouse_speed'] + '"')
        else:
            coreSettings.save('puae_mouse_speed', '"200"')
        # Jump on B
        if system.isOptSet('pad_options'):
            coreSettings.save('puae_retropad_options', '"' + system.config['pad_options'] + '"')
        elif system.name == 'amigacdtv':
            coreSettings.save('puae_retropad_options', '"disabled"')
        else:
            coreSettings.save('puae_retropad_options', '"jump"')

        if (system.name == 'amiga500') or (system.name == 'amiga1200'):
            # Floppy Turbo Speed
            if system.isOptSet('puae_floppy_speed'):
                coreSettings.save('puae_floppy_speed', '"' + system.config['puae_floppy_speed'] + '"')
            else:
                coreSettings.save('puae_floppy_speed', '"100"')
            # 2P Gamepad Mapping (Keyrah)
            if system.isOptSet('keyrah_mapping'):
                coreSettings.save('puae_keyrah_keypad_mappings', '"' + system.config['keyrah_mapping'] + '"')
            else:
                coreSettings.save('puae_keyrah_keypad_mappings', '"enabled"')
            # Whdload Launcher
            if system.isOptSet('whdload'):
                coreSettings.save('puae_use_whdload_prefs', '"' + system.config['whdload'] + '"')
            else:
                coreSettings.save('puae_use_whdload_prefs', '"config"')
            # Disable Emulator Joystick for Pad2Key
            if system.isOptSet('disable_joystick'):
                coreSettings.save('puae_physical_keyboard_pass_through', '"' + system.config['disable_joystick'] + '"')
            else:
                coreSettings.save('puae_physical_keyboard_pass_through', '"disabled"')

        if system.name == 'amigacd32' or (system.name == 'amigacdtv'):
            # Boot animation first inserting CD
            if system.isOptSet('puae_cd_startup_delayed_insert'):
                coreSettings.save('puae_cd_startup_delayed_insert', '"' + system.config['puae_cd_startup_delayed_insert'] + '"')
            else:
                coreSettings.save('puae_cd_startup_delayed_insert', '"disabled"')
            # CD Turbo Speed
            if system.isOptSet('puae_cd_speed'):
                coreSettings.save('puae_cd_speed', '"' + system.config['puae_cd_speed'] + '"')
            else:
                coreSettings.save('puae_cd_speed', '"100"')

        if system.name == 'amigacd32':
            # Jump on A (Blue)
            if system.isOptSet('puae_cd32pad_options'):
                coreSettings.save('puae_cd32pad_options', '"' + system.config['puae_cd32pad_options'] + '"')
            else:
                coreSettings.save('puae_cd32pad_options', '"disabled"')

    # Dolpin Wii
    if (system.config['core'] == 'dolphin'):
        # Wii System Languages
        if system.isOptSet('wii_language'):
            coreSettings.save('dolphin_language', '"' + system.config['wii_language'] + '"')
        else:
            coreSettings.save('dolphin_language', '"English"')
        # Wii Resolution Scale
        if system.isOptSet('wii_resolution'):
            coreSettings.save('dolphin_efb_scale', '"' + system.config['wii_resolution'] + '"')
        else:
            coreSettings.save('dolphin_efb_scale', '"x1 (640 x 528)"')
        # Anisotropic Filtering
        if system.isOptSet('wii_anisotropic'):
            coreSettings.save('dolphin_max_anisotropy', '"' + system.config['wii_anisotropic'] + '"')
        else:
            coreSettings.save('dolphin_max_anisotropy', '"x1"')
        # Wii Tv Mode
        if system.isOptSet('wii_widescreen'):
            coreSettings.save('dolphin_widescreen', '"' + system.config['wii_widescreen'] + '"')
        else:
            coreSettings.save('dolphin_widescreen', '"enabled"')
        # Widescreen Hack
        if system.isOptSet('wii_widescreen_hack'):
            coreSettings.save('dolphin_widescreen_hack', '"' + system.config['wii_widescreen_hack'] + '"')
        else:
            coreSettings.save('dolphin_widescreen_hack', '"disabled"')
        # Shader Compilation Mode
        if system.isOptSet('wii_shader_mode'):
            coreSettings.save('dolphin_shader_compilation_mode', '"' + system.config['wii_shader_mode'] + '"')
        else:
            coreSettings.save('dolphin_shader_compilation_mode', '"sync"')
        # OSD
        if system.isOptSet('wii_osd'):
            coreSettings.save('dolphin_osd_enabled', '"' + system.config['wii_osd'] + '"')
        else:
            coreSettings.save('dolphin_osd_enabled', '"enabled"')
    # Magnavox - Odyssey2 / Phillips Videopac+
    if (system.config['core'] == 'o2em'):
        # Virtual keyboard transparency
        coreSettings.save('o2em_vkbd_transparency', '"25"')
        # Emulated Hardware
        if system.isOptSet('o2em_bios'):
            coreSettings.save('o2em_bios', '"' + system.config['o2em_bios'] + '"')
        elif system.name == 'videopacplus':
            coreSettings.save('o2em_bios', '"g7400.bin"')
        else:
            coreSettings.save('o2em_bios', '"o2rom.bin"')
        # Emulated Hardware
        if system.isOptSet('o2em_region') and system.config['o2em_region'] != "autodetect":
            coreSettings.save('o2em_region', '"' + system.config['o2em_region'] + '"')
        else:
            coreSettings.save('o2em_region', '"auto"')
        # Swap Gamepad
        if system.isOptSet('o2em_swap_gamepads'):
            coreSettings.save('o2em_swap_gamepads', '"' + system.config['o2em_swap_gamepads'] + '"')
        else:
            coreSettings.save('o2em_swap_gamepads', '"disabled"')
        # Crop Overscan
        if system.isOptSet('o2em_crop_overscan'):
            coreSettings.save('o2em_crop_overscan', '"' + system.config['o2em_crop_overscan'] + '"')
        else:
            coreSettings.save('o2em_crop_overscan', '"enabled"')
        # Ghosting effect
        if system.isOptSet('o2em_mix_frames'):
            coreSettings.save('o2em_mix_frames', '"' + system.config['o2em_mix_frames'] + '"')
        else:
            coreSettings.save('o2em_mix_frames', '"disabled"')
        # Audio Filter
        if system.isOptSet('o2em_low_pass_range') and system.config['o2em_low_pass_range'] != "0":
            coreSettings.save('o2em_low_pass_filter', '"enabled"')
            coreSettings.save('o2em_low_pass_range', '"' + system.config['o2em_low_pass_range'] + '"')
        else:
            coreSettings.save('o2em_low_pass_filter', '"disabled"')
            coreSettings.save('o2em_low_pass_range',  '"0"')

    # MAME/MESS/MAMEVirtual
    if (system.config['core'] in [ 'mame', 'mess', 'mamevirtual' ]):
        # Lightgun mode
        coreSettings.save('mame_lightgun_mode', '"lightgun"')
        # Enable cheats
        coreSettings.save('mame_cheats_enable', '"enabled"')
        # CPU Overclock
        if system.isOptSet('mame_cpu_overclock'):
            coreSettings.save('mame_cpu_overclock', '"' + system.config['mame_cpu_overclock'] + '"')
        else:
            coreSettings.save('mame_cpu_overclock', '"default"')
        # Video Resolution
        if system.isOptSet('mame_altres'):
            coreSettings.save('mame_altres', '"' + system.config['mame_altres'] + '"')
        else:
            coreSettings.save('mame_altres', '"640x480"')
        # Disable controller profiling
        coreSettings.save('mame_buttons_profiles', '"disabled"')
        # Software Lists (MESS)
        coreSettings.save('mame_softlists_enable', '"disabled"')
        coreSettings.save('mame_softlists_auto_media', '"disabled"')
        # Enable config reading (for controls)
        coreSettings.save('mame_read_config', '"enabled"')
        # Use CLI (via CMD file) to boot
        coreSettings.save('mame_boot_from_cli', '"enabled"')
        # Activate mouse for Mac & Archimedes
        if system.name in [ 'macintosh', 'archimedes' ]:
            coreSettings.save('mame_mouse_enable', '"enabled"')
        else:
            coreSettings.save('mame_mouse_enable', '"disabled"')

    # SAME_CDI
    if (system.config['core'] == 'same_cdi'):
        # Lightgun mode
        coreSettings.save('same_cdi_lightgun_mode', '"lightgun"')
        # Enable cheats
        coreSettings.save('same_cdi_cheats_enable', '"enabled"')
        # CPU Overclock
        if system.isOptSet('same_cdi_cpu_overclock'):
            coreSettings.save('same_cdi_cpu_overclock', '"' + system.config['same_cdi_cpu_overclock'] + '"')
        else:
            coreSettings.save('same_cdi_cpu_overclock', '"default"')
        # Video Resolution
        if system.isOptSet('same_cdi_altres'):
            coreSettings.save('same_cdi_altres', '"' + system.config['same_cdi_altres'] + '"')
        else:
            coreSettings.save('same_cdi_altres', '"640x480"')
        # Disable controller profiling
        coreSettings.save('same_cdi_buttons_profiles', '"disabled"')
        # Software Lists (MESS)
        coreSettings.save('same_cdi_softlists_enable', '"disabled"')
        coreSettings.save('same_cdi_softlists_auto_media', '"disabled"')
        # Enable config reading (for controls)
        coreSettings.save('same_cdi_read_config', '"enabled"')
        # Use CLI (via CMD file) to boot
        coreSettings.save('same_cdi_boot_from_cli', '"enabled"')
        # Activate mouse
        coreSettings.save('same_cdi_mouse_enable', '"enabled"')

    # MAME 2003 Plus
    if (system.config['core'] == 'mame078plus'):
        # Skip Disclaimer and Warnings
        coreSettings.save('mame2003-plus_skip_disclaimer', '"enabled"')
        coreSettings.save('mame2003-plus_skip_warnings',   '"enabled"')
        # Control Mapping
        if system.isOptSet('mame2003-plus_analog'):
            coreSettings.save('mame2003-plus_analog', '"' + system.config['mame2003-plus_analog'] + '"')
        else:
            coreSettings.save('mame2003-plus_analog', '"digital"')
        # Frameskip
        if system.isOptSet('mame2003-plus_frameskip'):
            coreSettings.save('mame2003-plus_frameskip', '"' + system.config['mame2003-plus_frameskip'] + '"')
        else:
            coreSettings.save('mame2003-plus_frameskip', '"0"')
        # Input interface
        if system.isOptSet('mame2003-plus_input_interface'):
            coreSettings.save('mame2003-plus_input_interface', '"' + system.config['mame2003-plus_input_interface'] + '"')
        else:
            coreSettings.save('mame2003-plus_input_interface', '"retropad"')
        # TATE Mode
        if system.isOptSet('mame2003-plus_tate_mode'):
            coreSettings.save('mame2003-plus_tate_mode', '"' + system.config['mame2003-plus_tate_mode'] + '"')
        else:
            coreSettings.save('mame2003-plus_tate_mode', '"disabled"')
        # NEOGEO Bios
        if system.isOptSet('mame2003-plus_neogeo_bios'):
            coreSettings.save('mame2003-plus_neogeo_bios', '"' + system.config['mame2003-plus_neogeo_bios'] + '"')
        else:
            coreSettings.save('mame2003-plus_neogeo_bios', '"unibios33"')

        # gun
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('mame2003-plus_xy_device', '"lightgun"')
        else:
            coreSettings.save('mame2003-plus_xy_device', '"mouse"')
        # gun cross
        if system.isOptSet('mame2003-plus_crosshair_enabled'):
            coreSettings.save('mame2003-plus_crosshair_enabled', '"' + system.config['mame2003-plus_crosshair_enabled'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"enabled"'
            else:
                status = '"disabled"'
            coreSettings.save('mame2003-plus_crosshair_enabled', status)

    # MAME 2010
    if (system.config['core'] == 'mame0139'):
        # Skip Gameinfo / Nagscreen / Disclamers
        coreSettings.save('mame_current_skip_gameinfo',    '"enabled"')
        coreSettings.save('mame_current_skip_nagscreen',   '"enabled"')
        coreSettings.save('mame_current_skip_warnings',    '"enabled"')
        # Frameskip
        if system.isOptSet('mame_current_frame_skip'):
            coreSettings.save('mame_current_frame_skip', '"' + system.config['mame_current_frame_skip'] + '"')
        else:
            coreSettings.save('mame_current_frame_skip', '"0"')
        # Enable autofire
        if system.isOptSet('mame_current_turbo_button'):
            coreSettings.save('mame_current_turbo_button', '"' + system.config['mame_current_turbo_button'] + '"')
        else:
            coreSettings.save('mame_current_turbo_button', '"disabled"')
        # Set autofire pulse speed
        if system.isOptSet('mame_current_turbo_delay'):
            coreSettings.save('mame_current_turbo_delay', '"' + system.config['mame_current_turbo_delay'] + '"')
        else:
            coreSettings.save('mame_current_turbo_delay', '"medium"')

    # TODO: Add CORE options for MAME / iMame4all

    # MB Vectrex
    if (system.config['core'] == 'vecx'):
        # Res Multiplier
        if system.isOptSet('res_multi'):
            coreSettings.save('vecx_res_multi', '"' + system.config['res_multi'] + '"')
        else:
            coreSettings.save('vecx_res_multi', '"1"')

    # Microsoft DOS
    if (system.config['core'] == 'dosbox_pure'):
        # CPU Type
        if system.isOptSet('pure_cpu_type') and system.config['pure_cpu_type'] != "automatic":
            coreSettings.save('dosbox_pure_cpu_type', '"' + system.config['pure_cpu_type'] + '"')
        else:
            coreSettings.save('dosbox_pure_cpu_type', '"auto"')
        # CPU Core
        if system.isOptSet('pure_cpu_core') and system.config['pure_cpu_core'] != "automatic":
            coreSettings.save('dosbox_pure_cpu_core', '"' + system.config['pure_cpu_core'] + '"')
        else:
            coreSettings.save('dosbox_pure_cpu_core', '"auto"')
        # Emulated performance (CPU Cycles)
        if system.isOptSet('pure_cycles') and system.config['pure_cycles'] != "automatic":
            coreSettings.save('dosbox_pure_cycles', '"' + system.config['pure_cycles'] + '"')
        else:
            coreSettings.save('dosbox_pure_cycles', '"auto"')
        # Graphics Chip type
        if system.isOptSet('pure_machine'):
            coreSettings.save('dosbox_pure_machine', '"' + system.config['pure_machine'] + '"')
        else:
            coreSettings.save('dosbox_pure_machine', '"svga"')
        # Memory size
        if system.isOptSet('pure_memory_size'):
            coreSettings.save('dosbox_pure_memory_size', '"' + system.config['pure_memory_size'] + '"')
        else:
            coreSettings.save('dosbox_pure_memory_size', '"16"')
        # Save state
        if system.isOptSet('pure_savestate'):
            coreSettings.save('dosbox_pure_savestate', '"' + system.config['pure_savestate'] + '"')
        else:
            coreSettings.save('dosbox_pure_savestate', '"on"')
        # Keyboard Layout
        if system.isOptSet('pure_keyboard_layout'):
            coreSettings.save('dosbox_pure_keyboard_layout', '"' + system.config['pure_keyboard_layout'] + '"')
        else:
            coreSettings.save('dosbox_pure_keyboard_layout', '"us"')
        # Automatic Gamepad Mapping
        if system.isOptSet('pure_auto_mapping'):
            coreSettings.save('dosbox_pure_auto_mapping', '"' + system.config['pure_auto_mapping'] + '"')
        else:
            coreSettings.save('dosbox_pure_auto_mapping', '"true"')
        # Joystick Analog Deadzone
        if system.isOptSet('pure_joystick_analog_deadzone'):
            coreSettings.save('dosbox_pure_joystick_analog_deadzone', '"' + system.config['pure_joystick_analog_deadzone'] + '"')
        else:
            coreSettings.save('dosbox_pure_joystick_analog_deadzone', '"15"')
        # Enable Joystick Timed Intervals
        if system.isOptSet('pure_joystick_timed'):
            coreSettings.save('dosbox_pure_joystick_timed', '"' + system.config['pure_joystick_timed'] + '"')
        else:
            coreSettings.save('dosbox_pure_joystick_timed', '"true"')
        # SoundBlaster Type
        if system.isOptSet('pure_sblaster_type'):
            coreSettings.save('dosbox_pure_sblaster_type', '"' + system.config['pure_sblaster_type'] + '"')
        else:
            coreSettings.save('dosbox_pure_sblaster_type', '"sb16"')
        # Enable Gravis Sound
        if system.isOptSet("pure_gravis"):
            coreSettings.save("dosbox_pure_gus", '"' + system.config['pure_gravis'] + '"')
        else:
            coreSettings.save("dosbox_pure_gus", '"false"')
        # Midi Type
        if system.isOptSet('pure_midi'):
            coreSettings.save('dosbox_pure_midi', '"' + system.config['pure_midi'] + '"')
        else:
            coreSettings.save('dosbox_pure_midi', '"disabled"')

    # Microsoft MSX and Colecovision
    if (system.config['core'] == 'bluemsx'):
        # Auto Select Core
        if (system.name == 'colecovision'):
            coreSettings.save('bluemsx_msxtype', '"ColecoVision"')
        elif (system.name == 'msx1'):
            coreSettings.save('bluemsx_msxtype', '"MSX"')
        elif (system.name == 'msx2'):
            coreSettings.save('bluemsx_msxtype', '"MSX2"')
        elif (system.name == 'msx2+'):
            coreSettings.save('bluemsx_msxtype', '"MSX2+"')
        elif (system.name == 'msxturbor'):
            coreSettings.save('bluemsx_msxtype', '"MSXturboR"')
        # Forces cropping of overscanned frames
        if system.name == 'colecovision' or system.name == 'msx1':
            coreSettings.save('bluemsx_overscan', '"enabled"')
        else:
            coreSettings.save('bluemsx_overscan', '"MSX2"')
        # Reduce Sprite Flickering
        if system.isOptSet('bluemsx_nospritelimits') and system.config['bluemsx_nospritelimits'] == "False":
            coreSettings.save('bluemsx_nospritelimits', '"OFF"')
        else:
            coreSettings.save('bluemsx_nospritelimits', '"ON"')
        # Zoom, Hide Video Border
        if system.isOptSet('bluemsx_overscan'):
            coreSettings.save('bluemsx_overscan', '"' + system.config['bluemsx_overscan'] + '"')
        else:
            coreSettings.save('bluemsx_overscan', '"MSX2"')

    # Nec PC Engine / CD
    if system.config['core'] == 'pce' or system.config['core'] == 'pce_fast':
        # Remove 16-sprites-per-scanline hardware limit
        if system.isOptSet('pce_nospritelimit'):
            coreSettings.save('pce_nospritelimit', '"' + system.config['pce_nospritelimit'] + '"')
        else:
            coreSettings.save('pce_nospritelimit', '"enabled"')

    # Nec PC-8800
    if system.config['core'] == 'quasi88':
        # PC Model
        if system.isOptSet('q88_basic_mode'):
            coreSettings.save('q88_basic_mode', '"' + system.config['q88_basic_mode'] + '"')
        else:
            coreSettings.save('q88_basic_mode', '"N88 V2"')
        # CPU clock (Overclock)
        if system.isOptSet('q88_cpu_clock'):
            coreSettings.save('q88_cpu_clock', '"' + system.config['q88_cpu_clock'] + '"')
        else:
            coreSettings.save('q88_cpu_clock', '"4"')
        # Use PCG-8100
        if system.isOptSet('q88_pcg-8100'):
            coreSettings.save('q88_pcg-8100', '"' + system.config['q88_pcg-8100'] + '"')
        else:
            coreSettings.save('q88_pcg-8100', '"disabled"')

    # Nec PC-9800
    # https://github.com/AZO234/NP2kai/blob/6e8f651a72c2ece37cc52e17cdaf4fdb87a6b2f9/sdl/libretro/libretro_core_options.h
    if system.config['core'] == 'np2kai':
        # Use the American keyboard
        coreSettings.save('np2kai_keyboard', '"Us"')
        # Fast memcheck at startup
        coreSettings.save('np2kai_FastMC', '"ON"')
        # Sound Generator: Use "fmgen" for enhanced sound rendering, not "Default"
        #coreSettings.save('np2kai_usefmgen', '"fmgen"')
        # PC Model
        if system.isOptSet('np2kai_model'):
            coreSettings.save('np2kai_model', '"' + system.config['np2kai_model'] + '"')
        else:
            coreSettings.save('np2kai_model', '"PC-9801VX"')
        # CPU Feature
        if system.isOptSet('np2kai_cpu_feature'):
            coreSettings.save('np2kai_cpu_feature', '"' + system.config['np2kai_cpu_feature'] + '"')
        else:
            coreSettings.save('np2kai_cpu_feature', '"Intel 80386"')
        # CPU Clock Multiplier
        if system.isOptSet('np2kai_clk_mult'):
            coreSettings.save('np2kai_clk_mult', '"' + system.config['np2kai_clk_mult'] + '"')
        else:
            coreSettings.save('np2kai_clk_mult', '"4"')
        # RAM Size
        if system.isOptSet('np2kai_ExMemory'):
            coreSettings.save('np2kai_ExMemory', '"' + system.config['np2kai_ExMemory'] + '"')
        else:
            coreSettings.save('np2kai_ExMemory', '"3"')
        # GDC
        if system.isOptSet('np2kai_gdc'):
            coreSettings.save('np2kai_gdc', '"' + system.config['np2kai_gdc'] + '"')
        else:
            coreSettings.save('np2kai_gdc', '"uPD7220"')
        # Remove Scanlines (255 lines)
        if system.isOptSet('np2kai_skipline') and system.config['np2kai_skipline'] != "Full 255 lines":
            if system.config['np2kai_skipline'] == "True":
                coreSettings.save('np2kai_skipline', '"ON"')
            else:
                coreSettings.save('np2kai_skipline', '"OFF"')
        else:
            coreSettings.save('np2kai_skipline', '"Full 255 lines"')
        # Real Palettes
        if system.isOptSet('np2kai_realpal') and system.config['np2kai_realpal'] == "True":
            coreSettings.save('np2kai_realpal', '"ON"')
        else:
            coreSettings.save('np2kai_realpal', '"OFF"')
        # Sound Board
        if system.isOptSet('np2kai_SNDboard'):
            coreSettings.save('np2kai_SNDboard', '"' + system.config['np2kai_SNDboard'] + '"')
        else:
            coreSettings.save('np2kai_SNDboard', '"PC9801-26K + 86"')
        # JAST SOUND
        if system.isOptSet('np2kai_jast_snd') and system.config['np2kai_jast_snd'] == "True":
            coreSettings.save('np2kai_jast_snd', '"ON"')
        else:
            coreSettings.save('np2kai_jast_snd', '"OFF"')
        # Joypad to Keyboard Mapping
        if system.isOptSet('np2kai_joymode'):
            coreSettings.save('np2kai_joymode', '"' + system.config['np2kai_joymode'] + '"')
        else:
            coreSettings.save('np2kai_joymode', '"Arrows"')

    # Nec PC Engine SuperGrafx
    if (system.config['core'] == 'mednafen_supergrafx'):
        # Remove 16-sprites-per-scanline hardware limit
        if system.isOptSet('sgx_nospritelimit'):
            coreSettings.save('sgx_nospritelimit', '"' + system.config['sgx_nospritelimit'] + '"')
        else:
            coreSettings.save('sgx_nospritelimit', '"enabled"')

    # Nec PC-FX
    if (system.config['core'] == 'pcfx'):
        # Remove 16-sprites-per-scanline hardware limit
        if system.isOptSet('pcfx_nospritelimit'):
            coreSettings.save('pcfx_nospritelimit', '"' + system.config['pcfx_nospritelimit'] + '"')
        else:
            coreSettings.save('pcfx_nospritelimit', '"enabled"')

    # Nintendo 3DS
    # TODO: Add CORE Options for 3DS
    if (system.config['core'] == 'citra'):
        # Set OpenGL rendering
        if not os.path.exists(batoceraFiles.CONF + "/retroarch/3ds.cfg"):
            f = open(batoceraFiles.CONF + "/retroarch/3ds.cfg", "w")
            f.write("video_driver = \"glcore\"\n")
            f.close()

    # Nintendo 64
    if (system.config['core'] == 'mupen64plus-next'):
        # Threaded Rendering
        coreSettings.save('mupen64plus-ThreadedRenderer', '"True"')
        # Use High-Res Textures Pack
        # .htc files must be placed in 'Mupen64plus/cache'
        coreSettings.save('mupen64plus-txHiresEnable', '"True"')
        # Video 4:3 Resolution
        if system.isOptSet('mupen64plus-43screensize') and system.config['mupen64plus-43screensize'] != '320x240':
            coreSettings.save('mupen64plus-43screensize', '"' + system.config['mupen64plus-43screensize'] + '"')
        else:
            coreSettings.save('mupen64plus-43screensize', '"320x240"')
        # Video 16:9 Resolution
        if system.isOptSet('mupen64plus-169screensize') and system.config['mupen64plus-169screensize'] != '640x360':
            coreSettings.save('mupen64plus-169screensize', '"' + system.config['mupen64plus-169screensize'] + '"')
        else:
            coreSettings.save('mupen64plus-169screensize', '"640x360"')
        # Widescreen Hack
        # Increases from 4:3 to 16:9 in 3D games (bad for 2D)
        if system.isOptSet('mupen64plus-aspect') and system.isOptSet('ratio') and system.isOptSet('bezel') and system.config['mupen64plus-aspect'] == '16:9 adjusted' and system.config["ratio"] == "16/9" and system.config["bezel"] == "none":
            coreSettings.save('mupen64plus-aspect', '"16:9 adjusted"')
        else:
            coreSettings.save('mupen64plus-aspect', '"4:3"')
        # Bilinear Filtering
        if system.isOptSet('mupen64plus-BilinearMode') and system.config['mupen64plus-BilinearMode'] == '3point':
            coreSettings.save('mupen64plus-BilinearMode', '"3point"')
        else:
            coreSettings.save('mupen64plus-BilinearMode', '"standard"')
        # Anti-aliasing (MSA)
        if system.isOptSet('mupen64plus-MultiSampling') and system.config['mupen64plus-MultiSampling'] != '0':
            coreSettings.save('mupen64plus-MultiSampling', '"' + system.config['mupen64plus-MultiSampling'] + '"')
        else:
            coreSettings.save('mupen64plus-MultiSampling', '"0"')
        # Texture Filtering
        if system.isOptSet('mupen64plus-txFilterMode') and system.config['mupen64plus-txFilterMode'] != 'None':
            coreSettings.save('mupen64plus-txFilterMode', '"' + system.config['mupen64plus-txFilterMode'] + '"')
        else:
            coreSettings.save('mupen64plus-txFilterMode', '"None"')
        # Texture Enhancement
        if system.isOptSet('mupen64plus-txEnhancementMode') and system.config['mupen64plus-txEnhancementMode'] != 'None':
            coreSettings.save('mupen64plus-txEnhancementMode', '"' + system.config['mupen64plus-txEnhancementMode'] + '"')
        else:
            coreSettings.save('mupen64plus-txEnhancementMode', '"None"')

        # Check if any controller packs are set to auto rumble
        auto_rumble_pak = None
        for pak in range(1, 5):
            pak_value = f'mupen64plus-pak{pak}'
            if system.isOptSet(pak_value) and system.config[pak_value] == 'auto_rumble':
                auto_rumble_pak = pak_value
                break

        if auto_rumble_pak:
            metadata = controllersConfig.getGamesMetaData(system.name, rom)

        # Controller Pak 1
        if system.isOptSet('mupen64plus-pak1'):
            if system.config['mupen64plus-pak1'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('mupen64plus-pak1', '"rumble"')
                else:
                    coreSettings.save('mupen64plus-pak1', '"memory"')
            else:
                coreSettings.save('mupen64plus-pak1', '"' + system.config['mupen64plus-pak1'] + '"')
        else:
            coreSettings.save('mupen64plus-pak1', '"memory"')
        # Controller Pak 2
        if system.isOptSet('mupen64plus-pak2'):
            if system.config['mupen64plus-pak2'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('mupen64plus-pak2', '"rumble"')
                else:
                    coreSettings.save('mupen64plus-pak2', '"none"')
            else:
                coreSettings.save('mupen64plus-pak2', '"' + system.config['mupen64plus-pak2'] + '"')
        else:
            coreSettings.save('mupen64plus-pak2', '"none"')
        # Controller Pak 3
        if system.isOptSet('mupen64plus-pak3'):
            if system.config['mupen64plus-pak3'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('mupen64plus-pak3', '"rumble"')
                else:
                    coreSettings.save('mupen64plus-pak3', '"none"')
            else:
                coreSettings.save('mupen64plus-pak3', '"' + system.config['mupen64plus-pak3'] + '"')
        else:
            coreSettings.save('mupen64plus-pak3', '"none"')
        # Controller Pak 4
        if system.isOptSet('mupen64plus-pak4'):
            if system.config['mupen64plus-pak4'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('mupen64plus-pak4', '"rumble"')
                else:
                    coreSettings.save('mupen64plus-pak4', '"none"')
            else:
                coreSettings.save('mupen64plus-pak4', '"' + system.config['mupen64plus-pak4'] + '"')
        else:
            coreSettings.save('mupen64plus-pak4', '"none"')
        # RDP Plugin
        if system.isOptSet('mupen64plus-rdpPlugin'):
            coreSettings.save('mupen64plus-rdp-plugin', '"' + system.config['mupen64plus-rdpPlugin'] + '"')
        else:
            coreSettings.save('mupen64plus-rdp-plugin', '"gliden64"')
        # RSP Plugin
        if system.isOptSet('mupen64plus-rspPlugin'):
            coreSettings.save('mupen64plus-rsp-plugin', '"' + system.config['mupen64plus-rspPlugin'] + '"')
        else:
            coreSettings.save('mupen64plus-rsp-plugin', '"hle"')
        # CPU Core
        if system.isOptSet('mupen64plus-cpuCore'):
            coreSettings.save('mupen64plus-cpucore', '"' + system.config['mupen64plus-cpuCore'] + '"')
        else:
            coreSettings.save('mupen64plus-cpucore', '"dynamic_recompiler"')
        # Framerate
        if system.isOptSet('mupen64plus-Framerate'):
            coreSettings.save('mupen64plus-Framerate', '"' + system.config['mupen64plus-Framerate'] + '"')
        else:
            coreSettings.save('mupen64plus-Framerate', '"Original"')
        # Parallel-RDP Upscaling
        if system.isOptSet('mupen64plus-parallel-rdp-upscaling'):
            coreSettings.save('mupen64plus-parallel-rdp-upscaling', '"' + system.config['mupen64plus-parallel-rdp-upscaling'] + '"')
        else:
            coreSettings.save('mupen64plus-parallel-rdp-upscaling', '"1x"')
        # Joystick deadzone
        if system.isOptSet('mupen64plus-deadzone'):
            coreSettings.save('mupen64plus-astick-deadzone', '"' + system.config['mupen64plus-deadzone'] + '"')
        else:
            if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels') and len(wheels) > 0:
                coreSettings.save('mupen64plus-astick-deadzone', '"0"')
            else:
                coreSettings.save('mupen64plus-astick-deadzone', '"15"')

        # Joystick sensitivity
        if system.isOptSet('mupen64plus-sensitivity'):
            coreSettings.save('mupen64plus-astick-sensitivity', '"' + system.config['mupen64plus-sensitivity'] + '"')
        else:
            coreSettings.save('mupen64plus-astick-sensitivity', '"100"')

    if (system.config['core'] == 'parallel_n64'):
        coreSettings.save('parallel-n64-64dd-hardware', '"disabled"')
        coreSettings.save('parallel-n64-boot-device',   '"Default"')

        # Graphics Plugin
        if system.isOptSet('parallel-n64-gfxplugin'):
            coreSettings.save('parallel-n64-gfxplugin', '"' + system.config['parallel-n64-gfxplugin'] + '"')
        else:
            # vulkan doesn't work with auto
            if system.isOptSet('gfxbackend') and system.config['gfxbackend'] == "vulkan":
                coreSettings.save('parallel-n64-gfxplugin', '"parallel"')
            else:
                coreSettings.save('parallel-n64-gfxplugin', '"auto"')
        # Video Resolution
        if system.isOptSet('parallel-n64-screensize'):
            coreSettings.save('parallel-n64-screensize', '"' + system.config['parallel-n64-screensize'] + '"')
        else:
            coreSettings.save('parallel-n64-screensize', '"320x240"')
        # Widescreen Hack
        # Increases from 4:3 to 16:9 in 3D games (bad for 2D)
        if system.isOptSet('parallel-n64-aspectratiohint') and system.isOptSet('ratio') and system.isOptSet('bezel') and system.config['parallel-n64-aspectratiohint'] == 'widescreen' and system.config["ratio"] == "16/9" and system.config["bezel"] == "none":
            coreSettings.save('parallel-n64-aspectratiohint', '"widescreen"')
        else:
            coreSettings.save('parallel-n64-aspectratiohint', '"normal"')
        # Texture Filtering
        if system.isOptSet('parallel-n64-filtering'):
            coreSettings.save('parallel-n64-filtering', '"' + system.config['parallel-n64-filtering'] + '"')
        else:
            coreSettings.save('parallel-n64-filtering', '"automatic"')
        # Framerate
        if system.isOptSet('parallel-n64-framerate'):
            coreSettings.save('parallel-n64-framerate', '"' + system.config['parallel-n64-framerate'] + '"')
        else:
            coreSettings.save('parallel-n64-framerate', '"automatic"')

        # Check if any controller packs are set to auto rumble
        auto_rumble_pak = None
        for pak in range(1, 5):
            pak_value = f'parallel-n64-pak{pak}'
            if system.isOptSet(pak_value) and system.config[pak_value] == 'auto_rumble':
                auto_rumble_pak = pak_value
                break

        if auto_rumble_pak:
            metadata = controllersConfig.getGamesMetaData(system.name, rom)

        # Controller Pak 1
        if system.isOptSet('parallel-n64-pak1'):
            if system.config['parallel-n64-pak1'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('parallel-n64-pak1', '"rumble"')
                else:
                    coreSettings.save('parallel-n64-pak1', '"memory"')
            else:
                coreSettings.save('parallel-n64-pak1', '"' + system.config['parallel-n64-pak1'] + '"')
        else:
            coreSettings.save('parallel-n64-pak1', '"memory"')
        # Controller Pak 2
        if system.isOptSet('parallel-n64-pak2'):
            if system.config['parallel-n64-pak2'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('parallel-n64-pak2', '"rumble"')
                else:
                    coreSettings.save('parallel-n64-pak2', '"none"')
            else:
                coreSettings.save('parallel-n64-pak2', '"' + system.config['parallel-n64-pak2'] + '"')
        else:
            coreSettings.save('parallel-n64-pak2', '"none"')
        # Controller Pak 3
        if system.isOptSet('parallel-n64-pak3'):
            if system.config['parallel-n64-pak3'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('parallel-n64-pak3', '"rumble"')
                else:
                    coreSettings.save('parallel-n64-pak3', '"none"')
            else:
                coreSettings.save('parallel-n64-pak3', '"' + system.config['parallel-n64-pak3'] + '"')
        else:
            coreSettings.save('parallel-n64-pak3', '"none"')
        # Controller Pak 4
        if system.isOptSet('parallel-n64-pak4'):
            if system.config['parallel-n64-pak4'] == 'auto_rumble':
                if metadata.get("controller_rumble") == "true":
                    coreSettings.save('parallel-n64-pak4', '"rumble"')
                else:
                    coreSettings.save('parallel-n64-pak4', '"none"')
            else:
                coreSettings.save('parallel-n64-pak4', '"' + system.config['parallel-n64-pak4'] + '"')
        else:
            coreSettings.save('parallel-n64-pak4', '"none"')
        # Joystick deadzone
        if system.isOptSet('parallel-n64-deadzone'):
            coreSettings.save('parallel-n64-astick-deadzone', '"' + system.config['parallel-n64-deadzone'] + '"')
        else:
            if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels') and len(wheels) > 0:
                coreSettings.save('parallel-n64-astick-deadzone', '"0"')
            else:
                coreSettings.save('parallel-n64-astick-deadzone', '"15"')

        # Joystick sensitivity
        if system.isOptSet('parallel-n64-sensitivity'):
            coreSettings.save('parallel-n64-astick-sensitivity', '"' + system.config['parallel-n64-sensitivity'] + '"')
        else:
            coreSettings.save('parallel-n64-astick-sensitivity', '"100"')

        # Nintendo 64-DD
        if (system.name == 'n64dd'):
            # 64DD Hardware
            coreSettings.save('parallel-n64-64dd-hardware', '"enabled"')
            # Boot device
            coreSettings.save('parallel-n64-boot-device',   '"64DD IPL"')


    # Nintendo DS
    if (system.config['core'] == 'desmume'):
        # Emulate Stylus on Right Stick
        coreSettings.save('desmume_pointer_device_r', '"emulated"')
        # Internal Resolution
        if system.isOptSet('internal_resolution_desmume'):
            coreSettings.save('desmume_internal_resolution', '"' + system.config['internal_resolution_desmume'] + '"')
        else:
            coreSettings.save('desmume_internal_resolution', '"256x192"')
        # Anti-aliasing (MSAA)
        if system.isOptSet('multisampling'):
            coreSettings.save('desmume_gfx_multisampling', '"' + system.config['multisampling'] + '"')
        else:
            coreSettings.save('desmume_gfx_multisampling', '"disabled"')
        # Texture Smoothing
        if system.isOptSet('texture_smoothing'):
            coreSettings.save('desmume_gfx_texture_smoothing', '"' + system.config['texture_smoothing'] + '"')
        else:
            coreSettings.save('desmume_gfx_texture_smoothing', '"disabled"')
        # Textures Upscaling (XBRZ)
        if system.isOptSet('texture_scaling'):
            coreSettings.save('desmume_gfx_texture_scaling', '"' + system.config['texture_scaling'] + '"')
        else:
            coreSettings.save('desmume_gfx_texture_scaling', '"1"')
        # Frame Skip
        if system.isOptSet('frameskip_desmume'):
            coreSettings.save('desmume_frameskip', '"' + system.config['frameskip_desmume'] + '"')
        else:
            coreSettings.save('desmume_frameskip', '"0"')
        # Screen Layout
        if system.isOptSet('screens_layout'):
            coreSettings.save('desmume_screens_layout', '"' + system.config['screens_layout'] + '"')
        else:
            coreSettings.save('desmume_screens_layout', '"top/bottom"')

    if (system.config['core'] == 'melonds'):
        # Console Mode
        if system.isOptSet('melonds_console_mode'):
            coreSettings.save('melonds_console_mode', '"' + system.config['melonds_console_mode'] + '"')
        else:
            coreSettings.save('melonds_console_mode', '"DS"')
        # Language
        if system.isOptSet('melonds_language'):
            coreSettings.save('melonds_language', '"' + system.config['melonds_language'] + '"')
        else:
            coreSettings.save('melonds_language', '"English"')
        # External Firmware
        if system.isOptSet('melonds_use_fw_settings'):
            coreSettings.save('melonds_use_fw_settings', '"' + system.config['melonds_use_fw_settings'] + '"')
        else:
            coreSettings.save('melonds_use_fw_settings', '"disable"')
        # Enable threaded rendering
        coreSettings.save('melonds_threaded_renderer', '"enabled"')
        # Emulate Stylus on Right Stick
        if system.isOptSet('melonds_touch_mode'):
            coreSettings.save('melonds_touch_mode',  '"' + system.config['melonds_touch_mode'] + '"')
        else:
            coreSettings.save('melonds_touch_mode','"Joystick"')
        # Boot game directly
        if system.isOptSet('melonds_boot_directly'):
            coreSettings.save('melonds_boot_directly', '"' + system.config['melonds_boot_directly'] + '"')
        else:
            coreSettings.save('melonds_boot_directly', '"enabled"')
        # Screen Layout + Hybrid Ratio
        coreSettings.save('melonds_hybrid_ratio', '"2"')
        if system.isOptSet('melonds_screen_layout'):
            if system.config['melonds_screen_layout']   == "Hybrid Top-Ratio2":
                coreSettings.save('melonds_screen_layout', '"Hybrid Top"')
            elif system.config['melonds_screen_layout'] == "Hybrid Top-Ratio3":
                coreSettings.save('melonds_screen_layout', '"Hybrid Top"')
                coreSettings.save('melonds_hybrid_ratio',  '"3"')
            elif system.config['melonds_screen_layout'] == "Hybrid Bottom-Ratio2":
                coreSettings.save('melonds_screen_layout', '"Hybrid Bottom"')
            elif system.config['melonds_screen_layout'] == "Hybrid Bottom-Ratio3":
                coreSettings.save('melonds_screen_layout', '"Hybrid Bottom"')
                coreSettings.save('melonds_hybrid_ratio',  '"3"')
            else:
                coreSettings.save('melonds_screen_layout', '"' + system.config['melonds_screen_layout'] + '"')
        else:
            coreSettings.save('melonds_screen_layout',     '"Top/Bottom"')

    if (system.config['core'] == 'melondsds'):
        # System Settings
        if system.isOptSet('melondsds_console_mode'):
            coreSettings.save('melonds_console_mode', '"' + system.config['melonds_console_mode'] + '"')
        else:
            coreSettings.save('melonds_console_mode', '"DS"')

        # Video Settings
        if system.isOptSet('melondsds_render_mode'):
            coreSettings.save('melonds_render_mode', '"' + system.config['melondsds_render_mode'] + '"')
        else:
            coreSettings.save('melonds_render_mode', '"software"')
        if system.isOptSet('melondsds_resolution'):
            coreSettings.save('melonds_opengl_resolution', '"' + system.config['melondsds_resolution'] + '"')
        else:
            coreSettings.save('melonds_render_mode', '"1"')
        if system.isOptSet('melondsds_poygon'):
            coreSettings.save('melonds_opengl_better_polygons', '"' + system.config['melondsds_poygon'] + '"')
        else:
            coreSettings.save('melonds_opengl_better_polygons', '"disabled"')
        if system.isOptSet('melondsds_filtering'):
            coreSettings.save('melonds_opengl_filtering', '"' + system.config['melondsds_filtering'] + '"')
        else:
            coreSettings.save('melonds_opengl_filtering', '"nearest"')

        # Screen Settings
        if system.isOptSet('melondsds_cursor'):
            coreSettings.save('melonds_show_cursor', '"' + system.config['melondsds_cursor'] + '"')
        else:
            coreSettings.save('melonds_show_cursor', '"nearest"')
        if system.isOptSet('melondsds_cursor_timeout'):
            coreSettings.save('melonds_cursor_timeout', '"' + system.config['melondsds_cursor_timeout'] + '"')
        else:
            coreSettings.save('melonds_cursor_timeout', '"3"')
        if system.isOptSet('melondsds_touchmode'):
            coreSettings.save('melonds_touch_mode', '"' + system.config['melondsds_touchmode'] + '"')
        else:
            coreSettings.save('melonds_touch_mode', '"auto"')
        # set 1 screen for now top/botton
        coreSettings.save('melonds_number_of_screen_layouts', '"1"')
        coreSettings.save('melonds_screen_gap', '"0"')
        coreSettings.save('melonds_screen_layout1', '"top-bottom"')

        # Firmware Settings
        if system.isOptSet('melondsds_dns'):
            coreSettings.save('melonds_firmware_wfc_dns', '"' + system.config['melondsds_dns'] + '"')
        else:
            coreSettings.save('melonds_firmware_wfc_dns', '"178.62.43.212"')
        if system.isOptSet('melondsds_language'):
            coreSettings.save('melonds_firmware_language', '"' + system.config['melondsds_language'] + '"')
        else:
            coreSettings.save('melonds_firmware_language', '"default"')
        if system.isOptSet('melondsds_colour'):
            coreSettings.save('melonds_firmware_favorite_color', '"' + system.config['melondsds_colour'] + '"')
        else:
            coreSettings.save('melonds_firmware_favorite_color', '"default"')
        if system.isOptSet('melondsds_month'):
            coreSettings.save('melonds_firmware_birth_month', '"' + system.config['melondsds_month'] + '"')
        else:
            coreSettings.save('melonds_firmware_birth_month', '"default"')
        if system.isOptSet('melondsds_day'):
            coreSettings.save('melonds_firmware_birth_day', '"' + system.config['melondsds_day'] + '"')
        else:
            coreSettings.save('melonds_firmware_birth_day', '"default"')

        # Onscreen Display
        if system.isOptSet('melondsds_show_unsupported'):
            coreSettings.save('melonds_show_unsupported_features', '"' + system.config['melondsds_show_unsupported'] + '"')
        else:
            coreSettings.save('melonds_show_unsupported_features', '"disabled"')
        if system.isOptSet('melondsds_show_bios'):
            coreSettings.save('melonds_show_bios_warnings', '"' + system.config['melondsds_show_bios'] + '"')
        else:
            coreSettings.save('melonds_show_bios_warnings', '"disabled"')
        if system.isOptSet('melondsds_show_layout'):
            coreSettings.save('melonds_show_current_layout', '"' + system.config['melondsds_show_layout'] + '"')
        else:
            coreSettings.save('melonds_show_current_layout', '"disabled"')
        if system.isOptSet('melondsds_show_mic'):
            coreSettings.save('melonds_show_mic_state', '"' + system.config['melondsds_show_mic'] + '"')
        else:
            coreSettings.save('melonds_show_mic_state', '"disabled"')
        if system.isOptSet('melondsds_show_camera'):
            coreSettings.save('melonds_show_camera_state', '"' + system.config['melondsds_show_camera'] + '"')
        else:
            coreSettings.save('melonds_show_camera_state', '"disabled"')
        if system.isOptSet('melondsds_show_lid'):
            coreSettings.save('melonds_show_lid_state', '"' + system.config['melondsds_show_lid'] + '"')
        else:
            coreSettings.save('melonds_show_lid_state', '"disabled"')

    # Nintendo Gameboy (Dual Screen) / GB Color (Dual Screen)
    if (system.config['core'] == 'tgbdual'):
        # Emulates two Game Boy units
        coreSettings.save('tgbdual_gblink_enable',    '"enabled"')
        # Displays the selected player screens
        coreSettings.save('tgbdual_single_screen_mp', '"both players"')
        # Switches the screen layout
        coreSettings.save('tgbdual_screen_placement', '"left-right"')
        # Switch Game Boy sound
        coreSettings.save('tgbdual_audio_output',     '"Game Boy #1"')
        # Switches the player screens
        coreSettings.save('tgbdual_switch_screens',   '"normal"')

    # Nintendo Gameboy / GB Color / GB Advance
    if (system.config['core'] == 'gambatte'):
        # GB / GBC: Use official Bootlogo
        if system.isOptSet('gb_bootloader'):
            coreSettings.save('gambatte_gb_bootloader', '"' + system.config['gb_bootloader'] + '"')
        else:
            coreSettings.save('gambatte_gb_bootloader', '"enabled"')
        # GB / GBC: Interframe Blending (LCD ghosting effects)
        if system.isOptSet('gb_mix_frames'):
            coreSettings.save('gambatte_mix_frames', '"' + system.config['gb_mix_frames'] + '"')
        else:
            coreSettings.save('gambatte_mix_frames', '"disabled"')

        if (system.name == 'gbc'):
            # GBC Color Correction
            if system.isOptSet('gbc_color_correction'):
                coreSettings.save('gambatte_gbc_color_correction', '"' + system.config['gbc_color_correction'] + '"')
            else:
                coreSettings.save('gambatte_gbc_color_correction', '"disabled"')
        elif (system.name == 'gb'):
            coreSettings.save('gambatte_gbc_color_correction', '"disabled"')

        if (system.name == 'gb'):
            # GB: Colorization of GB games
            if system.isOptSet('gb_colorization'):
                if system.config['gb_colorization'] == 'none':                           #No Selection --> Classic Green
                    coreSettings.save('gambatte_gb_colorization',     '"internal"')
                    coreSettings.save('gambatte_gb_internal_palette', '"Special 1"')
                elif system.config['gb_colorization'] == 'GB - Disabled':                #Disabled --> Black and White Color
                    coreSettings.save('gambatte_gb_colorization',     '"disabled"')
                    coreSettings.save('gambatte_gb_internal_palette', '"Special 1"')
                elif system.config['gb_colorization'] == 'GB - SmartColor':              #Smart Coloring --> Gambatte's most colorful/appropriate color
                    coreSettings.save('gambatte_gb_colorization',     '"auto"')
                    coreSettings.save('gambatte_gb_internal_palette', '"Special 1"')
                elif system.config['gb_colorization'] == 'custom':                       #Custom Palettes --> Use the custom palettes in the bios/palettes folder
                    coreSettings.save('gambatte_gb_colorization',     '"custom"')
                    coreSettings.save('gambatte_gb_internal_palette', '"Special 1"')
                else:                                                                    #User Selection
                    coreSettings.save('gambatte_gb_colorization',     '"internal"')
                    coreSettings.save('gambatte_gb_internal_palette', '"' + system.config['gb_colorization'] + '"')
            else:
                coreSettings.save('gambatte_gb_colorization',         '"internal"')      #It's an empty file, set to Classic Green
                coreSettings.save('gambatte_gb_internal_palette',     '"Special 1"')

    if (system.config['core'] == 'mgba'):
        # Skip BIOS intro
        if system.isOptSet('skip_bios_mgba') and system.config['skip_bios_mgba'] == "True":
            coreSettings.save('mgba_skip_bios', '"ON"')
        else:
            coreSettings.save('mgba_skip_bios', '"OFF"')

        # Rumble
        if system.isOptSet('rumble_gain') and system.config['rumble_gain'] != "1":
            coreSettings.save('mgba_force_gbp', '"ON"')
        else:
            coreSettings.save('mgba_force_gbp', '"OFF"')

        if (system.name != 'gba'):
            # GB / GBC: Use Super Game Boy borders
            if system.isOptSet('sgb_borders') and system.config['sgb_borders'] == "True":
                coreSettings.save('mgba_sgb_borders', '"ON"')
            else:
                coreSettings.save('mgba_sgb_borders', '"OFF"')
            # GB / GBC: Color Correction
            if system.isOptSet('color_correction') and system.config['color_correction'] != "False":
                coreSettings.save('mgba_color_correction', '"' + system.config['color_correction'] + '"')
            else:
                coreSettings.save('mgba_color_correction', '"OFF"')

        if (system.name == 'gba'):
            # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
            if system.isOptSet('solar_sensor_level'):
                coreSettings.save('mgba_solar_sensor_level', '"' + system.config['solar_sensor_level'] + '"')
            else:
                coreSettings.save('mgba_solar_sensor_level', '"0"')
            # GBA: Frameskip
            if system.isOptSet('frameskip_mgba'):
                coreSettings.save('mgba_frameskip', '"' + system.config['frameskip_mgba'] + '"')
            else:
                coreSettings.save('mgba_frameskip', '"0"')
        # Force Super Game Boy mode for SGB system, auto for all others
        # No current option to override - add if needed.
        if (system.name == 'sgb'):
            coreSettings.save('mgba_gb_model', '"Super Game Boy"')
            # Default border to on for SGB
            if system.isOptSet('sgb_borders') and system.config['sgb_borders'] == "OFF":
                coreSettings.save('mgba_sgb_borders', '"OFF"')
            else:
                coreSettings.save('mgba_sgb_borders', '"ON"')
        else:
            coreSettings.save('mgba_gb_model', '"Autodetect"')

    if (system.config['core'] == 'vba-m'):
        # GB / GBC / GBA: Auto select fine hardware mode
        # Emulator AUTO mode not working fine
        if system.name == 'gb':
            coreSettings.save('vbam_gbHardware', '"gb"')
        elif system.name == 'gbc':
            coreSettings.save('vbam_gbHardware', '"gbc"')
        else:
            coreSettings.save('vbam_gbHardware', '"gba"')

        if (system.name == 'gb'):
        # GB: Colorisation of GB games
            if system.isOptSet('palettes'):
                coreSettings.save('vbam_palettes', '"' + system.config['palettes'] + '"')
            else:
                coreSettings.save('vbam_palettes', '"black and white"')

        if (system.name != 'gba'):
            # GB / GBC: Use Super Game Boy borders
            if system.isOptSet('showborders_gb') and system.name == 'gb':
                coreSettings.save('vbam_showborders', '"' + system.config['showborders_gb'] + '"')
                # Force SGB mode, "sgb2" is same
                coreSettings.save('vbam_gbHardware', '"sgb"')
            elif system.isOptSet('showborders_gbc') and system.name == 'gbc':
                coreSettings.save('vbam_showborders', '"' + system.config['showborders_gbc'] + '"')
                # Force SGB mode, "sgb2" is same
                coreSettings.save('vbam_gbHardware', '"sgb"')
            else:
                coreSettings.save('vbam_showborders', '"disabled"')
            # GB / GBC: Color Correction
            if system.isOptSet('gbcoloroption_gb') and system.name == 'gb':
                coreSettings.save('vbam_gbcoloroption', '"' + system.config['gbcoloroption_gb'] + '"')
            elif system.isOptSet('gbcoloroption_gbc') and system.name == 'gbc':
                coreSettings.save('vbam_gbcoloroption', '"' + system.config['gbcoloroption_gbc'] + '"')
            else:
                coreSettings.save('vbam_gbcoloroption', '"disabled"')

        if (system.name == 'gba'):
            # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
            if system.isOptSet('solarsensor'):
                coreSettings.save('vbam_solarsensor', '"' + system.config['solarsensor'] + '"')
            else:
                coreSettings.save('vbam_solarsensor', '"0"')
            # GBA: Sensor Sensitivity (Gyroscope) (%)
            if system.isOptSet('gyro_sensitivity'):
                coreSettings.save('vbam_gyro_sensitivity', '"' + system.config['gyro_sensitivity'] + '"')
            else:
                coreSettings.save('vbam_gyro_sensitivity', '"10"')
            # GBA: Sensor Sensitivity (Tilt) (%)
            if system.isOptSet('tilt_sensitivity'):
                coreSettings.save('vbam_tilt_sensitivity', '"' + system.config['tilt_sensitivity'] + '"')
            else:
                coreSettings.save('vbam_tilt_sensitivity', '"10"')

    # Nintendo NES / Famicom Disk System
    if (system.config['core'] == 'nestopia'):
        # gun
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('nestopia_zapper_device', '"lightgun"')
        else:
            # Mouse mode for Zapper
            coreSettings.save('nestopia_zapper_device', '"mouse"')

        # gun cross
        if system.isOptSet('nestopia_show_crosshair'):
            coreSettings.save('nestopia_show_crosshair', '"' + system.config['nestopia_show_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"enabled"'
            else:
                status = '"disabled"'
            coreSettings.save('nestopia_show_crosshair', status)

        # Reduce Sprite Flickering
        if system.isOptSet('nestopia_nospritelimit') and system.config['nestopia_nospritelimit'] == "disabled":
            coreSettings.save('nestopia_nospritelimit', '"disabled"')
        else:
            coreSettings.save('nestopia_nospritelimit', '"enabled"')
        # Crop Overscan
        if system.isOptSet('nestopia_cropoverscan') and system.config['nestopia_cropoverscan'] == "none":
            coreSettings.save('nestopia_overscan_h_left', '"0"')
            coreSettings.save('nestopia_overscan_h_right', '"0"')
            coreSettings.save('nestopia_overscan_v_top', '"0"')
            coreSettings.save('nestopia_overscan_v_bottom', '"0"')
        elif system.isOptSet('nestopia_cropoverscan') and system.config['nestopia_cropoverscan'] == "h":
            coreSettings.save('nestopia_overscan_h_left', '"8"')
            coreSettings.save('nestopia_overscan_h_right', '"8"')
            coreSettings.save('nestopia_overscan_v_top', '"0"')
            coreSettings.save('nestopia_overscan_v_bottom', '"0"')
        elif system.isOptSet('nestopia_cropoverscan') and system.config['nestopia_cropoverscan'] == "both":
            coreSettings.save('nestopia_overscan_h_left', '"8"')
            coreSettings.save('nestopia_overscan_h_right', '"8"')
            coreSettings.save('nestopia_overscan_v_top', '"8"')
            coreSettings.save('nestopia_overscan_v_bottom', '"8"')
        else:
            coreSettings.save('nestopia_overscan_h_left', '"0"')
            coreSettings.save('nestopia_overscan_h_right', '"0"')
            coreSettings.save('nestopia_overscan_v_top', '"8"')
            coreSettings.save('nestopia_overscan_v_bottom', '"8"')
        # Palette Choice
        if system.isOptSet('nestopia_palette'):
            coreSettings.save('nestopia_palette', '"' + system.config['nestopia_palette'] + '"')
        else:
            coreSettings.save('nestopia_palette', '"consumer"')
        # NTSC Filter
        if system.isOptSet('nestopia_blargg_ntsc_filter'):
            coreSettings.save('nestopia_blargg_ntsc_filter', '"' + system.config['nestopia_blargg_ntsc_filter'] + '"')
        else:
            coreSettings.save('nestopia_blargg_ntsc_filter', '"disabled"')
        # CPU Overclock
        if system.isOptSet('nestopia_overclock'):
            coreSettings.save('nestopia_overclock', '"' + system.config['nestopia_overclock'] + '"')
        else:
            coreSettings.save('nestopia_overclock', '"1x"')
        # 4 Player Adapter
        if system.isOptSet('nestopia_select_adapter') and system.config['nestopia_select_adapter'] != "automatic":
            coreSettings.save('nestopia_select_adapter', '"' + system.config['nestopia_select_adapter'] + '"')
        else:
            coreSettings.save('nestopia_select_adapter', '"auto"')

    if (system.config['core'] == 'fceumm'):
        # gun
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('fceumm_zapper_mode', '"lightgun"')
        else:
            # FCEumm Mouse mode for Zapper
            coreSettings.save('fceumm_zapper_mode', '"mouse"')

        # gun cross
        if system.isOptSet('fceumm_show_crosshair'):
            coreSettings.save('fceumm_show_crosshair', '"' + system.config['fceumm_show_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"enabled"'
            else:
                status = '"disabled"'
            coreSettings.save('fceumm_show_crosshair', status)

        # Reduce Sprite Flickering
        if system.isOptSet('fceumm_nospritelimit') and system.config['fceumm_nospritelimit'] == "disabled":
            coreSettings.save('fceumm_nospritelimit', '"disabled"')
        else:
            coreSettings.save('fceumm_nospritelimit', '"enabled"')
        # Crop Overscan
        if system.isOptSet('fceumm_cropoverscan') and system.config['fceumm_cropoverscan'] == "none":
            coreSettings.save('fceumm_overscan_h_left', '"0"')
            coreSettings.save('fceumm_overscan_h_right', '"0"')
            coreSettings.save('fceumm_overscan_v_top', '"0"')
            coreSettings.save('fceumm_overscan_v_bottom', '"0"')
        elif system.isOptSet('fceumm_cropoverscan') and system.config['fceumm_cropoverscan'] == "h":
            coreSettings.save('fceumm_overscan_h_left', '"8"')
            coreSettings.save('fceumm_overscan_h_right', '"8"')
            coreSettings.save('fceumm_overscan_v_top', '"0"')
            coreSettings.save('fceumm_overscan_v_bottom', '"0"')
        elif system.isOptSet('fceumm_cropoverscan') and system.config['fceumm_cropoverscan'] == "both":
            coreSettings.save('fceumm_overscan_h_left', '"8"')
            coreSettings.save('fceumm_overscan_h_right', '"8"')
            coreSettings.save('fceumm_overscan_v_top', '"8"')
            coreSettings.save('fceumm_overscan_v_bottom', '"8"')
        else:
            coreSettings.save('fceumm_overscan_h_left', '"0"')
            coreSettings.save('fceumm_overscan_h_right', '"0"')
            coreSettings.save('fceumm_overscan_v_top', '"8"')
            coreSettings.save('fceumm_overscan_v_bottom', '"8"')
        # Palette Choice
        if system.isOptSet('fceumm_palette'):
            coreSettings.save('fceumm_palette', '"' + system.config['fceumm_palette'] + '"')
        else:
            coreSettings.save('fceumm_palette', '"default"')
        # NTSC Filter
        if system.isOptSet('fceumm_ntsc_filter'):
            coreSettings.save('fceumm_ntsc_filter', '"' + system.config['fceumm_ntsc_filter'] + '"')
        else:
            coreSettings.save('fceumm_ntsc_filter', '"disabled"')
        # Sound Quality
        if system.isOptSet('fceumm_sndquality'):
            coreSettings.save('fceumm_sndquality', '"' + system.config['fceumm_sndquality'] + '"')
        else:
            coreSettings.save('fceumm_sndquality', '"Low"')
        # PPU Overclocking
        if system.isOptSet('fceumm_overclocking'):
            coreSettings.save('fceumm_overclocking', '"' + system.config['fceumm_overclocking'] + '"')
        else:
            coreSettings.save('fceumm_overclocking', '"disabled"')

    if (system.config['core'] == 'mesen'):
        if system.isOptSet('mesen_region'):
            coreSettings.save('mesen_region', '"' + system.config['mesen_region'] + '"')
        else:
            coreSettings.save('mesen_region', '"Auto"')
        # Screen rotation (for homebrew)
        if system.isOptSet('mesen_screenrotation'):
            coreSettings.save('mesen_screenrotation', '"' + system.config['mesen_screenrotation'] + '"')
        else:
            coreSettings.save('mesen_screenrotation', '"None"')
        # NTSC Filter
        if system.isOptSet('mesen_ntsc_filter'):
            coreSettings.save('mesen_ntsc_filter', '"' + system.config['mesen_ntsc_filter'] + '"')
        else:
            coreSettings.save('mesen_ntsc_filter', '"Disabled"')
        # Sprite limit removal
        if system.isOptSet('mesen_nospritelimit'):
            coreSettings.save('mesen_nospritelimit', '"' + system.config['mesen_nospritelimit'] + '"')
        else:
            coreSettings.save('mesen_nospritelimit', '"disabled"')
        # Palette
        if system.isOptSet('mesen_palette'):
            coreSettings.save('mesen_palette', '"' + system.config['mesen_palette'] + '"')
        else:
            coreSettings.save('mesen_palette', '"Default"')
        # HD texture replacements
        if system.isOptSet('mesen_hdpacks'):
            coreSettings.save('mesen_hdpacks', '"' + system.config['mesen_hdpacks'] + '"')
        else:
            coreSettings.save('mesen_hdpacks', '"enabled"')
        # FDS Auto-insert side A
        if system.isOptSet('mesen_fdsautoinsertdisk'):
            coreSettings.save('mesen_fdsautoinsertdisk', '"' + system.config['mesen_fdsautoinsertdisk'] + '"')
        else:
            coreSettings.save('mesen_fdsautoinsertdisk', '"disabled"')
        # FDS Fast forward floppy disk loading
        if system.isOptSet('mesen_fdsfastforwardload'):
            coreSettings.save('mesen_fdsfastforwardload', '"' + system.config['mesen_fdsautoinsertdisk'] + '"')
        else:
            coreSettings.save('mesen_fdsfastforwardload', '"disabled"')
        # RAM init state (speedrunning)
        if system.isOptSet('mesen_ramstate'):
            coreSettings.save('mesen_ramstate', '"' + system.config['mesen_ramstate'] + '"')
        else:
            coreSettings.save('mesen_ramstate', '"All 0s (Default)"')
        # NES CPU Overclock
        if system.isOptSet('mesen_overclock'):
            coreSettings.save('mesen_overclock', '"' + system.config['mesen_overclock'] + '"')
        else:
            coreSettings.save('mesen_overclock', '"None"')
        # Overclocking type (compatibility)
        if system.isOptSet('mesen_overclock_type'):
            coreSettings.save('mesen_overclock_type', '"' + system.config['mesen_overclock_type'] + '"')
        else:
            coreSettings.save('mesen_overclock_type', '"Before NMI (Recommended)"')

    # Nintendo Pokemon Mini
    if (system.config['core'] == 'pokemini'):
        # LCD Filter
        if system.isOptSet('pokemini_lcdfilter'):
            coreSettings.save('pokemini_lcdfilter', '"' + system.config['pokemini_lcdfilter'] + '"')
        else:
            coreSettings.save('pokemini_lcdfilter', '"dotmatrix"')
        # LCD Ghosting Effects
        if system.isOptSet('pokemini_lcdmode'):
            coreSettings.save('pokemini_lcdmode', '"' + system.config['pokemini_lcdmode'] + '"')
        else:
            coreSettings.save('pokemini_lcdmode', '"analog"')

    # Nintendo SNES
    if (system.config['core'] == 'snes9x'):
        # Reduce sprite flickering (Hack, Unsafe)
        if system.isOptSet('reduce_sprite_flicker'):
            coreSettings.save('snes9x_reduce_sprite_flicker', '"' + system.config['reduce_sprite_flicker'] + '"')
        else:
            coreSettings.save('snes9x_reduce_sprite_flicker', '"enabled"')
        # Reduce Slowdown (Hack, Unsafe)
        if system.isOptSet('reduce_slowdown'):
            coreSettings.save('snes9x_overclock_cycles', '"' + system.config['reduce_slowdown'] + '"')
        else:
            coreSettings.save('snes9x_overclock_cycles', '"disabled"')
        # SuperFX Overclocking
        if system.isOptSet('overclock_superfx'):
            coreSettings.save('snes9x_overclock_superfx', '"' + system.config['overclock_superfx'] + '"')
        else:
            coreSettings.save('snes9x_overclock_superfx', '"100%"')
        # Hi-Res Blending
        if system.isOptSet('hires_blend'):
            coreSettings.save('snes9x_hires_blend', '"' + system.config['hires_blend'] + '"')
        else:
            coreSettings.save('snes9x_hires_blend', '"disabled"')
        # Blargg NTSC Filter
        if system.isOptSet('snes9x_blargg_filter'):
            coreSettings.save('snes9x_blargg', '"' + system.config['snes9x_blargg_filter'] + '"')
        else:
            coreSettings.save('snes9x_blargg', '"disabled"')
        # Crosshair
        if system.isOptSet('superscope_crosshair'):
            coreSettings.save('snes9x_superscope_crosshair', '"' + system.config['superscope_crosshair'] + '"')
            coreSettings.save('snes9x_justifier1_crosshair', '"' + system.config['superscope_crosshair'] + '"')
            coreSettings.save('snes9x_justifier2_crosshair', '"' + system.config['superscope_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"2"'
            else:
                status = '"0"'
            coreSettings.save('snes9x_superscope_crosshair', status)
            coreSettings.save('snes9x_justifier1_crosshair', status)
            coreSettings.save('snes9x_justifier2_crosshair', status)
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('snes9x_superscope_reverse_buttons', '"disabled"')

    if (system.config['core'] == 'snes9x_next'):
        # Reduce sprite flickering (Hack, Unsafe)
        if system.isOptSet('2010_reduce_sprite_flicker'):
            coreSettings.save('snes9x_2010_reduce_sprite_flicker', '"' + system.config['2010_reduce_sprite_flicker'] + '"')
        else:
            coreSettings.save('snes9x_2010_reduce_sprite_flicker', '"enabled"')
        # Reduce Slowdown (Hack, Unsafe)
        if system.isOptSet('2010_reduce_slowdown'):
            coreSettings.save('snes9x_2010_overclock_cycles', '"' + system.config['2010_reduce_slowdown'] + '"')
        else:
            coreSettings.save('snes9x_2010_overclock_cycles', '"disabled"')
        # SuperFX Overclocking
        if system.isOptSet('2010_overclock_superfx'):
            coreSettings.save('snes9x_2010_overclock', '"' + system.config['2010_overclock_superfx'] + '"')
        else:
            coreSettings.save('snes9x_2010_overclock', '"10 MHz (Default)"')
        # Blargg NTSC Filter
        if system.isOptSet('snes9x_2010_blargg_filter'):
            coreSettings.save('snes9x_2010_blargg', '"' + system.config['snes9x_2010_blargg_filter'] + '"')
        else:
            coreSettings.save('snes9x_2010_blargg', '"disabled"')
        # Crosshair
        if system.isOptSet('superscope_crosshair'):
            coreSettings.save('snes9x_2010_superscope_crosshair', '"' + system.config['superscope_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"2"'
            else:
                status = '"disabled"'
            coreSettings.save('snes9x_2010_superscope_crosshair', status)

    # TODO: Add CORE options for BSnes and PocketSNES
    if (system.config['core'] == 'bsnes'):
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('bsnes_touchscreen_lightgun_superscope_reverse', '"OFF"')
        # Video Filters
        if system.isOptSet('bsnes_video_filter'):
            coreSettings.save('bsnes_video_filter', '"' + system.config['bsnes_video_filter'] + '"')
        else:
            coreSettings.save('bsnes_video_filter', '"disabled"')

    # Nintendo SNES/GB/GBC/SGB
    if (system.config['core'] == 'mesen-s'):
        # Force appropriate Game Boy mode for the system (unless overriden)
        if (system.name == 'sgb') and not system.isOptSet('mesen-s_gbmodel'):
            coreSettings.save('mesen-s_gbmodel', '"Super Game Boy"')
        elif (system.name == 'gb') and not system.isOptSet('mesen-s_gbmodel'):
            coreSettings.save('mesen-s_gbmodel', '"Game Boy"')
        elif (system.name == 'gbc') and not system.isOptSet('mesen-s_gbmodel'):
            coreSettings.save('mesen-s_gbmodel', '"Game Boy Color"')
        elif system.isOptSet('mesen-s_gbmodel'):
            coreSettings.save('mesen-s_gbmodel', '"' + system.config['mesen-s_gbmodel'] + '"')
        else:
            coreSettings.save('mesen-s_gbmodel', '"Auto"')
        # SGB2 Enable
        if system.isOptSet('mesen-s_sgb2'):
            coreSettings.save('mesen-s_sgb2', '"' + system.config['mesen-s_sgb2'] + '"')
        else:
            coreSettings.save('mesen-s_sgb2', '"enabled"')
        # NTSC Filter
        if system.isOptSet('mesen-s_ntsc_filter'):
            coreSettings.save('mesen-s_ntsc_filter', '"' + system.config['mesen-s_ntsc_filter'] + '"')
        else:
            coreSettings.save('mesen-s_ntsc_filter', '"disabled"')
        # Blending for high-res mode (Kirby's Dream Land 3 pseudo-transparency)
        if system.isOptSet('mesen-s_blend_high_res'):
            coreSettings.save('mesen-s_blend_high_res', '"' + system.config['mesen-s_blend_high_res'] + '"')
        else:
            coreSettings.save('mesen-s_blend_high_res', '"disabled"')
        # Change sound interpolation to cubic
        if system.isOptSet('mesen-s_cubic_interpolation'):
            coreSettings.save('mesen-s_cubic_interpolation', '"' + system.config['mesen-s_cubic_interpolation'] + '"')
        else:
            coreSettings.save('mesen-s_cubic_interpolation', '"disabled"')
        # SNES CPU Overclock
        if system.isOptSet('mesen-s_overclock'):
            coreSettings.save('mesen-s_overclock', '"' + system.config['mesen-s_overclock'] + '"')
        else:
            coreSettings.save('mesen-s_overclock', '"None"')
        # Overclocking type (compatibility)
        if system.isOptSet('mesen-s_overclock_type'):
            coreSettings.save('mesen-s_overclock_type', '"' + system.config['mesen-s_overclock_type'] + '"')
        else:
            coreSettings.save('mesen-s_overclock_type', '"Before NMI"')
        # SuperFX Overclock
        if system.isOptSet('mesen-s_superfx_overclock'):
            coreSettings.save('mesen-s_superfx_overclock', '"' + system.config['mesen-s_superfx_overclock'] + '"')
        else:
            coreSettings.save('mesen-s_superfx_overclock', '"100%"')

    # Nintendo Virtual Boy
    if (system.config['core'] == 'vb'):
        # 2D Color Mode
        if system.isOptSet('2d_color_mode'):
            coreSettings.save('vb_color_mode', '"' + system.config['2d_color_mode'] + '"')
        else:
            coreSettings.save('vb_color_mode', '"black & red"')
        # 3D Glasses Color Mode
        if system.isOptSet('3d_color_mode'):
            coreSettings.save('vb_anaglyph_preset', '"' + system.config['3d_color_mode'] + '"')
        else:
            coreSettings.save('vb_anaglyph_preset', '"disabled"')

    # Panasonic 3DO
    if (system.config['core'] == 'opera'):
        # Audio Process on separate CPU thread
        coreSettings.save('opera_dsp_threaded', '"enabled"')
        # High Resolution (640x480)
        if system.isOptSet('high_resolution'):
            coreSettings.save('opera_high_resolution', '"' + system.config['high_resolution'] + '"')
        else:
            coreSettings.save('opera_high_resolution', '"enabled"')
        # CPU Overclock
        if system.isOptSet('cpu_overclock'):
            coreSettings.save('opera_cpu_overclock', '"' + system.config['cpu_overclock'] + '"')
        else:
            coreSettings.save('opera_cpu_overclock', '"1.0x (12.50Mhz)"')
        # Active Input Devices Fix
        if system.isOptSet('active_devices'):
            coreSettings.save('opera_active_devices', '"' + system.config['active_devices'] + '"')
        else:
            coreSettings.save('opera_active_devices', '"1"')
        # Additional game fixes
        coreSettings.save('opera_hack_timing_1',    '"disabled"')
        coreSettings.save('opera_hack_timing_3',    '"disabled"')
        coreSettings.save('opera_hack_timing_5',    '"disabled"')
        coreSettings.save('opera_hack_timing_6',    '"disabled"')
        if system.isOptSet('game_fixes_opera') and system.config['game_fixes_opera'] != 'disabled':
            if system.config['game_fixes_opera'] == 'timing_hack1':
                coreSettings.save('opera_hack_timing_1',        '"enabled"')
            elif system.config['game_fixes_opera'] == 'timing_hack3':
                coreSettings.save('opera_hack_timing_3',        '"enabled"')
            elif system.config['game_fixes_opera'] == 'timing_hack5':
                coreSettings.save('opera_hack_timing_5',        '"enabled"')
            elif system.config['game_fixes_opera'] == 'timing_hack6':
                coreSettings.save('opera_hack_timing_6',        '"enabled"')
        # Shared nvram
        # If ROM includes the word Disc, assume it's a multi disc game, and enable shared nvram if the option isn't set.
        if system.isOptSet('opera_nvram_storage'):
            coreSettings.save('opera_nvram_storage', '"' + system.config['opera_nvram_storage'] + '"')
        elif 'disc' in rom.casefold():
            coreSettings.save('opera_nvram_storage', '"shared"')
        else:
            coreSettings.save('opera_nvram_storage', '"per game"')

    # Rick Dangerous
    if (system.config['core'] == 'xrick'):
        # Crop Borders
        if system.isOptSet('xrick_crop_borders') and system.getOptBoolean('xrick_crop_borders') == False:
            coreSettings.save('xrick_crop_borders', '"disabled"')
        else:
            coreSettings.save('xrick_crop_borders', '"enabled"')
        # Cheat 1 (Trainer Mode)
        if system.isOptSet('xrick_cheat1') and system.getOptBoolean('xrick_cheat1'):
            coreSettings.save('xrick_cheat1', '"enabled"')
        else:
            coreSettings.save('xrick_cheat1', '"disabled"')
        # Cheat 2 (Invulnerablilty Mode)
        if system.isOptSet('xrick_cheat2') and system.getOptBoolean('xrick_cheat2'):
            coreSettings.save('xrick_cheat2', '"enabled"')
        else:
            coreSettings.save('xrick_cheat2', '"disabled"')
        # Cheat 3 (Expose Mode)
        if system.isOptSet('xrick_cheat3') and system.getOptBoolean('xrick_cheat3'):
            coreSettings.save('xrick_cheat3', '"enabled"')
        else:
            coreSettings.save('xrick_cheat3', '"disabled"')

    # ScummVM CORE Options
    if (system.config['core'] == 'scummvm'):
        # Analog Deadzone
        if system.isOptSet('scummvm_analog_deadzone'):
            coreSettings.save('scummvm_analog_deadzone', '"' + system.config['scummvm_analog_deadzone'] + '"')
        else:
            coreSettings.save('scummvm_analog_deadzone', '"15"')
        # Gamepad Cursor Speed
        if system.isOptSet('scummvm_gamepad_cursor_speed'):
            coreSettings.save('scummvm_gamepad_cursor_speed', '"' + system.config['scummvm_gamepad_cursor_speed'] + '"')
        else:
            coreSettings.save('scummvm_gamepad_cursor_speed', '"1.0"')
        # Speed Hack (safe)
        if system.isOptSet('scummvm_speed_hack'):
            coreSettings.save('scummvm_speed_hack', '"' + system.config['scummvm_speed_hack'] + '"')
        else:
            coreSettings.save('scummvm_speed_hack', '"enabled"')

    # Sega Dreamcast / Atomiswave / Naomi
    if (system.config['core'] == 'flycast'):
        # force vmu all, to save in saves (otherwise, it saves in game_dir, which is bios)
        coreSettings.save('reicast_per_content_vmus',  '"All VMUs"')
        # Synchronous rendering
        if system.isOptSet('reicast_synchronous_rendering'):
            coreSettings.save('reicast_synchronous_rendering', '"' + system.config['reicast_synchronous_rendering'] + '"')
        else:
            coreSettings.save('reicast_synchronous_rendering', '"enabled"')
        # Threaded Rendering
        coreSettings.save('reicast_threaded_rendering',  '"enabled"')
        # Enable controller force feedback
        coreSettings.save('reicast_enable_purupuru',  '"enabled"')
        # Crossbar Colors
        if system.isOptSet('reicast_lightgun1_crosshair'):
            coreSettings.save('reicast_lightgun1_crosshair', '"' + system.config['reicast_lightgun1_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"Red"'
            else:
                status = '"disabled"'
            coreSettings.save('reicast_lightgun1_crosshair', status)
        if system.isOptSet('reicast_lightgun2_crosshair'):
            coreSettings.save('reicast_lightgun2_crosshair', '"' + system.config['reicast_lightgun2_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"Blue"'
            else:
                status = '"disabled"'
            coreSettings.save('reicast_lightgun2_crosshair', status)
        if system.isOptSet('reicast_lightgun3_crosshair'):
            coreSettings.save('reicast_lightgun3_crosshair', '"' + system.config['reicast_lightgun3_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"Green"'
            else:
                status = '"disabled"'
            coreSettings.save('reicast_lightgun3_crosshair', status)
        if system.isOptSet('reicast_lightgun4_crosshair'):
            coreSettings.save('reicast_lightgun4_crosshair', '"' + system.config['reicast_lightgun4_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"White"'
            else:
                status = '"disabled"'
            coreSettings.save('reicast_lightgun4_crosshair', status)
        # Video resolution
        if system.isOptSet('reicast_internal_resolution'):
            coreSettings.save('reicast_internal_resolution', '"' + system.config['reicast_internal_resolution'] + '"')
        else:
            coreSettings.save('reicast_internal_resolution', '"640x480"')
        # Textures Mip-mapping (blur)
        if system.isOptSet('reicast_mipmapping'):
            coreSettings.save('reicast_mipmapping', '"' + system.config['reicast_mipmapping'] + '"')
        else:
            coreSettings.save('reicast_mipmapping', '"disabled"')
        # Anisotropic Filtering
        if system.isOptSet('reicast_anisotropic_filtering'):
            coreSettings.save('reicast_anisotropic_filtering', '"' + system.config['reicast_anisotropic_filtering'] + '"')
        else:
            coreSettings.save('reicast_anisotropic_filtering', '"off"')
        # Texture Upscaling (xBRZ)
        if system.isOptSet('reicast_texupscale'):
            coreSettings.save('reicast_texupscale', '"' + system.config['reicast_texupscale'] + '"')
        else:
            coreSettings.save('reicast_texupscale', '"1"')
        # Frame Skip
        if system.isOptSet('reicast_frame_skipping'):
            coreSettings.save('reicast_frame_skipping', '"' + system.config['reicast_frame_skipping'] + '"')
        else:
            coreSettings.save('reicast_frame_skipping', '"disabled"')
        # Force Windows CE Mode
        if system.isOptSet('reicast_force_wince'):
            coreSettings.save('reicast_force_wince', '"' + system.config['reicast_force_wince'] + '"')
        else:
            coreSettings.save('reicast_force_wince', '"disabled"')
        # Widescreen Cheat
        if system.isOptSet('reicast_widescreen_cheats') and system.isOptSet('ratio') and system.isOptSet('bezel') and system.config['reicast_widescreen_cheats'] == 'enabled' and system.config["ratio"] == "16/9" and system.config["bezel"] == "none":
            coreSettings.save('reicast_widescreen_cheats', '"enabled"')
        else:
            coreSettings.save('reicast_widescreen_cheats', '"disabled"')
        # Widescreen Hack (prefer Cheat)
        if system.isOptSet('reicast_widescreen_hack') and system.isOptSet('ratio') and system.isOptSet('bezel') and system.isOptSet('reicast_widescreen_cheats') and system.config['reicast_widescreen_hack'] == 'enabled' and system.config["ratio"] == "16/9" and system.config["bezel"] == "none" and system.config['reicast_widescreen_cheats'] == 'disabled':
            coreSettings.save('reicast_widescreen_hack',   '"enabled"')
        else:
            coreSettings.save('reicast_widescreen_hack',   '"disabled"')
        # Bios
        if system.isOptSet('reicast_language'):
            coreSettings.save('reicast_language', '"' + system.config['reicast_language'] + '"')
        else:
            coreSettings.save('reicast_language', '"Default"')
        if system.isOptSet('reicast_region'):
            coreSettings.save('reicast_region', '"' + system.config['reicast_region'] + '"')
        else:
            coreSettings.save('reicast_region', '"Default"')

        ## Atomiswave / Naomi

        # Screen Orientation
        if system.isOptSet('screen_rotation_atomiswave') and system.name == 'atomiswave':
            coreSettings.save('reicast_screen_rotation', '"' + system.config['screen_rotation_atomiswave'] + '"')
        elif system.isOptSet('screen_rotation_naomi') and system.name == 'naomi':
                coreSettings.save('reicast_screen_rotation', '"' + system.config['screen_rotation_naomi'] + '"')
        else:
            coreSettings.save('reicast_screen_rotation', '"horizontal"')

        # wheel
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels') and len(wheels) > 0:
            coreSettings.save('reicast_analog_stick_deadzone', '"0%"')
        else:
            coreSettings.save('reicast_analog_stick_deadzone', '"15%"') # default value

    # Sega SG1000 / Master System / Game Gear / Megadrive / Mega CD
    if (system.config['core'] == 'genesisplusgx'):
        # Allows each game to have its own one brm file for save without lack of space
        coreSettings.save('genesis_plus_gx_bram', '"per game"')
        # Sometimes needs to be forced to NTSC-U for MSU-MD to work (this is to avoid an intentionally coded lock-out screen):
        # https://arcadetv.github.io/msu-md-patches/wiki/Lockout-screen.html
        if system.isOptSet('gpgx_region'):
            coreSettings.save('genesis_plus_region_detect', '"' + system.config['gpgx_region'] + '"')
        else:
            coreSettings.save('genesis_plus_region_detect', '"auto"')
        # Reduce sprite flickering
        if system.isOptSet('gpgx_no_sprite_limit'):
            coreSettings.save('genesis_plus_gx_no_sprite_limit', '"' + system.config['gpgx_no_sprite_limit'] + '"')
        else:
            coreSettings.save('genesis_plus_gx_no_sprite_limit', '"disabled"')
        # Blargg NTSC filter
        if system.isOptSet('gpgx_blargg_filter_md') and system.name == 'megadrive':
            coreSettings.save('genesis_plus_gx_blargg_ntsc_filter', '"' + system.config['gpgx_blargg_filter_md'] + '"')
        elif system.isOptSet('gpgx_blargg_filter_ms') and system.name == 'mastersystem':
            coreSettings.save('genesis_plus_gx_blargg_ntsc_filter', '"' + system.config['gpgx_blargg_filter_ms'] + '"')
        else:
            coreSettings.save('genesis_plus_gx_blargg_ntsc_filter', '"Off"')
        # Show Lightgun Crosshair
        if system.isOptSet('gun_cursor_md') and system.name == 'megadrive':
            coreSettings.save('genesis_plus_gx_gun_cursor', '"' + system.config['gun_cursor_md'] + '"')
        elif system.isOptSet('gun_cursor_ms') and system.name == 'mastersystem':
            coreSettings.save('genesis_plus_gx_gun_cursor', '"' + system.config['gun_cursor_ms'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"enabled"'
            else:
                status = '"disabled"'
            coreSettings.save('genesis_plus_gx_gun_cursor', status)
        # Megadrive FM (YM2612)
        if system.isOptSet('gpgx_fm'):
            coreSettings.save('genesis_plus_gx_ym2612', '"' + system.config['gpgx_fm'] + '"')
        else:
            coreSettings.save('genesis_plus_gx_ym2612', '"mame (ym2612)"')

        # system.name == 'mastersystem'
        # Master System FM (YM2413)
        if system.isOptSet('ym2413') and system.config['ym2413'] != "automatic":
            coreSettings.save('genesis_plus_gx_ym2413', '"' + system.config['ym2413'] + '"')
        else:
            coreSettings.save('genesis_plus_gx_ym2413', '"auto"')

        # system.name == 'gamegear'
        # Game Gear LCD Ghosting Filter
        if system.isOptSet('lcd_filter'):
            coreSettings.save('genesis_plus_gx_lcd_filter', '"' + system.config['lcd_filter'] + '"')
        else:
            coreSettings.save('genesis_plus_gx_lcd_filter', '"disabled"')
        # Game Gear Extended Screen
        if system.isOptSet('gg_extra'):
            coreSettings.save('genesis_plus_gx_gg_extra', '"' + system.config['gg_extra'] + '"')
        else:
            coreSettings.save('genesis_plus_gx_gg_extra', '"disabled"')

        # system.name == 'msu-md'
        # MSU-MD/MegaCD

        # Needs to be forced to sega/mega cd for MSU-MD to work.
        if system.isOptSet('gpgx_cd_add_on'):
            coreSettings.save('genesis_plus_gx_add_on', '"' + system.config['gpgx_cd_add_on'] + '"')
        elif system.name == 'msu-md':
            coreSettings.save('genesis_plus_gx_add_on', '"sega/mega cd"')
        else:
            coreSettings.save('genesis_plus_gx_add_on', '"auto"')

        # Volume setting is actually important, unlike MegaCD the MSU-MD is pre-amped at a different rate.
        # That is, the default level 100 will make the CD audio drown out the cartridge sound effects.
        if system.isOptSet('gpgx_cdda_volume'):
            coreSettings.save('genesis_plus_gx_cdda_volume', '"' + system.config['gpgx_cdda_volume'] + '"')
        elif system.name == 'msu-md':
            coreSettings.save('genesis_plus_gx_cdda_volume', '"70"')
        else:
            coreSettings.save('genesis_plus_gx_cdda_volume', '"100"')

        # gun
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save('genesis_plus_gx_gun_input', '"lightgun"')

    # Sega 32X (Sega Megadrive / MegaCD / Master System)
    if system.config['core'] == 'picodrive':
        # Reduce sprite flickering
        if system.isOptSet('picodrive_sprlim') and system.config['picodrive_sprlim'] == 'disabled':
            coreSettings.save('picodrive_sprlim',   '"disabled"')
        else:
            coreSettings.save('picodrive_sprlim',   '"enabled"')
        # Crop Overscan: the setting in picodrive shows overscan when enabled
        if system.isOptSet('picodrive_cropoverscan') and system.config['picodrive_cropoverscan'] == 'disabled':
            coreSettings.save('picodrive_overscan', '"enabled"')
        else:
            coreSettings.save('picodrive_overscan', '"disabled"')
        # 6 Button Controller 1
        if system.isOptSet('picodrive_controller1'):
            coreSettings.save('picodrive_sprlim', '"' + system.config['picodrive_controller1'] + '"')
        else:
            coreSettings.save('picodrive_input1', '"6 button pad"')
        # 6 Button Controller 2
        if system.isOptSet('picodrive_controller2'):
            coreSettings.save('picodrive_input2', '"' + system.config['picodrive_controller2'] + '"')
        else:
            coreSettings.save('picodrive_input2', '"6 button pad"')

        # Sega MegaCD
        # Emulate the Backup RAM Cartridge for games save (ex: Shining Force CD)
        if system.name == 'segacd':
            coreSettings.save('picodrive_ramcart', '"enabled"')
        else:
            coreSettings.save('picodrive_ramcart', '"disabled"')

    # Sega Saturn
    if (system.config['core'] == 'yabasanshiro'):
        # Video Resolution
        if system.isOptSet('resolution_mode'):
            coreSettings.save('yabasanshiro_resolution_mode', '"' + system.config['resolution_mode'] + '"')
        else:
            coreSettings.save('yabasanshiro_resolution_mode', '"original"')
        # Multitap
        if system.isOptSet('multitap_yabasanshiro') and system.config['multitap_yabasanshiro'] != 'disabled':
            if system.config['multitap_yabasanshiro'] == 'port1':
                coreSettings.save('yabasanshiro_multitap_port1', '"enabled"')
                coreSettings.save('yabasanshiro_multitap_port2', '"disabled"')
            elif system.config['multitap_yabasanshiro'] == 'port2':
                coreSettings.save('yabasanshiro_multitap_port1', '"disabled"')
                coreSettings.save('yabasanshiro_multitap_port2', '"enabled"')
            elif system.config['multitap_yabasanshiro'] == 'port12':
                coreSettings.save('yabasanshiro_multitap_port1', '"enabled"')
                coreSettings.save('yabasanshiro_multitap_port2', '"enabled"')
        else:
            coreSettings.save('yabasanshiro_multitap_port1', '"disabled"')
            coreSettings.save('yabasanshiro_multitap_port2', '"disabled"')
        # Language
        if system.isOptSet('yabasanshiro_language'):
            coreSettings.save('yabasanshiro_system_language', '"' + system.config['yabasanshiro_language'] + '"')
        else:
            coreSettings.save('yabasanshiro_system_language', '"english"')

    if (system.config['core'] == 'kronos'):
        # Set best OpenGL renderer
        coreSettings.save('kronos_videocoretype', '"opengl_cs"')
        # Video Resolution
        if system.isOptSet('kronos_resolution'):
            coreSettings.save('kronos_resolution_mode', '"' + system.config['kronos_resolution'] + '"')
        else:
            coreSettings.save('kronos_resolution_mode', '"original"')
        # Mesh mode
        if system.isOptSet('kronos_meshmode'):
            coreSettings.save('kronos_meshmode', '"' + system.config['kronos_meshmode'] + '"')
        else:
            coreSettings.save('kronos_meshmode', '"disabled"')
        # Banding mode
        if system.isOptSet('kronos_bandingmode'):
            coreSettings.save('kronos_bandingmode', '"' + system.config['kronos_bandingmode'] + '"')
        else:
            coreSettings.save('kronos_bandingmode', '"disabled"')
        # Share saves with Beetle
        if system.isOptSet('kronos_use_beetle_saves') and system.config['kronos_use_beetle_saves'] == 'disabled':
            coreSettings.save('kronos_use_beetle_saves', '"disabled"')
        else:
            coreSettings.save('kronos_use_beetle_saves', '"enabled"')
        # Multitap
        if system.isOptSet('kronos_multitap') and system.config['kronos_multitap'] != 'disabled':
            if system.config['kronos_multitap'] == 'port1':
                coreSettings.save('kronos_multitap_port1', '"enabled"')
                coreSettings.save('kronos_multitap_port2', '"disabled"')
            elif system.config['kronos_multitap'] == 'port2':
                coreSettings.save('kronos_multitap_port1', '"disabled"')
                coreSettings.save('kronos_multitap_port2', '"enabled"')
            elif system.config['kronos_multitap'] == 'port12':
                coreSettings.save('kronos_multitap_port1', '"enabled"')
                coreSettings.save('kronos_multitap_port2', '"enabled"')
        else:
            coreSettings.save('kronos_multitap_port1', '"disabled"')
            coreSettings.save('kronos_multitap_port2', '"disabled"')
        # BIOS langauge
        if system.isOptSet('kronos_language_id'):
            coreSettings.save('kronos_language_id', '"' + system.config['kronos_language_id'] + '"')
        else:
            coreSettings.save('kronos_language_id', '"English"')

    # gun cross / wheel
    if (system.config['core'] == 'beetle-saturn'):
        # gun
        if system.isOptSet('beetle-saturn_crosshair'):
            coreSettings.save('beetle_saturn_virtuagun_crosshair', '"' + system.config['beetle-saturn_crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"Cross"'
            else:
                status = '"Off"'
            coreSettings.save('beetle_saturn_virtuagun_crosshair', status)
        # wheel
        if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels') and len(wheels) > 0:
            coreSettings.save('beetle_saturn_analog_stick_deadzone', '"0%"')
        else:
            coreSettings.save('beetle_saturn_analog_stick_deadzone', '"15%"') # default value

    # Sharp X68000
    if (system.config['core'] == 'px68k'):
        # Fresh config file
        keropi_config = '/userdata/bios/keropi/config'
        keropi_sram = '/userdata/bios/keropi/sram.dat'
        for f in [ keropi_config, keropi_sram ]:
            if os.path.exists(f):
                os.remove(f)
        fd = open(keropi_config, "w")
        fd.write("[WinX68k]\n")
        fd.write("StartDir=/userdata/roms/x68000\n")
        fd.close()

        # To auto launch HDD games
        coreSettings.save('px68k_disk_path', '"disabled"')
        # CPU Speed (Overclock)
        if system.isOptSet('px68k_cpuspeed'):
            coreSettings.save('px68k_cpuspeed', '"' + system.config['px68k_cpuspeed'] + '"')
        else:
            coreSettings.save('px68k_cpuspeed', '"33Mhz (OC)"')
        # RAM Size
        if system.isOptSet('px68k_ramsize'):
            coreSettings.save('px68k_ramsize', '"' + system.config['px68k_ramsize'] + '"')
        else:
            coreSettings.save('px68k_ramsize', '"2MB"')
        # Frame Skip
        if system.isOptSet('px68k_frameskip'):
                coreSettings.save('px68k_frameskip', '"' + system.config['px68k_frameskip'] + '"')
        else:
            coreSettings.save('px68k_frameskip', '"Full Frame"')
        # Joypad Type for two players
        if system.isOptSet('px68k_joytype'):
            coreSettings.save('px68k_joytype1', '"' + system.config['px68k_joytype'] + '"')
            coreSettings.save('px68k_joytype2', '"' + system.config['px68k_joytype'] + '"')
        else:
            coreSettings.save('px68k_joytype1', '"Default (2 Buttons)"')
            coreSettings.save('px68k_joytype2', '"Default (2 Buttons)"')

    # Sinclair ZX81
    if (system.config['core'] == '81'):
        # Tape Fast Load
        coreSettings.save('81_fast_load', '"enabled"')
        # Enables sound emulatio
        coreSettings.save('81_sound',     '"Zon X-81"')
        # Colorisation (Chroma 81)
        if system.isOptSet('81_chroma_81'):
            if system.config['81_chroma_81'] == "automatic":
                coreSettings.save('81_chroma_81', '"auto"')
            else:
                coreSettings.save('81_chroma_81', '"' + system.config['81_chroma_81'] + '"')
        else:
            coreSettings.save('81_chroma_81', '"enabled"')
        # High Resolution
        if system.isOptSet('81_highres'):
            if system.config['81_highres'] == "automatic":
                coreSettings.save('81_highres', '"auto"')
            else:
                coreSettings.save('81_highres', '"' + system.config['81_highres'] + '"')
        else:
            coreSettings.save('81_highres', '"WRX"')

    # Sinclair ZX Spectrum
    if (system.config['core'] == 'fuse'):
        if system.isOptSet('fuse_machine'):
            coreSettings.save('fuse_machine', '"' + system.config['fuse_machine'] + '"')
        else:
            # The most common configuration same as ZX Spectrum+
            coreSettings.save('fuse_machine',   '"Spectrum 128K"')
        # Zoom, Hide Video Border
        if system.isOptSet('fuse_hide_border'):
            coreSettings.save('fuse_hide_border', '"' + system.config['fuse_hide_border'] + '"')
        else:
            coreSettings.save('fuse_hide_border', '"disabled"')

    # SNK Neogeo AES MVS / Neogeo CD
    if (system.config['core'] == 'fbneo'):
        romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
        # Diagnostic input
        coreSettings.save('fbneo-diagnostic-input', '"Start + L + R"')
        # Allow RetroAchievements in hardcore mode with FBNeo
        coreSettings.save('fbneo-allow-patched-romsets', '"disabled"')
        # CPU Clock
        if system.isOptSet('fbneo-cpu-speed-adjust'):
            coreSettings.save('fbneo-cpu-speed-adjust', '"' + system.config['fbneo-cpu-speed-adjust'] + '"')
        else:
            coreSettings.save('fbneo-cpu-speed-adjust', '"100%"')
        # Frameskip
        if system.isOptSet('fbneo-frameskip'):
            coreSettings.save('fbneo-frameskip', '"' + system.config['fbneo-frameskip'] + '"')
        else:
            coreSettings.save('fbneo-frameskip', '"0"')
        # Crosshair (Lightgun)
        if system.isOptSet('fbneo-lightgun-hide-crosshair'):
            coreSettings.save('fbneo-lightgun-hide-crosshair', '"' + system.config['fbneo-lightgun-hide-crosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"enabled"'
            else:
                status = '"disabled"'
            coreSettings.save('fbneo-lightgun-hide-crosshair', status)
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) >= 1:
            coreSettings.save("fbneo-dipswitch-" + romBase+ "-Controls", '"Light Gun"')
        else:
            coreSettings.save("fbneo-dipswitch-" + romBase+ "-Controls", '"Joystick"')

        # NEOGEO
        if system.name == 'neogeo':
            # Neogeo Mode
            romBase = os.path.splitext(os.path.basename(rom))[0] # filename without extension
            if system.isOptSet('fbneo-neogeo-mode-switch'):
                coreSettings.save("fbneo-neogeo-mode", '"DIPSWITCH"')
                if system.config['fbneo-neogeo-mode-switch'] == 'MVS Asia/Europe':
                    coreSettings.save("fbneo-dipswitch-" + romBase + "-BIOS",  '"MVS Asia/Europe ver. 5 (1 slot)"')
                elif system.config['fbneo-neogeo-mode-switch'] == 'MVS USA':
                    coreSettings.save("fbneo-dipswitch-" + romBase + "-BIOS",  '"MVS USA ver. 5 (2 slot)"')
                elif system.config['fbneo-neogeo-mode-switch'] == 'MVS Japan':
                    coreSettings.save("fbneo-dipswitch-" + romBase + "-BIOS",  '"MVS Japan ver. 5 (? slot)"')
                elif system.config['fbneo-neogeo-mode-switch'] == 'AES Asia':
                    coreSettings.save("fbneo-dipswitch-" + romBase + "-BIOS",  '"AES Asia"')
                elif system.config['fbneo-neogeo-mode-switch'] == 'AES Japan':
                    coreSettings.save("fbneo-dipswitch-" + romBase + "-BIOS",  '"AES Japan"')
                else:
                    coreSettings.save("fbneo-neogeo-mode", '"UNIBIOS"')
            else:
                coreSettings.save("fbneo-neogeo-mode",     '"UNIBIOS"')
                #coreSettings.save("fbneo-dipswitch-" + romBase + "-BIOS",      '"Universe BIOS ver. 4.0"')
            # Memory card mode
            if system.isOptSet('fbneo-memcard-mode'):
                coreSettings.save('fbneo-memcard-mode', '"' + system.config['fbneo-memcard-mode'] + '"')
            else:
                coreSettings.save('fbneo-memcard-mode', '"per-game"')

    # SNK Neogeo CD
    if (system.config['core'] == 'neocd'):
        # Console region
        if system.isOptSet('neocd_region'):
            coreSettings.save('neocd_region', '"' + system.config['neocd_region'] + '"')
        else:
            coreSettings.save('neocd_region', '"Japan"')
        # BIOS Select
        if system.isOptSet('neocd_bios'):
            coreSettings.save('neocd_bios', '"' + system.config['neocd_bios'] + '"')
        else:
            coreSettings.save('neocd_bios', '"neocd_z.rom (CDZ)"')
        # Per-Game saves
        if system.isOptSet('neocd_per_content_saves') and system.config['neocd_per_content_saves'] == "False":
            coreSettings.save('neocd_per_content_saves', '"Off"')
        else:
            coreSettings.save('neocd_per_content_saves', '"On"')

    # Sony PSP
    if (system.config['core'] == 'ppsspp'):
        if system.isOptSet('ppsspp_resolution'):
            coreSettings.save('ppsspp_internal_resolution', '"' + system.config['ppsspp_resolution'] + '"')
        else:
            coreSettings.save('ppsspp_internal_resolution', '"480x272"')

    # Sony PSX
    if (system.config['core'] == 'mednafen_psx'):
        # CPU Frequency Scaling (Overclock)
        if system.isOptSet('beetle_psx_hw_cpu_freq_scale'):
            coreSettings.save('beetle_psx_hw_cpu_freq_scale', '"' + system.config['beetle_psx_hw_cpu_freq_scale'] + '"')
        else:
            coreSettings.save('beetle_psx_hw_cpu_freq_scale', '"110%"') # If not 110% NO options are working!
        # Show official Bootlogo
        if system.isOptSet('beetle_psx_hw_skip_bios'):
            coreSettings.save('beetle_psx_hw_skip_bios', '"' + system.config['beetle_psx_hw_skip_bios'] + '"')
        else:
            coreSettings.save('beetle_psx_hw_skip_bios', '"disabled"')
        # Video Resolution
        if system.isOptSet('beetle_psx_hw_internal_resolution'):
            coreSettings.save('beetle_psx_hw_internal_resolution', '"' + system.config['beetle_psx_hw_internal_resolution'] + '"')
        else:
            coreSettings.save('beetle_psx_hw_internal_resolution', '"1x(native)"')
        # Widescreen Hack
        if system.isOptSet('beetle_psx_hw_widescreen_hack') and system.isOptSet('ratio') and system.isOptSet('bezel') and system.config['beetle_psx_hw_widescreen_hack'] == 'enabled' and system.config["ratio"] == "16/9" and system.config["bezel"] == "none":
            coreSettings.save('beetle_psx_hw_widescreen_hack', '"enabled"')
        else:
            coreSettings.save('beetle_psx_hw_widescreen_hack', '"disabled"')
        # Frame Duping (Speedup)
        if system.isOptSet('beetle_psx_hw_frame_duping'):
            coreSettings.save('beetle_psx_hw_frame_duping', '"' + system.config['beetle_psx_hw_frame_duping'] + '"')
        else:
            coreSettings.save('beetle_psx_hw_frame_duping', '"disabled"')
        # CPU Dynarec (Speedup)
        if system.isOptSet('beetle_psx_hw_cpu_dynarec'):
            coreSettings.save('beetle_psx_hw_cpu_dynarec', '"' + system.config['beetle_psx_hw_cpu_dynarec'] + '"')
        else:
            coreSettings.save('beetle_psx_hw_cpu_dynarec', '"disabled"')
        # Dynarec Code Invalidation
        if system.isOptSet('beetle_psx_hw_dynarec_invalidate'):
            coreSettings.save('beetle_psx_hw_dynarec_invalidate', '"' + system.config['beetle_psx_hw_dynarec_invalidate'] + '"')
        else:
            coreSettings.save('beetle_psx_hw_dynarec_invalidate', '"full"')
        # Analog Stick self calibration
        coreSettings.save('beetle_psx_hw_analog_calibration', '"enabled"')
        # Multitap
        if system.isOptSet('multitap_mednafen') and system.config['multitap_mednafen'] != 'disabled':
            if system.config['multitap_mednafen'] == 'port1':
                coreSettings.save('beetle_psx_hw_enable_multitap_port1', '"enabled"')
                coreSettings.save('beetle_psx_hw_enable_multitap_port2', '"disabled"')
            elif system.config['multitap_mednafen'] == 'port2':
                coreSettings.save('beetle_psx_hw_enable_multitap_port1', '"disabled"')
                coreSettings.save('beetle_psx_hw_enable_multitap_port2', '"enabled"')
            elif system.config['multitap_mednafen'] == 'port12':
                coreSettings.save('beetle_psx_hw_enable_multitap_port1', '"enabled"')
                coreSettings.save('beetle_psx_hw_enable_multitap_port2', '"enabled"')
        else:
            coreSettings.save('beetle_psx_hw_enable_multitap_port1', '"disabled"')
            coreSettings.save('beetle_psx_hw_enable_multitap_port2', '"disabled"')

    if (system.config['core'] == 'swanstation' or system.config['core'] == 'duckstation'):
        # renderer
        if system.isOptSet("gpu_software") and system.getOptBoolean("gpu_software"):
            coreSettings.save('swanstation_GPU_Renderer', '"Software"')
        else:
            if system.isOptSet("gfxbackend"):
                if system.config["gfxbackend"] == "vulkan":
                    coreSettings.save('swanstation_GPU_Renderer', '"Vulkan"')
                elif system.config["gfxbackend"] == "opengl" or system.config["gfxbackend"] == "glcore":
                    coreSettings.save('swanstation_GPU_Renderer', "OpenGL")
                else:
                    coreSettings.save('swanstation_GPU_Renderer', '"Auto"')
            else:
                coreSettings.save('swanstation_GPU_Renderer', '"Auto"')

        # Show official Bootlogo
        if system.isOptSet('swanstation_PatchFastBoot'):
            coreSettings.save('swanstation_BIOS_PatchFastBoot', '"' + system.config['swanstation_PatchFastBoot'] + '"')
        else:
            coreSettings.save('swanstation_BIOS_PatchFastBoot', '"false"')
        # Video Resolution
        if system.isOptSet('swanstation_resolution_scale'):
            coreSettings.save('swanstation_GPU_ResolutionScale', '"' + system.config['swanstation_resolution_scale'] + '"')
        else:
            coreSettings.save('swanstation_GPU_ResolutionScale', '"1"')
        # PGXP Geometry Correction
        if system.isOptSet('swanstation_pgxp'):
            coreSettings.save('swanstation_GPU_PGXPEnable', '"' + system.config['swanstation_pgxp'] + '"')
        else:
            coreSettings.save('swanstation_GPU_PGXPEnable', '"true"')
        # Anti-aliasing (MSAA/SSAA)
        if system.isOptSet('swanstation_antialiasing'):
            coreSettings.save('swanstation_GPU_MSAA', '"' + system.config['swanstation_antialiasing'] + '"')
        else:
            coreSettings.save('swanstation_GPU_MSAA', '"1"')
        # Texture Filtering
        if system.isOptSet('swanstation_texture_filtering'):
            coreSettings.save('swanstation_GPU_TextureFilter', '"' + system.config['swanstation_texture_filtering'] + '"')
        else:
            coreSettings.save('swanstation_GPU_TextureFilter', '"Nearest"')
        # Widescreen Hack
        if system.isOptSet('swanstation_widescreen_hack') and system.isOptSet('ratio') and system.isOptSet('bezel') and system.config['swanstation_widescreen_hack'] == 'true' and system.config["ratio"] == "16/9" and system.config["bezel"] == "none":
            coreSettings.save('swanstation_GPU_WidescreenHack',  '"true"')
            coreSettings.save('swanstation_Display_AspectRatio', '"16:9"')
        else:
            coreSettings.save('swanstation_GPU_WidescreenHack',  '"false"')
            coreSettings.save('swanstation_Display_AspectRatio', '"4:3"')
         # Crop Mode
        if system.isOptSet('swanstation_CropMode'):
            coreSettings.save('swanstation_Display_CropMode', '"' + system.config['swanstation_CropMode'] + '"')
        else:
            coreSettings.save('swanstation_Display_CropMode', '"Overscan"')
        # Gun crosshairs
        if system.isOptSet('swanstation_Controller_ShowCrosshair'):
            coreSettings.save('swanstation_Controller_ShowCrosshair', '"' + system.config['swanstation_Controller_ShowCrosshair'] + '"')
        else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"true"'
            else:
                status = '"false"'
            coreSettings.save('swanstation_Controller_ShowCrosshair', status)

    if (system.config['core'] == 'pcsx2'):
        # Fast Boot
        if system.isOptSet('lr_pcsx2_fast_boot'):
            coreSettings.save('pcsx2_fast_boot', '"' + system.config['lr_pcsx2_fast_boot'] + '"')
        else:
            coreSettings.save('pcsx2_fast_boot', '"disabled"')

    if (system.config['core'] == 'pcsx_rearmed'):
        # Display Games Hack Options
        coreSettings.save('pcsx_rearmed_show_gpu_peops_settings', '"enabled"')
        # Display Multitap/Gamepad Options
        coreSettings.save('pcsx_rearmed_show_other_input_settings', '"enabled"')
        # Enable Vibration
        coreSettings.save('pcsx_rearmed_vibration', '"enabled"')

        # Show Bios Bootlogo (Breaks some games)
        if system.isOptSet('show_bios_bootlogo'):
            coreSettings.save('pcsx_rearmed_show_bios_bootlogo', '"' + system.config['show_bios_bootlogo'] + '"')
        else:
            coreSettings.save('pcsx_rearmed_show_bios_bootlogo', '"disabled"')
        # Frameskip
        if system.isOptSet('frameskip_pcsx'):
            coreSettings.save('pcsx_rearmed_frameskip', '"' + system.config['frameskip_pcsx'] + '"')
        else:
            coreSettings.save('pcsx_rearmed_frameskip', '"0"')
        # Enhanced resolution at the cost of lower performance
        if system.isOptSet('neon_enhancement') and system.config['neon_enhancement'] != 'disabled':
            if system.config['neon_enhancement'] == 'enabled':
                coreSettings.save('pcsx_rearmed_neon_enhancement_enable',  '"enabled"')
                coreSettings.save('pcsx_rearmed_neon_enhancement_no_main', '"disabled"')
            elif system.config['neon_enhancement'] == 'enabled_with_speedhack':
                coreSettings.save('pcsx_rearmed_neon_enhancement_enable',  '"enabled"')
                coreSettings.save('pcsx_rearmed_neon_enhancement_no_main', '"enabled"')
        else:
            coreSettings.save('pcsx_rearmed_neon_enhancement_enable',  '"disabled"')
            coreSettings.save('pcsx_rearmed_neon_enhancement_no_main', '"disabled"')
        # Multitap
        if system.isOptSet('pcsx_rearmed_multitap'):
            coreSettings.save('pcsx_rearmed_multitap', '"' + system.config['pcsx_rearmed_multitap'] + '"')
        else:
            coreSettings.save('pcsx_rearmed_multitap', '"disabled"')
        # Additional game fixes
        coreSettings.save('pcsx_rearmed_idiablofix',                    '"disabled"')
        coreSettings.save('pcsx_rearmed_pe2_fix',                       '"disabled"')
        coreSettings.save('pcsx_rearmed_inuyasha_fix',                  '"disabled"')
        coreSettings.save('pcsx_rearmed_gpu_peops_odd_even_bit',        '"disabled"')
        coreSettings.save('pcsx_rearmed_gpu_peops_expand_screen_width', '"disabled"')
        coreSettings.save('pcsx_rearmed_gpu_peops_ignore_brightness',   '"disabled"')
        coreSettings.save('pcsx_rearmed_gpu_peops_lazy_screen_update',  '"disabled"')
        coreSettings.save('pcsx_rearmed_gpu_peops_repeated_triangles',  '"disabled"')
        if system.isOptSet('game_fixes_pcsx') and system.config['game_fixes_pcsx'] != 'disabled':
            if system.config['game_fixes_pcsx'] == 'Diablo_Music_Fix':
                coreSettings.save('pcsx_rearmed_idiablofix',                    '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'Parasite_Eve':
                coreSettings.save('pcsx_rearmed_pe2_fix',                       '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'InuYasha_Sengoku':
                coreSettings.save('pcsx_rearmed_inuyasha_fix',                  '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'Chrono_Chross':
                coreSettings.save('pcsx_rearmed_gpu_peops_odd_even_bit',        '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'Capcom_fighting':
                coreSettings.save('pcsx_rearmed_gpu_peops_expand_screen_width', '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'Lunar':
                coreSettings.save('pcsx_rearmed_gpu_peops_ignore_brightness',   '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'Pandemonium':
                coreSettings.save('pcsx_rearmed_gpu_peops_lazy_screen_update',  '"enabled"')
            elif system.config['game_fixes_pcsx'] == 'Dark_Forces':
                coreSettings.save('pcsx_rearmed_gpu_peops_repeated_triangles',  '"enabled"')
        # gun cross
        # Crossbar Colors
        for player in [ {"id": 1, "color": "red"}, {"id": 2, "color": "blue"} ]:
          if system.isOptSet('pcsx_rearmed_crosshair'+str(player["id"])):
            coreSettings.save('pcsx_rearmed_crosshair'+str(player["id"]), '"' + system.config['pcsx_rearmed_crosshair'+str(player["id"])] + '"')
          else:
            if controllersConfig.gunsNeedCrosses(guns):
                status = '"'+player["color"]+'"'
            else:
                status = '"disabled"'
            coreSettings.save('pcsx_rearmed_crosshair'+str(player["id"]), status)

    # Thomson MO5 / TO7
    if (system.config['core'] == 'theodore'):
        # Auto run games
        coreSettings.save('theodore_autorun',   '"enabled"')

    # Watara SuperVision
    if (system.config['core'] == 'potator'):
        # Watara Color Palette
        if system.isOptSet('watara_palette'):
            coreSettings.save('potator_palette', '"' + system.config['watara_palette'] + '"')
        else:
            coreSettings.save('potator_palette', 'gameking')
        # Watara Ghosting
        if system.isOptSet('watara_ghosting'):
            coreSettings.save('potator_lcd_ghosting', '"' + system.config['watara_ghosting'] + '"')
        else:
            coreSettings.save('potator_lcd_ghosting', '0')

    ## PORTs

    # DOOM
    if (system.config['core'] == 'prboom'):
        # Internal resolution
        if system.isOptSet('prboom-resolution'):
            coreSettings.save('prboom-resolution', '"' + system.config['prboom-resolution'] + '"')
        else:
            coreSettings.save('prboom-resolution', '"320x200"')

    # QUAKE
    if (system.config['core'] == 'tyrquake'):
        # Resolution
        if system.isOptSet('tyrquake_resolution'):
            coreSettings.save('tyrquake_resolution', '"' + system.config['tyrquake_resolution'] + '"')
        else:
            coreSettings.save('tyrquake_resolution', '"640x480"')
        # Frame rate
        if system.isOptSet('tyrquake_framerate') and system.config['tyrquake_framerate'] != "automatic":
            coreSettings.save('tyrquake_framerate', '"' + system.config['tyrquake_framerate'] + '"')
        else:
            coreSettings.save('tyrquake_framerate', '"Auto"')
        # Rumble
        if system.isOptSet('tyrquake_rumble'):
            coreSettings.save('tyrquake_rumble', '"' + system.config['tyrquake_rumble'] + '"')
        else:
            coreSettings.save('tyrquake_rumble', '"disabled"')

    # BOMBERMAN
    if (system.config['core'] == 'mrboom'):
        # Team mode
        if system.isOptSet('mrboom-aspect'):
            coreSettings.save('mrboom-aspect', '"' + system.config['mrboom-aspect'] + '"')
        else:
            coreSettings.save('mrboom-aspect', '"Native"')

    # OpenLara
    if (system.config['core'] == 'openlara'):
        # Internal resolution
        if system.isOptSet('lara-resolution'):
            coreSettings.save('openlara_resolution', '"' + system.config['lara-resolution'] + '"')
        else:
            coreSettings.save('openlara_resolution', '"1280x720"')

        # Framerate
        if system.isOptSet('lara-framerate'):
            coreSettings.save('openlara_framerate', '"' + system.config['lara-framerate'] + '"')
        else:
            coreSettings.save('openlara_framerate', '"60fps"')

    # HatariB
    if (system.config['core'] == 'hatarib'):
        # Defaults
        coreSettings.save('hatarib_statusbar', '"0"')
        coreSettings.save('hatarib_fast_floppy', '"1"')
        coreSettings.save('hatarib_show_welcome', '"0"')
        # Machine Type
        if system.isOptSet('hatarib_machine'):
            coreSettings.save('hatarib_machine', '"' + system.config['hatarib_machine'] + '"')
        else:
            coreSettings.save('hatarib_machine', '"0"')
        # CPU
        if system.isOptSet('hatarib_cpu'):
            coreSettings.save('hatarib_cpu', '"' + system.config['hatarib_cpu'] + '"')
        else:
            coreSettings.save('hatarib_cpu', '"-1"')
        # CPU Clock
        if system.isOptSet('hatarib_cpu_clock'):
            coreSettings.save('hatarib_cpu_clock', '"' + system.config['hatarib_cpu'] + '"')
        else:
            coreSettings.save('hatarib_cpu_clock', '"-1"')
        # ST Memory Size
        if system.isOptSet('hatarib_memory'):
            coreSettings.save('hatarib_memory', '"' + system.config['hatarib_memory'] + '"')
        else:
            coreSettings.save('hatarib_memory', '"0"')
        # Pause Screen
        if system.isOptSet('hatarib_pause'):
            coreSettings.save('hatarib_pause_osk', '"' + system.config['hatarib_pause'] + '"')
        else:
            coreSettings.save('hatarib_pause_osk', '"2"')
        # Aspect Ratio
        if system.isOptSet('hatarib_ratio'):
            coreSettings.save('hatarib_aspect', '"' + system.config['hatarib_ratio'] + '"')
        else:
            coreSettings.save('hatarib_aspect', '"0"')
        # Borders
        if system.isOptSet('hatarib_borders'):
            coreSettings.save('hatarib_borders', '"' + system.config['hatarib_borders'] + '"')
        else:
            coreSettings.save('hatarib_borders', '"0"')

    # Custom : Allow the user to configure directly retroarchcore.cfg via batocera.conf via lines like : snes.retroarchcore.opt=val
    for user_config in system.config:
        if user_config[:14] == "retroarchcore.":
            coreSettings.save(user_config[14:], '"' + system.config[user_config] + '"')

def generateHatariConf(hatariConf):
    hatariConfig = configparser.ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    hatariConfig.optionxform = str
    if os.path.exists(hatariConf):
        hatariConfig.read(hatariConf)

    # update the configuration file
    if not os.path.exists(os.path.dirname(hatariConf)):
        os.makedirs(os.path.dirname(hatariConf))
    with open(hatariConf, 'w') as configfile:
        hatariConfig.write(configfile)
