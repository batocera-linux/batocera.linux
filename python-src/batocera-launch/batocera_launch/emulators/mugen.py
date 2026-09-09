from __future__ import annotations

import os
import subprocess
from pathlib import Path

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

# Old MUGEN builds use different key codes and cap out at 640x480; newer ones
# use SDL scancodes and follow the chosen resolution.
_PRESETS: dict[str, dict[str, dict[str, str]]] = {
    'old': {
        'Video Win': {'FullScreen': '1', 'Width': '640', 'Height': '480', 'DXmode': 'Hardware'},
        'Input': {'P1.UseKeyboard': '1', 'P2.UseKeyboard': '1', 'P1.Joystick.type': '0', 'P2.Joystick.type': '0'},
        # key mappings for evmapy
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
        'Input': {'P1.UseKeyboard': '1', 'P2.UseKeyboard': '1', 'P1.Joystick.type': '0', 'P2.Joystick.type': '0'},
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


def _mugen_version(settings_path: Path, /) -> str:
    for line in settings_path.read_text(encoding='utf-8-sig').splitlines():
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']') and stripped[1:-1] == 'Video Win':
            return 'old'

    return 'new'


def _merge_ini(lines: list[str], sections_to_update: dict[str, dict[str, str]], /) -> list[str]:
    new_config: list[str] = []
    processed_sections: set[str] = set()
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith(';'):
            new_config.append(line)
            i += 1
            continue

        if stripped_line.startswith('[') and stripped_line.endswith(']'):
            current_section = stripped_line[1:-1]

            if current_section in processed_sections:
                # a duplicate section header - drop it and its body entirely
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

                    if stripped_line.startswith('['):
                        break

                    if not stripped_line or stripped_line.startswith(';'):
                        new_config.append(line)
                        i += 1
                        continue

                    if '=' in stripped_line:
                        key = stripped_line.split('=')[0].strip()
                        if key in sections_to_update[current_section]:
                            leading_space = line[: len(line) - len(line.lstrip())]
                            new_config.append(f'{leading_space}{key} = {sections_to_update[current_section][key]}\n')
                            updated_keys.add(key)
                        else:
                            new_config.append(line)
                    else:
                        new_config.append(line)
                    i += 1

                for key, value in sections_to_update[current_section].items():
                    if key not in updated_keys:
                        new_config.append(f'{key} = {value}\n')
                continue

        else:
            new_config.append(line)
            i += 1

    for section, values in sections_to_update.items():
        if section not in processed_sections:
            new_config.append(f'\n[{section}]\n')
            for key, value in values.items():
                new_config.append(f'{key} = {value}\n')

    return new_config


@cached_dataclass
class Mugen(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'mugen',
            'keys': {'exit': ['/usr/bin/batocera-wine mugen stop']},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        # no bezels: the rendered display matches the screen resolution
        return 16 / 9

    async def configure(self) -> Command:
        settings_path = self.rom / 'data' / 'mugen.cfg'
        settings_path.parent.mkdir(parents=True, exist_ok=True)

        if not settings_path.exists():
            raise BatoceraException(f'Configuration file not found: {settings_path}')

        version = _mugen_version(settings_path)
        sections_to_update = _PRESETS[version]
        if version == 'new':
            sections_to_update = {
                **sections_to_update,
                'Video': {
                    'FullScreen': '1',
                    'Width': str(self.resolution.width),
                    'Height': str(self.resolution.height),
                },
                'Config': {'GameWidth': str(self.resolution.width), 'GameHeight': str(self.resolution.height)},
            }

        lines = settings_path.read_text(encoding='utf-8-sig').splitlines(keepends=True)
        new_config = _merge_ini(lines, sections_to_update)
        settings_path.write_text(''.join(new_config), encoding='utf-8-sig')

        # Don't use a virtual desktop - fixes handhelds with rotated displays
        subprocess.run(['/usr/bin/batocera-settings-set', 'mugen.virtual_desktop', '0'], check=True)

        environment: dict[str, str | Path] = {}

        if Path('/var/tmp/nvidia.prime').exists():
            for variable_name in ('__NV_PRIME_RENDER_OFFLOAD', '__VK_LAYER_NV_optimus', '__GLX_VENDOR_LIBRARY_NAME'):
                os.environ.pop(variable_name, None)

            environment.update(
                VK_ICD_FILENAMES='/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json',
                VK_LAYER_PATH='/usr/share/vulkan/explicit_layer.d',
            )

        return Command(['batocera-wine', 'mugen', 'play', self.rom], env=environment)
