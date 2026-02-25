from __future__ import annotations

import shutil
from typing import Final

from configobj import ConfigObj

from batocera_common.paths import CONFIGS, ROMS
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property

_CONFIG_DIR: Final = CONFIGS / 'cgenius'
_CONFIG_FILE: Final = _CONFIG_DIR / 'cgenius.cfg'
_ROM_DIR: Final = ROMS / 'cgenius'

_CONTROLLER_MAPPING: Final = {
    'a': 'Fire',
    'b': 'Jump',
    'pageup': 'Camlead',
    'x': 'Status',
    'y': 'Pogo',
    'pagedown': 'Run',
    'up': 'Up',
    'down': 'Down',
    'left': 'Left',
    'right': 'Right',
}


@cached_dataclass
class CGenius(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'cgenius',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F6',
                'restore_state': 'KEY_F9',
            },
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9 if self.config.get('cgenius_aspect') in {'16:9', '16:10'} else 4 / 3

    async def configure(self) -> Command:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if _CONFIG_FILE.exists():
            config = ConfigObj(infile=str(_CONFIG_FILE))
        else:
            config = ConfigObj()
            config.filename = str(_CONFIG_FILE)

        if 'FileHandling' not in config:
            config['FileHandling'] = {}
        config['FileHandling']['EnableLogfile'] = 'false'
        config['FileHandling']['SearchPath1'] = str(_ROM_DIR)
        config['FileHandling']['SearchPath2'] = str(_ROM_DIR / 'games')

        if 'Video' not in config:
            config['Video'] = {}
        config['Video']['aspect'] = self.config.get_str('cgenius_aspect', '4:3')
        config['Video']['fullscreen'] = 'false'
        config['Video']['integerScaling'] = 'false'
        config['Video']['filter'] = self.config.get_str('cgenius_filter', 'none')
        config['Video']['OGLfilter'] = self.config.get_str('cgenius_quality', 'nearest')

        match self.config.get('cgenius_render'):
            case '240':
                game_width, game_height = '320', '240'
            case '360':
                game_width, game_height = '640', '360'
            case '480':
                game_width, game_height = '640', '480'
            case _:
                game_width, game_height = '320', '200'

        config['Video']['gameWidth'] = game_width
        config['Video']['gameHeight'] = game_height
        config['Video']['ShowCursor'] = self.config.get_str('cgenius_cursor', 'false')

        for controller in self.controllers[:4]:
            input_section = f'input{controller.index}'
            if input_section not in config:
                config[input_section] = {}

            for controller_input in controller.inputs.values():
                if (action := _CONTROLLER_MAPPING.get(controller_input.name)) is None:
                    continue

                if controller_input.type == 'hat':
                    binding = f'Joy{controller.index}-H{controller_input.value}'
                else:
                    binding = f'Joy{controller.index}-{controller_input.type[0].upper()}{controller_input.id}'

                config[input_section][action] = binding

        config.write()
        shutil.copy(_CONFIG_FILE, _ROM_DIR)

        rom_dir = self.rom.parent
        if rom_dir.is_relative_to(_ROM_DIR):
            rom_dir = rom_dir.relative_to(_ROM_DIR)

        return Command(['CGeniusExe', f'dir="{rom_dir}"'], env={'SDL_JOYSTICK_HIDAPI': '0'})
