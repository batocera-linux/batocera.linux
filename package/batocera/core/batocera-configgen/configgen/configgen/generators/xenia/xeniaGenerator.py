#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import sys
import shutil
import controllersConfig
import filecmp
import subprocess
import toml
from utils.logger import get_logger

eslog = get_logger(__name__)

class XeniaGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        wineprefix = batoceraFiles.SAVES + '/xenia-bottle'
        emupath = wineprefix + '/xenia'
        canarypath = wineprefix + '/xenia-canary'

        core = system.config['core']

        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)

        # create dir & copy xenia exe to wine bottle as necessary
        if not os.path.exists(emupath):
            shutil.copytree('/usr/xenia', emupath)
        if not os.path.exists(canarypath):
            shutil.copytree('/usr/xenia-canary', canarypath)
        # check binary then copy updated xenia exe's as necessary
        if not filecmp.cmp('/usr/xenia/xenia.exe', emupath + '/xenia.exe'):
            shutil.copytree('/usr/xenia', emupath, dirs_exist_ok=True)
        if not filecmp.cmp('/usr/xenia-canary/xenia_canary.exe', canarypath + '/xenia_canary.exe'):
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)

        # create portable txt file to try & stop file spam
        if not os.path.exists(emupath + '/portable.txt'):
            with open(emupath + '/portable.txt', 'w') as fp:
                pass
        if not os.path.exists(canarypath + '/portable.txt'):
            with open(canarypath + '/portable.txt', 'w') as fp:
                pass

        # are we loading a digital title?
        if os.path.splitext(rom)[1] == '.xbox360':
            eslog.debug(f'Found .xbox360 playlist: {rom}')
            pathLead = os.path.dirname(rom)
            openFile = open(rom, 'r')
            # Read only the first line of the file.
            firstLine = openFile.readlines(1)[0]
            # Strip of any new line characters.
            firstLine = firstLine.strip('\n').strip('\r')
            eslog.debug(f'Checking if specified disc installation / XBLA file actually exists...')
            xblaFullPath = pathLead + '/' + firstLine
            if os.path.exists(xblaFullPath):
                eslog.debug(f'Found! Switching active rom to: {firstLine}')
                rom = xblaFullPath
            else:
                eslog.error(f'Disc installation/XBLA title {firstLine} from {rom} not found, check path or filename.')
            openFile.close()
        
        # adjust the config toml file accordingly
        config = {}
        if core == 'xenia-canary':
            toml_file = canarypath + '/xenia-canary.config.toml'
        else:
            toml_file = emupath + '/xenia.config.toml'
        if os.path.isfile(toml_file):
            with open(toml_file) as f:
                config = toml.load(f)
        
        # [ Now adjust the config file defaults & options we want ]
        # add node CPU
        if 'CPU' not in config:
            config['CPU'] = {}
        # hack, needed for certain games
        config['CPU'] = {'break_on_unimplemented_instructions': False}
        # add node Content
        if 'Content' not in config:
            config['Content'] = {}
        # Default 1= First license enabled. Generally the full version license in Xbox Live Arcade (XBLA) titles.
        if system.isOptSet('xeniaLicense'):
            config['Content'] = {'license_mask': int(system.config['xeniaLicense'])}
        else:
            config['Content'] = {'license_mask': 1}
        # add node Display
        if 'Display' not in config:
            config['Display'] = {}
        # always run fullscreen & set internal resolution - default 1280x720
        displayRes = 8
        if system.isOptSet('xeniaResolution'):
            displayRes = int(system.config['xeniaResolution'])
        config['Display'] = {
            'fullscreen': True,
            'internal_display_resolution': displayRes}
        # add node GPU
        if 'GPU' not in config:
            config['GPU'] = {}
        # may be used to bypass fetch constant type errors in certain games.
        # ensure we use vulkan
        config['GPU'] = {
            'depth_float24_convert_in_pixel_shader': True,
            'gpu': 'vulkan',
            'gpu_allow_invalid_fetch_constants': True,
            'render_target_path_vulkan': 'any'}
        # add node General
        if 'General' not in config:
            config['General'] = {}
        # disable discord
        config['General'] = {'discord': False} 
        # add node HID
        if 'HID' not in config:
            config['HID'] = {}
        # ensure we use sdl2 for controllers
        config['HID'] = {'hid': 'sdl'}
        # add node Memory
        if 'Memory' not in config:
            config['Memory'] = {}
        # certain games require this to set be set to false to work around crashes.
        config['Memory'] = {'protect_zero': False}
        # add node UI
        if 'UI' not in config:
            config['UI'] = {}
        # run headless ?
        if system.isOptSet('xeniaHeadless') and system.getOptBoolean('xeniaHeadless') == True:
            config['UI'] = {'headless': True}
        else:
            config['UI'] = {'headless': False}
        # add node Vulkan
        if 'Vulkan' not in config:
            config['Vulkan'] = {}
        config['Vulkan'] = {'vulkan_sparse_shared_memory': False}
        # add node XConfig
        if 'XConfig' not in config:
            config['XConfig'] = {}
        # language
        if system.isOptSet('xeniaLanguage'):
            config['XConfig'] = {'user_language': int(system.config['xeniaLanguage'])}
        else:
            config['XConfig'] = {'user_language': 1}
        
        # now write the updated toml
        with open(toml_file, 'w') as f:
            toml.dump(config, f)

        # now setup the command array for the emulator
        if rom == 'config':
            if core == 'xenia-canary':
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia-canary/xenia_canary.exe']
            else:
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia/xenia.exe']
        else:
            if core == 'xenia-canary':
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia-canary/xenia_canary.exe', 'z:' + rom]
            else:
                commandArray = ['/usr/wine/lutris/bin/wine64', '/userdata/saves/xenia-bottle/xenia/xenia.exe', 'z:' + rom]

        return Command.Command(
            array=commandArray,
            env={
                'WINEPREFIX': wineprefix,
                'LD_LIBRARY_PATH': '/usr/lib:/lib32:/usr/wine/lutris/lib/wine',
                'LIBGL_DRIVERS_PATH': '/usr/lib/dri',
                'WINEESYNC': '1',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0',
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
                'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3'
            })

    # Show mouse on screen when needed
    # xenia auto-hides
    def getMouseMode(self, config):
        return True
