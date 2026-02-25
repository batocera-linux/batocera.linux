from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class BStone(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'bstone',
            'keys': {
                'exit': 'KEY_F10',
                'save_state': 'KEY_F2',
                'restore_state': 'KEY_F3',
                'menu': 'KEY_ESC',
                'screenshot': 'KEY_F5',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'bstone'

    @cached_property
    def in_game_ratio(self) -> float:
        if self.config.get_bool('bstone_widescreen') and self.config.get_bool('bstone_ui_stretched'):
            return 16 / 9

        return 4 / 3

    def _update_or_create_config(self) -> None:
        config_lines: list[str] = []

        config_lines.append(f'vid_width "{self.resolution.width}"\n')
        config_lines.append(f'vid_height "{self.resolution.height}"\n')

        # Configuration options
        config_lines.append(f'vid_is_widescreen "{1 if self.config.get_bool("bstone_widescreen") else 0}"\n')
        config_lines.append(f'vid_is_vsync "{1 if self.config.get_bool("bstone_vsync") else 0}"\n')
        config_lines.append(f'vid_is_ui_stretched "{1 if self.config.get_bool("bstone_ui_stretched") else 0}"\n')

        # Handle existing file or create a new file
        config_file = self.config_dir / 'bstone_config.txt'
        if config_file.exists():
            existing_lines = []
            with config_file.open('r') as f:
                existing_lines = f.readlines()

            with config_file.open('w') as f:
                for line in config_lines:
                    # Check for a match in the existing lines
                    match = False
                    for i, existing_line in enumerate(existing_lines):
                        if line.split('"')[0] in existing_line:
                            existing_lines[i] = line
                            match = True
                            break

                    # If there was no match, add to the config
                    if not match:
                        existing_lines.append(line)

                f.writelines(existing_lines)

        else:
            # Create new file with all config lines
            with config_file.open('w') as f:
                f.writelines(config_lines)

    async def configure(self) -> Command:
        self._update_or_create_config()

        rom_dir = self.rom.parent

        filename_to_flag = {
            'audiohed.bs1': '--aog_sw',
            'audiohed.bs6': '--aog',
            'audiohed.vsi': '--ps',
        }

        version_flags: set[str] = set()
        for file in rom_dir.iterdir():
            if file.is_file() and (version_flag := filename_to_flag.get(file.name.lower())) is not None:
                version_flags.add(version_flag)

        return Command(
            ['/usr/bin/bstone', '--profile_dir', self.config_dir, '--data_dir', rom_dir, *version_flags],
            env={'SDL_JOYSTICK_HIDAPI': '0'},
        )
