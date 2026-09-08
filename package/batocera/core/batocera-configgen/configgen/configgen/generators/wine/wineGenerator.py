from __future__ import annotations

import logging
import shlex
import tarfile
from contextlib import ExitStack, contextmanager
from datetime import datetime
from typing import TYPE_CHECKING, Final, cast

from batocera_launch_wine import emulator as wine_emulator, wine

from ... import Command
from ...batoceraPaths import ROMS, SAVES
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ..Generator import Generator

if TYPE_CHECKING:
    from collections.abc import Generator as Iterator
    from pathlib import Path

    from batocera_launch import Config as LaunchConfig

    from ...config import SystemConfig
    from ...types import HotkeysContext, Resolution

_logger = logging.getLogger(__name__)

# what windows_installers installs is a windows game, and shares its prefixes
_WINDOWS_SYSTEM: Final = 'windows'
_WINDOWS_INSTALLERS_SYSTEM: Final = 'windows_installers'

# roms that are a file rather than a directory, and run from where they sit
_FILE_SUFFIXES: Final = ('.exe', '.iso', '.msi')

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
        # the system whose prefixes the game runs in, until a call names another
        self.__system = _WINDOWS_SYSTEM

    # a wine prefix is written to as the game runs, so a squashed rom needs the overlay
    def writesToRom(self, config: SystemConfig) -> bool:
        return True

    def writableRomDir(self, system, rom: Path) -> Path:
        # what a squashed rom writes is prefix rather than saves, kept per runner
        self.__system = system.name

        return wine.get_prefix_path(system.name, wine.get_runner_name(system.config.get_str('wine-runner', '') or system.config.get_str('core', '')), rom)

    def getHotkeysContext(self) -> HotkeysContext:
        # closing the wineserver of the prefix generate() picked is what closes the game
        if (runner := self.__runner) is None:
            raise BatoceraException('The wine hotkeys are only known once the game has been prepared')

        return {
            "name": "wine",
            "keys": { "exit": f"WINEPREFIX={shlex.quote(str(runner.prefix_dir))} {shlex.quote(str(runner.wineserver))} -k" }
        }

    def getMouseMode(self, config, rom):
        return config.get_bool('force_mouse')

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9

    def executionDirectory(self, config, rom):
        # an installer, or a game that is a single executable, runs from where it sits
        if rom.suffix.lower() in _FILE_SUFFIXES:
            return rom.parent

        return wine.get_game_dir(self.__rom_dir(config, rom))

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        self.__system = system.name
        self.__installing = system.name == _WINDOWS_INSTALLERS_SYSTEM

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

            # nothing may hold the rom when this returns, wine exits before the game
            try:
                yield
            finally:
                runner.stop()

            if self.__installing:
                self.__generate_autorun_in_installed_prefix(runner)

    def __prepare(self, config: SystemConfig, rom: Path, /, *, prefix: Path | None = None) -> wine.Runner:
        """
        The runner and the prefix the rom runs in, built if it doesn't exist yet. Both
        executionDirectory() and generate() need them, and executionDirectory() is
        called first, so this is done once and kept. Whichever gets here first has told
        us the system, whose bottles the prefix is one of.
        """
        if self.__runner is not None:
            return self.__runner

        wanted_runner = config.get_str('wine-runner', '') or config.get_str('core', '')
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
        runner.create_or_update_prefix()

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

        return self.__prepare(config, rom).prefix_dir

    def __play(self, system, rom: Path, playersControllers, gameResolution: Resolution, /) -> Command.Command:
        config: SystemConfig = system.config
        runner = self.__prepare(config, rom)

        self.__setup_prefix(config, runner)

        environment = self.__environment(config, runner, playersControllers)

        command: list[str | Path] = [runner.wine]

        # a virtual desktop gives the game a window of its own, on black rather than blue
        if config.get_bool('virtual_desktop'):
            runner.set_registry_value(r'HKEY_CURRENT_USER\Control Panel\Colors', 'Background', 'REG_SZ', '0 0 0')
            command += ['explorer', f'/desktop=Wine,{gameResolution["width"]}x{gameResolution["height"]}']

        if rom.is_file() and rom.suffix.lower() == '.exe':
            # a bare .exe is the game, and runs from the directory it sits in
            command.append(rom.name)
            return Command.Command(array=command, env=environment)

        rom_dir = self.__rom_dir(config, rom)

        # what the game saves goes to /userdata/saves, if it says where it saves it
        wine.link_saves(rom_dir, runner.prefix_dir, SAVES / system.name / rom.stem)

        try:
            exe, arguments = wine.get_game_command(rom_dir)
        except BatoceraException as e:
            # what batocera-wine did without an autorun.cmd, let the user start it
            _logger.warning('%s, starting the file manager instead', e)
            command.append('explorer')
        else:
            command.append(exe)
            command += arguments

        environment.update(wine.get_autorun_environment(rom_dir))

        return Command.Command(array=command, env=environment)

    def __install(self, config: SystemConfig, rom: Path, playersControllers, /) -> Command.Command:
        # the installer builds the game, as a prefix in the roms of the windows system
        runner = self.__prepare(config, rom, prefix=ROMS / _WINDOWS_SYSTEM / f'{datetime.now():%y%m%d-%H%M%S}_{rom.stem}.wine')

        # and the game keeps the options that were chosen for its installer
        wine_emulator._copy_installer_settings(rom.name, runner.prefix_dir.name)

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

                drive = runner.prefix_dir / 'dosdevices' / 'd:'
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

    def __generate_autorun_in_installed_prefix(self, runner: wine.Runner, /) -> None:
        """Turn the prefix an installer wrote into a game the windows system can run."""
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
        runner.set_hidraw(wine_emulator._get_hidraw(cast('LaunchConfig', config), runner))

    def __environment(
        self,
        config: SystemConfig,
        runner: wine.Runner,
        playersControllers,
        /,
    ) -> dict[str, str | Path]:
        environment = runner.get_environment()
        environment.update(wine_emulator._wine_options(cast('LaunchConfig', config), runner))
        environment.update(wine.display_environment(wayland_driver=config.get_str('wayland_driver', 'xwayland')))
        environment.update(wine_emulator._dxvk_environment(cast('LaunchConfig', config), runner))

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
        environment.update(wine.nvidia_prime_environment())

        return environment
