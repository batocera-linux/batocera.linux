from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import ROMS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from pathlib import Path


@cached_dataclass
class IORTCW(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'iortcw',
            'keys': {
                'exit': ['KEY_LEFTALT', 'KEY_F4'],
                'menu': 'KEY_ESC',
                'pause': 'KEY_ESC',
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F9',
            },
        }

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    @cached_property
    def config_file(self) -> Path:
        return self.roms_dir / 'main' / 'wolfconfig.cfg'

    async def configure(self) -> Command:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        filtering = self.config.get_str('iortcw_filtering', '2')
        aa = self.config.get_str('iortcw_aa', '0')

        options_to_set = {
            'seta r_mode': '-1',
            'seta r_noborder': '1',
            'seta r_fullscreen': '1',
            'seta r_allowResize': '0',
            'seta r_centerWindow': '1',
            'seta r_inGameVideo': '1',
            'seta r_customheight': str(self.resolution.height),
            'seta r_customwidth': str(self.resolution.width),
            'seta in_joystick': '1',
            'seta in_joystickUseAnalog': '1',
            'bind PAD0_A': '+moveup',
            'bind PAD0_X': '+movedown',
            'bind PAD0_Y': '+useitem',
            'bind PAD0_B': '+activate',
            'bind PAD0_LEFTSHOULDER': 'weapnext',
            'bind PAD0_RIGHTSHOULDER': 'weapprev',
            'bind PAD0_LEFTSTICK_LEFT': '+moveleft',
            'bind PAD0_LEFTSTICK_RIGHT': '+moveright',
            'bind PAD0_LEFTSTICK_UP': '+forward',
            'bind PAD0_LEFTSTICK_DOWN': '+back',
            'bind PAD0_RIGHTSTICK_LEFT': '+left',
            'bind PAD0_RIGHTSTICK_RIGHT': '+right',
            'bind PAD0_RIGHTSTICK_UP': '+lookup',
            'bind PAD0_RIGHTSTICK_DOWN': '+lookdown',
            'bind PAD0_LEFTTRIGGER': '+speed',
            'bind PAD0_RIGHTTRIGGER': '+attack',
            'seta cl_renderer': self.config.get_str('iortcw_api', 'opengl1'),
            'seta r_swapInterval': self.config.get_bool('iortcw_vsync', return_values=('1', '0')),
            'seta com_maxfps': self.config.get_str('iortcw_fps', '60'),
            'seta r_ext_texture_filter_anisotropic': '0' if filtering == '2' else '1',
            'seta r_ext_max_anisotropy': filtering,
            'seta r_ext_multisample': aa,
            'seta r_ext_framebuffer_multisample': aa,
            'seta com_introplayed': self.config.get_bool('iortcw_skip_video', return_values=('1', '0')),
            'seta cl_language': self.config.get_str('iortcw_language', '0'),
        }

        self._update_config_file(options_to_set)

        # iortcw looks for roms in home + /iortcw
        return Command(
            ['/usr/bin/iortcw/iowolfsp'],
            env={'XDG_DATA_HOME': ROMS},
        )

    def _update_config_file(self, options_to_set: dict[str, str], /) -> None:
        if self.config_file.is_file():
            lines = self.config_file.read_text(encoding='utf-8').splitlines(keepends=True)

            for key, value in options_to_set.items():
                option_line = f'{key} "{value}"\n'
                if any(key in line for line in lines):
                    lines = [option_line if key in line else line for line in lines]
                else:
                    lines.append(option_line)

            self.config_file.write_text(''.join(lines), encoding='utf-8')
        else:
            self.config_file.write_text(
                ''.join(f'{key} "{value}"\n' for key, value in options_to_set.items()),
                encoding='utf-8',
            )
