from __future__ import annotations

import logging
import shlex
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property

from ..command import Command
from ..emulator import Emulator
from ..exceptions import BatoceraException

if TYPE_CHECKING:
    from types import ModuleType

    from batocera_launch_wine import wine as wine_utils

    from ..types import HotkeysContext

_logger = logging.getLogger(__name__)


def get_mugen_version(settings_path: Path) -> str:
    version = 'new'
    with settings_path.open('r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith('[') and stripped_line.endswith(']'):
            current_section = stripped_line[1:-1]
            if current_section == 'Video Win':
                version = 'old'
                break

    return version


@cached_dataclass
class Mugen(Emulator):
    """
    Runs a mugen game through wine, in the prefix batocera-wine kept for the system.
    The game is a windows one and says what to run in its autorun.cmd, as any wine rom
    does, and its mugen.cfg is rewritten at each start for the screen and the controls.
    """

    _runner: wine_utils.Runner | None = field(init=False, default=None)

    # mugen.cfg is rewritten at each start, so a squashfs rom needs a writable overlay
    @property
    def needs_overlayfs(self) -> bool:
        return True

    @cached_property
    def _wine(self) -> ModuleType:
        try:
            from batocera_launch_wine import wine
        except ImportError as e:
            raise BatoceraException('mugen games run through wine, which this build has not') from e

        return wine

    def _prepare(self) -> wine_utils.Runner:
        if (runner := self._runner) is None:
            # mugen only ever runs on wine-tkg, see es_systems.yml
            self._runner = runner = self._wine.Runner.default('mugen')

        return runner

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        # closing the wineserver of the prefix is what closes mugen.exe
        runner = self._prepare()

        return {
            'name': 'mugen',
            'keys': {
                'exit': f'WINEPREFIX={shlex.quote(str(runner.prefix_dir))} {shlex.quote(str(runner.wineserver))} -k'
            },
        }

    # No bezels as the rendered display matches the screen resolution
    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @property
    def execution_path(self) -> Path | None:
        return self._wine.get_game_dir(Path(self.rom))

    async def run(self) -> int:
        try:
            return await super().run()
        finally:
            # wine exits before the game, and being here this runs on a kill too
            if self._runner is not None:
                self._runner.stop()

    async def configure(self) -> Command:
        self._write_config()

        runner = self._prepare()
        runner.create_or_update_prefix()

        # some mugen games need it for their sound to come out at all
        runner.install_wine_trick('openal')

        game_exe = self._wine.get_game_exe(Path(self.rom))

        # nvapi is nvidia only and mugen never asks for it, batocera-wine left it off too
        environment = runner.get_environment()
        environment.update(self._wine.display_environment())
        environment.update(self._wine.dxvk_environment(runner))

        # Ensure NVIDIA driver is used for Vulkan (if applicable)
        environment.update(self._wine.nvidia_prime_environment())

        return Command(runner.game_command(game_exe), env=environment)

    @cached_property
    def _presets(self) -> dict[str, dict[str, dict[str, str]]]:
        # Define the settings we want to update
        return {
            'old': {
                # old mugen version don't have same key mapping value and is 640x480 max
                'Video Win': {'FullScreen': '1', 'Width': '640', 'Height': '480', 'DXmode': 'Hardware'},
                'Input': {
                    'P1.UseKeyboard': '1',
                    'P2.UseKeyboard': '1',
                    'P1.Joystick.type': '0',
                    'P2.Joystick.type': '0',
                },
                # Define the key mappings for evmapy
                'P1 Keys': {
                    'Jump': '200',
                    'Crouch': '208',
                    'Left': '203',
                    'Right': '205',
                    'A': '51',
                    'B': '52',
                    'C': '53',
                    'X': '38',
                    'Y': '39',
                    'Z': '40',
                    'Start': '28',
                },
                'P2 Keys': {
                    'Jump': '17',
                    'Crouch': '31',
                    'Left': '30',
                    'Right': '32',
                    'A': '33',
                    'B': '34',
                    'C': '35',
                    'X': '19',
                    'Y': '20',
                    'Z': '21',
                    'Start': '22',
                },
            },
            'new': {
                'Video': {
                    'FullScreen': '1',
                    'Width': str(self.resolution.width),
                    'Height': str(self.resolution.height),
                },
                'Config': {
                    'GameWidth': str(self.resolution.width),
                    'GameHeight': str(self.resolution.height),
                },
                'Input': {
                    'P1.UseKeyboard': '1',
                    'P2.UseKeyboard': '1',
                    'P1.Joystick.type': '0',
                    'P2.Joystick.type': '0',
                },
                # Define the key mappings for evmapy
                'P1 Keys': {
                    'Jump': '273',
                    'Crouch': '274',
                    'Left': '276',
                    'Right': '275',
                    'A': '44',
                    'B': '46',
                    'C': '47',
                    'X': '108',
                    'Y': '59',
                    'Z': '39',
                    'Start': '13',
                },
                'P2 Keys': {
                    'Jump': '119',
                    'Crouch': '115',
                    'Left': '97',
                    'Right': '100',
                    'A': '102',
                    'B': '103',
                    'C': '104',
                    'X': '114',
                    'Y': '116',
                    'Z': '121',
                    'Start': '117',
                },
            },
        }

    def _write_config(self) -> None:
        settings_path = self.rom / 'data' / 'mugen.cfg'
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        if not settings_path.exists():
            raise BatoceraException(f'Configuration file not found: {settings_path}')

        mugen_version = get_mugen_version(settings_path)
        sections_to_update = self._presets[mugen_version]

        _logger.debug('%s is a %s mugen', settings_path, mugen_version)

        with settings_path.open('r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        new_config: list[str] = []
        current_section = None
        processed_sections: set[str] = set()
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            # Keep empty lines and comments as they are
            if not stripped_line or stripped_line.startswith(';'):
                new_config.append(line)
                i += 1
                continue

            # Check for section headers
            if stripped_line.startswith('[') and stripped_line.endswith(']'):
                current_section = stripped_line[1:-1]

                # Skip if we've already processed this section
                if current_section in processed_sections:
                    i += 1
                    continue

                new_config.append(line)
                processed_sections.add(current_section)
                i += 1

                if current_section in sections_to_update:
                    updated_keys: set[str] = set()
                    while i < len(lines):
                        line = lines[i]
                        stripped_line = line.strip()

                        # End of section
                        if stripped_line.startswith('['):
                            break

                        if not stripped_line or stripped_line.startswith(';'):
                            new_config.append(line)
                            i += 1
                            continue

                        # Process key-value pairs
                        if '=' in stripped_line:
                            key = stripped_line.split('=')[0].strip()
                            if key in sections_to_update[current_section]:
                                # Use the new value
                                leading_space = line[: len(line) - len(line.lstrip())]
                                new_config.append(
                                    f'{leading_space}{key} = {sections_to_update[current_section][key]}\n'
                                )
                                updated_keys.add(key)
                            else:
                                # Keep the original line if we're not updating the key
                                new_config.append(line)
                        else:
                            # Keep any other lines in the section also
                            new_config.append(line)
                        i += 1

                    # Add any new keys that weren't in the original section
                    if updated_keys != set(sections_to_update[current_section].keys()):
                        for key, value in sections_to_update[current_section].items():
                            if key not in updated_keys:
                                new_config.append(f'{key} = {value}\n')
                    continue

            else:
                new_config.append(line)
                i += 1

        # Add any sections that didn't exist in the original file
        for section, values in sections_to_update.items():
            if section not in processed_sections:
                new_config.append(f'\n[{section}]\n')
                for key, value in values.items():
                    new_config.append(f'{key} = {value}\n')

        # Save the configuration
        with settings_path.open('w', encoding='utf-8-sig') as f:
            f.writelines(new_config)
