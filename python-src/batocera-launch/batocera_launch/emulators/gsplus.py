from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BIOS, CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path

_FLOPPY_SUFFIXES: Final = {'.dsk', '.do', '.nib'}

_DSK_SETTINGS: Final = {
    'bram1[00]': '00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00',
    'bram1[10]': '00 00 07 06 02 01 01 00 00 00 0f 06 06 00 05 06',
    'bram1[20]': '01 00 00 00 00 00 00 01 06 00 00 00 03 02 02 02',
    'bram1[30]': '00 00 00 00 00 00 00 00 00 00 01 02 03 04 05 06',
    'bram1[40]': '07 00 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d',
    'bram1[50]': '0e 0f ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[60]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[70]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[80]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[90]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[a0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[b0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[c0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[d0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[e0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[f0]': 'ff ff ff ff ff ff ff ff ff ff ff ff fe 17 54 bd',
    'bram3[00]': '00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00',
    'bram3[10]': '00 00 07 06 02 01 01 00 00 00 0f 06 00 00 05 06',
    'bram3[20]': '01 00 00 00 00 00 00 01 00 00 00 00 05 02 02 00',
    'bram3[30]': '00 00 2d 2d 00 00 00 00 00 00 02 02 02 06 08 00',
    'bram3[40]': '01 02 03 04 05 06 07 0a 00 01 02 03 04 05 06 07',
    'bram3[50]': '08 09 0a 0b 0c 0d 0e 0f 00 00 ff ff ff ff ff ff',
    'bram3[60]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[70]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[80]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[90]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[a0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[b0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[c0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[d0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[e0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram3[f0]': 'ff ff ff ff ff ff ff ff ff ff ff ff 05 cf af 65',
    'g_limit_speed': '1',
}

_PO_SETTINGS: Final = {
    'bram1[00]': '00 00 00 01 00 00 0d 06 02 01 01 00 01 00 00 00',
    'bram1[10]': '00 00 07 06 02 01 01 00 00 00 0f 06 06 00 05 06',
    'bram1[20]': '01 00 00 00 00 00 00 01 00 00 00 00 03 02 02 02',
    'bram1[30]': '00 00 00 00 00 00 00 00 08 00 01 02 03 04 05 06',
    'bram1[40]': '07 0a 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d',
    'bram1[50]': '0e 0f ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[60]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[70]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[80]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[90]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[a0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[b0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[c0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[d0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[e0]': 'ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff',
    'bram1[f0]': 'ff ff ff ff ff ff ff ff ff ff ff ff 13 24 b9 8e',
    'bram3[00]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[10]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[20]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[30]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[40]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[50]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[60]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[70]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[80]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[90]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[a0]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[b0]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[c0]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[d0]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[e0]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'bram3[f0]': '00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00',
    'g_limit_speed': '2',
}


@cached_dataclass
class GSplus(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'gsplus',
            'keys': {
                'exit': ['KEY_LEFTSHIFT', 'KEY_F6'],
                'menu': 'KEY_F4',
                'pause': 'KEY_F4',
            },
        }

    @cached_property
    def config_dir(self) -> Path:
        # The GSplus binary looks in this mixed-case path (see 001-paths.patch).
        return CONFIGS / 'GSplus'

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_dir / 'config.txt'

        config = KeyValueConfig(' ')
        config.read(config_file)

        if self.rom.suffix.lower() in _FLOPPY_SUFFIXES:
            config['s6d1'] = str(self.rom)
            config['s5d1'] = ''
            config['s7d1'] = ''
            settings = _DSK_SETTINGS
        else:
            config['s7d1'] = str(self.rom)
            config['s5d1'] = ''
            config['s6d1'] = ''
            settings = _PO_SETTINGS

        for key, value in settings.items():
            config[key] = value

        config['g_cfg_rom_path'] = str(BIOS / self.config.get_str('gsplus_bios_filename', 'ROM.03'))
        config.write(config_file)

        return Command(['GSplus', '-fullscreen'])
