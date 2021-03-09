#!/usr/bin/env python

import glob
import os
import re
import shutil

import Command
from generators.Generator import Generator
import controllersConfig

_ROMS_DIR = '/userdata/roms/xash3d_fwgs'

_HLSDK_LIBS_DIR = '/usr/lib/xash3d/hlsdk'

_DEFAULT_SERVER_LIB = 'hl'


def _rom_dir(game):
    return _ROMS_DIR + '/' + game


def _config_dir(game):
    return '/userdata/system/configs/xash3d_fwgs/' + game


def _save_dir(game):
    return '/userdata/saves/xash3d_fwgs/' + game


def _client_lib_path(server_lib, arch_suffix):
    return _HLSDK_LIBS_DIR + '/' + server_lib + '/cl_dlls/client' + arch_suffix + '.so'


def _server_lib_path(server_lib, arch_suffix):
    return _HLSDK_LIBS_DIR + '/' + server_lib + '/dlls/' + server_lib + arch_suffix + '.so'


def _get_server_lib_basename_from_liblist_gam(game):
    """Gets the base name of the server library from liblist.gam in the game directory."""
    path = _rom_dir(game) + '/liblist.gam'
    if not os.path.exists(path):
        return None
    pattern = re.compile(r'gamedll\w*\s+"(?:dlls[/\\])?([^.]*)')
    with open(path, 'r') as f:
        for line in f:
            m = pattern.match(line)
            if m:
                return m.group(1)
    return None


def _find_server_lib(server_lib, arch_suffix):
    """Finds and returns the server library.

    Falls back to _DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        path = _server_lib_path(server_lib, arch_suffix)
        if os.path.exists(path):
            return path

    return _server_lib_path(_DEFAULT_SERVER_LIB, arch_suffix)


def _find_client_lib(server_lib, arch_suffix):
    """Finds and returns the client library.

    Falls back to the client library for _DEFAULT_SERVER_LIB if none is found.
    """
    if server_lib:
        path = _client_lib_path(server_lib, arch_suffix)
        if os.path.exists(path):
            return path

    return _client_lib_path(_DEFAULT_SERVER_LIB, arch_suffix)


def _get_arch_suffix():
    """Returns the architecture suffix, e.g. _amd64, based on a known server library."""
    path_prefix = _HLSDK_LIBS_DIR + '/hl/dlls/hl'
    return glob.glob(path_prefix + '*.so')[0][len(path_prefix):-3]


class Xash3dFwgsGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        game = os.path.splitext(os.path.basename(rom))[0]

        arch_suffix = _get_arch_suffix()
        server_lib = _get_server_lib_basename_from_liblist_gam(game)

        # Useful options for debugging:
        # -log        # Log to /userdata/roms/xash3d_fwgs/engine.log
        # -dev 2      # Verbose logging
        # -ref gles2  # Select a specific renderer (gl, gl4es, gles1, gles2, soft)
        commandArray = ['/usr/lib/xash3d/xash3d', '-fullscreen']

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

        # https://github.com/FWGS/xash3d-fwgs/issues/307
        commandArray.append('+sv_validate_changelevel')
        commandArray.append('0')

        self._maybeInitConfig(game)
        self._maybeInitSaveDir(game)

        return Command.Command(
            array=commandArray,
            env={
                'XASH3D_BASEDIR': _ROMS_DIR,
                'XASH3D_EXTRAS_PAK1': _ROMS_DIR + '/extras.pak',
                'LD_LIBRARY_PATH': '/usr/lib/xash3d',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })

    def _maybeInitConfig(self, game):
        rom_dir = _rom_dir(game)
        if not os.path.exists(rom_dir + '/userconfig.cfg'):
            with open(rom_dir + '/userconfig.cfg', 'w') as f:
                f.write('exec gamepad.cfg\nexec custom.cfg\n')

        if not os.path.exists(rom_dir + '/gamepad.cfg'):
            shutil.copy(os.path.dirname(os.path.abspath(__file__)) +
                        '/gamepad.cfg', rom_dir + '/gamepad.cfg')

        config_dir = _config_dir(game)
        if not os.path.exists(config_dir + '/custom.cfg'):
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            with open(config_dir + '/custom.cfg', 'w') as f:
                f.write('\n')
            if not os.path.exists(rom_dir + '/custom.cfg'):
                os.symlink(config_dir + '/custom.cfg', rom_dir + '/custom.cfg')

    def _maybeInitSaveDir(self, game):
        rom_dir = _rom_dir(game)
        if not os.path.isdir(rom_dir + '/save'):
            save_dir = _save_dir(game)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            if not os.path.exists(rom_dir + '/save'):
                os.symlink(save_dir, rom_dir + '/save')
