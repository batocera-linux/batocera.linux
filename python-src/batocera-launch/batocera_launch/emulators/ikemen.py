from __future__ import annotations

import json
import logging
import os
import stat
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypedDict

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from types import ModuleType

    from batocera_launch_wine import wine as wine_utils

_logger: Final = logging.getLogger(__name__)

_SYSTEM_BINARY: Final = Path('/usr/bin/ikemen')
# the engine a game may ship instead of the one batocera builds, cased any which way
_GAME_BINARY: Final = 'ikemen_go_linux'


class _PadConfig(TypedDict):
    Joystick: int
    Buttons: list[str]


_UNUSED_BUTTONS: Final = ['Not used'] * 14

_KEY_MAPPING: Final[list[_PadConfig]] = [
    {
        'Joystick': -1,
        'Buttons': [
            'UP',
            'DOWN',
            'LEFT',
            'RIGHT',
            'a',
            's',
            'd',
            'z',
            'x',
            'c',
            'RETURN',
            'f',
            'v',
            'q',
        ],
    },
    {
        'Joystick': -1,
        'Buttons': [
            'KP_8',
            'KP_5',
            'KP_4',
            'KP_6',
            'p',
            'LBRACKET',
            'RBRACKET',
            'SEMICOLON',
            'QUOTE',
            'BACKSLASH',
            'SLASH',
            'o',
            'l',
            'PERIOD',
        ],
    },
    {'Joystick': -1, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': -1, 'Buttons': list(_UNUSED_BUTTONS)},
]

_JOY_MAPPING: Final[list[_PadConfig]] = [
    {'Joystick': 0, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': 1, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': 2, 'Buttons': list(_UNUSED_BUTTONS)},
    {'Joystick': 3, 'Buttons': list(_UNUSED_BUTTONS)},
]


# the Buttons arrays above are positional, config.ini names those fourteen in order
_BUTTON_NAMES: Final = (
    'up',
    'down',
    'left',
    'right',
    'a',
    'b',
    'c',
    'x',
    'y',
    'z',
    'start',
    'd',
    'w',
    'menu',
)


def _nvidia_prime_environment() -> dict[str, str | Path]:
    """
    What a native game needs to draw on the nvidia card of a prime laptop: the offload
    the session sets for what it starts, and the driver named for vulkan. A windows game
    is given what any game run through wine is, see wine.nvidia_prime_environment.
    """
    if not Path('/var/tmp/nvidia.prime').exists():
        return {}

    # a native game is the 64bit build batocera ships, unlike one running in a prefix
    driver = '/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json'

    return {
        '__NV_PRIME_RENDER_OFFLOAD': '1',
        '__VK_LAYER_NV_optimus': 'NVIDIA_only',
        '__GLX_VENDOR_LIBRARY_NAME': 'nvidia',
        # VK_DRIVER_FILES is what named it before the loader renamed it
        'VK_ICD_FILENAMES': driver,
        'VK_DRIVER_FILES': driver,
        'VK_LAYER_PATH': '/usr/share/vulkan/explicit_layer.d',
    }


@cached_dataclass
class Ikemen(Emulator):
    """
    Ikemen engine code is pretty unstable, and each game can run different engine
    version. Some games are provided both ikemen linux bin && windows .exe, some other
    none. A game is run in the order it says what it is:

    1) an autorun.cmd is present -> the windows executable it names, through wine
    2) an ikemen_go_linux is in the game directory -> the linux binary it ships
    3) neither -> the ikemen batocera builds
    """

    needs_sdl_game_controller_config = True

    _runner: wine_utils.Runner | None = field(init=False, default=None)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'ikemen',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'menu': 'KEY_ESC'},
        }

    # a game keeps its config and its saves inside itself, so a squashed rom needs the overlay
    @property
    def needs_overlayfs(self) -> bool:
        return True

    @property
    def execution_path(self) -> Path | None:
        return self._game_dir

    @cached_property
    def _wine(self) -> ModuleType | None:
        """
        The wine utils, for a game that is a windows one: an autorun.cmd is what says it
        is, as it does for any wine rom. None when the game is a linux one, and when
        batocera-launch-wine is not installed, which is the case wherever wine is not
        built.
        """
        if not (self.rom / 'autorun.cmd').is_file():
            return None

        try:
            from batocera_launch_wine import wine
        except ImportError:
            _logger.warning('%s is a windows game, which needs a wine this build has not', self.rom)
            return None

        return wine

    @cached_property
    def _game_dir(self) -> Path:
        # the DIR= of the autorun.cmd when the game names one, the rom itself otherwise
        if (wine := self._wine) is None:
            return Path(self.rom)

        return wine.get_game_dir(Path(self.rom))

    @cached_property
    def _windows_exe(self) -> Path | None:
        if (wine := self._wine) is None:
            return None

        return wine.get_game_exe(Path(self.rom))

    @cached_property
    def _linux_binary(self) -> Path:
        """The engine provided by the game ships or the batocera system build."""
        binary = next((entry for entry in self._game_dir.glob('*') if entry.name.lower() == _GAME_BINARY), None)

        if binary is None or not binary.is_file():
            return _SYSTEM_BINARY

        if not os.access(binary, os.X_OK):
            try:
                binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except OSError as e:
                _logger.warning("%s can't be made executable (%s), running our own binary instead", binary, e)
                return _SYSTEM_BINARY

            if not os.access(binary, os.X_OK):
                _logger.warning('%s stayed non executable, running our own binary instead', binary)
                return _SYSTEM_BINARY

            _logger.info('made %s executable', binary)

        _logger.debug('linux binary: %s', binary)

        return binary

    async def configure(self) -> Command:
        save_dir = self._game_dir / 'save'
        game_exe = self._windows_exe
        scale_internal_resolution = self.config.get_bool('scale_internal_resolution')

        # since December 2024, ikemen use config.ini
        if (ini_config := save_dir / 'config.ini').is_file():
            self._write_ini_config(ini_config, scale_internal_resolution=scale_internal_resolution)
        elif (json_config := save_dir / 'config.json').is_file() or (
            game_exe is None and self._linux_binary == _SYSTEM_BINARY
        ):
            self._write_json_config(json_config, scale_internal_resolution=scale_internal_resolution)
        else:
            _logger.warning(
                '%s ships no save/config.ini nor save/config.json, leaving the controls to its own engine',
                self.rom,
            )

        if game_exe is None or (wine := self._wine) is None:
            return Command([self._linux_binary], env=_nvidia_prime_environment())

        return self._wine_command(wine, game_exe)

    def _wine_command(self, wine: ModuleType, game_exe: Path, /) -> Command:
        runner = wine.Runner('wine-proton', 'ikemen')
        self._runner = runner

        runner.create_or_update_prefix()

        runner.install_wine_trick('openal')
        runner.install_wine_trick('corefonts')

        # nvapi is nvidia only and an ikemen game never asks for it
        env = runner.get_environment()
        env.update(wine.display_environment())
        env.update(wine.dxvk_environment(runner))

        # ensure nvidia driver used for vulkan
        env.update(wine.nvidia_prime_environment())

        return Command(runner.game_command(game_exe), env=env)

    async def run(self) -> int:
        try:
            return await super().run()
        finally:
            # wine exits before the game, the rom may only be unmounted after it
            if self._runner is not None:
                self._runner.stop()

    def _write_json_config(self, config_path: Path, /, *, scale_internal_resolution: bool) -> None:
        conf: dict[str, object] = {}

        if config_path.is_file():
            try:
                conf = json.loads(config_path.read_text())
            except OSError, json.JSONDecodeError:
                # a config we can't read is left alone, the game's own paths live in it
                _logger.warning('%s could not be read, leaving it as it is', config_path)
                return

        # Joystick configuration is broken in 0.98.2 Linux, force keyboard and pad2key
        conf['KeyConfig'] = _KEY_MAPPING
        conf['JoystickConfig'] = _JOY_MAPPING
        conf['Fullscreen'] = True

        conf['FullscreenWidth'] = self.resolution.width
        conf['FullscreenHeight'] = self.resolution.height

        if scale_internal_resolution:
            conf['GameWidth'] = self.resolution.width
            conf['GameHeight'] = self.resolution.height

        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(conf, indent=2))

    def _write_ini_config(self, config_path: Path, /, *, scale_internal_resolution: bool) -> None:
        video = {
            'Fullscreen': '1',
            'WindowWidth': str(self.resolution.width),
            'WindowHeight': str(self.resolution.height),
        }

        if scale_internal_resolution:
            video['GameWidth'] = str(self.resolution.width)
            video['GameHeight'] = str(self.resolution.height)

        wanted: dict[str, dict[str, str]] = {'Video': video}

        for section, mapping in (('Keys', _KEY_MAPPING), ('Joystick', _JOY_MAPPING)):
            for player, player_config in enumerate(mapping, start=1):
                wanted[f'{section}_P{player}'] = {
                    'Joystick': str(player_config['Joystick']),
                    **dict(zip(_BUTTON_NAMES, player_config['Buttons'], strict=True)),
                }

        lowered = {
            section.lower(): {key.lower(): value for key, value in values.items()} for section, values in wanted.items()
        }

        original = config_path.read_text(encoding='utf-8-sig', errors='replace').splitlines()

        lines: list[str] = []
        values: dict[str, str] | None = None

        # only our keys are rewritten, in place, the rest the game keeps is its own
        for line in original:
            stripped = line.strip()

            if stripped.startswith('[') and stripped.endswith(']'):
                values = lowered.get(stripped[1:-1].lower())
            elif values and not stripped.startswith(';'):
                key, separator, _ = line.partition('=')
                if separator and (value := values.get(key.strip().lower())) is not None:
                    line = f'{key}= {value}'

            lines.append(line)

        config_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
