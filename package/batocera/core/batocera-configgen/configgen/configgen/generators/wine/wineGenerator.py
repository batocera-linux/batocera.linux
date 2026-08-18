from __future__ import annotations

import logging
import os
import re
import resource
import shlex
import subprocess
import tarfile
from contextlib import ExitStack, contextmanager
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BATOCERA_CONF, CACHE, ROMS, SAVES
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ...settings.unixSettings import UnixSettings
from ...utils import wine
from ..Generator import Generator

if TYPE_CHECKING:
    from collections.abc import Generator as Iterator

    from ...config import SystemConfig
    from ...types import HotkeysContext, Resolution

_logger = logging.getLogger(__name__)

# the system an installed game belongs to, and the one whose prefixes and settings the
# installers share: what windows_installers installs is a windows game
_WINDOWS: Final = 'windows'
_WINDOWS_INSTALLERS: Final = 'windows_installers'

# roms that are a file rather than a directory, and run from where they sit: the
# installers, and the bare .exe a windows rom may be
_FILE_SUFFIXES: Final = ('.exe', '.iso', '.msi')

_NVIDIA_PRIME: Final = Path('/var/tmp/nvidia.prime')
_NVIDIA_CACHE: Final = CACHE / 'nvidia'


class WineGenerator(Generator):
    """
    Runs a game through wine, in the shapes batocera-wine established for them. Any
    system may ask for it, mugen as much as windows, and each keeps its prefixes under
    /userdata/system/wine-bottles/<system>/<runner>/ as batocera-wine did:

    - a .wine rom is a complete wine prefix and runs in itself
    - a .wsquashfs is that prefix squashed, mounted with a writable overlay kept in
      /userdata/system/wine-bottles, so what reaches generate() is a prefix like any
      other
    - a .wtgz is that prefix as a tarball, unpacked once into a prefix of its own
    - a .pc rom is a directory of game files, and a bare .exe a single one, both run in
      a prefix of their own under /userdata/system/wine-bottles
    - a windows_installers rom is an installer, run in a new prefix in
      /userdata/roms/windows that becomes the installed game

    A rom says what to run, and how, in its autorun.cmd, see utils/wine.py.
    """

    def __init__(self) -> None:
        # what has to stay mounted while the game runs, released by running()
        self.__resources = ExitStack()
        self.__runner: wine.Runner | None = None
        self.__installing = False
        # the system whose bottles the game runs in: any system may run its games through
        # wine, and each keeps prefixes of its own. Every call that builds one is given
        # the system first, this is only what it is until one of them has run
        self.__system = _WINDOWS

    # a wine prefix is written to as the game runs, so a squashed rom needs the overlay
    def writesToRom(self, config: SystemConfig) -> bool:
        return True

    def writableRomDir(self, system, rom: Path) -> Path:
        # a squashed rom is a prefix, and what it writes is prefix rather than saves:
        # it belongs where the prefix of any other rom lives, kept per runner so that
        # changing runner doesn't reuse what another one wrote. what the game saves is
        # linked out to /userdata/saves by the SAVEDIR of its autorun.cmd
        self.__system = system.name

        return wine.get_prefix_path(system.name, wine.get_runner_name(_runner_name(system.config)), rom)

    def getHotkeysContext(self) -> HotkeysContext:
        # closing the wineserver of the prefix is what closes the game, and the prefix
        # is the one generate() picked: the hotkeys are set once it has run
        if (runner := self.__runner) is None:
            raise BatoceraException('The wine hotkeys are only known once the game has been prepared')

        return {
            "name": "wine",
            "keys": { "exit": f"WINEPREFIX={shlex.quote(str(runner.bottle_dir))} {shlex.quote(str(runner.wineserver))} -k" }
        }

    def getMouseMode(self, config, rom):
        return config.get_bool('force_mouse')

    def executionDirectory(self, config, rom):
        # an installer, or a game that is a single executable, runs from where it sits
        if rom.suffix.lower() in _FILE_SUFFIXES:
            return rom.parent

        return wine.get_game_dir(self.__rom_dir(config, rom))

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        self.__system = system.name
        self.__installing = system.name == _WINDOWS_INSTALLERS

        try:
            if self.__installing:
                return self.__install(system.config, rom, playersControllers)

            return self.__play(system, rom, playersControllers, gameResolution)
        except BaseException:
            # the game won't start, so running() won't be there to release them
            self.__resources.close()
            raise

    @contextmanager
    def running(self, config, rom) -> Iterator[None]:
        with self.__resources:
            if (runner := self.__runner) is None:
                yield
                return

            # the rom is unmounted the moment this returns, so nothing may still be
            # holding it: wine hands the game over to the wineserver and exits first
            with runner.running():
                yield

            if self.__installing:
                self.__installed(runner)

    def __prepare(self, config: SystemConfig, rom: Path, /, *, prefix: Path | None = None) -> wine.Runner:
        """
        The runner and the prefix the rom runs in, built if it doesn't exist yet. Both
        executionDirectory() and generate() need them, and executionDirectory() is
        called first, so this is done once and kept. Whichever gets here first has told
        us the system, whose bottles the prefix is one of.
        """
        if self.__runner is not None:
            return self.__runner

        wanted_runner = _runner_name(config)
        runner_name = wine.get_runner_name(wanted_runner)

        if prefix is None:
            prefix = wine.get_prefix_path(self.__system, runner_name, rom)

        runner = wine.Runner.from_prefix(
            wanted_runner,
            prefix,
            arch=wine.wanted_prefix_arch(runner_name, enable_win32=config.get_bool('enable_win32')),
        )
        self.__runner = runner

        _logger.debug('running %s in %s with %s', rom.name, prefix, runner.runner_name)

        wine.log_filesystems(rom, prefix)

        built = (prefix / 'system.reg').exists()
        runner.create_bottle()

        # a .wtgz is a prefix in a tarball, unpacked into the prefix built for it
        if not built and rom.suffix.lower() == '.wtgz':
            _logger.info('unpacking %s into %s', rom, prefix)
            with tarfile.open(rom) as tar:
                tar.extractall(prefix, filter='tar')

        return runner

    def __rom_dir(self, config: SystemConfig, rom: Path, /) -> Path:
        """
        Where the autorun.cmd of the game is: a rom that is a directory holds it, whether
        it keeps the game files next to its own as a .pc rom does or is a prefix itself
        as a .wine rom and a mounted .wsquashfs are. Only an archive describes itself in
        the prefix it is unpacked into, which is the one thing here worth building.
        """
        if rom.is_dir():
            return rom

        return self.__prepare(config, rom).bottle_dir

    def __play(self, system, rom: Path, playersControllers, gameResolution: Resolution, /) -> Command.Command:
        config: SystemConfig = system.config
        runner = self.__prepare(config, rom)

        self.__setup_prefix(config, runner)

        environment = self.__environment(config, runner, playersControllers)

        command: list[str | Path] = [runner.wine]

        # a virtual desktop puts the game in a window of its own, at the size it expects,
        # on a black background rather than wine's blue
        if config.get_bool('virtual_desktop'):
            runner.set_registry_value(r'HKEY_CURRENT_USER\Control Panel\Colors', 'Background', 'REG_SZ', '0 0 0')
            command += ['explorer', f'/desktop=Wine,{gameResolution["width"]}x{gameResolution["height"]}']

        if rom.is_file() and rom.suffix.lower() == '.exe':
            # a bare .exe is the game, and runs from the directory it sits in
            command.append(rom.name)
            return Command.Command(array=command, env=environment)

        rom_dir = self.__rom_dir(config, rom)

        # what the game saves goes to /userdata/saves, if it says where it saves it
        wine.link_saves(rom_dir, runner.bottle_dir, SAVES / system.name / rom.stem)

        try:
            exe, arguments = wine.get_game_command(rom_dir)
        except BatoceraException as e:
            # what batocera-wine did without an autorun.cmd: open the prefix and let
            # the user start the game themselves
            _logger.warning('%s, starting the file manager instead', e)
            command.append('explorer')
        else:
            command.append(exe)
            command += arguments

        environment.update(wine.get_autorun_environment(rom_dir))

        return Command.Command(array=command, env=environment)

    def __install(self, config: SystemConfig, rom: Path, playersControllers, /) -> Command.Command:
        # the installer builds the game, as a prefix in the roms of the windows system
        runner = self.__prepare(config, rom, prefix=ROMS / _WINDOWS / _installed_name(rom))

        # and the game keeps the options that were chosen for its installer
        _copy_installer_settings(rom.name, runner.bottle_dir.name)

        self.__setup_prefix(config, runner)

        environment = self.__environment(config, runner, playersControllers)

        command: list[str | Path]

        match rom.suffix.lower():
            case '.exe':
                command = [runner.wine, rom]
            case '.msi':
                command = [runner.msiexec, '-i', rom]
            case '.iso':
                # the image is the installation media, mounted as the d: drive
                mount_point = self.__resources.enter_context(wine.mount_iso(rom))

                drive = runner.bottle_dir / 'dosdevices' / 'd:'
                drive.parent.mkdir(parents=True, exist_ok=True)

                if drive.is_symlink() or drive.exists():
                    drive.unlink()
                drive.symlink_to(mount_point)

                if (installer := wine.autorun_inf_command(mount_point)) is not None:
                    _logger.info('the autorun.inf of %s runs %s', rom.name, ' '.join(installer))
                    command = [runner.wine, *installer]
                else:
                    _logger.info('%s names no installer to run, opening its drive instead', rom.name)
                    command = [runner.wine, 'explorer', 'd:']
            case suffix:
                raise BatoceraException(f'Unknown installer type: {suffix}')

        return Command.Command(array=command, env=environment)

    def __installed(self, runner: wine.Runner, /) -> None:
        """Turn the prefix an installer wrote into a game the windows system can run."""
        prefix = runner.bottle_dir

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
                len(executables), prefix,
            )

        wine.write_autorun_cmd(prefix, executables[0] if len(executables) == 1 else None)

    def __setup_prefix(self, config: SystemConfig, runner: wine.Runner, /) -> None:
        """What a prefix is given before the game runs, whether it is new or not."""
        runner.install_redists()
        runner.install_msis()
        runner.install_rawinput()
        runner.install_regs()
        runner.install_fonts()
        runner.sandbox_prefix()
        runner.set_hidraw(config.get_bool('enable_hidraw'))

    def __environment(
        self,
        config: SystemConfig,
        runner: wine.Runner,
        playersControllers,
        /,
    ) -> dict[str, str | Path]:
        environment = runner.get_environment()
        environment.update(_wine_options(config))
        environment.update(_display_environment(config))
        environment.update(_dxvk_environment(config, runner))

        if language := config.get_str('system.language', ''):
            environment.update({
                "LANG": f'{language}.UTF-8',
                "LC_ALL": f'{language}.UTF-8',
            })

        # sdl controller option - default is on
        if config.get_bool('sdl_config', True):
            environment.update({
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
            })

        # ensure nvidia driver used for vulkan
        if _NVIDIA_PRIME.exists():
            for variable_name in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
                os.environ.pop(variable_name, None)

            environment.update({
                'VK_ICD_FILENAMES': '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json:/usr/share/vulkan/icd.d/nvidia_icd.i686.json',
            })

        return environment


def _runner_name(config: SystemConfig, /) -> str:
    # the runner chosen for the game, falling back to the core, which is what the
    # runner was called before it had an option of its own
    return config.get_str('wine-runner', '') or config.get_str('core', '')


def _installed_name(rom: Path, /) -> str:
    # the time keeps a game installed twice from landing on the prefix of the first one
    return f'{datetime.now():%y%m%d-%H%M%S}_{rom.stem}.wine'


def _display_environment(config: SystemConfig, /) -> dict[str, str | Path]:
    """
    Wine draws through XWayland unless the game asks for the native wayland driver, in
    which case it is given no DISPLAY at all and picks the wayland driver itself.
    """
    try:
        display_mode = subprocess.run(
            ['batocera-resolution', 'getDisplayMode'], capture_output=True, text=True, timeout=5, check=False,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        _logger.warning('unable to tell what the display is running: %s', e)
        display_mode = ''

    if display_mode == 'wayland' and config.get_str('wayland_driver', 'xwayland') == 'native':
        _logger.debug('wayland with the native driver requested, running without a DISPLAY')
        return {'DISPLAY': ''}

    # x11, or xwayland: give the game the keyboard layout of the system
    if keyboard := _system_setting('system.kblayout'):
        _run(['setxkbmap', keyboard])

    return {}


def _wine_options(config: SystemConfig, /) -> dict[str, str | Path]:
    """The wine and driver knobs the windows systems expose, as their environment."""
    debug = config.get_bool('wine_debug')

    _NVIDIA_CACHE.mkdir(parents=True, exist_ok=True)

    environment: dict[str, str | Path] = {
        'WINEDEBUG': 'err+all,fixme+all' if debug else '-all',
        'PBA_ENABLE': config.get_bool('pba', return_values=('1', '0')),
        'DXVK_FRAME_RATE': config.get_bool('fps_limit', return_values=('60', '0')),
        'WINE_ENABLE_HIDRAW': config.get_bool('enable_hidraw', return_values=('1', '0')),
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
        '__GL_SHADER_DISK_CACHE_PATH': _NVIDIA_CACHE,
    }

    # the debug variables are read by whether they are set at all, not by their value
    if not debug:
        environment['DXVK_LOG_LEVEL'] = 'none'
        environment['VKD3D_DEBUG'] = 'none'

    # so is fsr: leaving it out is what turns it on
    if not config.get_bool('fsr'):
        environment['WINE_FULLSCREEN_FSR'] = '0'

    # ESYNC and FSYNC are deprecated in favor of NTSYNC with modern Wine and kernel.
    # NTSYNC is enabled by default when supported, the option is there to turn it off.
    environment['WINEDISABLEFASTSYNC'] = '0' if _setup_ntsync(config.get_bool('ntsync', True)) else '1'

    # While esync is deprecated, the ulimit is still important for Wine performance.
    _raise_file_limit()

    return environment


def _dxvk_environment(config: SystemConfig, runner: wine.Runner, /) -> dict[str, str | Path]:
    """
    Install the direct3d dlls the game is to draw through, and tell wine to load them.
    dxvk translates direct3d to vulkan, and is only built on the architectures it
    supports; without it, the game runs on the wined3d dlls wine ships itself.
    """
    nvapi = config.get_bool('enable_nvapi') or config.get_bool('enable_vkreflex')

    environment: dict[str, str | Path] = {
        'DXVK_STATE_CACHE': 'reset' if config.get_bool('dxvk_reset_cache') else '1',
        'DXVK_ENABLE_NVAPI': '1' if nvapi else '0',
        'NVAPI': '1' if nvapi else '0',
    }

    # Reflex requires NVAPI to function; force it on if Reflex is enabled
    if config.get_bool('enable_vkreflex'):
        environment['DXVK_NVAPI_VKREFLEX'] = '1'
    else:
        environment['DISABLE_DXVK_NVAPI_VKREFLEX'] = '1'

    if config.get_bool('dxvk_hud'):
        environment['DXVK_HUD'] = '1'

    # no start menu entries wanted, batocera is what starts the games
    dll_overrides = ['winemenubuilder.exe=']

    if config.get_bool('dxvk') and (dxvk_dlls := runner.install_dxvk()):
        environment.update({
            'DXVK_ASYNC': '1',
            'DXVK_CONFIG_FILE': wine.USER_WINE_DIR / 'dxvk.conf',
            'DXVK_STATE_CACHE_PATH': CACHE,
        })

        if graphics := sorted(dll for dll in dxvk_dlls if not dll.startswith(('nvapi', 'nvofapi'))):
            dll_overrides.append(f"{','.join(graphics)}=n")

        if nvapi_dlls := sorted(dll for dll in dxvk_dlls if dll.startswith(('nvapi', 'nvofapi'))):
            dll_overrides.append(f"{','.join(nvapi_dlls)}={'n' if nvapi else ''}")
    else:
        environment['DXVK_ASYNC'] = '0'

        # a prefix that ran with dxvk still links into it, put wine's own dlls back
        if builtin := sorted(runner.install_builtin_d3d()):
            dll_overrides.append(f"{','.join(builtin)}=b")

        dll_overrides.append('nvapi64,nvapi=')

    environment['WINEDLLOVERRIDES'] = ';'.join(dll_overrides)

    return environment


def _run(command: list[str], /) -> None:
    """Run a system tool, none of which is worth failing a game start over."""
    try:
        subprocess.run(command, capture_output=True, check=False)
    except OSError as e:
        _logger.warning('%s failed: %s', command[0], e)


def _setup_ntsync(wanted: bool, /) -> bool:
    """Load or unload the ntsync module, and say whether wine may use it."""
    if not wanted:
        _run(['rmmod', 'ntsync'])
        _logger.debug('ntsync disabled for wine')
        return False

    _run(['modprobe', 'ntsync'])

    if os.access('/dev/ntsync', os.R_OK):
        return True

    _logger.warning('/dev/ntsync is not accessible, disabling ntsync in wine')
    return False


def _raise_file_limit() -> None:
    wanted = 1048576

    try:
        _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(wanted, hard), hard))
    except (OSError, ValueError) as e:
        _logger.warning('could not raise the file limit, which may impact performance: %s', e)


def _system_setting(name: str, /) -> str | None:
    # a system-wide setting, which isn't one of the options of a system
    return UnixSettings(BATOCERA_CONF).config.get('DEFAULT', name, fallback=None)


def _copy_installer_settings(installer_name: str, installed_name: str, /) -> None:
    """
    Carry the options chosen for an installer over to the game it installs, so that the
    runner and the tweaks it was installed with are the ones it runs with.
    """
    settings = UnixSettings(BATOCERA_CONF)
    wanted = re.compile(rf'^{_WINDOWS_INSTALLERS}(\["{re.escape(installer_name)}"\])?\.')

    for key, value in list(settings.config.items('DEFAULT')):
        if not wanted.match(key):
            continue

        installed_key = key.replace(_WINDOWS_INSTALLERS, _WINDOWS, 1).replace(installer_name, installed_name, 1)

        _logger.debug('%s -> %s = %s', key, installed_key, value)

        _run(['batocera-settings-set', installed_key, value])
