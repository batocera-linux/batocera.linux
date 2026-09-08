from __future__ import annotations

import logging
import os
import shlex
import subprocess
import tarfile
from contextlib import ExitStack
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BATOCERA_CONF, CACHE, ROMS
from batocera_launch import BatoceraException, Command, Emulator

from . import wine

if TYPE_CHECKING:
    from batocera_launch import Config, HotkeysContext

_logger = logging.getLogger(__name__)

# what windows_installers installs is a windows game, and shares its prefixes
_WINDOWS_SYSTEM: Final = 'windows'
_WINDOWS_INSTALLERS_SYSTEM: Final = 'windows_installers'

_NVIDIA_CACHE_DIR: Final = CACHE / 'nvidia'


@cached_dataclass
class Wine(Emulator):
    """
    Runs a game through wine

    - a .wine rom is a complete wine prefix and runs in itself
    - a .wsquashfs is that prefix squashed, mounted with a writable overlay kept in
      /userdata/system/wine-bottles, so what reaches configure() is a prefix like any
      other
    - a .wtgz is that prefix as a tarball, unpacked once into a prefix of its own
    - a .pc rom is a directory of game files, and a bare .exe a single one, both run in
      a prefix of their own under /userdata/system/wine-bottles
    - a windows_installers rom is an installer, run in a new prefix in
      /userdata/roms/windows that becomes the installed game

    """

    # what has to stay mounted while the game runs, released by run()
    _resources: ExitStack = field(init=False, default_factory=ExitStack)
    _runner: wine.Runner | None = field(init=False, default=None)

    @cached_property
    def _wanted_runner(self) -> str:
        # the runner chosen for the game, or the core, as it was named before
        return self.config.get_str('wine-runner', '') or self.core

    @property
    def _is_installer(self) -> bool:
        return self.system == _WINDOWS_INSTALLERS_SYSTEM

    @property
    def needs_overlayfs(self) -> bool:
        return True

    @cached_property
    def writable_overlayfs_dir(self) -> Path:
        return wine.get_prefix_path(self.system, wine.get_runner_name(self._wanted_runner), self.config.rom)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        runner = self._prepare()

        return {
            'name': 'wine',
            'keys': {
                'exit': f'WINEPREFIX={shlex.quote(str(runner.prefix_dir))} {shlex.quote(str(runner.wineserver))} -k'
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return self.config.get_bool('force_mouse')

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @property
    def execution_path(self) -> Path | None:
        if self.rom.suffix.lower() in ('.exe', '.iso', '.msi'):
            return self.rom.parent

        return wine.get_game_dir(self._rom_dir)

    async def configure(self) -> Command:
        if self._is_installer:
            return self._configure_install()

        return self._configure_play()

    async def run(self) -> int:
        with self._resources:
            try:
                exit_code = await super().run()
            finally:
                # nothing may hold the rom when run() returns, wine exits before the game
                if self._runner is not None:
                    self._runner.stop()

            if self._is_installer and self._runner is not None:
                self._generate_autorun_in_installed_prefix(self._runner)

            return exit_code

    def _prepare(self) -> wine.Runner:
        """
        Create or update the wine prefix with the correct arch
        """
        if self._runner is not None:
            return self._runner

        wanted_runner = self._wanted_runner
        runner_name = wine.get_runner_name(wanted_runner)

        if self._is_installer:
            # the installer builds the game as a prefix in the windows roms, timed so two don't collide
            prefix = ROMS / _WINDOWS_SYSTEM / f'{datetime.now():%y%m%d-%H%M%S}_{self.rom.stem}.wine'
        else:
            prefix = wine.get_prefix_path(self.system, runner_name, self.rom)

        runner = wine.Runner.from_prefix(
            wanted_runner,
            prefix,
            arch=wine.wanted_prefix_arch(runner_name, enable_win32=self.config.get_bool('enable_win32')),
        )
        self._runner = runner

        _logger.debug('running %s in %s with %s', self.rom.name, prefix, runner.runner_name)

        wine.log_filesystems(Path(self.rom), prefix)

        built = (prefix / 'system.reg').exists()
        runner.create_or_update_prefix()

        # a .wtgz is a prefix in a tarball, unpacked into the prefix built for it
        if not built and self.rom.suffix.lower() == '.wtgz':
            _logger.info('unpacking %s into %s', self.rom, prefix)
            with tarfile.open(self.rom) as tar:
                tar.extractall(prefix, filter='tar')

        return runner

    @property
    def _rom_dir(self) -> Path:
        if self.rom.is_dir():
            return Path(self.rom)

        return self._prepare().prefix_dir

    def _configure_play(self) -> Command:
        runner = self._prepare()

        self._setup_prefix(runner)

        environment = self._environment(runner)

        args: list[str | Path] = [runner.wine]

        # a virtual desktop gives the game a window of its own, on black rather than blue
        if self.config.get_bool('virtual_desktop'):
            runner.set_registry_value(r'HKEY_CURRENT_USER\Control Panel\Colors', 'Background', 'REG_SZ', '0 0 0')
            args += ['explorer', f'/desktop=Wine,{self.resolution.width}x{self.resolution.height}']

        if self.rom.is_file() and self.rom.suffix.lower() == '.exe':
            # a bare .exe is the game, and runs from the directory it sits in
            args.append(self.rom.name)
            return Command(args, environment)

        rom_dir = self._rom_dir

        # link saves dirs to /userdata/saves
        wine.link_saves(rom_dir, runner.prefix_dir, self.saves_dir / self.rom.id)

        try:
            exe, arguments = wine.get_game_command(rom_dir)
        except BatoceraException as e:
            # what batocera-wine did without an autorun.cmd, let the user start it
            _logger.warning('%s, starting the file manager instead', e)
            args.append('explorer')
        else:
            args.append(exe)
            args += arguments

        environment.update(wine.get_autorun_environment(rom_dir))

        return Command(args, environment)

    def _configure_install(self) -> Command:
        runner = self._prepare()

        # the game keeps the options that were chosen for its installer
        _copy_installer_settings(self.rom.name, runner.prefix_dir.name)

        self._setup_prefix(runner)

        environment = self._environment(runner)

        args: list[str | Path]

        match self.rom.suffix.lower():
            case '.exe':
                args = [runner.wine, self.rom]
            case '.msi':
                args = [runner.msiexec, '-i', self.rom]
            case '.iso':
                # the image is the installation media, mounted as the d: drive
                mount_point = self._resources.enter_context(wine.mount_iso(Path(self.rom)))

                drive = runner.prefix_dir / 'dosdevices' / 'd:'
                drive.parent.mkdir(parents=True, exist_ok=True)

                if drive.is_symlink() or drive.exists():
                    drive.unlink()
                drive.symlink_to(mount_point)

                if (installer := wine.autorun_inf_command(mount_point)) is not None:
                    _logger.info('the autorun.inf of %s runs %s', self.rom.name, ' '.join(installer))
                    args = [runner.wine, *installer]
                else:
                    _logger.info('%s names no installer to run, opening its drive instead', self.rom.name)
                    args = [runner.wine, 'explorer', 'd:']
            case suffix:
                raise BatoceraException(f'Unknown installer type: {suffix}')

        return Command(args, environment)

    def _generate_autorun_in_installed_prefix(self, runner: wine.Runner, /) -> None:
        prefix = runner.prefix_dir

        # the image is unmounted, and a link to it would only confuse the next start
        drive = prefix / 'dosdevices' / 'd:'
        if drive.is_symlink():
            drive.unlink()

        if not (prefix / 'system.reg').exists():
            _logger.warning('%s was not created, nothing was installed', prefix)
            return

        executables = wine.find_game_executables(prefix)

        if len(executables) != 1:
            _logger.info(
                '%s executables found in %s, leaving its autorun.cmd to be filled in',
                len(executables),
                prefix,
            )

        wine.write_autorun_cmd(prefix, executables[0] if len(executables) == 1 else None)

    def _setup_prefix(self, runner: wine.Runner, /) -> None:
        runner.install_redists()
        runner.install_msis()
        runner.install_rawinput()
        runner.install_regs()
        runner.install_fonts()
        runner.sandbox_prefix()
        runner.set_hidraw(_get_hidraw(self.config, runner))

    def _environment(self, runner: wine.Runner, /) -> dict[str, str | Path]:
        config = self.config

        environment = runner.get_environment()
        environment.update(_wine_options(config, runner))
        environment.update(wine.display_environment(wayland_driver=config.get_str('wayland_driver', 'xwayland')))
        environment.update(_dxvk_environment(config, runner))
        environment.update(wine.nvidia_prime_environment())

        if language := config.get_str('system.language', ''):
            environment.update(
                {
                    'LANG': f'{language}.UTF-8',
                    'LC_ALL': f'{language}.UTF-8',
                }
            )

        # sdl controller option - default is on
        if config.get_bool('sdl_config', True):
            environment.update(
                {
                    'SDL_GAMECONTROLLERCONFIG': self.get_sdl_game_controller_config(),
                    'SDL_JOYSTICK_HIDAPI': '0',
                }
            )

        return environment


def _get_hidraw(config: Config, runner: wine.Runner, /) -> bool:
    # ge-proton11 force hidraw by default and don't report any gamepad through sdl
    return config.get_bool('enable_hidraw', runner.forces_hidraw)


def _wine_options(config: Config, runner: wine.Runner, /) -> dict[str, str | Path]:

    debug = config.get_bool('wine_debug')
    hidraw = _get_hidraw(config, runner)

    _NVIDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    environment: dict[str, str | Path] = {
        'WINEDEBUG': 'err+all,fixme+all' if debug else '-all',
        'PBA_ENABLE': config.get_bool('pba', return_values=('1', '0')),
        'DXVK_FRAME_RATE': config.get_bool('fps_limit', return_values=('60', '0')),
        'WINE_ENABLE_HIDRAW': '1' if hidraw else '0',
        # Wine-mono override for FNA games
        'WINE_MONO_OVERRIDES': 'Microsoft.Xna.Framework.*,Gac=n',
        # Disable XIM support until libx11 >= 1.7 is widespread
        'WINE_ALLOW_XIM': config.get_bool('allow_xim', return_values=('1', '0')),
        # Advanced options from proton
        'WINE_DISABLE_WRITE_WATCH': config.get_bool('no_write_watch', return_values=('1', '0')),
        'WINE_LARGE_ADDRESS_AWARE': config.get_bool('force_large_adress', return_values=('1', '0')),
        'WINE_HEAP_DELAY_FREE': config.get_bool('heap_delay_free', return_values=('1', '0')),
        'WINE_HIDE_NVIDIA_GPU': config.get_bool('hide_nvidia_gpu', return_values=('1', '0')),
        'NTFS_MODE': config.get_bool('wine_ntfs', return_values=('1', '0')),
        'STAGING_SHARED_MEMORY': '1',
        'USE_BUILTIN_VKD3D': '0',
        # the shader caches of wine and of the drivers, all under /userdata/system/cache
        'XDG_CACHE_HOME': CACHE,
        'VKD3D_SHADER_CACHE_PATH': CACHE,
        # Nvidia variables
        '__GL_SHADER_DISK_CACHE_SIZE': '2147483648',
        '__GL_SHADER_DISK_CACHE_SKIP_CLEANUP': '1',
        '__GL_SHADER_DISK_CACHE_PATH': _NVIDIA_CACHE_DIR,
    }

    # for geproton11, a sony pad still has to be told to look like an xinput one
    if hidraw and runner.forces_hidraw:
        environment['PROTON_SONY_HIDRAW_XINPUT'] = '1'

    # the debug variables are read by whether they are set at all, not by their value
    if not debug:
        environment['DXVK_LOG_LEVEL'] = 'none'
        environment['VKD3D_DEBUG'] = 'none'

    # so is fsr: leaving it out is what turns it on
    if not config.get_bool('fsr'):
        environment['WINE_FULLSCREEN_FSR'] = '0'

    # ESYNC and FSYNC are deprecated in favor of NTSYNC, which is on when supported
    environment['WINEDISABLEFASTSYNC'] = '0' if _setup_ntsync(config.get_bool('ntsync', True)) else '1'

    return environment


def _dxvk_environment(config: Config, runner: wine.Runner, /) -> dict[str, str | Path]:

    environment = wine.dxvk_environment(
        runner,
        enabled=config.get_bool('dxvk'),
        nvapi=config.get_bool('enable_nvapi'),
        vkreflex=config.get_bool('enable_vkreflex'),
        hud=config.get_bool('dxvk_hud'),
        reset_cache=config.get_bool('dxvk_reset_cache'),
    )

    # d7vk symlinks ddraw.dll and is overridden like dxvk, disabled by default
    if runner.install_d7vk(config.get_bool('d7vk')):
        environment['WINEDLLOVERRIDES'] = f'{environment["WINEDLLOVERRIDES"]};ddraw=n,b'

    return environment


def _run(command: list[str], /) -> None:
    """Run a system tool, none of which is worth failing a game start over."""
    try:
        subprocess.run(command, capture_output=True, check=False)
    except OSError as e:
        _logger.warning('%s failed: %s', command[0], e)


def _setup_ntsync(wanted: bool, /) -> bool:
    if not wanted:
        _run(['rmmod', 'ntsync'])
        _logger.debug('ntsync disabled for wine')
        return False

    _run(['modprobe', 'ntsync'])

    if os.access('/dev/ntsync', os.R_OK):
        return True

    _logger.warning('/dev/ntsync is not accessible, disabling ntsync in wine')
    return False


def _copy_installer_settings(installer_name: str, installed_name: str, /) -> None:
    """
    Carry the options chosen for an installer over to the game it installs, so that the
    runner and the tweaks it was installed with are the ones it runs with.
    """
    settings = KeyValueConfig(BATOCERA_CONF)

    # what every installer was given goes to every windows game, this one's to its game
    sections = (
        (_WINDOWS_INSTALLERS_SYSTEM, _WINDOWS_SYSTEM),
        (f'{_WINDOWS_INSTALLERS_SYSTEM}["{installer_name}"]', f'{_WINDOWS_SYSTEM}["{installed_name}"]'),
    )

    for installer_section, installed_section in sections:
        for key, value in settings.section_items(installer_section, keep_defaults=True):
            installed_key = f'{installed_section}.{key}'

            _logger.debug('%s.%s -> %s = %s', installer_section, key, installed_key, value)

            _run(['batocera-settings-set', installed_key, value])
