from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, SAVES, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


_CONFIG_DIR: Final = CONFIGS / 'xash3d_fwgs'
_ROMS_DIR: Final = ROMS / 'xash3d_fwgs'
_SAVES_DIR: Final = SAVES / 'xash3d_fwgs'
_HLSDK_LIBS_DIR: Final = Path('/usr/lib/xash3d/hlsdk')
_DEFAULT_SERVER_LIB: Final = 'hl'


def _rom_dir(game: str) -> Path:
    return _ROMS_DIR / game


def _config_dir(game: str) -> Path:
    return _CONFIG_DIR / game


def _save_dir(game: str) -> Path:
    return _SAVES_DIR / game


def _client_lib_path(server_lib: str, arch_suffix: str) -> Path:
    return _HLSDK_LIBS_DIR / server_lib / 'cl_dlls' / f'client{arch_suffix}.so'


def _server_lib_path(server_lib: str, arch_suffix: str) -> Path:
    return _HLSDK_LIBS_DIR / server_lib / 'dlls' / f'{server_lib}{arch_suffix}.so'


def _get_server_lib_basename_from_liblist_gam(game: str) -> str | None:
    """Gets the base name of the server library from liblist.gam in the game directory."""
    path = _rom_dir(game) / 'liblist.gam'
    if not path.exists():
        return None
    pattern = re.compile(r'gamedll\w*\s+"(?:dlls[/\\])?([^.]*)')
    with path.open('r') as f:
        for line in f:
            m = pattern.match(line)
            if m:
                return m.group(1)
    return None


def _find_server_lib(server_lib: str, arch_suffix: str) -> Path:
    """Finds and returns the server library.

    Falls back to _DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        path = _server_lib_path(server_lib, arch_suffix)
        if path.exists():
            return path

    return _server_lib_path(_DEFAULT_SERVER_LIB, arch_suffix)


def _find_client_lib(server_lib: str, arch_suffix: str) -> Path:
    """Finds and returns the client library.

    Falls back to the client library for _DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        path = _client_lib_path(server_lib, arch_suffix)
        if path.exists():
            return path

    return _client_lib_path(_DEFAULT_SERVER_LIB, arch_suffix)


def _get_arch_suffix() -> str:
    """Returns the architecture suffix, e.g. _amd64, based on a known server library."""
    path_prefix = _HLSDK_LIBS_DIR / 'hl' / 'dlls'
    return next(path_prefix.glob('hl*.so')).stem[2:]


class Xash3dFwgsGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "xash3dFwgs",
            "keys": { "exit": "KEY_F10", "menu": "KEY_ESC", "pause": "KEY_ESC", "save_state": "KEY_F6", "restore_state": "KEY_F7" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        game = Path(rom).stem

        arch_suffix = _get_arch_suffix()
        server_lib = _get_server_lib_basename_from_liblist_gam(game)

        # Useful options for debugging:
        # -log        # Log to /userdata/roms/xash3d_fwgs/engine.log
        # -dev 2      # Verbose logging
        # -ref gles2  # Select a specific renderer (gl, gl4es, gles1, gles2, soft)
        commandArray = ['/usr/bin/xash3d', '-fullscreen', '-dev']

        # By default, xash3d will use `dlls/hl.so` in the valve directory (via the `liblist.gam` config file).
        # However, that `so` is incompatible with xash3d (it's the x86-glibc version from Valve).
        # We instead point to the hlsdk-xash3d `so`.
        commandArray.append('-clientlib')
        commandArray.append(_find_client_lib(server_lib, arch_suffix))

        commandArray.append('-dll')
        commandArray.append(_find_server_lib(server_lib, arch_suffix))

        commandArray.append('-game')
        commandArray.append(game)

        commandArray.append('+showfps')
        commandArray.append('1' if system.getOptBoolean('showFPS') == True else '0')

        self._maybeInitConfig(game)
        self._maybeInitSaveDir(game)

        return Command.Command(
            array=commandArray,
            env={
                'XASH3D_BASEDIR': _ROMS_DIR,
                'XASH3D_EXTRAS_PAK1': '/usr/share/xash3d/valve/extras.pk3',
                'LD_LIBRARY_PATH': '/usr/lib/xash3d',
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })

    def _maybeInitConfig(self, game: str) -> None:
        rom_dir = _rom_dir(game)
        user_config = rom_dir / 'userconfig.cfg'
        if not user_config.exists():
            with user_config.open('w') as f:
                f.write('exec gamepad.cfg\nexec custom.cfg\n')

        gamepad_config = rom_dir / 'gamepad.cfg'
        if not gamepad_config.exists():
            shutil.copy(Path(__file__).absolute().parent / 'gamepad.cfg', gamepad_config)

        config_dir = _config_dir(game)
        custom_config = config_dir / 'custom.cfg'
        custom_rom_config = rom_dir / 'custom.cfg'
        if not custom_config.exists():
            with ensure_parents_and_open(custom_config, 'w') as f:
                f.write('\n')
            if not custom_rom_config.exists():
                custom_rom_config.symlink_to(custom_config)

    def _maybeInitSaveDir(self, game: str) -> None:
        rom_dir = _rom_dir(game)
        rom_save_dir = rom_dir / 'save'
        if not rom_save_dir.is_dir():
            save_dir = _save_dir(game)
            mkdir_if_not_exists(save_dir)
            if not rom_save_dir.exists():
                rom_save_dir.symlink_to(save_dir)
