from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

from batocera_common.paths import HOME, ROMS, SAVES
from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class TGBDual(Core):
    @cached_property
    def _link_roms(self) -> list[tuple[Path, str]]:
        if self.system not in {'gb2players', 'gbc2players'}:
            return []

        default_save_system = 'gb' if self.system == 'gb2players' else 'gbc'
        roms: list[tuple[Path, str]] = []

        # If ROM file is a .gb2 text, retrieve the filenames
        if self.rom.suffix.lower() in {'.gb2', '.gbc2'}:
            with self.rom.open() as fp:
                for line in fp:
                    gb_multi_text = line.strip()
                    if gb_multi_text.lower().startswith('gb:'):
                        roms.append((ROMS / 'gb' / gb_multi_text[3:], 'gb'))
                    elif gb_multi_text.lower().startswith('gbc:'):
                        roms.append((ROMS / 'gbc' / gb_multi_text[4:], 'gbc'))
                    else:
                        roms.append((ROMS / self.system / gb_multi_text, default_save_system))
        else:
            # Otherwise fill in the list with the single game
            roms.append((self.rom, default_save_system))

        return roms

    @cached_property
    def rom_argument(self) -> str | Path | None:
        if len(self._link_roms) >= 2:
            return None

        return self.rom

    def get_command_arguments(self) -> list[str | Path] | None:
        if len(self._link_roms) < 2:
            return None

        return [self._link_roms[0][0], '--subsystem', 'gb_link_2p', self._link_roms[1][0]]

    def generate_special_configs(self) -> None:
        if self.config.get('sync_saves') != '1' or not self._link_roms:
            return

        save_roms = self._link_roms[:2]

        # Verifies all the save paths exist
        (SAVES / 'gb').mkdir(parents=True, exist_ok=True)
        (SAVES / 'gbc').mkdir(parents=True, exist_ok=True)
        (SAVES / 'gb2players').mkdir(parents=True, exist_ok=True)
        (SAVES / 'gbc2players').mkdir(parents=True, exist_ok=True)

        # Copies the saves if they exist
        for rom, save_system in save_roms:
            save_file = SAVES / save_system / f'{rom.stem}.srm'
            new_save_file = SAVES / self.system / f'{rom.stem}.srm'
            if save_file.exists():
                shutil.copy(save_file, new_save_file)

        # Generates a script to copy the saves back on exit
        script_dir = HOME / 'scripts' / 'gb2savesync'
        script_dir.mkdir(parents=True, exist_ok=True)
        script_file = script_dir / 'exitsync.sh'
        script_file.unlink(missing_ok=True)

        script_lines = [
            '#!/bin/bash\n',
            '#This script is created by the Game Boy link cable system to sync save files.\n',
            '#\n',
            '\n',
            'case $1 in\n',
            '   gameStop)\n',
            "       if [ $2 = 'gb2players' ] || [ $2 = 'gbc2players' ]\n",
            '       then\n',
        ]
        for rom, save_system in save_roms:
            save_file = SAVES / save_system / f'{rom.stem}.srm'
            new_save_file = SAVES / self.system / f'{rom.stem}.srm'
            script_lines.append(f'           cp "{new_save_file}" "{save_file}"\n')
        script_lines.extend(
            [
                '       fi\n',
                f'       rm {script_file}\n',
                '   ;;\n',
                'esac\n',
            ]
        )
        script_file.write_text(''.join(script_lines))
        script_file.chmod(script_file.stat().st_mode | 0o111)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Emulates two Game Boy units
        core_options.set('tgbdual_gblink_enable', 'enabled')
        # Displays the selected player screens
        core_options.set('tgbdual_single_screen_mp', 'both players')
        # Switches the screen layout
        core_options.set('tgbdual_screen_placement', 'left-right')
        # Switch Game Boy sound
        core_options.set('tgbdual_audio_output', 'Game Boy #1')
        # Switches the player screens
        core_options.set('tgbdual_switch_screens', 'normal')
