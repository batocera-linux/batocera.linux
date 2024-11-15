from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class MugenGenerator(Generator):
    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "mugen",
            "keys": {"exit": ["KEY_ESC"]}
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)

        # Define the key mappings for evmapy
        p1_keys = {
            "Jump": "273",
            "Crouch": "274",
            "Left": "276",
            "Right": "275",
            "A": "44",
            "B": "46",
            "C": "47",
            "X": "108",
            "Y": "59",
            "Z": "39",
            "Start": "13"
        }

        p2_keys = {
            "Jump": "119",
            "Crouch": "115",
            "Left": "97",
            "Right": "100",
            "A": "102",
            "B": "103",
            "C": "104",
            "X": "114",
            "Y": "116",
            "Z": "121",
            "Start": "117"
        }

        settings_path = rom_path / "data" / "mugen.cfg"
        mkdir_if_not_exists(settings_path.parent)

        if not settings_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {settings_path}")

        # Define the settings we want to update
        sections_to_update = {
            "Video": {
                "FullScreen": "1",
                "Width": str(gameResolution['width']),
                "Height": str(gameResolution['height'])
            },
            "Config": {
                "GameWidth": str(gameResolution['width']),
                "GameHeight": str(gameResolution['height'])
            },
            "Input": {
                "P1.UseKeyboard": "1",
                "P2.UseKeyboard": "1",
                "P1.Joystick.type": "0",
                "P2.Joystick.type": "0"
            },
            "P1 Keys": p1_keys,
            "P2 Keys": p2_keys
        }

        with settings_path.open("r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        new_config = []
        current_section = None
        processed_sections = set()
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
                    updated_keys = set()
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
                                leading_space = line[:len(line) - len(line.lstrip())]
                                new_config.append(f"{leading_space}{key} = {sections_to_update[current_section][key]}\n")
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
                                new_config.append(f"{key} = {value}\n")
                    continue

            else:
                new_config.append(line)
                i += 1

        # Add any sections that didn't exist in the original file
        for section, values in sections_to_update.items():
            if section not in processed_sections:
                new_config.append(f"\n[{section}]\n")
                for key, value in values.items():
                    new_config.append(f"{key} = {value}\n")

        # Save the configuration
        with settings_path.open("w", encoding="utf-8-sig") as f:
            f.writelines(new_config)
        
        # Foce use of virtual desktop
        subprocess.run(['/usr/bin/batocera-settings-set', 'mugen.virtual_desktop', '1'], check=True)

        environment={}

        # Ensure NVIDIA driver is used for Vulkan (if applicable)
        if Path("/var/tmp/nvidia.prime").exists():
            variables_to_remove = ["__NV_PRIME_RENDER_OFFLOAD", "__VK_LAYER_NV_optimus", "__GLX_VENDOR_LIBRARY_NAME"]
            for variable_name in variables_to_remove:
                if variable_name in os.environ:
                    del os.environ[variable_name]

            environment.update({
                "VK_ICD_FILENAMES": "/usr/share/vulkan/icd.d/nvidia_icd.x86_64.json",
                "VK_LAYER_PATH": "/usr/share/vulkan/explicit_layer.d"
            })

        commandArray = ["batocera-wine", "mugen", "play", str(rom_path)]
        
        return Command.Command(
            array=commandArray,
            env=environment
        )

    # No bezels are the rendered display matches the screen resolution
    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
