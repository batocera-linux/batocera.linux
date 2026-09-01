from __future__ import annotations

import filecmp
import logging
import os
import shutil
import subprocess
from pathlib import Path, PureWindowsPath

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import BIOS, SAVES
from batocera_common.vulkan import is_available as vulkan_is_available
from batocera_common.wine import WINE_BASE, Runner
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

_logger = logging.getLogger(__name__)


def _sync_directories(source_dir: Path, dest_dir: Path, /) -> None:
    dcmp = filecmp.dircmp(source_dir, dest_dir)
    # Files that are only in the source directory or are different
    for name in [*dcmp.diff_files, *dcmp.left_only]:
        shutil.copy2(source_dir / name, dest_dir / name)


@cached_dataclass
class Demul(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'demul',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.config.get_int('demulRatio', 1) in (0, 2) else 4 / 3

    async def configure(self) -> Command:
        if not vulkan_is_available():
            raise BatoceraException('Vulkan driver required is not available on the system')

        wine_runner = Runner.default('demul')
        emupath = wine_runner.bottle_dir / 'demul'

        wine_runner.bottle_dir.mkdir(parents=True, exist_ok=True)
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        # Create dir & copy demul binary to wine bottle as necessary
        source_emu = Path('/usr/demul')

        if not emupath.exists():
            shutil.copytree(source_emu, emupath)

        # Check binary then copy updated files as necessary
        if not filecmp.cmp(source_emu / 'demul.exe', emupath / 'demul.exe'):
            _sync_directories(source_emu, emupath)

        wine_runner.install_wine_trick('d3dcompiler_47')

        # Handle DLLs (DXVK). Since we use WINEARCH=win32, 32-bit DLLs go into system32.
        for dll in ('d3d11.dll', 'dxgi.dll', 'd3dcompiler_43.dll', 'd3dcompiler_47.dll'):
            try:
                src_path = WINE_BASE / 'dxvk' / 'x32' / dll
                dest_path = wine_runner.bottle_dir / 'drive_c' / 'windows' / 'system32' / dll

                if src_path.exists():
                    if dest_path.exists() or dest_path.is_symlink():
                        dest_path.unlink()
                    dest_path.symlink_to(src_path)
            except OSError as e:
                _logger.debug('Error creating 32-bit link for %s: %s', dll, e)

        # Prepare Demul.ini
        config_file = emupath / 'Demul.ini'
        config = CaseSensitiveRawConfigParser()
        if config_file.exists():
            with config_file.open(encoding='utf_8_sig') as fp:
                config.read_file(fp)

        plugins = SAVES / 'demul' / 'demul' / 'plugins'
        if not plugins.exists():
            plugins = emupath / 'plugins'

        if not config.has_section('files'):
            config.add_section('files')
        config.set('files', 'nvram', f'Z:{PureWindowsPath(self.saves_dir)}')
        config.set('files', 'roms0', f'Z:{PureWindowsPath(BIOS)}')
        config.set('files', 'romsPathsCount', '8')
        config.set('files', 'roms1', f'Z:{PureWindowsPath("/userdata/roms/hikaru")}')
        config.set('files', 'roms2', f'Z:{PureWindowsPath("/userdata/roms/gaelco")}')
        config.set('files', 'roms3', f'Z:{PureWindowsPath("/userdata/roms/cave3rd")}')

        if not config.has_section('plugins'):
            config.add_section('plugins')
        config.set('plugins', 'directory', f'Z:{PureWindowsPath(plugins)}')
        config.set('plugins', 'spu', 'spuDemul.dll')
        config.set('plugins', 'pad', 'padDemul.dll')
        config.set('plugins', 'net', 'netDemul.dll')
        # Gaelco won't work with the new DX11 plugin
        config.set('plugins', 'gpu', 'gpuDX11old.dll' if self.system == 'gaelco' else 'gpuDX11.dll')
        if self.rom.suffix.lower() in ('.zip', '.7z'):
            config.set('plugins', 'gdr', 'gdrImage.dll')

        with config_file.open('w', encoding='utf_8_sig') as fp:
            config.write(fp)

        # Adjust fullscreen & resolution in gpuDX11.ini (or old)
        gpu_config_file = emupath / ('gpuDX11old.ini' if self.system == 'gaelco' else 'gpuDX11.ini')
        gpu_config = CaseSensitiveRawConfigParser()
        if gpu_config_file.exists():
            with gpu_config_file.open(encoding='utf_8_sig') as fp:
                gpu_config.read_file(fp)

        if not gpu_config.has_section('main'):
            gpu_config.add_section('main')
        gpu_config.set('main', 'UseFullscreen', '1')
        gpu_config.set('main', 'aspect', str(self.config.get_int('demulRatio', 1)))
        gpu_config.set('main', 'Vsync', str(self.config.get_int('demulVSync', 0)))
        gpu_config.set('main', 'scaling', str(self.config.get_int('demulScaling', 1)))

        if not gpu_config.has_section('resolution'):
            gpu_config.add_section('resolution')
        gpu_config.set('resolution', 'Width', str(self.resolution.width))
        gpu_config.set('resolution', 'Height', str(self.resolution.height))

        with gpu_config_file.open('w', encoding='utf_8_sig') as fp:
            gpu_config.write(fp)

        args: list[str | Path] = [
            wine_runner.wine,
            emupath / 'demul.exe',
            f'-run={self.system}',
            f'-rom={self.rom.stem}',
        ]

        environment: dict[str, str | Path] = wine_runner.get_environment()
        environment.update(
            WINEARCH='win32',
            LD_LIBRARY_PATH=f'/lib32:/usr/lib32:{environment["LD_LIBRARY_PATH"]}',
            WINEDLLOVERRIDES='d3d11,dxgi,d3dcompiler_47=n,b',
            SPA_PLUGIN_DIR='/usr/lib/spa-0.2:/lib32/spa-0.2',
            PIPEWIRE_MODULE_DIR='/usr/lib/pipewire-0.3:/lib32/pipewire-0.3',
        )

        # Handle window quirks with Demul systems: some systems start non-fullscreen
        # and need a synthetic F3 (+ Alt+Enter under X11) to force fullscreen.
        if self.system in ('cave3rd', 'gaelco'):
            trigger_cmd = 'sleep 5 && export DISPLAY=:0 && xdotool getactivewindow key F3'
            if 'WAYLAND_DISPLAY' not in os.environ:
                trigger_cmd += ' && xdotool getactivewindow key alt+Return'

            try:
                subprocess.Popen(
                    ['sh', '-c', trigger_cmd],
                    env=os.environ,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except OSError as e:
                _logger.error('Failed to schedule fullscreen trigger: %s', e)

        return Command(args, env=environment)
