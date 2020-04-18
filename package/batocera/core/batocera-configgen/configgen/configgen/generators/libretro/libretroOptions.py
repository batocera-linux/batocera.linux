#!/usr/bin/env python
import sys
import os
import ConfigParser
from settings.unixSettings import UnixSettings

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
            coreSettings.save('atari800_system',    '"800XL (64K)"')
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

    if (system.config['core'] == 'pcsx_rearmed'):
        for n in range(1, 8+1):
            val = coreSettings.load('pcsx_rearmed_pad{}type'.format(n))
            if val == '"none"' or val == "" or val is None:
                coreSettings.save('pcsx_rearmed_pad{}type'.format(n), '"standard"')

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
