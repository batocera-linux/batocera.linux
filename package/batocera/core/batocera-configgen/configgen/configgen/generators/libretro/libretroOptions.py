#!/usr/bin/env python
import sys
import os
import ConfigParser
from settings.unixSettings import UnixSettings
import batoceraFiles

def generateCoreSettings(retroarchCore, system):
    # retroarch-core-options.cfg
    if not os.path.exists(os.path.dirname(retroarchCore)):
        os.makedirs(os.path.dirname(retroarchCore))

    try:
        coreSettings = UnixSettings(retroarchCore, separator=' ')
    except UnicodeError:
        # invalid retroarch-core-options.cfg
        # remove it and try again
        os.remove(retroarchCore)
        coreSettings = UnixSettings(retroarchCore, separator=' ')

    # Atari 800 and 5200
    if (system.config['core'] == 'atari800'):
        if (system.name == 'atari800'):
            coreSettings.save('atari800_system',    '"130XE (128K)"')
            coreSettings.save('RAM_SIZE',           '"64"')
            coreSettings.save('STEREO_POKEY',       '"1"')
            coreSettings.save('BUILTIN_BASIC',      '"1"')
        else:
            coreSettings.save('atari800_system',    '"5200"')
            coreSettings.save('RAM_SIZE',           '"16"')
            coreSettings.save('STEREO_POKEY',       '"0"')
            coreSettings.save('BUILTIN_BASIC',      '"0"')

    # Colecovision and MSX
    if (system.config['core'] == 'bluemsx'):
        coreSettings.save('bluemsx_overscan', '"enabled"')
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

    if (system.config['core'] == 'citra'):
        if not os.path.exists(batoceraFiles.CONF + "/retroarch/3ds.cfg"):
            f = open(batoceraFiles.CONF + "/retroarch/3ds.cfg", "w")
            f.write("video_driver = \"glcore\"\n")
            f.close()

    if (system.config['core'] == 'tgbdual'):
        coreSettings.save('tgbdual_audio_output',       '"Game Boy #1"')
        coreSettings.save('tgbdual_gblink_enable',      '"enabled"')
        coreSettings.save('tgbdual_screen_placement',   '"left-right"')
        coreSettings.save('tgbdual_single_screen_mp',   '"both players"')
        coreSettings.save('tgbdual_switch_screens',     '"normal"')

    if (system.config['core'] == 'gambatte'):
        if 'colorization' in system.renderconfig and system.renderconfig['colorization'] != None:
            coreSettings.save('gambatte_gb_colorization',     '"internal"')
            coreSettings.save('gambatte_gb_internal_palette', '"' + system.renderconfig['colorization'] + '"')
        else:
            coreSettings.save('gambatte_gb_colorization',     '"disabled"')

    if (system.config['core'] == 'desmume'):
        coreSettings.save('desmume_pointer_device_r',   '"emulated"')
        # multisampling aa
        if system.isOptSet('multisampling'):
            coreSettings.save("desmume_gfx_multisampling", system.config["multisampling"])
        else:
            coreSettings.save("desmume_gfx_multisampling", "disabled")
        # texture smoothing
        if system.isOptSet('texture_smoothing'):
            coreSettings.save("desmume_gfx_texture_smoothing", system.config["texture_smoothing"])
        else:
            coreSettings.save("desmume_gfx_texture_smoothing", "disabled")
        # texture scaling (xBrz)
        if system.isOptSet('texture_scaling'):
            coreSettings.save("desmume_gfx_texture_scaling", system.config["texture_scaling"])
        else:
            coreSettings.save("desmume_gfx_texture_scaling", "1")

    if (system.config['core'] == 'mame078'):
        coreSettings.save('mame2003_skip_disclaimer',   '"enabled"')
        coreSettings.save('mame2003_skip_warnings',     '"enabled"')

    if (system.config['core'] == 'mame078plus'):
        coreSettings.save('mame2003-plus_skip_disclaimer',  '"enabled"')
        coreSettings.save('mame2003-plus_skip_warnings',    '"enabled"')
        coreSettings.save('mame2003-plus_analog',           '"digital"')

    if (system.config['core'] == 'pce'):
        coreSettings.save('pce_keepaspect', '"enabled"')
    
    if (system.config['core'] == 'pce_fast'):
        coreSettings.save('pce_keepaspect', '"enabled"')

    if (system.config['core'] == 'picodrive'):
        coreSettings.save('picodrive_input1',   '"6 button pad"')
        coreSettings.save('picodrive_input2',   '"6 button pad"')

    if (system.config['core'] == '81'):
        coreSettings.save('81_sound',   '"Zon X-81"')

    if (system.config['core'] == 'cap32'):
        if (system.name == 'gx4000'):
            coreSettings.save('cap32_model',    '"6128+"')
        else:
            coreSettings.save('cap32_model',    '"6128"')

    if (system.config['core'] == 'fuse'):
        coreSettings.save('fuse_machine',   '"Spectrum 128K"')

    if (system.config['core'] == 'opera'):
        coreSettings.save('opera_dsp_threaded',   '"enabled"')

    if (system.config['core'] == 'virtualjaguar'):
        coreSettings.save('virtualjaguar_usefastblitter',   '"enabled"')

    if (system.config['core'] == 'vice'):
        coreSettings.save('vice_Controller',    '"joystick"')
        coreSettings.save('vice_JoyPort',       '"port_1"')

    if (system.config['core'] == 'theodore'):
        coreSettings.save('theodore_autorun',   '"enabled"')

    if (system.config['core'] == 'flycast'):
        coreSettings.save('reicast_threaded_rendering',   '"enabled"')
        # widescreen hack
        if system.isOptSet('widescreen_hack'):
            coreSettings.save("reicast_widescreen_hack", system.config["widescreen_hack"])
        else:
            coreSettings.save("reicast_widescreen_hack", "disabled")
        # anisotropic filtering
        if system.isOptSet('anisotropic_filtering'):
            coreSettings.save("reicast_anisotropic_filtering", system.config["anisotropic_filtering"])
        else:
            coreSettings.save("reicast_anisotropic_filtering", "off")
        # texture upscaling (xBRZ)
        if system.isOptSet('texture_upscaling'):
            coreSettings.save("reicast_texupscale", system.config["texture_upscaling"])
        else:
            coreSettings.save("reicast_texupscale", "off")
        # render to texture upscaling
        if system.isOptSet('render_to_texture_upscaling'):
            coreSettings.save("reicast_render_to_texture_upscaling", system.config["render_to_texture_upscaling"])
        else:
            coreSettings.save("reicast_render_to_texture_upscaling", "1x")

    if (system.config['core'] == 'dosbox'):
        coreSettings.save('dosbox_svn_pcspeaker', '"true"')

    if (system.config['core'] == 'px68k'):
        coreSettings.save('px68k_disk_path', '"disabled"')

    if (system.config['core'] == 'mednafen_psx'):
        # internal resolution
        if system.isOptSet('internal_resolution'):
            coreSettings.save("beetle_psx_hw_internal_resolution", system.config["internal_resolution"])
        else:
            coreSettings.save("beetle_psx_hw_internal_resolution", "1x(native)")
        # texture filtering
        if system.isOptSet('texture_filtering'):
            coreSettings.save("beetle_psx_hw_filter", system.config["texture_filtering"])
        else:
            coreSettings.save("beetle_psx_hw_filter", "nearest")
        # widescreen hack
        if system.isOptSet('widescreen_hack'):
            coreSettings.save("beetle_psx_hw_widescreen_hack", system.config["widescreen_hack"])
        else:
            coreSettings.save("beetle_psx_hw_widescreen_hack", "disabled")

    if (system.config['core'] == 'pcsx_rearmed'):
        for n in range(1, 8+1):
            val = coreSettings.load('pcsx_rearmed_pad{}type'.format(n))
            if val == '"none"' or val == "" or val is None:
                coreSettings.save('pcsx_rearmed_pad{}type'.format(n), '"standard"')
        # force multitap no value / auto to disable
        # only let enabled when it is forced while previous values enable it
        val = coreSettings.load('pcsx_rearmed_multitap1')
        if val == '"auto"' or val == "" or val is None:
            coreSettings.save('pcsx_rearmed_multitap1', '"disabled"')
        val = coreSettings.load('pcsx_rearmed_multitap2')
        if val == '"auto"' or val == "" or val is None:
            coreSettings.save('pcsx_rearmed_multitap2', '"disabled"')

    # custom : allow the user to configure directly retroarchcore.cfg via batocera.conf via lines like : snes.retroarchcore.opt=val
    for user_config in system.config:
        if user_config[:14] == "retroarchcore.":
            coreSettings.save(user_config[14:], system.config[user_config])

    coreSettings.write()


def generateHatariConf(hatariConf):
    hatariConfig = ConfigParser.ConfigParser()
    # To prevent ConfigParser from converting to lower case
    hatariConfig.optionxform = str
    if os.path.exists(hatariConf):
        hatariConfig.read(hatariConf)

    # Screen section
    if not hatariConfig.has_section("Screen"):
        hatariConfig.add_section("Screen")
    hatariConfig.set("Screen", "bAllowOverscan", "FALSE")

    # update the configuration file
    if not os.path.exists(os.path.dirname(hatariConf)):
        os.makedirs(os.path.dirname(hatariConf))
    with open(hatariConf, 'w') as configfile:
        hatariConfig.write(configfile)
