from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveRawConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS
from batocera_launch import Command, Emulator, HotkeysContext

if TYPE_CHECKING:
    from io import TextIOWrapper
    from pathlib import Path

# Map each core binary to the vicerc section name it uses for its settings
_SYSTEM_CORE_MAP: Final = {
    'x64': 'C64',
    'x64dtv': 'C64DTV',
    'xplus4': 'PLUS4',
    'xscpu64': 'SCPU64',
    'xvic': 'VIC20',
    'xpet': 'PET',
}

# Map each core to its emulated video chip(s) as documented in the manual
_CORE_CHIP_MAP: Final = {
    'C64': ['VICII'],
    'C64DTV': ['VICII'],
    'PLUS4': ['TED'],
    'SCPU64': ['VICII'],
    'VIC20': ['VIC'],
    'PET': ['Crtc'],
    'C128': ['VICII', 'VDC'],
}

# inputtype:
# 0      axis
# 1      button
# 2      hat
# 3      ball
#
# Note that each axis has 2 inputindex entries and each hat has 4.
#
# action [action_parameters]:
# 0               none
# 1 port pin      joystick (pin: 1/2/4/8/16/32/64/128/256/512/1024/2048 = u/d/l/r/fire(A)/fire2(B)/fire3(X)/Y/LB/RB/select/start)
# 2 row col       keyboard
# 3               map
# 4               UI activate
# 5 path&to&item  UI function
# 6 pot axis      joystick (pot: 1/2/3/4 = x1/y1/x2/y2)
_VICE_JOYSTICK: Final = {
    'up': '# 2 0 1 / 1',
    'down': '# 2 1 1 / 2',
    'left': '# 2 2 1 / 4',
    'right': '# 2 3 1 / 8',
    'start': '# 1 ? 0',
    'select': '# 1 ? 4',
    'hotkey': '# 1 ? 5 Quit emulator',
    'a': '# 1 ? 1 / 32',  # Space
    'b': '# 1 ? 1 / 16',  # Fire button
    'x': '# 1 ? 0',
    'y': '# 1 ? 1 / 64',  # Y
    'pageup': '# 1 ? 0',
    'pagedown': '# 1 ? 0',
    'l1': '# 1 ? 0',
    'r1': '# 1 ? 0',
}


class _EqualsSpaceRemover:
    def __init__(self, new_output_file: TextIOWrapper) -> None:
        self.output_file = new_output_file

    def write(self, what: str) -> None:
        self.output_file.write(what.replace(' = ', '=', 1))


@cached_dataclass
class Vice(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {'name': 'vice', 'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']}}

    def _write_vicerc(self) -> Path:
        vicerc = self.config_dir / 'sdl-vicerc'
        joymap = self.config_dir / 'sdl-joymap.vjm'

        config = CaseSensitiveRawConfigParser(interpolation=None)
        if vicerc.exists():
            config.read(vicerc)

        system_core = _SYSTEM_CORE_MAP.get(self.core, 'C128')

        if not config.has_section(system_core):
            config.add_section(system_core)

        config.set(system_core, 'SaveResourcesOnExit', '0')
        config.set(system_core, 'SoundDeviceName', 'alsa')

        # Determine border and aspect values
        if self.config.get_bool('noborder'):
            aspect_mode = '0'
            border_mode = '3'
        else:
            aspect_mode = '2'
            border_mode = '0'

        # Dynamically apply settings to the correct video chip(s)
        chips = _CORE_CHIP_MAP.get(system_core, ['VICII'])
        for chip in chips:
            # Fullscreen configurations
            config.set(system_core, f'{chip}Fullscreen', '1')
            config.set(system_core, f'{chip}FullscreenMode', '0')  # 0 = Use desktop resolution

            # Aspect Ratio Mode
            config.set(system_core, f'{chip}AspectMode', aspect_mode)

            # Border display mode (Only VIC-II, VIC-I, and TED chips support borders)
            if chip in ('VICII', 'VIC', 'TED'):
                config.set(system_core, f'{chip}BorderMode', border_mode)

        if self.config.use_guns and self.guns:
            if self.metadata.get('gun_type') == 'stack_light_rifle':
                joyport1 = '15'
            else:
                joyport1 = '14'
        else:
            joyport1 = '1'
        config.set(system_core, 'JoyPort1Device', joyport1)

        config.set(system_core, 'JoyDevice1', '4')
        if system_core != 'VIC20':
            config.set(system_core, 'JoyDevice2', '4')
        config.set(system_core, 'JoyMapFile', str(joymap))

        # custom : allow the user to configure directly sdl-vicerc via batocera.conf via lines like : vice.section.option=value
        for section_option, user_config_value in self.config.items(starts_with='vice.'):
            custom_section, _, custom_option = section_option.partition('.')
            if not config.has_section(custom_section):
                config.add_section(custom_section)
            config.set(custom_section, custom_option, user_config_value)

        with vicerc.open('w') as configfile:
            config.write(_EqualsSpaceRemover(configfile))

        return joymap

    def _write_joymap(self, joymap: Path) -> None:
        # vic20 uses a slightly different port
        joy_port = '0' if self.core == 'xvic' else '1'

        lines = ['# Batocera configured controllers', '', '!CLEAR']
        for pad in self.controllers:
            lines.append('')
            lines.append(f'# {pad.real_name}')
            for input_name, input_value in pad.inputs.items():
                if input_name in _VICE_JOYSTICK:
                    line = _VICE_JOYSTICK[input_name]
                    line = line.replace('#', str(pad.index)).replace('?', str(input_value.id))
                    lines.append(line.replace('/', joy_port))
            lines.append('')

        joymap.write_text('\n'.join(lines) + '\n')

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)

        joymap = self._write_vicerc()
        self._write_joymap(joymap)

        return Command(
            [self.core, self.rom],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
