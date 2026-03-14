from __future__ import annotations

import filecmp
import logging
import os
import re
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import toml

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, configure_emulator, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...utils import vulkan, wine
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

class XeniaGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xenia",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    @staticmethod
    def sync_directories(source_dir: Path, dest_dir: Path):
        dcmp = filecmp.dircmp(source_dir, dest_dir)
        # Files that are only in the source directory or are different
        differing_files = dcmp.diff_files + dcmp.left_only
        for file in differing_files:
            src_path = source_dir / file
            dest_path = dest_dir / file
            # Copy and overwrite the files from source to destination
            shutil.copy2(src_path, dest_path)

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Use wine proton
        wine_runner = wine.Runner("wine-proton", 'xbox360')

        xeniaConfig = CONFIGS / 'xenia'
        xeniaCache = CACHE / 'xenia'
        xeniaSaves = SAVES / 'xbox360'
        emupath = wine_runner.bottle_dir / 'xenia'
        canarypath = wine_runner.bottle_dir / 'xenia-canary'

        core = system.config.core

        # check Vulkan first before doing anything
        if vulkan.is_available():
            _logger.debug("Vulkan driver is available on the system.")
            vulkan_version = vulkan.get_version()
            if vulkan_version > "1.3":
                _logger.debug("Using Vulkan version: %s", vulkan_version)
            else:
                if system.config.get('xenia_api') == "D3D12":
                    _logger.debug("Vulkan version: %s is not compatible with Xenia when using D3D12", vulkan_version)
                    _logger.debug("You may have performance & graphical errors, switching to native Vulkan")
                    system.config['xenia_api'] = "Vulkan"
                else:
                    _logger.debug("Vulkan version: %s is not recommended with Xenia", vulkan_version)
        else:
            _logger.debug("*** Vulkan driver required is not available on the system!!! ***")
            sys.exit()

        # set to 64bit environment by default
        os.environ['WINEARCH'] = 'win64'

        # make system directories
        mkdir_if_not_exists(wine_runner.bottle_dir)
        mkdir_if_not_exists(xeniaConfig)
        mkdir_if_not_exists(xeniaCache)
        mkdir_if_not_exists(xeniaSaves)

        # create dir & copy xenia exe to wine bottle as necessary
        if not emupath.exists():
            shutil.copytree('/usr/xenia', emupath)
        if not canarypath.exists():
            shutil.copytree('/usr/xenia-canary', canarypath)
        # check binary then copy updated xenia exe's as necessary
        if not filecmp.cmp('/usr/xenia/xenia.exe', emupath / 'xenia.exe'):
            shutil.copytree('/usr/xenia', emupath, dirs_exist_ok=True)
        # xenia canary - copy patches directory also
        if not filecmp.cmp('/usr/xenia-canary/xenia_canary.exe', canarypath / 'xenia_canary.exe'):
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)
        if not (canarypath / 'patches').exists():
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)
        # update patches accordingly
        self.sync_directories(Path('/usr/xenia-canary'), canarypath)

        # create portable txt file to try & stop file spam
        if not (emupath / 'portable.txt').exists():
            with (emupath / 'portable.txt').open('w'):
                pass
        if not (canarypath / 'portable.txt').exists():
            with (canarypath / 'portable.txt').open('w'):
                pass

        wine_runner.install_wine_trick('vcrun2022')

        dll_files = ["d3d12.dll", "d3d12core.dll", "d3d11.dll", "d3d10core.dll", "d3d9.dll", "d3d8.dll", "dxgi.dll"]
        # Create symbolic links for 64-bit DLLs
        for dll in dll_files:
            try:
                src_path = wine.WINE_BASE / "dxvk" / "x64" / dll
                dest_path = wine_runner.bottle_dir / "drive_c" / "windows" / "system32" / dll
                # Remove existing link if it already exists
                if dest_path.exists() or dest_path.is_symlink():
                    dest_path.unlink()
                dest_path.symlink_to(src_path)
            except Exception as e:
                _logger.debug("Error creating 64-bit link for %s: %s", dll, e)

        # Create symbolic links for 32-bit DLLs
        for dll in dll_files:
            try:
                src_path = wine.WINE_BASE / "dxvk" / "x32" / dll
                dest_path = wine_runner.bottle_dir / "drive_c" / "windows" / "syswow64" / dll
                # Remove existing link if it already exists
                if dest_path.exists() or dest_path.is_symlink():
                    dest_path.unlink()
                dest_path.symlink_to(src_path)
            except Exception as e:
                _logger.debug("Error creating 32-bit link for %s: %s", dll, e)

        # are we loading a digital title?
        if rom.suffix == '.xbox360':
            _logger.debug('Found .xbox360 playlist: %s', rom)
            pathLead = rom.parent
            with rom.open() as openFile:
                # Read only the first line of the file.
                firstLine = openFile.readlines(1)[0]
                # Strip of any new line characters.
                firstLine = firstLine.strip('\n').strip('\r').lstrip('/')
                _logger.debug('Checking if specified disc installation / XBLA file actually exists...')
                xblaFullPath = pathLead / firstLine
                if xblaFullPath.exists():
                    _logger.debug('Found! Switching active rom to: %s', firstLine)
                    rom = xblaFullPath
                else:
                    _logger.error('Disc installation/XBLA title %s from %s not found, check path or filename.', firstLine, rom)

        # adjust the config toml file accordingly
        config: dict[str, dict[str, Any]] = {}
        if core == 'xenia-canary':
            toml_file = canarypath / 'xenia-canary.config.toml'
        else:
            toml_file = emupath / 'xenia.config.toml'
        if toml_file.is_file():
            with toml_file.open() as f:
                config: dict[str, dict[str, Any]] = toml.load(f)

        # [ Now adjust the config file defaults & options we want ]
        # add node CPU
        if 'CPU' not in config:
            config['CPU'] = {}
        # hack, needed for certain games
        config['CPU'] = {'break_on_unimplemented_instructions': False}
        # add node Content
        if 'Content' not in config:
            config['Content'] = {}
        # default 1 = First license enabled. Generally the full version license in Xbox Live Arcade (XBLA) titles.
        config['Content'] = {'license_mask': system.config.get_int('xenia_license', 1)}

        # add node D3D12
        if 'D3D12' not in config:
            config['D3D12'] = {}
        # readback resolve
        config['D3D12']['d3d12_readback_resolve'] = system.config.get_bool('xenia_readback_resolve')

        # add node Display
        if 'Display' not in config:
            config['Display'] = {}
        # always run fullscreen & set internal resolution - default 1280x720
        config['Display'] = {
            'fullscreen': True,
            'internal_display_resolution': system.config.get_int('xenia_resolution', 8)}
        # add node GPU
        if 'GPU' not in config:
            config['GPU'] = {}
        # may be used to bypass fetch constant type errors in certain games.
        # set the API to use
        config['GPU']['gpu'] = system.config.get('xenia_api', 'D3D12').lower()

        # vsync
        config['GPU']['vsync'] = system.config.get_bool('xenia_vsync', True)
        config['GPU']['framerate_limit'] = system.config.get_int('xenia_vsync_fps', 0)
        # page state
        config['GPU']['clear_memory_page_state'] = system.config.get_bool('xenia_page_state')
        # render target path
        config['GPU']['render_target_path_d3d12'] = system.config.get('xenia_target_path', 'rtv')
        # query occlusion
        config['GPU']['query_occlusion_fake_sample_count'] = system.config.get_int('xenia_query_occlusion', 1000)
        # cache
        config['GPU']['texture_cache_memory_limit_hard'] = system.config.get_int('xenia_limit_hard', 768)
        config['GPU']['texture_cache_memory_limit_render_to_texture'] = system.config.get_int('xenia_limit_render_to_texture', 24)
        config['GPU']['texture_cache_memory_limit_soft'] = system.config.get_int('xenia_limit_soft', 384)
        config['GPU']['texture_cache_memory_limit_soft_lifetime'] = system.config.get_int('xenia_limit_soft_lifetime', 30)
        # add node General
        if 'General' not in config:
            config['General'] = {}
        # disable discord
        config['General']['discord'] = False
        # patches
        config['General'] = {'apply_patches': system.config.get_bool('xenia_patches')}
        # add node HID
        if 'HID' not in config:
            config['HID'] = {}
        # ensure we use sdl for controllers
        config['HID'] = {'hid': 'sdl'}
        # add node Logging
        if 'Logging' not in config:
            config['Logging'] = {}
        # reduce log spam
        config['Logging'] = {
            'log_level': 1
            }
        # add node Memory
        if 'Memory' not in config:
            config['Memory'] = {}
        # certain games require this to set be set to false to work around crashes.
        config['Memory'] = {'protect_zero': False}
        # add node Storage
        if 'Storage' not in config:
            config['Storage'] = {}
        # certain games require this to set be set to true to work around crashes.
        config['Storage'] = {
            'cache_root': str(xeniaCache),
            'content_root': str(xeniaSaves),
            'mount_scratch': True,
            'storage_root': str(xeniaConfig)
            }
        # mount cache
        config['Storage']['mount_cache'] = system.config.get_bool('xenia_cache', True)

        # add node UI
        if 'UI' not in config:
            config['UI'] = {}
        # run headless ?
        config['UI']['headless'] = system.config.get_bool('xenia_headless')
        # achievements
        config['UI']['show_achievement_notification'] = system.config.get_bool('xenia_achievement')
        # add node Vulkan
        if 'Vulkan' not in config:
            config['Vulkan'] = {}
        config['Vulkan'] = {'vulkan_sparse_shared_memory': False}
        # add node XConfig
        if 'XConfig' not in config:
            config['XConfig'] = {}
        # console country
        config['XConfig']['user_country'] = system.config.get_int('xenia_country', 103)  # 103 = US
        # language
        config['XConfig']['user_language'] = system.config.get_int('xenia_language', 1)

        # now write the updated toml
        with toml_file.open('w') as f:
            toml.dump(config, f)

        # handle patches files to set all matching toml files keys to true
        rom_name = rom.stem
        # simplify the name for matching
        rom_name = re.sub(r'\[.*?\]', '', rom_name)
        rom_name = re.sub(r'\(.*?\)', '', rom_name)
        if system.config.get_bool('xenia_patches'):
            # pattern to search for matching .patch.toml files
            matching_files = [file_path for file_path in (canarypath / 'patches').glob(f'*{rom_name}*.patch.toml') if re.search(rom_name, file_path.name, re.IGNORECASE)]
            if matching_files:
                for file_path in matching_files:
                    _logger.debug('Enabling patches for: %s', file_path)
                    # load the matchig .patch.toml file
                    with file_path.open('r') as f:
                        patch_toml = toml.load(f)
                    # modify all occurrences of the `is_enabled` key to `true`
                    for patch in patch_toml.get('patch', []):
                        if 'is_enabled' in patch:
                            patch['is_enabled'] = True
                    # save the updated .patch.toml file
                    with file_path.open('w') as f:
                        toml.dump(patch_toml, f)
            else:
                _logger.debug('No patch file found for %s', rom_name)

        # now setup the command array for the emulator
        if configure_emulator(rom):
            if core == 'xenia-canary':
                commandArray = [wine_runner.wine64, canarypath / 'xenia_canary.exe']
            else:
                commandArray = [wine_runner.wine64, emupath / 'xenia.exe']
        else:
            if core == 'xenia-canary':
                commandArray = [wine_runner.wine64, canarypath / 'xenia_canary.exe', f'z:{rom}']
            else:
                commandArray = [wine_runner.wine64, emupath / 'xenia.exe', f'z:{rom}']

        environment = wine_runner.get_environment()
        environment.update(
            {
                'LD_LIBRARY_PATH': f'/usr/lib:{environment["LD_LIBRARY_PATH"]}',
                'LIBGL_DRIVERS_PATH': '/usr/lib/dri',
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0',
                'VKD3D_SHADER_CACHE_PATH': xeniaCache,
                'WINEDLLOVERRIDES': "winemenubuilder.exe=;dxgi,d3d8,d3d9,d3d10core,d3d11,d3d12,d3d12core=n",
            }
        )

        # ensure nvidia driver used for vulkan
        if Path('/var/tmp/nvidia.prime').exists():
            variables_to_remove = ['__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME']
            for variable_name in variables_to_remove:
                if variable_name in os.environ:
                    del os.environ[variable_name]

            environment.update(
                {
                    'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                    'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d'
                }
            )

        return Command.Command(array=commandArray, env=environment)

    # Show mouse on screen when needed
    # xenia auto-hides
    def getMouseMode(self, config, rom):
        return True
