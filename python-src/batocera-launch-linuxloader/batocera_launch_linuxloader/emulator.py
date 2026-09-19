#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
from __future__ import annotations

import filecmp
import logging
import os
import re
import shutil
import socket
import stat
import tarfile
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SAVES
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
    ParallelStartupTaskMixin,
)
from batocera_launch.asyncio import download

from .config import Configuration
from .controllers import ControllersMixin

_logger = logging.getLogger(__name__)

_SOURCE_DIR: Final = Path('/usr/bin/linuxloader')
_EEPROM_URL: Final = 'https://raw.githubusercontent.com/batocera-linux/lindbergh-eeprom/main/lindbergh-eeprom.tar.xz'
_EXECUTABLE_FILES: Final = [
    'a.elf',
    'abc',
    'apacheM.elf',
    'chopperM.elf',
    'drive.elf',
    'dsr',
    'gsevo',
    'hod4M.elf',
    'hodexRI.elf',
    'hummer_Master.elf',
    'id4.elf',
    'id5.elf',
    'Jennifer',
    'lgj_final',
    'lgjsp_app',
    'main.exe',
    'mj4',
    'q2satl_lind',
    'ramboM.elf',
    'vf5',
    'vsg',
    'vt3',
    'vt3_Lindbergh',
]


def _get_ip_address(destination: str = '1.1.1.1', port: int = 80) -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((destination, port))
            return s.getsockname()[0]
    except Exception as e:
        _logger.debug('Error retrieving IP address: %s', e)
        return None


def _resolve_real_rom_path(rom_dir: Path, /) -> Path:
    try:
        rom_dir_str = str(rom_dir)
        with Path('/proc/mounts').open() as f:
            for line in f:
                parts = line.split()
                if len(parts) < 3 or parts[2] != 'fuse.mergerfs':
                    continue
                mount_point = parts[1]
                if not rom_dir_str.startswith(mount_point + '/') and rom_dir_str != mount_point:
                    continue
                branches_raw = parts[0]
                relative = rom_dir_str[len(mount_point) :]
                _logger.debug(
                    'mergerfs mount=%s source=%s relative=%s',
                    mount_point,
                    branches_raw,
                    relative,
                )
                for branch in branches_raw.split(':'):
                    branch = branch.strip()
                    if not branch:
                        continue
                    # Ensure absolute path
                    if not branch.startswith('/'):
                        branch = '/' + branch
                    candidate = Path(branch.rstrip('/') + relative)
                    _logger.debug('trying candidate: %s', candidate)
                    if candidate.is_dir():
                        _logger.debug('resolved %s -> %s', rom_dir, candidate)
                        return candidate
    except Exception as e:
        _logger.debug('failed, using original path: %s', e)
    return rom_dir


@cached_dataclass
class LinuxLoader(ControllersMixin, ParallelStartupTaskMixin, Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'linuxloader',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'coin': 'KEY_5',
            },
        }

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'lindbergh'

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @property
    def execution_path(self) -> Path | None:
        return _SOURCE_DIR

    async def configure(self) -> Command:
        rom_dir = self.rom.parent
        rom_name = self.rom.name
        short_rom_name = Path(rom_name.lower()).stem
        _logger.debug('ROM path: %s', rom_dir)

        # check for mergerfs path
        rom_dir = _resolve_real_rom_path(rom_dir)
        _logger.debug('Effective ROM path is: %s', rom_dir)

        ### conf file
        self._setup_config(rom_dir, rom_name)

        ### libraries
        self._setup_libraries(rom_dir, rom_name)

        # Check for known executable files and make them executable if needed
        # Details in the mainShared.c file
        for exe_file in _EXECUTABLE_FILES:
            file_path = rom_dir / exe_file
            # Check if file is executable
            if file_path.exists() and not os.access(file_path, os.X_OK):
                # Add executable permission (equivalent to chmod +x)
                current_permissions = file_path.stat().st_mode
                executable_permissions = current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                file_path.chmod(executable_permissions)
                _logger.debug('Made %s executable', exe_file)

        environment: dict[str, str | Path] = {
            # Libraries
            'LD_LIBRARY_PATH': f'/lib32:/lib32/extralibs:/lib:/usr/lib:{_SOURCE_DIR}:{rom_dir}',
            'LD_PRELOAD': _SOURCE_DIR / 'linuxloader.so',
            # Graphics
            'GST_PLUGIN_SYSTEM_PATH_1_0': '/lib32/gstreamer-1.0:/usr/lib/gstreamer-1.0',
            'GST_REGISTRY_1_0': '/userdata/system/.cache/gstreamer-1.0/registry..bin:/userdata/system/.cache/gstreamer-1.0/registry.x86_64.bin',
            'LIBGL_DRIVERS_PATH': '/lib32/dri:/usr/lib/dri',
            # Audio
            'SPA_PLUGIN_DIR': '/lib32/spa-0.2:/usr/lib/spa-0.2',
            'PIPEWIRE_MODULE_DIR': '/lib32/pipewire-0.3:/usr/lib/pipewire-0.3',
            # Controller(s)
            'SDL_JOYSTICK_HIDAPI': '0',
        }

        # ALSA SDL driver causes hangs during race start in OutRun but it's needed for other roms.
        if not short_rom_name.startswith('outr'):
            environment['SDL_AUDIODRIVER'] = 'alsa'

        # Run command - Use -c * -o for ini files and -g for the game folder
        config_file = self.config_dir / 'linuxloader.ini'
        controller_file = self.config_dir / 'controls.ini'
        command_array: list[str | Path] = [
            _SOURCE_DIR / 'linuxloader',
            '-c',
            config_file,
            '-o',
            controller_file,
            '-g',
            rom_dir,
        ]

        if self.config.get_bool('linuxloader_zink'):
            command_array.append('--zink')
            environment.update({'MESA_LOADER_DRIVER_OVERRIDE': 'zink', 'VK_LOADER_LAYERS_DISABLE': '~all~'})

        if self.config.get_bool('linuxloader_test'):
            command_array.append('-t')

        return Command(command_array, env=environment)

    async def parallel_startup_task(self) -> None:
        # Set up eeprom files as necessary
        self.saves_dir.mkdir(parents=True, exist_ok=True)

        last_extracted = self.saves_dir / '.eeprom.extracted'
        etag_file = self.saves_dir / '.eeprom.etag'

        try:
            last_extracted_files = last_extracted.read_text().strip().splitlines() if last_extracted.exists() else []
            has_missing_files = not last_extracted_files or any(
                not Path(path).exists() for path in last_extracted_files
            )
            etag = etag_file.read_text().strip() if etag_file.exists() and not has_missing_files else None

            # Download the file
            async with download(
                self.client_session,
                _EEPROM_URL,
                self.saves_dir,
                etag=etag,
            ) as (fetched, etag_received):
                if fetched is None:
                    return

                _logger.debug('Extracting the file...')

                extracted_files: list[str] = []

                with tarfile.open(fetched, mode='r:xz') as tar:
                    for member in tar.getmembers():
                        extracted_files.append(f'{self.saves_dir / member.name}')
                        tar.extract(member, path=self.saves_dir)

                last_extracted.write_text('\n'.join(extracted_files))

                if etag_received is not None:
                    etag_file.write_text(etag_received)

                _logger.debug('Files extracted to %s', self.saves_dir)
        except Exception:
            _logger.exception('An error occurred')

    def _build_conf_file(self, conf: Configuration, rom_dir: Path, rom_name: str) -> None:
        conf.set('WIDTH', self.resolution.width)
        conf.set('HEIGHT', self.resolution.height)
        conf.set(
            'FULLSCREEN',
            'true' if self.config.get_bool('linuxloader_fullscreen', True) else 'false',
        )
        conf.set('REGION', self.config.get_str('linuxloader_region', 'EX'))
        conf.set('FPS_TARGET', self.config.get_str('linuxloader_fps', '60.0'))
        conf.set(
            'FPS_LIMITER_ENABLED',
            'true' if self.config.get_bool('linuxloader_limit', True) else 'false',
        )
        conf.set('FREEPLAY', 'true' if self.config.get_bool('linuxloader_freeplay') else 'false')
        conf.set(
            'KEEP_ASPECT_RATIO',
            'true' if self.config.get_bool('linuxloader_aspect', True) else 'false',
        )
        conf.set('DEBUG_MSGS', 'true' if self.config.get_bool('linuxloader_debug') else 'false')
        conf.set('HUMMER_FLICKER_FIX', 'true' if self.config.get_bool('linuxloader_hummer') else 'false')
        conf.set(
            'OUTRUN_LENS_GLARE_ENABLED',
            'true' if self.config.get_bool('linuxloader_lens', True) else 'false',
        )
        conf.set('BOOST_RENDER_RES', 'true' if self.config.get_bool('linuxloader_boost') else 'false')
        # disable by default, otherwise no FFB
        conf.set(
            'SKIP_OUTRUN_CABINET_CHECK',
            'false' if 'outrun' in rom_name.lower() or 'outr2sdx' in rom_name.lower() else 'true',
        )
        conf.set('SRAM_PATH', f'"{self.saves_dir}/sram.bin.{Path(rom_name).stem.lower()}"')
        conf.set('EEPROM_PATH', f'"{self.saves_dir}/eeprom.bin.{Path(rom_name).stem.lower()}"')
        conf.set(
            'HIDE_CURSOR',
            'true' if self.config.get_bool('linuxloader_hide_cursor', True) else 'false',
        )
        conf.set(
            'DISABLE_BUILTIN_FONT',
            'true' if self.config.get_bool('linuxloader_disable_font') else 'false',
        )
        conf.set(
            'DISABLE_BUILTIN_LOGOS',
            'true' if self.config.get_bool('linuxloader_disable_logos') else 'false',
        )
        conf.set(
            'ENABLE_NETWORK_PATCHES',
            'true' if self.config.get_bool('linuxloader_network_patches', True) else 'false',
        )
        conf.set('ENABLE_CROSSHAIRS', 'true' if self.config.get_bool('linuxloader_crosshairs') else 'false')

        # Cg Shader Compiler Library Path
        if any(
            keyword in rom_name.lower()
            for keyword in ('harley', 'hdkotr', 'spicy', 'rambo', 'hotdex', 'dead ex', 'initiad', 'letsgoju', 'tennis')
        ):
            conf.set('LIBCG_PATH', f'"{rom_dir}/libCg.so"')

        ## -= Additional game specific options =-

        # Driveboard emulation for FFB on gamepad
        has_ffb = (
            'outr' in rom_name.lower()
            or 'hummer' in rom_name.lower()
            or 'rtuned' in rom_name.lower()
            or 'segartv' in rom_name.lower()
        )
        conf.set(
            'EMULATE_DRIVEBOARD',
            'true' if has_ffb and self.config.get_bool('linuxloader_ffb', True) else 'auto',
        )

        # enabling network patches blocks hdkotr from booting, checking network with a timeout error
        if 'harley' in rom_name.lower() or 'hdkotr' in rom_name.lower():
            conf.set('ENABLE_NETWORK_PATCHES', 'false')

        # Virtua Tennis / R-Tuned / Initial D - Card Reader
        if ('tennis' in rom_name.lower() or 'rtuned' in rom_name.lower()) and self.config.get_bool(
            'linuxloader_card', True
        ):
            conf.set('EMULATE_HW210_CARDREADER', 'true')
            conf.set('CARDFILE_01', 'Card_01.crd')
            conf.set('CARDFILE_02', 'Card_02.crd')
            conf.set('ID_CARDFOLDER', f'"{self.saves_dir}"')
        else:
            conf.set('EMULATE_HW210_CARDREADER', 'false')

        if 'initiad' in rom_name.lower() and self.config.get_bool('linuxloader_card', True):
            conf.set('EMULATE_ID_CARD_READER', 'true')
            conf.set('ID_CARDFILE_AUTOLOAD', 'true')
            conf.set('ID_CARDFOLDER', f'"{self.saves_dir}"')
        else:
            conf.set('EMULATE_ID_CARD_READER', 'false')

        # Rambo switch
        if 'rambo' in rom_name.lower():
            conf.set(
                'RAMBO_GUNS_SWITCH',
                'true' if self.config.get_bool('linuxloader_rambo_switch') else 'false',
            )

        # House of the Dead 4 - CPU speed
        cpu_speed = self.config.get_str('linuxloader_speed')
        if 'hotd4' in rom_name.lower() and cpu_speed:
            cpu_speed_f = float(cpu_speed)
            _logger.debug('Current CPU Speed : %.2f GHz', cpu_speed_f)
            conf.set('CPU_FREQ_GHZ', f'{cpu_speed_f:.1f}')
        else:
            conf.comment('CPU_FREQ_GHZ')

        # OutRun 2 - Network
        if 'outr2sdx' in rom_name.lower() and self.config.get_bool('linuxloader_ip'):
            ip = _get_ip_address()
            if not ip:
                _logger.debug('Primary destination unreachable. Trying fallback...')
                ip = _get_ip_address(destination='8.8.8.8')

            if ip:
                _logger.debug('Current IP Address: %s', ip)
                conf.set('OR2_IPADDRESS', f'"{ip}"')
                conf.set('OR2_NETMASK', '255.255.255.0')
            else:
                _logger.debug('Unable to retrieve IP address.')

        # Primeval Hunt mode (touch screen)
        if 'primevah' in rom_name.lower() or 'primehunt' in rom_name.lower():
            conf.set('PRIMEVAL_HUNT_SCREEN_MODE', self.config.get_str('linuxloader_hunt', '1'))
            conf.set('EMULATE_TOUCHSCREEN', 'true')

        ## Guns
        if self.config.use_guns and self.guns:
            if (border_dimensions := self.gun_border_dimensions) is not None:
                borders_inner_size, borders_outer_size = border_dimensions
                conf.set('WHITE_BORDER_PERCENTAGE', borders_inner_size)
                conf.set('BLACK_BORDER_PERCENTAGE', borders_outer_size)

            conf.set('BORDER_ENABLED', 'true' if border_dimensions is not None else 'false')

            if 'letsgojusp' in rom_name.lower():
                conf.set('BORDER_ENABLED', 'false')
        else:
            conf.set('BORDER_ENABLED', 'false')

        # Crosshairs (ghostsev; hotd4; hotd4sp; primevil, rambo)
        crosshairs = self.config.get_str('linuxloader_crosshairs') == '1'
        conf.set(
            'P1_CROSSHAIR_PATH',
            '/usr/bin/linuxloader/crosshairs/p1_crosshair.png' if crosshairs else '',
        )
        conf.set(
            'P2_CROSSHAIR_PATH',
            '/usr/bin/linuxloader/crosshairs/p2_crosshair.png' if crosshairs else '',
        )
        if 'ghostsev' in rom_name.lower():
            conf.set('CUSTOM_CROSSHAIRS_WIDTH', '28')
            conf.set('CUSTOM_CROSSHAIRS_HEIGHT', '28')
        else:
            conf.set('CUSTOM_CROSSHAIRS_WIDTH', '64')
            conf.set('CUSTOM_CROSSHAIRS_HEIGHT', '64')

        self._setup_controllers(conf, rom_name)

    def _setup_libraries(self, rom_dir: Path, rom_name: str) -> None:
        # Setup some library quirks for GPU support (NVIDIA?)
        source = Path('/lib32/libkswapapi.so')
        if source.exists():
            destination = Path(rom_dir) / 'libGLcore.so.1'
            if not destination.exists():
                shutil.copy2(source, destination)
                _logger.debug('Copied: %s from %s', destination, source)

        # -= Game specific library versions =-
        if any(keyword in rom_name.lower() for keyword in ('harley', 'hdkotr', 'spicy', 'rambo', 'hotdex', 'dead ex')):
            dest_cg = Path(rom_dir) / 'libCg.so'
            dest_cg_gl = Path(rom_dir) / 'libCgGL.so'
            src_cg = Path('/lib32/extralibs/libCg.so.harley')
            src_cg_gl = Path('/lib32/extralibs/libCgGL.so.harley')
            if src_cg.exists() and (not dest_cg.exists() or not filecmp.cmp(src_cg, dest_cg, shallow=False)):
                shutil.copy2(src_cg, dest_cg)
                _logger.debug('Copied: %s', dest_cg)
            if src_cg_gl.exists() and (
                not dest_cg_gl.exists() or not filecmp.cmp(src_cg_gl, dest_cg_gl, shallow=False)
            ):
                shutil.copy2(src_cg_gl, dest_cg_gl)
                _logger.debug('Copied: %s', dest_cg_gl)

        # fixes shadows and textures, the bundled libs are known-bad.
        # Scan first; if diff, overwrite
        elif any(keyword in rom_name.lower() for keyword in ('initiad', 'letsgoju', 'tennis')):
            dest_cg = Path(rom_dir) / 'libCg.so'
            dest_cg_gl = Path(rom_dir) / 'libCgGL.so'
            src_cg = Path('/lib32/extralibs/libCg.so.other')
            src_cg_gl = Path('/lib32/extralibs/libCgGL.so.other')
            if src_cg.exists() and (not dest_cg.exists() or not filecmp.cmp(src_cg, dest_cg, shallow=False)):
                shutil.copy2(src_cg, dest_cg)
                _logger.debug('Overwriting bad lib: %s', dest_cg)
            if src_cg_gl.exists() and (
                not dest_cg_gl.exists() or not filecmp.cmp(src_cg_gl, dest_cg_gl, shallow=False)
            ):
                shutil.copy2(src_cg_gl, dest_cg_gl)
                _logger.debug('Overwriting bad lib: %s', dest_cg_gl)

        # Remove legacy/conflicting files from the ROM directory
        legacy_files = ['libsegaapi.so', 'lindbergh', 'lindbergh.conf', 'lindbergh.so', 'lindbergh.ini']
        for legacy_file in legacy_files:
            legacy_path = rom_dir / legacy_file
            if legacy_path.exists():
                try:
                    legacy_path.unlink()
                    _logger.debug('Removed legacy file: %s', legacy_path)
                except Exception as e:
                    _logger.debug('Could not remove legacy file %s: %s', legacy_path, e)

    def _setup_config(self, rom_dir: Path, rom_name: str) -> None:
        linuxloader_config_file = self.config_dir / 'linuxloader.ini'
        linuxloader_controls_file = self.config_dir / 'controls.ini'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # get an initial version if no version is here - Sync linuxloader.ini
        source_file = _SOURCE_DIR / 'linuxloader.ini'
        if (
            not linuxloader_config_file.exists()
            or source_file.stat().st_mtime > linuxloader_config_file.stat().st_mtime
        ):
            shutil.copy2(source_file, linuxloader_config_file)
            _logger.debug('Updated linuxloader.ini')

        # Sync controls.ini
        source_controls = _SOURCE_DIR / 'controls.ini'
        if (
            not linuxloader_controls_file.exists()
            or source_controls.stat().st_mtime > linuxloader_controls_file.stat().st_mtime
        ):
            shutil.copy2(source_controls, linuxloader_controls_file)
            _logger.debug('Updated controls.ini')

        ### Adjust controls.ini (SDL mode) ###
        content = linuxloader_controls_file.read_text()

        # Steering deadzone - lower for driving games, mandatory for ID4/5
        steer_deadzone = '800' if 'initiad' in rom_name.lower() else '1000'
        content = re.sub(r'Steer_DeadZone\s*=\s*\d+', f'Steer_DeadZone = {steer_deadzone}', content)

        # Test and Service buttons - same as evdev (dpad down / facebutton down)
        if self.config.get_bool('linuxloader_test'):
            content = re.sub(r'Test\s*=\s*.*', 'Test = KEY_T, GC0_BUTTON_A, JOY0_BUTTON_0', content)
            content = re.sub(
                r'P1_Service\s*=\s*.*',
                'P1_Service = KEY_S, GC0_BUTTON_DPDOWN, JOY0_HAT0_DOWN',
                content,
            )
        else:
            content = re.sub(r'Test\s*=\s*.*', 'Test = KEY_T', content)
            content = re.sub(
                r'P1_Service\s*=\s*.*',
                'P1_Service = KEY_S, JOY0_BUTTON_10, GC0_BUTTON_BACK',
                content,
            )

        linuxloader_controls_file.write_text(content)

        # load and modify it if needed and save it
        conf = Configuration(linuxloader_config_file)
        self._build_conf_file(conf, rom_dir, rom_name)
        conf.save()
