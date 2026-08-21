from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Final

from batocera_common.paths import CONFIGS, SAVES
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

_SYSTEM_DIR: Final = Path('/usr/bin/sonic3-air')


@cached_dataclass
class Sonic3AIR(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'sonic3_air',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F8',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'Sonic3AIR'

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'sonic3-air'

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        config_file = _SYSTEM_DIR / 'config.json'
        oxygen_file = _SYSTEM_DIR / 'oxygenproject.json'
        config_dest_file = self.config_dir / 'config.json'
        oxygen_dest_file = self.config_dir / 'oxygenproject.json'
        settings_file = self.config_dir / 'settings.json'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not config_dest_file.exists():
            shutil.copy(config_file, config_dest_file)
        if not oxygen_dest_file.exists():
            shutil.copy(oxygen_file, oxygen_dest_file)

        # can't use json as the file is not compliant
        json_text = config_dest_file.read_text()
        json_text = json_text.replace('"SaveStatesDir":  "saves/states"', f'"SaveStatesDir":  "{self.saves_dir}"')

        current_resolution = json_text.split('"WindowSize": "')[1].split('"')[0]
        new_resolution = f'{self.resolution.width} x {self.resolution.height}'
        json_text = json_text.replace(f'"WindowSize": "{current_resolution}"', f'"WindowSize": "{new_resolution}"')
        config_dest_file.write_text(json_text)

        if settings_file.exists():
            settings_data = json.loads(settings_file.read_text())
            settings_data['Fullscreen'] = 1
        else:
            settings_data = {'Fullscreen': 1}

        settings_file.write_text(json.dumps(settings_data, indent=4))

        return Command(
            [_SYSTEM_DIR / 'sonic3air_linux'],
            env={
                'XDG_DATA_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
                'SDL_AUDIODRIVER': 'alsa',
            },
        )
