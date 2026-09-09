from __future__ import annotations

import filecmp
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Any, Final

import toml

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, SAVES
from batocera_common.vulkan import get_version as vulkan_get_version, is_available as vulkan_is_available
from batocera_common.wine import WINE_BASE, Runner
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext
from batocera_launch.paths import configure_emulator

_logger = logging.getLogger(__name__)

_XBOX360_SAVES: Final = SAVES / 'xbox360'

# 64-bit DLLs go into system32, 32-bit into syswow64 - opposite of what the
# names suggest, but that is how Windows lays out a WoW64 prefix.
_DLLS: Final = ('d3d12.dll', 'd3d12core.dll', 'd3d11.dll', 'd3d10core.dll', 'd3d9.dll', 'd3d8.dll', 'dxgi.dll')
_DLL_ARCHES: Final = (('x64', 'system32'), ('x32', 'syswow64'))


def _sync_directories(source_dir: Path, dest_dir: Path, /) -> None:
    dcmp = filecmp.dircmp(source_dir, dest_dir)
    for name in [*dcmp.diff_files, *dcmp.left_only]:
        shutil.copy2(source_dir / name, dest_dir / name)


@cached_dataclass
class Xenia(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'xenia',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def config_dir(self) -> Path:
        # Shared between the xenia and xenia-canary entry points - both binaries
        # are always installed and configured, so they share one bottle/config.
        return CONFIGS / 'xenia'

    @property
    def needs_mouse(self) -> bool:
        # xenia auto-hides its own cursor
        return True

    async def configure(self) -> Command:
        if not vulkan_is_available():
            raise BatoceraException('Vulkan driver required is not available on the system')

        is_canary = self.core == 'xenia-canary'

        vulkan_version = vulkan_get_version()
        if vulkan_version > '1.3':
            _logger.debug('Using Vulkan version: %s', vulkan_version)
        elif self.config.get('xenia_api') == 'D3D12':
            _logger.debug('Vulkan version %s is not compatible with Xenia when using D3D12', vulkan_version)
            _logger.debug('You may have performance & graphical errors, switching to native Vulkan')
            self.config['xenia_api'] = 'Vulkan'
        else:
            _logger.debug('Vulkan version %s is not recommended with Xenia', vulkan_version)

        # Set here (not just on the launch command's own env below) since
        # install_wine_trick() below inherits the process environment, not
        # get_environment()'s.
        os.environ['WINEARCH'] = 'win64'

        wine_runner = Runner('wine-proton', 'xbox360')
        xenia_cache = CACHE / 'xenia'

        wine_runner.bottle_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        xenia_cache.mkdir(parents=True, exist_ok=True)
        _XBOX360_SAVES.mkdir(parents=True, exist_ok=True)

        emupath = wine_runner.bottle_dir / 'xenia'
        canarypath = wine_runner.bottle_dir / 'xenia-canary'

        # Create dir & copy xenia exe(s) to the wine bottle as necessary, and keep
        # them in sync with the installed binaries (both variants regardless of
        # which one is selected, since either can be picked at any time).
        if not emupath.exists():
            shutil.copytree('/usr/xenia', emupath)
        if not canarypath.exists():
            shutil.copytree('/usr/xenia-canary', canarypath)
        if not filecmp.cmp('/usr/xenia/xenia.exe', emupath / 'xenia.exe'):
            shutil.copytree('/usr/xenia', emupath, dirs_exist_ok=True)
        if not filecmp.cmp('/usr/xenia-canary/xenia_canary.exe', canarypath / 'xenia_canary.exe'):
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)
        if not (canarypath / 'patches').exists():
            shutil.copytree('/usr/xenia-canary', canarypath, dirs_exist_ok=True)
        _sync_directories(Path('/usr/xenia-canary'), canarypath)

        # A portable.txt file stops each build from spamming AppData for config.
        for path in (emupath, canarypath):
            portable_file = path / 'portable.txt'
            if not portable_file.exists():
                portable_file.touch()

        wine_runner.install_wine_trick('vcrun2022')

        for arch, windows_dir in _DLL_ARCHES:
            for dll in _DLLS:
                src_path = WINE_BASE / 'dxvk' / arch / dll
                dest_path = wine_runner.bottle_dir / 'drive_c' / 'windows' / windows_dir / dll
                try:
                    if dest_path.exists() or dest_path.is_symlink():
                        dest_path.unlink()
                    dest_path.symlink_to(src_path)
                except OSError as e:
                    _logger.debug('Error linking %s (%s): %s', dll, arch, e)

        rom = self.rom
        if rom.suffix == '.xbox360':
            # A digital title: the file is a playlist naming the actual XBLA/disc
            # install to launch, relative to the playlist's own directory.
            _logger.debug('Found .xbox360 playlist: %s', rom)
            first_line = rom.read_text().splitlines()[0].strip().lstrip('/')
            xbla_full_path = rom.parent / first_line
            if xbla_full_path.exists():
                _logger.debug('Found! Switching active rom to: %s', first_line)
                rom = xbla_full_path
            else:
                _logger.error(
                    'Disc installation/XBLA title %s from %s not found, check path or filename.', first_line, rom
                )

        toml_file = canarypath / 'xenia-canary.config.toml' if is_canary else emupath / 'xenia.config.toml'
        config: dict[str, dict[str, Any]] = toml.load(toml_file) if toml_file.is_file() else {}

        config['CPU'] = {'break_on_unimplemented_instructions': False}  # hack, needed for certain games
        # default 1 = the full-version license, generally XBLA's first slot
        config['Content'] = {'license_mask': self.config.get_int('xenia_license', 1)}
        config['D3D12'] = {'d3d12_readback_resolve': self.config.get_bool('xenia_readback_resolve')}
        config['Display'] = {
            'fullscreen': True,
            'internal_display_resolution': self.config.get_int('xenia_resolution', 8),
            'postprocess_scaling_and_sharpening': self.config.get_str(
                'xenia_postprocess_scaling_and_sharpening', 'bilinear'
            ),
            'postprocess_antialiasing': self.config.get_str('xenia_postprocess_antialiasing', 'none'),
            'postprocess_ffx_cas_additional_sharpness': self.config.get(
                'xenia_postprocess_ffx_cas_additional_sharpness', 0.0
            ),
            'postprocess_ffx_fsr_sharpness_reduction': self.config.get(
                'xenia_postprocess_ffx_fsr_sharpness_reduction', 0.2
            ),
        }
        config['GPU'] = {
            # may bypass fetch-constant-type errors in certain games
            'gpu': self.config.get_str('xenia_api', 'D3D12').lower(),
            'vsync': self.config.get_bool('xenia_vsync', True),
            'framerate_limit': self.config.get_int('xenia_vsync_fps', 0),
            'clear_memory_page_state': self.config.get_bool('xenia_page_state'),
            'render_target_path_d3d12': self.config.get_str('xenia_target_path', 'rtv'),
            'query_occlusion_fake_sample_count': self.config.get_int('xenia_query_occlusion', 1000),
            'texture_cache_memory_limit_hard': self.config.get_int('xenia_limit_hard', 768),
            'texture_cache_memory_limit_render_to_texture': self.config.get_int('xenia_limit_render_to_texture', 24),
            'texture_cache_memory_limit_soft': self.config.get_int('xenia_limit_soft', 384),
            'texture_cache_memory_limit_soft_lifetime': self.config.get_int('xenia_limit_soft_lifetime', 30),
        }
        config['General'] = {
            'discord': False,
            'apply_patches': self.config.get_bool('xenia_patches'),
        }
        config['HID'] = {'hid': 'sdl'}
        config['Logging'] = {'log_level': 1}  # reduce log spam
        # certain games require protect_zero=False / mount_scratch=True to avoid crashes
        config['Memory'] = {'protect_zero': False}
        config['Storage'] = {
            'cache_root': str(xenia_cache),
            'content_root': str(_XBOX360_SAVES),
            'mount_scratch': True,
            'storage_root': str(self.config_dir),
            'mount_cache': self.config.get_bool('xenia_cache', True),
        }
        config['UI'] = {
            'headless': self.config.get_bool('xenia_headless'),
            'show_achievement_notification': self.config.get_bool('xenia_achievement'),
        }
        config['Vulkan'] = {'vulkan_sparse_shared_memory': False}
        config['XConfig'] = {
            'user_country': self.config.get_int('xenia_country', 103),  # 103 = US
            'user_language': self.config.get_int('xenia_language', 1),
        }

        with toml_file.open('w') as f:
            toml.dump(config, f)

        if self.config.get_bool('xenia_patches'):
            # Simplify the rom name to match a patch file's own naming (which
            # drops region/revision tags in brackets/parens).
            rom_name = re.sub(r'\[.*?\]|\(.*?\)', '', rom.stem)
            matching_files = [
                file_path
                for file_path in (canarypath / 'patches').glob(f'*{rom_name}*.patch.toml')
                if re.search(rom_name, file_path.name, re.IGNORECASE)
            ]
            if matching_files:
                for file_path in matching_files:
                    _logger.debug('Enabling patches for: %s', file_path)
                    patch_toml = toml.load(file_path)
                    for patch in patch_toml.get('patch', []):
                        if 'is_enabled' in patch:
                            patch['is_enabled'] = True
                    with file_path.open('w') as f:
                        toml.dump(patch_toml, f)
            else:
                _logger.debug('No patch file found for %s', rom_name)

        exe = canarypath / 'xenia_canary.exe' if is_canary else emupath / 'xenia.exe'
        args: list[str | Path] = [wine_runner.wine, exe]
        if not configure_emulator(rom):
            args.append(f'z:{rom}')

        environment = wine_runner.get_environment()
        environment.update(
            WINEARCH='win64',
            LD_LIBRARY_PATH=f'/usr/lib:{environment["LD_LIBRARY_PATH"]}',
            LIBGL_DRIVERS_PATH='/usr/lib/dri',
            SDL_JOYSTICK_HIDAPI='0',
            VKD3D_SHADER_CACHE_PATH=xenia_cache,
            WINEDLLOVERRIDES='winemenubuilder.exe=;dxgi,d3d8,d3d9,d3d10core,d3d11,d3d12,d3d12core=n',
        )

        # ensure the nvidia driver gets used for vulkan
        if Path('/var/tmp/nvidia.prime').exists():
            for variable_name in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
                os.environ.pop(variable_name, None)

            environment.update(
                VK_ICD_FILENAMES='/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                VK_LAYER_PATH='/usr/share/vulkan/explicit_layer.d',
            )

        return Command(args, env=environment)
