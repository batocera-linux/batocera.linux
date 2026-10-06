from __future__ import annotations

import re
import shutil
from importlib import resources
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import SAVES
from batocera_launch import Command, Emulator, HotkeysContext

_HLSDK_LIBS_DIR: Final = Path('/usr/lib/xash3d/hlsdk')
_DEFAULT_SERVER_LIB: Final = 'hl'
_GAMEDLL_RE: Final = re.compile(r'gamedll\w*\s+"(?:dlls[/\\])?([^.]*)')


def _client_lib_path(server_lib: str, arch_suffix: str) -> Path:
    return _HLSDK_LIBS_DIR / server_lib / 'cl_dlls' / f'client{arch_suffix}.so'


def _server_lib_path(server_lib: str, arch_suffix: str) -> Path:
    return _HLSDK_LIBS_DIR / server_lib / 'dlls' / f'{server_lib}{arch_suffix}.so'


def _find_server_lib(server_lib: str | None, arch_suffix: str) -> Path:
    if server_lib:
        path = _server_lib_path(server_lib, arch_suffix)
        if path.exists():
            return path

    return _server_lib_path(_DEFAULT_SERVER_LIB, arch_suffix)


def _find_client_lib(server_lib: str | None, arch_suffix: str) -> Path:
    if server_lib:
        path = _client_lib_path(server_lib, arch_suffix)
        if path.exists():
            return path

    return _client_lib_path(_DEFAULT_SERVER_LIB, arch_suffix)


def _get_arch_suffix() -> str:
    path_prefix = _HLSDK_LIBS_DIR / 'hl' / 'dlls'
    return next(path_prefix.glob('hl*.so')).stem[2:]


@cached_dataclass
class Xash3dFwgs(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'xash3dFwgs',
            'keys': {
                'exit': 'KEY_F10',
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F7',
            },
        }

    @cached_property
    def rom_data_dir(self) -> Path:
        return self.roms_dir / self.rom.stem

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'xash3d_fwgs'

    async def configure(self) -> Command:
        arch_suffix = _get_arch_suffix()
        server_lib = self._get_server_lib_basename_from_liblist_gam()

        # By default, xash3d will use `dlls/hl.so` in the valve directory (via the `liblist.gam` config file).
        # However, that `so` is incompatible with xash3d (it's the x86-glibc version from Valve).
        # We instead point to the hlsdk-xash3d `so`.
        args: list[str | Path] = [
            '/usr/bin/xash3d',
            '-fullscreen',
            '-dev',
            '-clientlib',
            _find_client_lib(server_lib, arch_suffix),
            '-dll',
            _find_server_lib(server_lib, arch_suffix),
            '-game',
            self.rom.stem,
            '+cl_showfps',
            '1' if self.config.show_fps else '0',
        ]

        self._maybe_init_config()
        self._maybe_init_save_dir()

        return Command(
            args,
            env={
                'XASH3D_BASEDIR': self.rom_data_dir,
                'XASH3D_EXTRAS_PAK1': '/usr/share/xash3d/valve/extras.pk3',
                'LD_LIBRARY_PATH': '/usr/lib/xash3d',
            },
        )

    def _get_server_lib_basename_from_liblist_gam(self) -> str | None:
        path = self.rom_data_dir / 'liblist.gam'
        if not path.exists():
            return None

        for line in path.read_text().splitlines():
            if m := _GAMEDLL_RE.match(line):
                return m.group(1)

        return None

    def _maybe_init_config(self) -> None:
        user_config = self.rom_data_dir / 'userconfig.cfg'
        if not user_config.exists():
            user_config.write_text('exec gamepad.cfg\nexec custom.cfg\n')

        gamepad_config = self.rom_data_dir / 'gamepad.cfg'
        if not gamepad_config.exists():
            with resources.as_file(resources.files().joinpath('gamepad.cfg')) as gamepad_cfg:
                shutil.copy(gamepad_cfg, gamepad_config)

        config_dir = self.config_dir / self.rom.stem
        custom_config = config_dir / 'custom.cfg'
        custom_rom_config = self.rom_data_dir / 'custom.cfg'
        if not custom_config.exists():
            config_dir.mkdir(parents=True, exist_ok=True)
            custom_config.write_text('\n')
        if not custom_rom_config.exists():
            custom_rom_config.symlink_to(custom_config)

    def _maybe_init_save_dir(self) -> None:
        rom_save_dir = self.rom_data_dir / 'save'
        if not rom_save_dir.exists():
            save_dir = self.saves_dir / self.rom.stem
            save_dir.mkdir(parents=True, exist_ok=True)
            rom_save_dir.symlink_to(save_dir)
