from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Final

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, LibretroConfig
from batocera_launch_mame_common import (
    MameControlScheme,
    MessSystemInfo,
    PadConfigMixin,
    load_mame_control_scheme,
    reverse_mapping,
    write_pad_config,
)

from .command import build_command_line, write_cmd_file

if TYPE_CHECKING:
    from batocera_launch import Controller, Gun

# RetroPad inputs as seen by the MAME libretro core
_RETRO_PAD: Final = {
    'joystick1up': 'YAXIS_UP_SWITCH',
    'joystick1down': 'YAXIS_DOWN_SWITCH',
    'joystick1left': 'XAXIS_LEFT_SWITCH',
    'joystick1right': 'XAXIS_RIGHT_SWITCH',
    'up': 'HAT{0}UP',
    'down': 'HAT{0}DOWN',
    'left': 'HAT{0}LEFT',
    'right': 'HAT{0}RIGHT',
    'joystick2up': 'RYAXIS_NEG_SWITCH',
    'joystick2down': 'RYAXIS_POS_SWITCH',
    'joystick2left': 'RXAXIS_NEG_SWITCH',
    'joystick2right': 'RXAXIS_POS_SWITCH',
    'b': 'BUTTON1',
    'a': 'BUTTON2',
    'y': 'BUTTON3',
    'x': 'BUTTON4',
    'pageup': 'BUTTON5',
    'pagedown': 'BUTTON6',
    'l2': 'RZAXIS_POS_SWITCH',
    'r2': 'ZAXIS_POS_SWITCH',
    'l3': 'BUTTON12',
    'r3': 'BUTTON11',
    'select': 'SELECT',
    'start': 'START',
}


def _format_hat(code: str, joycode: int, /) -> str:
    return code.format(joycode) if '{0}' in code else code


def _retropad_definition(
    key: str, retropad_input: str, joycode: int, /, *, alt_buttons: MameControlScheme, ignore_axis: bool = False
) -> str:
    if 'BUTTON' in retropad_input or 'HAT' in retropad_input or retropad_input in {'START', 'SELECT'}:
        return f'JOYCODE_{joycode}_{_format_hat(retropad_input, joycode)}'

    if 'AXIS' not in retropad_input:
        return 'unknown'

    if alt_buttons == 'qbert':
        if key in {'joystick1up', 'up'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD["joystick1up"]}_{joycode}_{_RETRO_PAD["joystick1right"]} OR '
                f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["up"], joycode)} JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["right"], joycode)}'
            )
        if key in {'joystick1down', 'down'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD["joystick1down"]} JOYCODE_{joycode}_{_RETRO_PAD["joystick1left"]} OR '
                f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["down"], joycode)} JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["left"], joycode)}'
            )
        if key in {'joystick1left', 'left'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD["joystick1left"]} JOYCODE_{joycode}_{_RETRO_PAD["joystick1up"]} OR '
                f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["left"], joycode)} JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["up"], joycode)}'
            )
        if key in {'joystick1right', 'right'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD["joystick1right"]} JOYCODE_{joycode}_{_RETRO_PAD["joystick1down"]} OR '
                f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["right"], joycode)} JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["down"], joycode)}'
            )
        return f'JOYCODE_{joycode}_{retropad_input}'

    if ignore_axis:
        if key in {'joystick1up', 'up'}:
            return f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["up"], joycode)}'
        if key in {'joystick1down', 'down'}:
            return f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["down"], joycode)}'
        if key in {'joystick1left', 'left'}:
            return f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["left"], joycode)}'
        if key in {'joystick1right', 'right'}:
            return f'JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["right"], joycode)}'
    else:
        if key in {'joystick1up', 'up'}:
            return f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["up"], joycode)}'
        if key in {'joystick1down', 'down'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["down"], joycode)}'
            )
        if key in {'joystick1left', 'left'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["left"], joycode)}'
            )
        if key in {'joystick1right', 'right'}:
            return (
                f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_format_hat(_RETRO_PAD["right"], joycode)}'
            )
        if key == 'joystick2up':
            return f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_RETRO_PAD["x"]}'
        if key == 'joystick2down':
            return f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_RETRO_PAD["b"]}'
        if key == 'joystick2left':
            return f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_RETRO_PAD["y"]}'
        if key == 'joystick2right':
            return f'JOYCODE_{joycode}_{_RETRO_PAD[key]} OR JOYCODE_{joycode}_{_RETRO_PAD["a"]}'

        return f'JOYCODE_{joycode}_{retropad_input}'

    return 'unknown'


@cached_dataclass
class Mame(PadConfigMixin, Core):
    gun_mapping: ClassVar = {'default': {'p1': 0, 'p2': 1, 'p3': 2}}

    @cached_property
    def library_prefix(self) -> str:
        return 'mame'

    @cached_property
    def mess_system_info(self) -> MessSystemInfo | None:
        return MessSystemInfo.load(self.system)

    @cached_property
    def mame_control_scheme(self) -> MameControlScheme:
        return load_mame_control_scheme(self.config.get_str('altlayout', 'auto'), self.rom.id)

    @cached_property
    def rom_argument(self) -> str | Path | None:
        return Path('/var/run/cmdfiles') / f'{self.rom.id}.cmd'

    def generate_pad_sequence(
        self,
        controller: Controller,
        key: str,
        /,
        *,
        reversed: bool = False,
        ignore_axis: bool = False,
        mapping: str = '',
        player_number: int = 1,
        input_key: str | None = None,
    ) -> str:
        lookup = input_key if input_key is not None else key

        if reversed:
            reverse = reverse_mapping(lookup)
            lookup = reverse if reverse is not None else lookup

        if lookup not in _RETRO_PAD:
            sequence = 'unknown'
        else:
            sequence = _retropad_definition(
                key,
                _RETRO_PAD[lookup],
                controller.index + 1,
                alt_buttons=self.mame_control_scheme,
                ignore_axis=ignore_axis,
            )

        if mapping == 'COIN' and player_number == 1:
            return f'{sequence} OR KEYCODE_{player_number}_F{player_number + 11}'

        return sequence

    def should_configure_pads(self) -> bool:
        return not (self.config.use_guns and self.guns)

    def can_reverse_pad_mapping(self, controller: Controller, reversed_key: str, /) -> bool:
        return reversed_key in _RETRO_PAD

    def should_emit_unbound_pad_mapping(self) -> bool:
        return True

    def should_overwrite_system_cfg(self, cfg_path: Path, mess_system_name: str, alt_cfg_exists: bool, /) -> bool:
        custom_cfg = self.config.get_bool('customcfg')
        per_game_cfg = self.config.get_bool('pergamecfg')
        return not (alt_cfg_exists and (custom_cfg or per_game_cfg))

    def ui_select_key(self) -> str:
        return 'a'

    def generate_special_configs(self) -> None:
        super().generate_special_configs()

        command_line, cfg_path, mess_model, special_controller = build_command_line(self)
        write_cmd_file(self, command_line)
        write_pad_config(self, cfg_path, mess_model, special_controller)

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Lightgun mode
        core_options.set('mame_lightgun_mode', 'lightgun')

        # Enable cheats
        core_options.set('mame_cheats_enable', 'enabled')

        # CPU Overclock
        core_options.set_from_config('mame_cpu_overclock', default='default')

        # Video Resolution
        core_options.set_from_config('mame_altres', default='640x480')

        # Disable controller profiling
        core_options.set('mame_buttons_profiles', 'disabled')

        # Software Lists (MESS)
        core_options.set('mame_softlists_enable', 'disabled')
        core_options.set('mame_softlists_auto_media', 'disabled')

        # Enable config reading (for controls)
        core_options.set('mame_read_config', 'enabled')

        # Use CLI (via CMD file) to boot
        core_options.set('mame_boot_from_cli', 'enabled')

        # Activate mouse for Mac & Archimedes
        core_options.set('mame_mouse_enable', 'enabled' if self.system in {'macintosh', 'archimedes'} else 'disabled')

    def get_pedal_config_name_for_player(self, player_number: int, /) -> str:
        return f'input_player{player_number}_gun_aux_a'

    def set_gun_config_for_player(self, custom_config: LibretroConfig, player_number: int, gun: Gun, /) -> None:
        custom_config.set(f'input_player{player_number}_gun_offscreen_shot_mbtn', '')
        custom_config.set(f'input_player{player_number}_gun_aux_a_mbtn', 2)
        custom_config.set(f'input_player{player_number}_start_mbtn', 3)
        custom_config.set(f'input_player{player_number}_select_mbtn', 4)
