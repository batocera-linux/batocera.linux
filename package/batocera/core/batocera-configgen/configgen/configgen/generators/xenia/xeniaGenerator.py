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
import glob
import re
from utils.logger import get_logger

eslog = get_logger(__name__)

class XeniaGenerator(Generator):

    @staticmethod
    def sync_directories(source_dir, dest_dir):
        dcmp = filecmp.dircmp(source_dir, dest_dir)
        # Files that are only in the source directory or are different
        differing_files = dcmp.diff_files + dcmp.left_only
        for file in differing_files:
            src_path = os.path.join(source_dir, file)
            dest_path = os.path.join(dest_dir, file)
            # Copy and overwrite the files from source to destination
            shutil.copy2(src_path, dest_path)
    
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        wineprefix = '/userdata/system/wine-bottles/xbox360'
        wineBinary = '/usr/wine/ge-custom/bin/wine64'
        xeniaConfig = '/userdata/system/configs/xenia'
        xeniaCache = '/userdata/system/cache/xenia'
        xeniaSaves = '/userdata/saves/xbox360'
        emupath = wineprefix + '/xenia'
        canarypath = wineprefix + '/xenia-canary'

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
        if not os.path.exists(wineprefix):
            os.makedirs(wineprefix)
        if not os.path.exists(xeniaConfig):
            os.makedirs(xeniaConfig)
        if not os.path.exists(xeniaCache):
            os.makedirs(xeniaCache)
        if not os.path.exists(xeniaSaves):
            os.makedirs(xeniaSaves)
        
        # create dir & copy xenia exe to wine bottle as necessary
        if not os.path.exists(emupath):
            shutil.copytree('/usr/xenia', emupath)
        if not os.path.exists(canarypath):
            shutil.copytree('/usr/xenia-canary', canarypath)
        # check binary then copy updated xenia exe's as necessary
        if not filecmp.cmp('/usr/xenia/xenia.exe', emupath + '/xenia.exe'):
            shutil.copytree('/usr/xenia', emupath, dirs_exist_ok=True)
        # xenia canary - copy patches directory also
        if not filecmp.cmp('/usr/xenia-canary/xenia_canary.exe', canarypath + '/xenia_canary.exe'):
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)
        if not os.path.exists(canarypath + '/patches'):
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)
        
        # create portable txt file to try & stop file spam
        if not os.path.exists(emupath + '/portable.txt'):
            with open(emupath + '/portable.txt', 'w') as fp:
                pass
        if not os.path.exists(canarypath + '/portable.txt'):
            with open(canarypath + '/portable.txt', 'w') as fp:
                pass
        
        if not os.path.exists(wineprefix + "/vkd3d.done"):
            cmd = ["/usr/wine/winetricks", "-q", "vkd3d"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/ge-custom/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/ge-custom/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/vkd3d.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/vcrun2019.done"):
            cmd = ["/usr/wine/winetricks", "-q", "vcrun2019"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/ge-custom/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/ge-custom/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/vcrun2019.done", "w") as f:
                f.write("done")

        if not os.path.exists(wineprefix + "/dxvk.done"):
            cmd = ["/usr/wine/winetricks", "-q", "dxvk"]
            env = {"LD_LIBRARY_PATH": "/lib32:/usr/wine/ge-custom/lib/wine", "WINEPREFIX": wineprefix }
            env.update(os.environ)
            env["PATH"] = "/usr/wine/ge-custom/bin:/bin:/usr/bin"
            eslog.debug(f"command: {str(cmd)}")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            exitcode = proc.returncode
            eslog.debug(out.decode())
            eslog.error(err.decode())
            with open(wineprefix + "/dxvk.done", "w") as f:
                f.write("done")

        # check & copy newer dxvk files
        self.sync_directories("/usr/wine/dxvk/x64", wineprefix + "/drive_c/windows/system32")

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
        # add node D3D12
        if 'D3D12' not in config:
            config['D3D12'] = {}
        config['D3D12'] = {'d3d12_readback_resolve': True}
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
        # set the API to use
        if system.isOptSet('xenia_api') and system.config['xenia_api'] == 'Vulkan':
            config['GPU'] = {
                'depth_float24_convert_in_pixel_shader': True,
                'gpu': 'vulkan',
                'gpu_allow_invalid_fetch_constants': True,
                'render_target_path_vulkan': 'any'
            }
        else:
            config['GPU'] = {
                'depth_float24_convert_in_pixel_shader': True,
                'gpu_allow_invalid_fetch_constants': True,
                'gpu': 'd3d12',
                'render_target_path_d3d12': 'rtv'
            }
        # vsync
        config['GPU']['vsync'] = system.config.get('xenia_vsync', False)
        config['GPU']['vsync_fps'] = int(system.config.get('xenia_vsync_fps', 60))
        # page state
        config['GPU']['clear_memory_page_state'] = system.config.get('xenia_page_state', False)
        # render target path
        config['GPU']['render_target_path_d3d12'] = system.config.get('xenia_target_path', 'rtv')
        # query occlusion
        config['GPU']['query_occlusion_fake_sample_count'] = int(system.config.get('xenia_query_occlusion', 1000))
        # readback resolve
        config['GPU']['d3d12_readback_resolve'] = system.config.get('xenia_readback_resolve', False)
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
        if system.isOptSet('xeniaPatches') and system.config['xeniaPatches'] == 'True':
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
            'cache_root': xeniaCache,
            'content_root': xeniaSaves,
            'mount_scratch': True,
            'storage_root': xeniaConfig
            }
        # mount cache
        config['Storage']['mount_cache'] = system.config.get('xenia_cache', False)

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
        
        # handle patches files to set all matching toml files keys to true
        rom_name = os.path.splitext(os.path.basename(rom))[0]
        # simplify the name for matching
        rom_name = re.sub(r'\[.*?\]', '', rom_name)
        rom_name = re.sub(r'\(.*?\)', '', rom_name)
        if system.isOptSet('xeniaPatches') and system.config['xeniaPatches'] == 'True':            
            # pattern to search for matching .patch.toml files
            pattern = os.path.join(canarypath, 'patches', '*' + rom_name + '*.patch.toml')
            matching_files = [file_path for file_path in glob.glob(pattern) if re.search(rom_name, os.path.basename(file_path), re.IGNORECASE)]
            if matching_files:
                for file_path in matching_files:
                    eslog.debug(f'Enabling patches for: {file_path}')
                    # load the matchig .patch.toml file
                    with open(file_path, 'r') as f:
                        patch_toml = toml.load(f)
                    # modify all occurrences of the `is_enabled` key to `true`
                    for patch in patch_toml.get('patch', []):
                        if 'is_enabled' in patch:
                            patch['is_enabled'] = True
                    # save the updated .patch.toml file
                    with open(file_path, 'w') as f:
                        toml.dump(patch_toml, f)
            else:
                eslog.debug(f'No patch file found for {rom_name}')
        
        # now setup the command array for the emulator
        if rom == 'config':
            if core == 'xenia-canary':
                commandArray = [wineBinary, canarypath + '/xenia_canary.exe']
            else:
                commandArray = [wineBinary, emupath + '/xenia.exe']
        else:
            if core == 'xenia-canary':
                commandArray = [wineBinary, canarypath + '/xenia_canary.exe', 'z:' + rom]
            else:
                commandArray = [wineBinary, emupath + '/xenia.exe', 'z:' + rom]
        
        environment={
                'WINEPREFIX': wineprefix,
                'LD_LIBRARY_PATH': '/usr/lib:/lib32:/usr/wine/ge-custom/lib/wine',
                'LIBGL_DRIVERS_PATH': '/usr/lib/dri',
                'WINEESYNC': '1',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0',
                # hum pw 0.2 and 0.3 are hardcoded, not nice
                'SPA_PLUGIN_DIR': '/usr/lib/spa-0.2:/lib32/spa-0.2',
                'PIPEWIRE_MODULE_DIR': '/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
                'VKD3D_SHADER_CACHE_PATH': xeniaCache
            }
        
        # ensure nvidia driver used for vulkan
        if os.path.exists('/var/tmp/nvidia.prime'):
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
