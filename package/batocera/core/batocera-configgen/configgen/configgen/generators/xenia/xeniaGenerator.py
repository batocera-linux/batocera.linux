from __future__ import annotations

import filecmp
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import toml

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, HOME, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

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
        rom_path = Path(rom)

        wineprefix = HOME / 'wine-bottles' / 'xbox360'
        winePath = Path('/usr/wine/wine-tkg')
        wineBinary = winePath / 'bin' / 'wine64'
        xeniaConfig = CONFIGS / 'xenia'
        xeniaCache = CACHE / 'xenia'
        xeniaSaves = SAVES / 'xbox360'
        emupath = wineprefix / 'xenia'
        canarypath = wineprefix / 'xenia-canary'

        core = system.config['core']

        # check Vulkan first before doing anything
        try:
            have_vulkan = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasVulkan"], text=True).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    vulkan_version = subprocess.check_output(["/usr/bin/batocera-vulkan", "vulkanVersion"], text=True).strip()
                    if vulkan_version > "1.3":
                        eslog.debug("Using Vulkan version: {}".format(vulkan_version))
                    else:
                        if system.isOptSet('xenia_api') and system.config['xenia_api'] == "D3D12":
                            eslog.debug("Vulkan version: {} is not compatible with Xenia when using D3D12".format(vulkan_version))
                            eslog.debug("You may have performance & graphical errors, switching to native Vulkan".format(vulkan_version))
                            system.config['xenia_api'] = "Vulkan"
                        else:
                            eslog.debug("Vulkan version: {} is not recommended with Xenia".format(vulkan_version))
                except subprocess.CalledProcessError:
                    eslog.debug("Error checking for Vulkan version.")
            else:
                eslog.debug("*** Vulkan driver required is not available on the system!!! ***")
                sys.exit()
        except subprocess.CalledProcessError:
            eslog.debug("Error executing batocera-vulkan script.")

        # set to 64bit environment by default
        os.environ['WINEARCH'] = 'win64'

        # make system directories
        mkdir_if_not_exists(wineprefix)
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
        
        vcrun2019_done = wineprefix / "vcrun2019.done"
        if not vcrun2019_done.exists():
            cmd = ["/usr/wine/winetricks", "-q", "vcrun2019"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/wine-tkg/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/wine-tkg/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with vcrun2019_done.open("w") as f:
                f.write("done")
        
        dll_files = ["d3d12.dll", "d3d12core.dll", "d3d11.dll", "d3d10core.dll", "d3d9.dll", "d3d8.dll", "dxgi.dll"]
        # Create symbolic links for 64-bit DLLs  
        try:
            for dll in dll_files:
                src_path = Path("/usr/wine/dxvk/x64") / dll
                dest_path = wineprefix / "drive_c" / "windows" / "system32" / dll
                # Remove existing link if it already exists
                if dest_path.exists() or dest_path.is_symlink():
                    dest_path.unlink()
                dest_path.symlink_to(src_path)
        except Exception as e:
            eslog.debug(f"Error creating 64-bit link for {dll}: {e}")

        # Create symbolic links for 32-bit DLLs
        try:
            for dll in dll_files:
                src_path = Path("/usr/wine/dxvk/x32") / dll
                dest_path = wineprefix / "drive_c" / "windows" / "syswow64" / dll
                # Remove existing link if it already exists
                if dest_path.exists() or dest_path.is_symlink():
                    dest_path.unlink()
                dest_path.symlink_to(src_path)
        except Exception as e:
            eslog.debug(f"Error creating 32-bit link for {dll}: {e}")
        
        # are we loading a digital title?
        if rom_path.suffix == '.xbox360':
            eslog.debug(f'Found .xbox360 playlist: {rom}')
            pathLead = rom_path.parent
            with rom_path.open() as openFile:
                # Read only the first line of the file.
                firstLine = openFile.readlines(1)[0]
                # Strip of any new line characters.
                firstLine = firstLine.strip('\n').strip('\r')
                eslog.debug(f'Checking if specified disc installation / XBLA file actually exists...')
                xblaFullPath = pathLead / firstLine
                if xblaFullPath.exists():
                    eslog.debug(f'Found! Switching active rom to: {firstLine}')
                    rom_path = xblaFullPath
                    rom = str(xblaFullPath)
                else:
                    eslog.error(f'Disc installation/XBLA title {firstLine} from {rom} not found, check path or filename.')

        # adjust the config toml file accordingly
        config = {}
        if core == 'xenia-canary':
            toml_file = canarypath / 'xenia-canary.config.toml'
        else:
            toml_file = emupath / 'xenia.config.toml'
        if toml_file.is_file():
            with toml_file.open() as f:
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
        # default 1 = First license enabled. Generally the full version license in Xbox Live Arcade (XBLA) titles.
        if system.isOptSet('xenia_license'):
            config['Content'] = {'license_mask': int(system.config['xenia_license'])}
        else:
            config['Content'] = {'license_mask': 1}
        # add node D3D12
        if 'D3D12' not in config:
            config['D3D12'] = {}
        # readback resolve
        if system.isOptSet('xenia_readback_resolve') and system.config['xenia_readback_resolve'] == 'True':
            config['D3D12']['d3d12_readback_resolve'] = True
        else:
            config['D3D12']['d3d12_readback_resolve'] = False
        # add node Display
        if 'Display' not in config:
            config['Display'] = {}
        # always run fullscreen & set internal resolution - default 1280x720
        displayRes = 8
        if system.isOptSet('xenia_resolution'):
            displayRes = int(system.config['xenia_resolution'])
        config['Display'] = {
            'fullscreen': True,
            'internal_display_resolution': displayRes}
        # add node GPU
        if 'GPU' not in config:
            config['GPU'] = {}
        # may be used to bypass fetch constant type errors in certain games.
        # set the API to use
        if system.isOptSet('xenia_api') and system.config['xenia_api'] == 'Vulkan':
            config['GPU']['gpu'] = 'vulkan'
        else:
            config['GPU']['gpu'] = 'd3d12'
        # vsync
        if system.isOptSet('xenia_vsync') and system.config['xenia_vsync'] == 'False':
            config['GPU']['vsync'] = False
        else:
            config['GPU']['vsync'] = True
        config['GPU']['framerate_limit'] = int(system.config.get('xenia_vsync_fps', 0))
        # page state
        if system.isOptSet('xenia_page_state') and system.config['xenia_page_state'] == 'True':
            config['GPU']['clear_memory_page_state'] = True
        else:
            config['GPU']['clear_memory_page_state'] = False
        # render target path
        config['GPU']['render_target_path_d3d12'] = system.config.get('xenia_target_path', 'rtv')
        # query occlusion
        config['GPU']['query_occlusion_fake_sample_count'] = int(system.config.get('xenia_query_occlusion', 1000))
        # cache
        config['GPU']['texture_cache_memory_limit_hard'] = int(system.config.get('xenia_limit_hard', 768))
        config['GPU']['texture_cache_memory_limit_render_to_texture'] = int(system.config.get('xenia_limit_render_to_texture', 24))
        config['GPU']['texture_cache_memory_limit_soft'] = int(system.config.get('xenia_limit_soft', 384))
        config['GPU']['texture_cache_memory_limit_soft_lifetime'] = int(system.config.get('xenia_limit_soft_lifetime', 30))
        # add node General
        if 'General' not in config:
            config['General'] = {}
        # disable discord
        config['General']['discord'] = False
        # patches
        if system.isOptSet('xenia_patches') and system.config['xenia_patches'] == 'True':
            config['General'] = {'apply_patches': True}
        else:
            config['General'] = {'apply_patches': False}
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
        if system.isOptSet('xenia_cache') and system.config['xenia_cache'] == 'False':
            config['Storage']['mount_cache'] = False
        else:
            config['Storage']['mount_cache'] = True
        
        # add node UI
        if 'UI' not in config:
            config['UI'] = {}
        # run headless ?
        if system.isOptSet('xenia_headless') and system.config['xenia_headless'] == 'True':
            config['UI']['headless'] = True
        else:
            config['UI']['headless'] = False
        # achievements
        if system.isOptSet('xenia_achievement') and system.config['xenia_achievement'] == 'True':
            config['UI']['show_achievement_notification'] = True
        else:
            config['UI']['show_achievement_notification'] = False
        # add node Vulkan
        if 'Vulkan' not in config:
            config['Vulkan'] = {}
        config['Vulkan'] = {'vulkan_sparse_shared_memory': False}
        # add node XConfig
        if 'XConfig' not in config:
            config['XConfig'] = {}
        # console country
        if system.isOptSet('xenia_country'):
            config['XConfig'] = {'user_country': int(system.config['xenia_country'])}
        else:
            config['XConfig'] = {'user_country': 103} # US
        # language
        if system.isOptSet('xenia_language'):
            config['XConfig'] = {'user_language': int(system.config['xenia_language'])}
        else:
            config['XConfig'] = {'user_language': 1}
        
        # now write the updated toml
        with toml_file.open('w') as f:
            toml.dump(config, f)

        # handle patches files to set all matching toml files keys to true
        rom_name = rom_path.stem
        # simplify the name for matching
        rom_name = re.sub(r'\[.*?\]', '', rom_name)
        rom_name = re.sub(r'\(.*?\)', '', rom_name)
        if system.isOptSet('xenia_patches') and system.config['xenia_patches'] == 'True':
            # pattern to search for matching .patch.toml files
            pattern = canarypath / 'patches' / f'*{rom_name}*.patch.toml'
            matching_files = [file_path for file_path in (canarypath / 'patches').glob(f'*{rom_name}*.patch.toml') if re.search(rom_name, file_path.name, re.IGNORECASE)]
            if matching_files:
                for file_path in matching_files:
                    eslog.debug(f'Enabling patches for: {file_path}')
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
                eslog.debug(f'No patch file found for {rom_name}')

        # now setup the command array for the emulator
        if rom == 'config':
            if core == 'xenia-canary':
                commandArray = [wineBinary, canarypath / 'xenia_canary.exe']
            else:
                commandArray = [wineBinary, emupath / 'xenia.exe']
        else:
            if core == 'xenia-canary':
                commandArray = [wineBinary, canarypath / 'xenia_canary.exe', 'z:' + rom]
            else:
                commandArray = [wineBinary, emupath / 'xenia.exe', 'z:' + rom]

        environment={
                'WINEPREFIX': wineprefix,
                'LD_LIBRARY_PATH': '/usr/lib:/lib32:/usr/wine/wine-tkg/lib/wine',
                'LIBGL_DRIVERS_PATH': '/usr/lib/dri',
                'WINEFSYNC': '1',
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0',
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
                'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
                'VKD3D_SHADER_CACHE_PATH': xeniaCache,
                'WINEDLLOVERRIDES': "winemenubuilder.exe=;dxgi,d3d8,d3d9,d3d10core,d3d11,d3d12,d3d12core=n",
            }
        
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
