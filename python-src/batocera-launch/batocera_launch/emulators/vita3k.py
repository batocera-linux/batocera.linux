from __future__ import annotations

import logging
import platform
import re
import shutil
import subprocess
from typing import TYPE_CHECKING, Any, cast

import ruamel.yaml
import ruamel.yaml.util

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CACHE, CONFIGS, SAVES
from batocera_common.vulkan import (
    get_discrete_gpu_index,
    has_discrete_gpu,
    is_available as vulkan_is_available,
)
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_logger = logging.getLogger(__name__)

_PSVITA_SAVES = SAVES / 'psvita'


def _has_opengl_4_4_support() -> bool:
    # ARM systems only natively support OpenGL ES, not desktop OpenGL 4.4
    if 'arm' in platform.machine().lower() or 'aarch64' in platform.machine().lower():
        _logger.debug('ARM system detected. Desktop OpenGL 4.4 is not supported (only OpenGL ES is available).')
        return False

    try:
        res = subprocess.run(['glxinfo', '-B'], capture_output=True, text=True, timeout=2, check=False)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if 'OpenGL core profile version string' in line or 'OpenGL version string' in line:
                    match = re.search(
                        r'OpenGL (?:core profile )?version string:\s*([0-9]+)\.([0-9]+)', line, re.IGNORECASE
                    )
                    if match:
                        major, minor = int(match.group(1)), int(match.group(2))
                        return major > 4 or (major == 4 and minor >= 4)
    except Exception:
        _logger.debug('OpenGL 4.4 check failed or glxinfo not available', exc_info=True)

    return False


@cached_dataclass
class Vita3k(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'vita3k',
            'keys': {'exit': ['KEY_LEFTCTRL', 'KEY_F12']},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'vita3k'

    @property
    def needs_mouse(self) -> bool:
        # for touchscreen actions
        return self.config.get_bool('vita3k_show_pointer', True)

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        config_file = self.config_dir / 'config.yml'
        gui_configs = self.config_dir / 'gui-configs'
        ini_file = gui_configs / 'CurrentSettings.ini'

        _PSVITA_SAVES.mkdir(parents=True, exist_ok=True)

        # Migrate saves from the old layout, if present
        if (self.config_dir / 'ux0').is_dir():
            for item in self.config_dir.iterdir():
                if item.name not in ('data', 'lang', 'shaders-builtin') and item.is_dir():
                    shutil.move(item, _PSVITA_SAVES)

        self.config_dir.mkdir(parents=True, exist_ok=True)
        gui_configs.mkdir(parents=True, exist_ok=True)

        ini_config = CaseSensitiveConfigParser()
        if ini_file.is_file():
            ini_config.read(ini_file)
        if not ini_config.has_section('MainWindow'):
            ini_config.add_section('MainWindow')
        ini_config.set('MainWindow', 'warnAdminPrivileges', 'false')
        with ini_file.open('w') as configfile:
            # space_around_delimiters=False ensures it writes as key=value without spaces
            ini_config.write(configfile, space_around_delimiters=False)

        config: dict[str, Any] | None = None
        indent: int | None = None
        block_seq_indent: int | None = None
        if config_file.is_file():
            with config_file.open('r') as stream:
                config, indent, block_seq_indent = cast(
                    'tuple[dict[str, Any] | None, int | None, int | None]',
                    ruamel.yaml.util.load_yaml_guess_indent(stream),  # pyright: ignore
                )

        if config is None:
            config = {}
        if indent is None:
            indent = 2
        if block_seq_indent is None:
            block_seq_indent = 0

        config['pref-path'] = str(_PSVITA_SAVES)
        config['initial-setup'] = False
        config['boot-apps-full-screen'] = True
        config['validation-layer'] = False
        config['discord-rich-presence'] = False
        config['show-welcome'] = False
        config['check-for-updates-mode'] = 0
        config['log-level'] = 6  # None

        gfx_backend = self.config.get_str('vita3k_gfxbackend')
        _logger.debug('User selected graphics backend: %s', gfx_backend)

        use_vulkan = gfx_backend == 'Vulkan'
        if not use_vulkan:
            _logger.debug('OpenGL backend selected/default. Verifying if OpenGL 4.4 is supported...')
            if _has_opengl_4_4_support():
                _logger.debug('OpenGL 4.4 is supported on this system. Sticking with OpenGL.')
                config['backend-renderer'] = 'OpenGL'
            else:
                _logger.debug('OpenGL 4.4 is NOT supported. Attempting to fall back to Vulkan...')
                use_vulkan = True

        if use_vulkan:
            if vulkan_is_available():
                _logger.debug('Vulkan driver is available on the system.')
                config['backend-renderer'] = 'Vulkan'

                if has_discrete_gpu():
                    _logger.debug('A discrete GPU is available on the system. We will use that for performance')
                    discrete_index = get_discrete_gpu_index()
                    if discrete_index:
                        _logger.debug('Using Discrete GPU Index: %s for Vita3K', discrete_index)
                        config['gpu-idx'] = discrete_index
                    else:
                        _logger.debug("Couldn't get discrete GPU index")
                else:
                    _logger.debug('Discrete GPU is not available on the system. Using default.')
                    config['gpu-idx'] = 0
            else:
                _logger.debug('Vulkan requested or triggered as fallback, but the driver is not available.')
                config['backend-renderer'] = 'OpenGL'

        res_mult = float(self.config.get_str('vita3k_resolution', '1'))
        config['resolution-multiplier'] = int(res_mult) if res_mult.is_integer() else res_mult

        config['v-sync'] = self.config.get_bool('vita3k_vsync', True)
        config['anisotropic-filtering'] = self.config.get_int('vita3k_anisotropic', 1)
        config['screen-filter'] = self.config.get_str('vita3k_filter', 'Bilinear')
        config['disable-surface-sync'] = self.config.get_bool('vita3k_surface', True)
        config['async-pipeline-compilation'] = self.config.get_bool('vita3k_sync', True)
        config['fullscreen_hd_res_pixel_perfect'] = self.config.get_bool('vita3k_hd_pixel', False)
        config['high-accuracy'] = self.config.get_bool('vita3k_accuracy', False)
        config['texture-cache'] = self.config.get_bool('vita3k_texture', True)
        config['shader-cache'] = self.config.get_bool('vita3k_shader', True)
        config['memory-mapping'] = self.config.get_str('vita3k_mapping', 'double-buffer')
        config['sys-lang'] = self.config.get_int('vita3k_system_language', 1)

        # Vita3K is fussy over its yml file; match its own formatting as closely as
        # possible, since 'vectors' otherwise cause formatting issues on its side.
        yaml = ruamel.yaml.YAML()
        yaml.explicit_start = True
        yaml.explicit_end = True
        yaml.indent(mapping=indent, sequence=indent, offset=block_seq_indent)

        with config_file.open('w') as fp:
            yaml.dump(config, fp)  # pyright: ignore

        # Simplify the rom name to whatever's inside the outermost [...] (its title id)
        begin, end = self.rom.stem.find('['), self.rom.stem.rfind(']')
        simple_rom_name = self.rom.stem[begin + 1 : end]

        # Because of the yml formatting, we don't let Vita3K rewrite it: -w and -f
        # keep it from re-writing the config / prompting in its GUI, so an already
        # installed game loads straight away.
        args: list[str | Path] = ['/usr/bin/vita3k/Vita3K', '-F', '-w', '-f', '-c', config_file]
        if (_PSVITA_SAVES / 'ux0' / 'app' / simple_rom_name).is_dir():
            args += ['-r', simple_rom_name]
        else:
            # not installed yet - open the menu
            args.append(self.rom)

        # use x11 for now to avoid crashes on certain games
        return Command(
            args,
            env={
                'SDL_JOYSTICK_HIDAPI': '0',
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_DATA_HOME': SAVES,
                'XDG_CACHE_HOME': CACHE,
                'QT_QPA_PLATFORM': 'xcb',
                'SDL_VIDEODRIVER': 'x11',
            },
        )
