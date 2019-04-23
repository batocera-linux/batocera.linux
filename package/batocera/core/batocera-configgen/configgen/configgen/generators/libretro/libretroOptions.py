#!/usr/bin/env python
import sys
import os
from settings.unixSettings import UnixSettings

def generateCoreSettings(retroarchCore, system):
    # retroarch-core-options.cfg
    if not os.path.exists(os.path.dirname(retroarchCore)):
        os.makedirs(os.path.dirname(retroarchCore))    
    
    coreSettings = UnixSettings(retroarchCore, separator=' ')

    # default
    coreSettings.save('system_hw',          'auto')
    coreSettings.save('region_detect',      'auto')
    coreSettings.save('force_dtack',        'enabled')
    coreSettings.save('addr_error',         'enabled')
    coreSettings.save('lock_on',            'disabled')
    coreSettings.save('padtype',            'auto')
    coreSettings.save('multitap',           'disabled')
    coreSettings.save('portb',              'enabled')
    coreSettings.save('ym2413',             'enabled')
    coreSettings.save('dac_bits',           'disabled')
    coreSettings.save('blargg_ntsc_filter', 'disabled')
    coreSettings.save('overscan',           'disabled')
    coreSettings.save('render',             'single field')
    coreSettings.save('dino_timer',         'enabled')
    coreSettings.save('gamepad',            'gamepad')
    coreSettings.save('frameskip',          '0')
    coreSettings.save('region',             'Auto')
    coreSettings.save('pad1type',           'standard')
    coreSettings.save('rearmed_drc',        'enabled')
    coreSettings.save('nes_palette',        'asqrealc')
    coreSettings.save('gg_extra',           'disabled')
    coreSettings.save('nes_palette',        'asqrealc')

    # Atari 800 and 5200
    if (system.config['core'] == 'atari800'):
        if (system.name == 'atari800'):
            coreSettings.save('atari800_system',    '"800XL (64K)"')
            coreSettings.save('RAM_SIZE',           '64')
            coreSettings.save('STEREO_POKEY',       '1')
            coreSettings.save('BUILTIN_BASIC',      '1')
        else:
            coreSettings.save('atari800_system',    '5200')
            coreSettings.save('RAM_SIZE',           '16')
            coreSettings.save('STEREO_POKEY',       '0')
            coreSettings.save('BUILTIN_BASIC',      '0')

    # Colecovision and MSX
    if (system.config['core'] == 'bluemsx'):
        coreSettings.save('bluemsx_msxtype', 'Auto')

    if (system.config['core'] == 'fmsx'):
        coreSettings.save('fmsx_mode',              'MSX2')
        coreSettings.save('fmsx_video_mode',        'NTSC')
        coreSettings.save('fmsx_mapper_type_mode',  'Guess Mapper Type A')

    if (system.config['core'] == 'tgbdual'):
        coreSettings.save('tgbdual_audio_output',       'Game Boy #1')
        coreSettings.save('tgbdual_gblink_enable',      'enabled')
        coreSettings.save('tgbdual_screen_placement',   'left-right')
        coreSettings.save('tgbdual_single_screen_mp',   'both players')
        coreSettings.save('tgbdual_switch_screens',     'normal')

    if (system.config['core'] == 'desmume'):
        coreSettings.save('desmume_pointer_device_r',   'emulated')

    if (system.config['core'] == 'mame078'):
        coreSettings.save('mame2003_skip_disclaimer',   'enabled')
        coreSettings.save('mame2003_skip_warnings',     'enabled')

    if (system.config['core'] == 'mame078plus'):
        coreSettings.save('mame2003-plus_skip_disclaimer',  'enabled')
        coreSettings.save('mame2003-plus_skip_warnings',    'enabled')

    if (system.config['core'] == 'pce'):
        coreSettings.save('pce_fast_cdimagecache',  'disabled')
        coreSettings.save('pce_nospritelimit',      'disabled')
        coreSettings.save('pce_keepaspect',         'enabled')
        coreSettings.save('pce_cddavolume',         '100')
        coreSettings.save('pce_adpcmvolume',        '100')
        coreSettings.save('pce_cdpsgvolume',        '100')
        coreSettings.save('pce_cdspeed',            '1')

    if (system.config['core'] == 'picodrive'):
        coreSettings.save('picodrive_input1',   '6 button pad')
        coreSettings.save('picodrive_input2',   '6 button pad')
        coreSettings.save('picodrive_sprlim',   'disabled')
        coreSettings.save('picodrive_ramcart',  'disabled')
        coreSettings.save('picodrive_drc',      'enabled')

    if (system.config['core'] == 'fba'):
        coreSettings.save('fba-diagnostics',        'disabled')
        coreSettings.save('fba-unibios',            'disabled')
        coreSettings.save('fba-cpu-speed-adjust',   '100')
        coreSettings.save('fba-controls',           'gamepad')

    if (system.config['core'] == '81'):
        coreSettings.save('81_fast_load',       'enabled')
        coreSettings.save('81_chroma_81',       'enabled')
        coreSettings.save('81_video_presets',   'clean')
        coreSettings.save('81_sound',           'Zon X-81')

    if (system.config['core'] == 'cap32'):
        coreSettings.save('cap32_autorun',  'enabled')
        coreSettings.save('cap32_Model',    '6128')
        coreSettings.save('cap32_Ram',      '128')

    if (system.config['core'] == 'fuse'):
        coreSettings.save('fuse_machine',    'Spectrum 128K')

    if (system.config['core'] == 'gb'):
        coreSettings.save('gb_colorization', 'disabled')
        coreSettings.save('gb_gbamode',      'disabled')

    if (system.config['core'] == 'gbc'):
        coreSettings.save('gbc_color_correction',   'enabled')

    if (system.config['core'] == 'snes9x'):
        coreSettings.save('snes9x_opt0',    'disabled')
    
    if (system.config['core'] == 'pcsx_rearmed'):
        coreSettings.save('pcsx_rearmed_duping_enable',   'on')